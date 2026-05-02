#!/usr/bin/env python3
"""
GRVT 推广内容生成器 - 使用真实市场数据生成推广文案
"""
import json
import os
import subprocess
from datetime import datetime
import random

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
            if output.startswith("["):
                return json.loads(output)
            return output
        return None
    except:
        return None

def fetch_crypto_news():
    """抓取加密市场行情"""
    # 用yahoo-finance查BTC价格
    btc = run_autocli(["yahoo-finance", "quote", "--symbol", "BTC-USD", "--format", "json"])
    eth = run_autocli(["yahoo-finance", "quote", "--symbol", "ETH-USD", "--format", "json"])
    
    result = {}
    if btc and isinstance(btc, list) and len(btc) > 0:
        result['btc'] = btc[0].get('price', 'N/A')
    if eth and isinstance(eth, list) and len(eth) > 0:
        result['eth'] = eth[0].get('price', 'N/A')
    return result

def generate_fee_comparison(market_data):
    """GRVT vs CEX 手续费对比"""
    btc_price = market_data.get('btc', 'N/A')
    eth_price = market_data.get('eth', 'N/A')
    
    return f"""💎 GRVT vs CEX 手续费对比（{datetime.now().strftime('%Y-%m-%d')}）

当前BTC: ${btc_price} | ETH: ${eth_price}

📊 开一单10万U的BTC永续合约，手续费差多少？

| 平台 | Maker | Taker |
|------|-------|-------|
| Binance | 0.02% = $20 | 0.05% = $50 |
| Bybit | 0.01% = $10 | 0.06% = $60 |
| GRVT | 0.00% = $0 | 0.00% = $0 |

🔥 GRVT = 0 gas费 + 0手续费
🚀 支持最高 100x 杠杆
⚡ 基于ZK-Rollup，即时成交

一天开10单，省下 $200-$500！
一年省下几万U不是梦 👇
{REFERRAL_LINK}

#GRVT #永续合约 #交易 #DeFi"""

def generate_feature_intro(market_data):
    """GRVT功能亮点"""
    return f"""🚀 GRVT 凭什么值得一试？

1️⃣ 零 Gas 费
   L3 ZK-Rollup 架构，交易0 gas费
   再也不用心疼以太坊的gas了

2️⃣ 百倍杠杆
   最高 100x，灵活配置仓位
   保证金模式随意切换

3️⃣ 机构级流动性
   Wintermute、Amber Group 等做市商
   滑点极低，大单也能吃

4️⃣ 合规持牌
   百慕大金融管理局（BMA）牌照
   资金安全有保障

5️⃣ 社交交易
   可跟单高手交易员
   新手也能快速上手

📊 当前行情参考：BTC ${market_data.get('btc', 'N/A')}

👇 注册即享VIP费率
{REFERRAL_LINK}

#GRVT #加密交易 #DeFi #永续合约"""

def generate_beginner_guide(market_data):
    """新手教程"""
    return f"""📖 合约新手在GRVT的3步入门

Step 1: 注册
   → 链接钱包（MetaMask/OKX Wallet）
   → 充入 USDT/USDC
   → 全过程＜3分钟

Step 2: 选择交易对
   BTC/USDT | ETH/USDT | SOL/USDT ...
   Maker 0手续费！Taker 0手续费！
   
Step 3: 设置参数
   ✅ 杠杆倍数（建议先5x）
   ✅ 止盈止损（必设！）
   ✅ 逐仓/全仓

💡 新手建议：
   • 先从5x以下开始
   • 每次风险控制在1-2%
   • 设好止损不扛单

📊 BTC现价: ${market_data.get('btc', 'N/A')}

🔗 立即体验：{REFERRAL_LINK}

#GRVT #合约教程 #新手教学 #加密货币"""

def main():
    output_dir = os.path.expanduser("~/hermes_output/grvt_promo")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(output_dir, f"grvt_promo_{timestamp}.txt")
    
    # 获取真实行情数据
    print("📡 获取市场行情...")
    market_data = fetch_crypto_news()
    if not market_data:
        market_data = {'btc': '获取中...', 'eth': '获取中...'}
    
    # 随机选择一种内容类型
    content_types = [
        generate_fee_comparison,
        generate_feature_intro,
        generate_beginner_guide
    ]
    
    all_contents = []
    # 生成所有类型的内容，都保存
    for gen in content_types:
        content = gen(market_data)
        all_contents.append(content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"📢 GRVT 推广内容合集\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"市场行情: BTC ${market_data.get('btc', 'N/A')}\n")
        f.write("=" * 60 + "\n\n")
        
        for i, content in enumerate(all_contents, 1):
            f.write(f"--- 文案 #{i} ---\n\n")
            f.write(content)
            f.write("\n\n" + "=" * 60 + "\n\n")
        
        f.write(f"\n🎯 提示：以上文案可直接发布到 X/Twitter\n")
    
    print(f"✅ GRVT推广内容已保存到: {output_file}")
    print(f"📊 共生成 {len(all_contents)} 套文案")
    print(f"🔗 返佣链接: {REFERRAL_LINK}")

if __name__ == "__main__":
    main()
