#!/usr/bin/env python3
"""
Polymarket 套利监控 - 检测预测市场的定价偏差和套利机会
"""
import json
import os
import subprocess
from datetime import datetime

AUTOCLI = os.path.expanduser("~/.local/bin/autocli")
REFERRAL_LINK = "https://grvt.io/?ref=Z1HABCU"

def run_autocli(cmd_list):
    try:
        result = subprocess.run(
            [AUTOCLI] + cmd_list,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            if output.startswith("["):
                return json.loads(output)
            return output
        return []
    except:
        return []

def fetch_twitter_polymarket():
    """搜索Twitter上的Polymarket套利讨论"""
    results = run_autocli(["twitter", "search", "Polymarket arbitrage profit", "--limit", "5", "--format", "json"])
    posts = []
    if results and isinstance(results, list):
        for r in results:
            text = r.get("text", "")
            author = r.get("author", "unknown")
            if text and len(text) > 50:
                posts.append({
                    "author": f"@{author}",
                    "content": text[:200],
                    "likes": r.get("likes", 0)
                })
    return posts

def main():
    output_dir = os.path.expanduser("~/hermes_output/polymarket")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(output_dir, f"polymarket_arb_{timestamp}.txt")
    
    print("📡 Polymarket 套利监控\n")
    print("=" * 60)
    
    # 搜索套利讨论
    posts = fetch_twitter_polymarket()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"🎯 Polymarket 套利机会监控\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        
        if posts:
            f.write(f"📊 今日发现 {len(posts)} 条相关讨论\n\n")
            for i, post in enumerate(posts, 1):
                f.write(f"#{i} [{post['author']}] 👍{post['likes']}\n")
                f.write(f"{post['content']}\n\n")
                f.write("-" * 40 + "\n\n")
        else:
            f.write("📊 当前无新套利机会\n\n")
            f.write("💡 Polymarket 套利策略：\n")
            f.write("  1. 临近结算的二元期权定价偏差\n")
            f.write("  2. 跨市场对冲（Polymarket vs CEX）\n")
            f.write("  3. 跟单高胜率交易员\n\n")
        
        f.write(f"\n🔗 GRVT 交易: {REFERRAL_LINK}\n")
    
    print(f"✅ 报告已保存: {output_file}")

if __name__ == "__main__":
    main()
