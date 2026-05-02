#!/usr/bin/env python3
"""
ProductHunt新产品→即刻/知乎产品评测
从Hacker News Show HN / V2EX抓取真实产品讨论，生成中文评测

数据源（按优先级）：
  1. Hacker News Show HN — 独立开发者展示产品，与ProductHunt最接近
  2. V2EX hot/latest — 中文社区的产品讨论
"""

import subprocess
import json
import os
import sys
from pathlib import Path

AUTOCLI = os.path.expanduser("~/.local/bin/autocli")
OUTPUT_DIR = Path(os.path.expanduser("~/.hermes_output/producthunt_review"))

# 产品关键词过滤——只保留和"产品/工具/项目"相关的话题
PRODUCT_KEYWORDS = [
    "app", "tool", "cli", "api", "平台", "工具", "开源", "发布",
    "show hn", "launched", "built", "create", "made",
    "启动", "上线", "推出", "开发", "项目", "产品",
    "ai", "gpt", "llm", "agent", "自动化", "编辑器",
    "saas", "service", "platform", "framework", "library",
    "库", "框架", "服务", "网站", "系统",
]


def run_autocli(cmd_args: list, timeout: int = 30) -> list | None:
    """Run autocli command and parse JSON output."""
    full_cmd = [AUTOCLI] + cmd_args + ["--format", "json"]
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            print(f"⚠️ autocli 命令失败: {' '.join(cmd_args)}", file=sys.stderr)
            print(f"  stderr: {result.stderr[:200]}", file=sys.stderr)
            return None
        data = json.loads(result.stdout)
        if isinstance(data, list):
            return data
        return None
    except Exception as e:
        print(f"⚠️ autocli 执行异常: {e}", file=sys.stderr)
        return None


def is_product_like(post: dict) -> bool:
    """判断是否像产品发布/工具分享帖."""
    title = post.get("title", "").lower()
    for kw in PRODUCT_KEYWORDS:
        if kw in title:
            return True
    return False


def fetch_hackernews_products(limit: int = 5) -> list[dict]:
    """从Hacker News Show HN抓取产品."""
    posts = run_autocli(["hackernews", "show", "--limit", str(limit + 5)])
    if posts is None:
        return []
    
    products = []
    for p in posts:
        products.append({
            "name": p["title"].replace("Show HN: ", "").replace("Show HN:", "").strip(),
            "tagline": f"由 {p.get('author', 'unknown')} 发布于 Hacker News",
            "upvotes": p.get("score", 0),
            "comments": p.get("comments", 0),
            "url": p.get("url", ""),
            "source": "Hacker News",
            "author": p.get("author", ""),
        })
        if len(products) >= limit:
            break
    return products


def fetch_v2ex_products(limit: int = 5) -> list[dict]:
    """从V2EX热门话题抓取产品讨论."""
    # 先拿hot榜，再拿latest榜补充
    all_posts = []
    hot = run_autocli(["v2ex", "hot", "--limit", "10"])
    latest = run_autocli(["v2ex", "latest", "--limit", "10"])
    
    if hot:
        all_posts.extend(hot)
    if latest:
        all_posts.extend(latest)
    
    # 去重
    seen = set()
    unique = []
    for p in all_posts:
        t = p.get("title", "")
        if t not in seen:
            seen.add(t)
            unique.append(p)
    
    products = []
    for p in unique:
        title = p.get("title", "")
        replies = p.get("replies", 0)
        
        # 判断是否像产品
        if not is_product_like(p):
            continue
        
        products.append({
            "name": title,
            "tagline": f"V2EX 热门讨论 · {replies} 条回复",
            "upvotes": replies,
            "comments": replies,
            "url": "",
            "source": "V2EX",
            "author": "",
        })
        if len(products) >= limit:
            break
    
    return products


def fetch_products(limit: int = 5) -> list[dict]:
    """主抓取函数，按优先级尝试数据源."""
    # 优先 Hacker News
    products = fetch_hackernews_products(limit)
    if products:
        print(f"📡 数据源: Hacker News Show HN", file=sys.stderr)
        return products
    
    # 备选 V2EX
    products = fetch_v2ex_products(limit)
    if products:
        print(f"📡 数据源: V2EX 热门话题", file=sys.stderr)
        return products
    
    # 都没数据
    print("❌ 所有数据源均无法获取", file=sys.stderr)
    return []


def generate_jike_post(product: dict) -> str:
    """生成即刻风格动态."""
    name = product["name"]
    tagline = product["tagline"]
    upvotes = product["upvotes"]
    source = product["source"]
    
    text = f"""
发现了一个有意思的产品：{name}

{tagline}

{'ProductHunt' if source == 'Hacker News' else source}热度 {upvotes} {'👍' if source == 'Hacker News' else '💬'}，说明很多人在关注。

{'#产品 #工具' if source == 'Hacker News' else '#V2EX #产品推荐'}
"""
    return text.strip()


def generate_zhihu_review(product: dict) -> str:
    """生成知乎风格评测."""
    name = product["name"]
    upvotes = product["upvotes"]
    source = product["source"]
    comments = product.get("comments", 0)
    
    text = f"""
## 一、产品简介
{name}

## 二、热度分析
该产品在{source}上获得了 {upvotes} 个{'赞' if source == 'Hacker News' else '回复'}、{comments} 条讨论，说明市场关注度较高。

## 三、核心价值
{product.get('tagline', '待深入了解')}

## 四、适用人群
- 独立开发者
- 技术爱好者
- 效率工具控

## 五、总结
{name} 在开发者社区获得了不错的反响。建议实际体验后再做判断。

推荐指数：⭐⭐⭐⭐
"""
    return text.strip()


def ensure_output_dir():
    """确保输出目录存在."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_product(product: dict, index: int):
    """保存单个产品信息到输出目录."""
    safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in product["name"][:50])
    filepath = OUTPUT_DIR / f"{index:02d}_{safe_name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(product, f, ensure_ascii=False, indent=2)


def main():
    ensure_output_dir()
    
    products = fetch_products(limit=5)
    
    if not products:
        print("❌ 没有获取到产品数据，请稍后重试")
        return
    
    print("🚀 新产品发现 → 即刻/知乎评测\n")
    print("=" * 50)
    
    for i, product in enumerate(products, 1):
        save_product(product, i)
        
        jike_post = generate_jike_post(product)
        zhihu_review = generate_zhihu_review(product)
        
        print(f"\n🔥 产品 #{i}")
        print(f"名称: {product['name']}")
        print(f"Slogan: {product['tagline']}")
        print(f"{'👍' if product['source'] == 'Hacker News' else '💬'} 热度: {product['upvotes']}")
        print(f"来源: {product['source']}")
        if product.get("url"):
            print(f"链接: {product['url']}")
        print()
        print("【即刻动态】")
        print(jike_post)
        print("\n【知乎评测】")
        print(zhihu_review)
        print("\n" + "-" * 50)


if __name__ == "__main__":
    main()
