# -*- coding: utf-8 -*-
"""
视频操作步骤提取器 — 命令行主入口
==================================
使用 Google Gemini AI 分析视频中的操作步骤，
输出结构化的 JSON 或人类可读的文本报告。

用法:
    python main.py video.mp4                          # 终端文本输出
    python main.py video.mp4 -o result.txt            # 保存文本报告
    python main.py video.mp4 -o result.json --json    # 保存 JSON
    python main.py video.mp4 --model gemini-2.5-pro   # 指定模型
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 强制设置标准输出编码为 UTF-8，解决 Windows (GBK) 终端乱码和 UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    try:
        from io import TextIOWrapper
        sys.stdout = TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

from video_processor import get_video_info, format_timestamp
from ai_analyzer import analyze_video, format_result_text

try:
    from gui import run_gui
    HAS_GUI = True
except ImportError:
    HAS_GUI = False


def main():
    parser = argparse.ArgumentParser(
        description="视频操作步骤提取器 — 使用 Gemini AI 分析视频中的操作步骤",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  %(prog)s tutorial.mp4                        分析视频并在终端显示
  %(prog)s tutorial.mp4 -o report.txt          分析后保存为文本报告
  %(prog)s tutorial.mp4 -o data.json --json    分析后保存为 JSON 数据
  %(prog)s tutorial.mp4 --model gemini-2.5-pro 使用 Gemini 2.5 Pro 模型
        """
    )
    parser.add_argument("video", help="MP4 视频文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径（不指定则输出到终端）")
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="输出原始 JSON 格式（默认输出格式化的可读文本）"
    )
    parser.add_argument(
        "--api-key",
        help="Google AI API Key（也可设置 GOOGLE_API_KEY 环境变量）"
    )
    parser.add_argument(
        "--model",
        help="指定 Gemini 模型（默认: gemini-2.0-flash）"
    )
    args = parser.parse_args()

    # 如果没有提供视频路径且 GUI 可用，则启动 GUI
    if not args.video and HAS_GUI:
        print("启动图形化界面...")
        run_gui()
        return

    # 如果没有提供视频路径且 GUI 不可用，则报错
    if not args.video:
        parser.print_help()
        sys.exit(1)

    # ---- 前置检查 ----

    # 检查视频文件
    if not os.path.isfile(args.video):
        print(f"Error: 视频文件不存在: {args.video}")
        sys.exit(1)

    # 获取 API Key
    api_key = args.api_key or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: 请通过 --api-key 参数或 GOOGLE_API_KEY 环境变量提供 API Key")
        sys.exit(1)

    # ---- 视频信息 ----

    try:
        info = get_video_info(args.video)
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

    duration = format_timestamp(info["duration_sec"])
    file_size_mb = os.path.getsize(args.video) / (1024 * 1024)

    print("=" * 60)
    print("  📹 AI 视频操作步骤提取器")
    print("=" * 60)
    print(f"  视频文件:  {os.path.basename(args.video)}")
    print(f"  时长:      {duration}")
    print(f"  分辨率:    {info['width']}x{info['height']}")
    print(f"  帧率:      {info['fps']:.1f} FPS")
    print(f"  文件大小:  {file_size_mb:.1f} MB")
    print("=" * 60)
    print()

    # ---- AI 分析 ----

    try:
        result = analyze_video(args.video, api_key, model=args.model)
    except RuntimeError as e:
        print(f"❌ 分析失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未预期的错误: {e}")
        sys.exit(1)

    # ---- 结果输出 ----

    if args.json_output:
        # JSON 格式输出
        output_content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        # 人类可读的文本报告
        header = (
            f"{'=' * 60}\n"
            f"  视频操作步骤分析报告\n"
            f"{'=' * 60}\n"
            f"  视频:   {os.path.basename(args.video)}\n"
            f"  时长:   {duration}\n"
            f"  分辨率: {info['width']}x{info['height']}\n"
            f"{'=' * 60}\n\n"
        )
        output_content = header + format_result_text(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"\n📁 结果已保存到: {args.output}")
    else:
        print()
        print(output_content)

    # 统计信息
    step_count = len(result.get("steps", []))
    tip_count = len(result.get("tips", []))
    print(f"\n📊 统计: 提取了 {step_count} 个操作步骤, {tip_count} 条技巧提示")


if __name__ == "__main__":
    main()
