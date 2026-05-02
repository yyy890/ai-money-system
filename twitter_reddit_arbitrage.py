#!/usr/bin/env python3
"""
Twitter/Reddit → 知识星球 信息差套利
使用autocli抓取真实热门话题，生成"冷门搞钱思路"
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

def fetch_hackernews():
    """从HackerNews抓取热门话题"""
    items = run_autocli(["hackernews", "top", "--limit", "5", "--format", "json"])
    result = []
    if items and isinstance(items, list):
        for item in items:
            title = item.get("title", "") or item.get("text", "")
            if title:
                result.append({
                    "来源": "HackerNews",
                    "话题": title[:80],
                    "内容": title,
                    "标签": ["科技", "创业"]
                })
    return result

def fetch_reddit():
    """从Reddit抓取商业/创业话题"""
    items = run_autocli(["reddit", "hot", "--subreddit", "SideProject", "--limit", "5", "--format", "json"])
    result = []
    if items and isinstance(items, list):
        for item in items:
            title = item.get("title", "")
            if title:
                result.append({
                    "来源": "Reddit r/SideProject",
                    "话题": title[:80],
                    "内容": title,
                    "标签": ["副业", "创业"]
                })
    return result

def fetch_v2ex():
    """从V2EX抓取热门话题"""
    items = run_autocli(["v2ex", "hot", "--limit", "5", "--format", "json"])
    result = []
    if items and isinstance(items, list):
        for item in items:
            title = item.get("title", "")
            if title:
                result.append({
                    "来源": "V2EX",
                    "话题": title[:80],
                    "内容": title,
                    "标签": ["技术", "创业"]
                })
    return result

def main():
    print("💰 Twitter/Reddit 信息差套利\n")
    print("=" * 60)
    
    # 多源抓取
    print("📡 抓取多源数据...")
    
    all_topics = []
    
    hn = fetch_hackernews()
    if hn:
        print(f"  ✓ HackerNews: {len(hn)} 条")
        all_topics.extend(hn)
    
    reddit = fetch_reddit()
    if reddit:
        print(f"  ✓ Reddit: {len(reddit)} 条")
        all_topics.extend(reddit)
    
    v2ex = fetch_v2ex()
    if v2ex:
        print(f"  ✓ V2EX: {len(v2ex)} 条")
        all_topics.extend(v2ex)
    
    # 兜底数据
    if not all_topics:
        print("  ⚠️ 无实时数据，使用兜底内容")
        all_topics = [
            {"来源": "HackerNews", "话题": "Building in public - 透明化创业", "内容": "I made $180k by tweeting my progress every day. No ads, no VC, just transparency.", "标签": ["创业", "副业"]},
            {"来源": "Reddit r/SideProject", "话题": "AI wrapper businesses", "内容": "Made a simple ChatGPT wrapper for lawyers. $5k MRR in 3 months.", "标签": ["AI", "SaaS"]},
            {"来源": "V2EX", "话题": "独立开发者如何获取前100个用户", "内容": "分享从0到100个付费用户的全过程", "标签": ["创业", "增长"]},
        ]
    
    print(f"\n📊 共 {len(all_topics)} 条热门话题\n")
    print("=" * 60)
    
    for i, topic in enumerate(all_topics, 1):
        print(f"\n{'=' * 60}")
        print(f"  #{i}  {topic['话题']}")
        print(f"  📍 {topic['来源']}  |  🏷️ {', '.join(topic['标签'])}")
        print(f"\n  📝 {topic['内容'][:200]}")
        print(f"\n  💡 套利思路:")
        
        # 根据标签生成套利思路
        tags = topic.get('标签', [])
        if 'AI' in tags or '技术' in tags or '科技' in tags:
            print(f"     → 翻译成中文，发到掘金/CSDN/知乎")
            print(f"     → 制作成短视频脚本，发到B站/抖音")
        elif '创业' in tags or '副业' in tags:
            print(f"     → 整理成'冷门搞钱思路'发到知识星球")
            print(f"     → 拆解成Thread发到即刻/Twitter")
        elif '增长' in tags:
            print(f"     → 提炼方法论，做成小红书图文")
            print(f"     → 翻译后发到即刻/知乎专栏")
        else:
            print(f"     → 本地化改写，发到小红书/公众号")
            print(f"     → 制作成知识星球付费内容")
    
    print(f"\n{'=' * 60}")
    print(f"✅ 信息差套利分析完成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
