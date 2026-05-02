#!/usr/bin/env python3
"""
GitHub Trending→掘金/CSDN技术内容
抓取HackerNews/DevTo热门内容，生成技术文章（替代原Mock数据方案）
"""

import json
import subprocess
import sys
import os
from datetime import datetime

AUTOCLI_PATH = os.path.expanduser("~/.local/bin/autocli")
OUTPUT_DIR = os.path.expanduser("~/.hermes_output/github_tech/")


def run_autocli(args):
    """Run autocli command and return parsed JSON data."""
    cmd = [AUTOCLI_PATH] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as e:
        print(f"⚠ autocli 错误: {e}", file=sys.stderr)
    return None


def fetch_hackernews_top(limit=5):
    """Fetch top HackerNews stories."""
    data = run_autocli(["hackernews", "top", "--limit", str(limit), "--format", "json"])
    if data:
        items = []
        for item in data[:limit]:
            items.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "author": item.get("author", ""),
                "score": item.get("score", 0),
                "comments": item.get("comments", 0),
                "source": "HackerNews",
                "category": guess_category(item.get("title", "")),
            })
        return items
    return None


def fetch_devto_top(limit=5):
    """Fetch top DEV.to articles."""
    data = run_autocli(["devto", "top", "--limit", str(limit), "--format", "json"])
    if data:
        items = []
        for item in data[:limit]:
            items.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "author": item.get("author", ""),
                "reactions": item.get("reactions", 0),
                "comments": item.get("comments", 0),
                "tags": item.get("tags", ""),
                "source": "DevTo",
                "category": guess_category(item.get("title", "")),
            })
        return items
    return None


def fetch_devto_by_tag(tag, limit=3):
    """Fetch DEV.to articles by tag."""
    data = run_autocli(["devto", "tag", tag, "--limit", str(limit), "--format", "json"])
    if data:
        items = []
        for item in data[:limit]:
            items.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "author": item.get("author", ""),
                "reactions": item.get("reactions", 0),
                "comments": item.get("comments", 0),
                "tags": item.get("tags", ""),
                "source": f"DevTo #{tag}",
                "category": tag.capitalize(),
            })
        return items
    return None


def guess_category(title):
    """Guess category from title keywords."""
    title_lower = title.lower()
    if any(kw in title_lower for kw in ["ai", "machine learning", "llm", "gpt", "neural", "deep learning", "copilot"]):
        return "AI/机器学习"
    elif any(kw in title_lower for kw in ["react", "vue", "css", "tailwind", "ui", "frontend", "web", "component"]):
        return "前端/UI"
    elif any(kw in title_lower for kw in ["rust", "go", "python", "java", "c++", "typescript", "javascript", "programming"]):
        return "编程语言"
    elif any(kw in title_lower for kw in ["docker", "kubernetes", "k8s", "devops", "deploy", "cloud", "aws"]):
        return "云计算/DevOps"
    elif any(kw in title_lower for kw in ["security", "privacy", "hack", "vuln", "cve"]):
        return "安全"
    elif any(kw in title_lower for kw in ["database", "sql", "nosql", "redis", "postgres", "mongo"]):
        return "数据库"
    elif any(kw in title_lower for kw in ["linux", "kernel", "os", "system", "performance"]):
        return "系统/运维"
    else:
        return "技术综合"


def generate_article_title(item):
    """Generate Chinese tech article title."""
    title = item["title"]
    source = item["source"]
    category = item["category"]
    return f"🔥 {title} | {source}精选 | {category}"


def generate_article(item):
    """Generate Chinese tech article content."""
    title = item["title"]
    url = item.get("url", "")
    author = item.get("author", "")
    source = item["source"]
    category = item["category"]
    score = item.get("score", item.get("reactions", ""))
    comments = item.get("comments", 0)

    article = f"""
## 文章概述
**{title}**

来自 {source} 的热门内容，作者 {author}，当前获得 {score} 分/赞，共 {comments} 条评论。

## 亮点
- 📌 **来源**: {source}
- 👤 **作者**: {author}
- 🏷️ **分类**: {category}
- 💬 **讨论热度**: {comments} 条评论

## 为什么值得关注？
这是 {source} 当前最热门的技术内容之一，反映了开发者社区的关注焦点。
- 高互动量（{comments} 条评论）说明社区讨论活跃
- 内容涉及 {category} 领域的最新动态

## 延伸阅读
- 原文链接: {url}
- 更多类似内容可关注 {source}

---

> 本文由自动化脚本生成，数据来源 {source}
"""
    return article


def save_to_file(content, prefix="hackernews"):
    """Save content to output directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{prefix}_{timestamp}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def main():
    print("💻 GitHub Trending→掘金/CSDN技术文章 (实时数据版)\n")
    print("=" * 50)

    all_items = []

    # 1) Fetch HackerNews top stories
    print("\n📡 正在从 HackerNews 获取热门...", file=sys.stderr)
    hn_items = fetch_hackernews_top(5)
    if hn_items:
        all_items.extend(hn_items)
        print(f"✅ 获取到 {len(hn_items)} 条 HackerNews 内容", file=sys.stderr)
    else:
        print("⚠ HackerNews 抓取失败", file=sys.stderr)

    # 2) Fetch DEV.to top articles
    print("\n📡 正在从 DevTo 获取热门...", file=sys.stderr)
    devto_items = fetch_devto_top(5)
    if devto_items:
        all_items.extend(devto_items)
        print(f"✅ 获取到 {len(devto_items)} 条 DevTo 内容", file=sys.stderr)
    else:
        print("⚠ DevTo 抓取失败", file=sys.stderr)

    # 3) Fetch DEV.to articles by tag (python, webdev)
    for tag in ["python", "webdev"]:
        print(f"\n📡 正在从 DevTo #{tag} 获取...", file=sys.stderr)
        tag_items = fetch_devto_by_tag(tag, 2)
        if tag_items:
            all_items.extend(tag_items)
            print(f"✅ 获取到 {len(tag_items)} 条 DevTo #{tag} 内容", file=sys.stderr)
        else:
            print(f"⚠ DevTo #{tag} 抓取失败", file=sys.stderr)

    # 兜底: 如果完全没数据，用fallback内容
    if not all_items:
        print("\n⚠ 所有数据源均无法获取，使用兜底内容\n", file=sys.stderr)
        all_items = [
            {
                "title": "无法获取实时数据，请检查网络和 autocli 配置",
                "url": "",
                "author": "System",
                "source": "Fallback",
                "category": "技术综合",
                "score": 0,
                "comments": 0,
            }
        ]

    # 同时保存到文件
    md_content = f"# 技术热点日报 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
    md_content += f"共 {len(all_items)} 条内容 | 来源: HackerNews + DevTo\n\n"

    for i, item in enumerate(all_items, 1):
        article_title = generate_article_title(item)
        content = generate_article(item)

        # stdout输出（供cron捕获）
        print(f"\n⭐ 项目 #{i} - {item['category']}")
        print(f"来源: {item['source']} | 作者: {item.get('author', 'N/A')}")
        print(f"标题: {item['title']}")
        print(f"链接: {item.get('url', 'N/A')}\n")
        print(f"【掘金/CSDN标题】")
        print(article_title)
        print(f"\n【文章正文】")
        print(content)
        print("\n" + "-" * 50)

        # 拼接markdown内容
        md_content += f"## ⭐ #{i} - {item['category']}\n"
        md_content += f"**{item['title']}**\n\n"
        md_content += f"- 来源: {item['source']} | 作者: {item.get('author', 'N/A')}\n"
        md_content += f"- 链接: {item.get('url', 'N/A')}\n\n"
        md_content += f"{content}\n\n---\n\n"

    # 保存到文件
    saved_path = save_to_file(md_content)
    print(f"\n📁 文件已保存: {saved_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
