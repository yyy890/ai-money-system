#!/usr/bin/env python3
"""
GMGN + XAPI 链上+社交搜索 Meme异动监控
组合链上数据 + 社交热度，发现潜在机会
"""
import json
import os
import subprocess
import re
from datetime import datetime

AUTOCLI = os.path.expanduser("~/.local/bin/autocli")
REFERRAL_LINK = "https://grvt.io/?ref=Z1HABCU"

def run_autocli(cmd_list):
    try:
        result = subprocess.run(
            [AUTOCLI] + cmd_list,
            capture_output=True, text=True, timeout=25
        )
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            if output.startswith("[") or output.startswith("{"):
                return json.loads(output)
            return output
        return []
    except:
        return []

def fetch_crypto_trending():
    """从Twitter获取加密热门话题"""
    tweets = run_autocli(["twitter", "search", "meme coin solana ETH 异动", "--limit", "8", "--format", "json"])
    result = []
    seen = set()
    if tweets and isinstance(tweets, list):
        for t in tweets:
            text = t.get("text", "")
            # 提取可能的币种/合约地址
            coins = re.findall(r'\$([A-Z]{2,10})', text)
            addresses = re.findall(r'0x[a-fA-F0-9]{40}', text)
            
            if coins or addresses or any(kw in text.lower() for kw in ["meme", "暴涨", "异动", "fomo", "moon", "sol"]):
                key = text[:50]
                if key not in seen:
                    seen.add(key)
                    result.append({
                        "text": text[:300],
                        "author": t.get("author", "?"),
                        "likes": t.get("likes", 0),
                        "coins": coins,
                        "addresses": addresses[:2]
                    })
    return result[:8]

def fetch_gmgn_data():
    """尝试通过gmgn wrapper获取链上数据"""
    try:
        # 尝试爬gmgn.ai热门
        result = subprocess.run(
            ["curl", "-s", "https://gmgn.ai/api/v1/meme/trending?limit=10"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except:
        pass
    return None

def main():
    output_dir = os.path.expanduser("~/hermes_output/meme_monitor")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(output_dir, f"meme_anomaly_{timestamp}.txt")
    
    print("🐶🧵 GMGN + XAPI Meme异动监控\n")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print("=" * 60)
    
    # 社交搜索（XAPI替代）
    print("\n📡 社交热度扫描 (XAPI风格)...")
    tweets = fetch_crypto_trending()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"🐶 GMGN + XAPI Meme异动监控\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        
        if tweets:
            print(f"  发现 {len(tweets)} 个潜在异动信号\n")
            f.write(f"📊 发现 {len(tweets)} 个潜在异动信号\n\n")
            
            for i, tweet in enumerate(tweets, 1):
                coins_str = ", ".join(tweet.get('coins', [])) or "未知"
                print(f"  #{i} 币种: {coins_str}")
                print(f"     来源: @{tweet['author']} | 👍{tweet['likes']}")
                print(f"     内容: {tweet['text'][:100]}")
                print(f"     热度分: {min(tweet['likes'] * 10 + 50, 100)}/100")
                print()
                
                f.write(f"🔹 信号 #{i}\n")
                f.write(f"   币种: {coins_str}\n")
                f.write(f"   来源: @{tweet['author']} | 👍{tweet['likes']}\n")
                f.write(f"   热度: {min(tweet['likes'] * 10 + 50, 100)}/100\n")
                f.write(f"   内容: {tweet['text'][:200]}\n")
                if tweet.get('addresses'):
                    f.write(f"   合约: {tweet['addresses'][0][:20]}...\n")
                f.write("\n")
        else:
            print("  ⚠️ 当前无meme异动信号")
            f.write("📊 当前无meme异动信号\n\n")
        
        f.write(f"\n💡 策略建议:\n")
        f.write(f"  1. 关注高热度+高点赞的币种\n")
        f.write(f"  2. 多链同名币可能有联动机会\n")
        f.write(f"  3. 结合链上数据确认成交量\n\n")
        f.write(f"🔗 GRVT 交易: {REFERRAL_LINK}\n")
    
    print(f"\n✅ 报告已保存: {output_file}")

if __name__ == "__main__":
    main()
