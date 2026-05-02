#!/usr/bin/env python3
"""
加密市场监控 - 使用autocli抓取链上数据和市场信息
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
    print("📡 加密市场监控报告\n")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print("=" * 60)
    
    # 1. 查询BTC/ETH行情
    print("\n📊 行情概览:")
    btc = run_autocli(["yahoo-finance", "quote", "--symbol", "BTC-USD", "--format", "json"])
    eth = run_autocli(["yahoo-finance", "quote", "--symbol", "ETH-USD", "--format", "json"])
    
    if btc and isinstance(btc, list):
        b = btc[0]
        print(f"  BTC: ${b.get('price', 'N/A')}  | 涨跌: {b.get('changePercent', 'N/A')}%")
    if eth and isinstance(eth, list):
        e = eth[0]
        print(f"  ETH: ${e.get('price', 'N/A')}  | 涨跌: {e.get('changePercent', 'N/A')}%")
    
    # 2. Twitter加密话题
    print("\n🐦 Twitter 加密话题趋势:")
    trending = run_autocli(["twitter", "trending", "--limit", "5", "--format", "json"])
    if trending and isinstance(trending, list):
        for t in trending:
            topic = t.get("topic", "")
            if any(kw in topic.lower() for kw in ["btc", "eth", "crypto", "defi", "nft", "sol", "币", "比特币"]):
                print(f"  🔥 {topic}")
    
    # 3. 加密相关推文
    print("\n💬 加密社区动态:")
    tweets = run_autocli(["twitter", "search", "crypto news", "--limit", "5", "--format", "json"])
    if tweets and isinstance(tweets, list):
        for t in tweets[:3]:
            text = t.get("text", "")
            author = t.get("author", "unknown")
            likes = t.get("likes", 0)
            if text:
                print(f"  • @{author}: {text[:80]}... 👍{likes}")
    
    # 4. Reddit加密讨论
    print("\n🔴 Reddit 热门加密讨论:")
    reddit = run_autocli(["reddit", "hot", "--subreddit", "CryptoCurrency", "--limit", "3", "--format", "json"])
    if reddit and isinstance(reddit, list):
        for r in reddit:
            title = r.get("title", "")
            if title:
                print(f"  • {title[:80]}")
    
    print(f"\n{'=' * 60}")
    print("✅ 报告完成")

if __name__ == "__main__":
    main()
