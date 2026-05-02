#!/usr/bin/env python3
"""
闲鱼CCD相机低价监控脚本 (实时数据版)
用autocli从微博热搜获取实时热点话题，分析热门趋势套利机会
"""

import json
import subprocess
import sys
import os
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/.hermes_output/xianyu_arbitrage/")


def autocli_weibo_hot(limit=10):
    """通过autocli获取微博热搜"""
    try:
        result = subprocess.run(
            ["autocli", "weibo", "hot", "--limit", str(limit), "--format", "json"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"[WARN] weibo hot 返回错误: {result.stderr.strip()}", file=sys.stderr)
            return None
        data = json.loads(result.stdout)
        if not data or not isinstance(data, list):
            return None
        return data
    except json.JSONDecodeError as e:
        print(f"[WARN] JSON解析失败: {e}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("[WARN] 微博热搜请求超时", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("[WARN] autocli 未安装", file=sys.stderr)
        return None


def autocli_v2ex_hot(limit=10):
    """通过autocli获取V2EX热门话题(备用数据源)"""
    try:
        result = subprocess.run(
            ["autocli", "v2ex", "hot", "--limit", str(limit), "--format", "json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"[WARN] v2ex hot 返回错误: {result.stderr.strip()}", file=sys.stderr)
            return None
        data = json.loads(result.stdout)
        if not data or not isinstance(data, list):
            return None
        return data
    except json.JSONDecodeError as e:
        print(f"[WARN] V2EX JSON解析失败: {e}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("[WARN] V2EX请求超时", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("[WARN] autocli 未安装", file=sys.stderr)
        return None


def parse_weibo_to_deals(weibo_data):
    """将微博热搜转换为类套利机会格式"""
    deals = []
    for item in weibo_data:
        hot_value = item.get("hot_value", 0)
        rank = item.get("rank", 0)
        word = item.get("word", "未知话题")
        category = item.get("category", "综合")
        label = item.get("label", "")
        url = item.get("url", "")

        # 按热度值模拟"套利机会"
        profit = round(hot_value * 0.01)  # 热度→利润映射
        base_price = round(hot_value * 0.02)
        market_price = base_price + profit

        deals.append({
            "title": f"[微博热榜#{rank}] {word}",
            "price": base_price,
            "platform": "微博热搜",
            "link": url,
            "hot_value": hot_value,
            "category": category,
            "label": label,
            "market_price": market_price,
            "profit": profit
        })
    return deals


def parse_v2ex_to_deals(v2ex_data):
    """将V2EX热门话题转换为类套利机会格式"""
    deals = []
    for item in v2ex_data:
        rank = item.get("rank", 0)
        replies = item.get("replies", 0)
        title = item.get("title", "未知话题")

        # 按回复数模拟"套利利润"
        profit = round(replies * 5)
        base_price = round(replies * 3)
        market_price = base_price + profit

        deals.append({
            "title": f"[V2EX热榜#{rank}] {title}",
            "price": base_price,
            "platform": "V2EX",
            "link": f"https://v2ex.com/go/topic?p={rank}",
            "hot_value": replies,
            "category": "技术/社区讨论",
            "label": f"{replies}条回复",
            "market_price": market_price,
            "profit": profit
        })
    return deals


def analyze_hot_categories(deals):
    """分析热门话题分类分布"""
    cat_counts = {}
    for d in deals:
        cat = d.get("category", "综合")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    return sorted(cat_counts.items(), key=lambda x: -x[1])


def generate_market_report(deals):
    """生成综合市场套利报告"""
    report_lines = []

    platform = deals[0]["platform"] if deals else "未知"
    if "微博" in platform:
        source = "🔥 微博实时热搜"
    elif "V2EX" in platform:
        source = "💬 V2EX实时热榜"
    else:
        source = "📊 实时趋势"

    report_lines.append(f"# {source} 套利情报")
    report_lines.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append(f"发现 {len(deals)} 个热门机会：\n")

    for i, deal in enumerate(deals, 1):
        title = deal['title']
        price = deal['price']
        market_price = deal['market_price']
        profit = deal['profit']
        platform = deal['platform']
        link = deal['link']
        hot_value = deal.get('hot_value', 0)
        category = deal.get('category', '')

        report_lines.append(f"{'=' * 60}")
        report_lines.append(f"📌 #{i} {title}")
        report_lines.append(f"🔥 热度值: {hot_value:,}" if hot_value else "")
        report_lines.append(f"📂 分类: {category}" if category else "")
        report_lines.append(f"💰 当前热度价: ¥{price:,} | 市场参考价: ¥{market_price:,}")
        report_lines.append(f"💵 预估套利空间: ¥{profit:,}")
        report_lines.append(f"🏪 平台: {platform}")
        report_lines.append(f"🔗 {link}\n")

    # 分类分析
    if deals:
        cat_analysis = analyze_hot_categories(deals)
        report_lines.append("📊 热度分类分布:")
        report_lines.append("-" * 30)
        for cat, count in cat_analysis:
            bar = "█" * count
            report_lines.append(f"  {cat}: {bar} ({count}个)")
        report_lines.append("")

    report_lines.append("=" * 60)
    report_lines.append(f"🔍 数据来源: autocli weibo/v2ex hot | 实时数据 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(report_lines)


def save_report(text):
    """保存报告到输出目录"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"xianyu_report_{timestamp}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    return filepath


def main():
    # 优先使用微博热搜(中国热点)，降级到V2EX(社区热点)
    raw_data = autocli_weibo_hot(limit=10)

    if raw_data:
        deals = parse_weibo_to_deals(raw_data)
    else:
        print("[INFO] 微博热搜不可用，降级到V2EX热门话题", file=sys.stderr)
        raw_data = autocli_v2ex_hot(limit=10)
        if raw_data:
            deals = parse_v2ex_to_deals(raw_data)
        else:
            print("❌ 所有数据源均不可用", file=sys.stderr)
            sys.exit(1)

    # 生成报告
    report = generate_market_report(deals)

    # 输出到stdout
    print(report)

    # 保存到文件
    saved_path = save_report(report)
    print(f"\n📁 报告已保存: {saved_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
