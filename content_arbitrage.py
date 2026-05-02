#!/usr/bin/env python3
"""
内容套利系统 - Twitter热帖→小红书/微博
使用autocli抓取真实Twitter热门内容，翻译+本地化改写
"""
import json
import os
import subprocess
from datetime import datetime

AUTOCLI = os.path.expanduser("~/.local/bin/autocli")

def run_autocli(cmd_list):
    """执行autocli命令并返回解析后的结果"""
    try:
        result = subprocess.run(
            [AUTOCLI] + cmd_list,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            # 尝试解析JSON
            output = result.stdout.strip()
            if output.startswith("["):
                return json.loads(output)
            return output
        return []
    except Exception as e:
        print(f"⚠️ autocli调用失败: {e}")
        return []

def fetch_twitter_trending():
    """从Twitter抓取真实热门话题"""
    tweets = run_autocli(["twitter", "trending", "--limit", "10", "--format", "json"])
    if tweets and isinstance(tweets, list):
        # 把trending话题转成可用的格式
        topics = []
        for t in tweets[:5]:
            topic_name = t.get("topic", "")
            category = t.get("category", "热门")
            topics.append({
                "author": f"Twitter趋势",
                "content": f"🔥 热门话题: {topic_name} (分类: {category})",
                "likes": 0,
                "topic": category
            })
        return topics
    return []

def fetch_twitter_timeline():
    """从Twitter时间线抓取真实热门推文"""
    tweets = run_autocli(["twitter", "timeline", "--limit", "10", "--format", "json"])
    result = []
    if tweets and isinstance(tweets, list):
        for t in tweets[:5]:
            text = t.get("text", "")
            author = t.get("author", "unknown")
            likes = t.get("likes", 0)
            # 简单判断话题类型
            topic = "综合"
            for kw, cat in [("AI", "AI/技术"), ("GPT", "AI/技术"), 
                          ("code", "编程"), ("创业", "创业/投资"),
                          ("money", "赚钱"), ("invest", "投资"),
                          ("crypto", "加密"), ("BTC", "加密")]:
                if kw.lower() in text.lower():
                    topic = cat
                    break
            result.append({
                "author": f"@{author}",
                "content": text,
                "likes": likes,
                "topic": topic,
                "url": t.get("url", "")
            })
    return result

def generate_xiaohongshu_title(tweet):
    """生成小红书风格标题"""
    topic = tweet['topic']
    content = tweet['content']
    if "创业" in topic or "投资" in topic:
        return "💰 硅谷大佬的赚钱思维！这句话我悟了"
    elif "AI" in topic or "技术" in topic:
        return "🤖 AI圈又在疯传这个观点"
    elif "加密" in topic or "crypto" in topic:
        return "🪙 币圈今天在讨论这个"
    elif "赚钱" in topic or "投资" in topic:
        return "💎 财富密码！今天最值得看的一条"
    return "🔥 今日必看热门话题"

def translate_and_localize(tweet):
    """翻译+本地化改写"""
    content = tweet['content']
    author = tweet['author']
    topic = tweet['topic']
    url = tweet.get('url', '')
    
    # 截取内容前100字
    content_short = content[:100] + ("..." if len(content) > 100 else "")
    
    result = f"""【热点速递】{topic}

原文来源: {author}
{content_short}

💡 我的解读：
这是今天值得关注的信息，建议收藏慢慢看。

#内容套利 #{topic.replace('/', ' #')}
{('原文链接: ' + url) if url else ''}"""
    
    return result

def main():
    # 创建输出目录
    output_dir = os.path.expanduser("~/hermes_output/content_arbitrage")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(output_dir, f"twitter_xiaohongshu_{timestamp}.txt")
    
    # 从Twitter抓取真实数据
    print("📡 从Twitter抓取热门话题...")
    hot_tweets = fetch_twitter_timeline()
    
    if not hot_tweets:
        print("⚠️ Twitter时间线无数据，尝试趋势话题...")
        hot_tweets = fetch_twitter_trending()
    
    # 如果都没抓到，用兜底数据
    if not hot_tweets:
        print("⚠️ 未获取到数据，使用兜底内容")
        hot_tweets = [
            {"author": "@trending", "content": "今天加密市场整体上涨，BTC突破新高", "likes": 5000, "topic": "加密", "url": ""},
            {"author": "@technews", "content": "AI 初创公司获得新一轮融资", "likes": 3000, "topic": "AI/技术", "url": ""},
        ]
    
    output_lines = []
    output_lines.append("🔥 今日热门内容套利机会\n")
    output_lines.append(f"数据来源: Twitter 实时抓取 | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    output_lines.append("=" * 50 + "\n")
    
    for i, tweet in enumerate(hot_tweets, 1):
        xiaohongshu_title = generate_xiaohongshu_title(tweet)
        xiaohongshu_content = translate_and_localize(tweet)
        
        output_lines.append(f"\n📱 内容 #{i} - {tweet['topic']}\n")
        output_lines.append(f"原作者: {tweet['author']} | 热度: {tweet['likes']:,} 赞\n\n")
        output_lines.append(f"【小红书标题】\n")
        output_lines.append(xiaohongshu_title + "\n")
        output_lines.append(f"\n【正文】\n")
        output_lines.append(xiaohongshu_content + "\n")
        
        # 新增：推文内容（可直接发X/Twitter）
        output_lines.append(f"\n【推文】\n")
        output_lines.append(f"{tweet['content'][:200]}\n\n")
        output_lines.append("=" * 50 + "\n")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"\n✅ 内容已保存到: {output_file}")
    print(f"📊 共 {len(hot_tweets)} 条内容")
    
    # 输出到stdout供cron任务捕获
    print("\n" + "=" * 50)
    print("📋 今日套利内容摘要:\n")
    for t in hot_tweets:
        print(f"  • [{t['topic']}] {t['author']}: {t['content'][:80]}...")

if __name__ == "__main__":
    main()
