#!/usr/bin/env python3
"""
空投监控系统 - 从Twitter/Reddit抓取最新空投信息
"""
import json
import os
import subprocess
from datetime import datetime

AUTOCLI = os.path.expanduser("~/.local/bin/autocli")

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

def main():
    print("🪂 空投监控日报\n")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print("=" * 60)
    
    # 从Twitter搜索空投信息
    print("📡 搜索Twitter空投信息...")
    queries = [
        "airdrop crypto claim",
        "new airdrop 2026",
        "airdrop farming"
    ]
    
    all_airdrops = set()
    
    for query in queries:
        results = run_autocli(["twitter", "search", query, "--limit", "5", "--format", "json"])
        if results and isinstance(results, list):
            for r in results:
                text = r.get("text", "")
                if text and any(kw in text.lower() for kw in ["airdrop", "claim", "farming", "earn"]):
                    all_airdrops.add(text[:150])
    
    if all_airdrops:
        for a in list(all_airdrops)[:5]:
            print(f"\n• {a}")
    else:
        print("\n📭 暂无新的空投信息")
        print("\n💡 关注的空投源：")
        print("  • @airdrops_xyz")
        print("  • @defi_airdrops")
        print("  • Reddit r/airdrops")
    
    # Reddit搜索
    print("\n🔴 Reddit空投讨论:")
    reddit = run_autocli(["reddit", "hot", "--subreddit", "airdrops", "--limit", "3", "--format", "json"])
    if reddit and isinstance(reddit, list):
        for r in reddit:
            title = r.get("title", "")
            if title:
                print(f"  • {title[:100]}")
    
    print(f"\n{'=' * 60}")
    print("✅ 空投监控完成")

if __name__ == "__main__":
    main()
