#!/usr/bin/env python3
"""
YouTube热门视频→B站/视频号 (视频生成版)
使用 autocli 从 HackerNews/Google 抓取真实热门数据
下载素材 + 生成配音 + 添加字幕 + 输出视频
"""
import os
import json
import subprocess
import random
from pathlib import Path

OUTPUT_DIR = Path.home() / ".hermes_output" / "video_content"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUTOCLI = Path.home() / ".local" / "bin" / "autocli"

# ----- 兜底数据（autocli 抓取失败时使用）-----
FALLBACK_VIDEOS = [
    {
        "title": "I Built a $10,000/month SaaS in 30 Days",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "channel": "Pieter Levels",
        "views": "850K",
        "topic": "创业/副业"
    }
]

FALLBACK_SCRIPTS = {
    "I Built a $10,000/month SaaS in 30 Days": """大家好，今天分享一个国外爆火的视频。

这个叫Pieter的老外，30天做了个SaaS产品，现在月收入7万人民币。

他的方法很简单：
第一，不做市场调研，直接开干
第二，第一周上线MVP，边做边改
第三，在Twitter疯狂发进度，积累种子用户
第四，定价29美元每月，第10天就有付费用户

完美的产品永远做不出来，先上线再说。

这个思路值得学习，不是产品有多牛，是执行力够快。评论区说说你的想法。"""
}


def run_autocli(args):
    """运行 autocli 命令并返回解析后的 JSON 输出"""
    try:
        cmd = [str(AUTOCLI)] + args + ["--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        else:
            # 尝试从 stderr 末尾提取可能的 JSON
            stderr_lines = result.stderr.strip().split("\n")
            for line in reversed(stderr_lines):
                line = line.strip()
                if line.startswith("[") or line.startswith("{"):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        pass
            return None
    except Exception as e:
        print(f"  ⚠️  autocli 执行失败: {e}")
        return None


def fetch_hackernews_trending():
    """从 HackerNews 抓取热门科技/AI 话题（autocli，无需认证）"""
    print("  🌐 从 HackerNews 抓取热门科技话题...")

    # 1) 先取 best stories（热门精选）
    best = run_autocli(["hackernews", "best", "--limit", "10"])
    # 2) 再搜 AI tutorial 相关
    ai_search = run_autocli(["hackernews", "search", "AI tutorial", "--limit", "10"])

    hn_items = []
    if best and isinstance(best, list):
        hn_items.extend(best)
    if ai_search and isinstance(ai_search, list):
        hn_items.extend(ai_search)

    if not hn_items:
        print("  ⚠️  未从 HackerNews 获取到数据，使用兜底数据")
        return None

    # 去重（按 title）
    seen_titles = set()
    unique_items = []
    for item in hn_items:
        t = item.get("title", "")
        if t and t not in seen_titles:
            seen_titles.add(t)
            unique_items.append(item)

    # 映射为统一格式
    videos = []
    for item in unique_items[:5]:
        title = item.get("title", "")
        url = item.get("url", "")
        author = item.get("author", "unknown")
        score = item.get("score", 0)
        comments = item.get("comments", 0)

        # 判断 topic
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["ai", "llm", "gpt", "neural", "machine learning", "deep learning", "agent"]):
            topic = "AI/技术"
        elif any(kw in title_lower for kw in ["startup", "saas", "创业", "business", "funding", "product"]):
            topic = "创业/商业"
        elif any(kw in title_lower for kw in ["code", "programming", "dev", "开源", "github", "rust", "python"]):
            topic = "编程/开发"
        else:
            topic = "科技/综合"

        views_str = f"{score} points" if score else "热门"
        channel = author

        videos.append({
            "title": title,
            "url": url,
            "channel": channel,
            "views": views_str,
            "topic": topic,
            "comments": comments,
            "source": "HackerNews"
        })

    print(f"  ✅ 取得 {len(videos)} 条真实热门内容")
    return videos


def fetch_videos():
    """尝试从 autocli 获取真实数据，失败则用兜底"""
    # 主数据源：HackerNews（无需认证）
    videos = fetch_hackernews_trending()

    if videos and len(videos) >= 2:
        return videos

    # 兜底
    print("  ⚠️  使用兜底数据")
    return FALLBACK_VIDEOS


def generate_bilibili_title(video):
    """生成B站风格标题"""
    topic = video['topic']
    title = video['title']
    if "AI" in topic or "ai" in topic.lower():
        return f"这个AI项目火了：{title[:30]}..."
    elif "创业" in topic:
        return "30天做出月入7万的产品？这个方法绝了"
    elif "编程" in topic or "开发" in topic:
        return f"开发者必看：{title[:30]}..."
    elif "科技" in topic:
        return f"科技圈炸了：{title[:30]}..."
    return f"今日热门：{title[:30]}..."


def generate_script(video):
    """生成视频文案"""
    title = video['title']

    # 检查是否有预设文案
    if title in FALLBACK_SCRIPTS:
        return FALLBACK_SCRIPTS[title]

    # 动态生成文案
    topic = video['topic']
    channel = video['channel']
    comments = video.get('comments', 0)

    script = f"""大家好，今天分享一个在HackerNews上爆火的内容。

这篇文章/项目标题是：{title}

来自作者 {channel}，获得了很多社区讨论{'（' + str(comments) + '条评论）' if comments else ''}。

{'这是一个AI/技术相关的内容，最近这类话题讨论度非常高。' if 'AI' in topic else ''}
{'这是一个创业相关的内容，对想做副业的朋友很有参考价值。' if '创业' in topic else ''}
{'这是一个编程开发相关的内容，建议开发者朋友们都看看。' if '编程' in topic or '开发' in topic else ''}

感兴趣的话可以去原文看看，链接放在简介里。

觉得有用的话点个赞，关注我获取更多科技前沿内容。评论区说说你的看法。"""

    return script


def generate_video(video, script, index):
    """生成视频：下载真实素材 + AI配音 + 字幕"""
    try:
        video_id = f"video_{index}"

        # 1. 生成占位视频（HackerNews 没有视频，用背景画面+文字）
        print("  🎬 生成背景视频...")
        raw_video = OUTPUT_DIR / f"{video_id}_raw.mp4"

        # 生成深色背景视频（根据内容长度调整时长）
        script_duration = max(30, len(script) // 10)  # 粗略估计：每秒10个字
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=#1a1a1a:s=1280x720:d={script_duration}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p",
            str(raw_video)
        ], check=True, capture_output=True)

        # 2. 生成AI配音（使用macOS TTS）
        print("  🎙️  生成AI配音...")
        audio_file = OUTPUT_DIR / f"{video_id}_audio.mp3"

        subprocess.run([
            "say", "-v", "Ting-Ting", "-r", "200",
            "-o", str(audio_file.with_suffix('.aiff')),
            script
        ], check=True, capture_output=True)

        subprocess.run([
            "ffmpeg", "-y", "-i", str(audio_file.with_suffix('.aiff')),
            "-ar", "44100", "-ac", "2", "-b:a", "192k",
            str(audio_file)
        ], check=True, capture_output=True)

        # 3. 生成字幕文件（SRT格式）
        print("  📝 生成字幕...")
        srt_file = OUTPUT_DIR / f"{video_id}.srt"

        sentences = [s.strip() for s in script.replace('。', '.')
                     .replace('？', '?').replace('！', '!').split('.') if s.strip()]
        srt_content = ""
        for i, sentence in enumerate(sentences, 1):
            start_time = (i - 1) * 3
            end_time = i * 3
            srt_content += f"{i}\n"
            srt_content += f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n"
            srt_content += f"{sentence}。\n\n"

        srt_file.write_text(srt_content, encoding='utf-8')

        # 4. 合成最终视频
        print("  🎬 合成最终视频...")
        final_video = OUTPUT_DIR / f"{video_id}_final.mp4"

        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(raw_video),
            "-i", str(audio_file),
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(final_video)
        ], check=True, capture_output=True)

        # 保留字幕文件
        final_srt = OUTPUT_DIR / f"{video_id}_final.srt"
        srt_file.rename(final_srt)

        # 清理临时文件
        raw_video.unlink(missing_ok=True)
        audio_file.unlink(missing_ok=True)
        audio_file.with_suffix('.aiff').unlink(missing_ok=True)
        srt_file.unlink(missing_ok=True)

        return final_video

    except Exception as e:
        print(f"  ❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_srt_time(seconds):
    """格式化SRT时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    print("🎬 YouTube→B站/视频号 视频生成（autocli 真实数据版）\n")
    print("=" * 50)

    # 用 autocli 抓取真实数据
    hot_videos = fetch_videos()

    print(f"\n📊 共获取 {len(hot_videos)} 条热门内容\n")

    results = []

    for i, video in enumerate(hot_videos, 1):
        source_tag = video.get('source', 'HackerNews')
        print(f"\n📹 处理 #{i}: {video['title']}")
        print(f"   📎 来源: {source_tag} | 作者: {video['channel']}")

        # 生成文案
        bilibili_title = generate_bilibili_title(video)
        script = generate_script(video)

        # 生成视频
        video_path = generate_video(video, script, i)

        result = {
            "原标题": video['title'],
            "频道/作者": video['channel'],
            "热度": video['views'],
            "主题": video['topic'],
            "B站标题": bilibili_title,
            "文案": script,
            "视频路径": str(video_path) if video_path else "生成失败"
        }
        results.append(result)

        if video_path:
            print(f"✅ 视频已保存: {video_path}")
        else:
            print(f"❌ 视频生成失败")

    # 输出汇总（cron 捕获格式）
    print("\n" + "=" * 50)
    print("📦 生成完成\n")
    for r in results:
        print(f"【{r['B站标题']}】")
        print(f"原文: {r['原标题']}")
        print(f"来源: {r['频道/作者']} | 热度: {r['热度']}")
        print(f"视频: {r['视频路径']}")
        print(f"\n{r['文案']}\n")
        print("-" * 50)

    # JSON 汇总输出（供其他程序使用）
    summary_file = OUTPUT_DIR / "summary.json"
    summary_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n📄 汇总 JSON: {summary_file}")


if __name__ == "__main__":
    main()
