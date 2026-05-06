# -*- coding: utf-8 -*-
"""
视频操作步骤提取器 — 统一入口
==============================
支持两种运行模式：
  1. GUI 模式 (默认): python main.py
  2. CLI 模式:        python main.py video.mp4 [-o report.txt] [--json]
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 强制 UTF-8 输出 (Windows GBK 兼容)
if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
    try:
        from io import TextIOWrapper
        sys.stdout = TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

from src.analyzer.engine import analyze_video
from src.utils.video import get_video_info, format_timestamp
from src.utils.export import format_result_text, export_markdown, export_json


def run_cli(args):
    """命令行模式主逻辑。"""

    if not os.path.isfile(args.video):
        print(f"Error: file not found: {args.video}")
        sys.exit(1)

    api_key = args.api_key or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: provide API Key via --api-key or GOOGLE_API_KEY env var")
        sys.exit(1)

    try:
        info = get_video_info(args.video)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    duration = format_timestamp(info["duration_sec"])
    file_size_mb = os.path.getsize(args.video) / (1024 * 1024)

    print("=" * 60)
    print("  AI Video Operation Extractor")
    print("=" * 60)
    print(f"  File:       {os.path.basename(args.video)}")
    print(f"  Duration:   {duration}")
    print(f"  Resolution: {info['width']}x{info['height']}")
    print(f"  FPS:        {info['fps']:.1f}")
    print(f"  Size:       {file_size_mb:.1f} MB")
    print("=" * 60)
    print()

    try:
        result = analyze_video(args.video, api_key, model=args.model)
    except Exception as e:
        print(f"Analysis failed: {e}")
        sys.exit(1)

    # 输出结果
    if args.json_output:
        output_content = export_json(result)
    elif args.markdown:
        output_content = export_markdown(result, os.path.basename(args.video))
    else:
        header = (
            f"{'=' * 60}\n"
            f"  Video Analysis Report\n"
            f"{'=' * 60}\n"
            f"  File:       {os.path.basename(args.video)}\n"
            f"  Duration:   {duration}\n"
            f"  Resolution: {info['width']}x{info['height']}\n"
            f"{'=' * 60}\n\n"
        )
        output_content = header + format_result_text(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"\nSaved to: {args.output}")
    else:
        print()
        print(output_content)

    step_count = len(result.get("steps", []))
    tip_count = len(result.get("tips", []))
    print(f"\nStats: {step_count} steps, {tip_count} tips")


def main():
    parser = argparse.ArgumentParser(
        description="AI Video Operation Extractor - Gemini powered",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s                                 Launch GUI
  %(prog)s tutorial.mp4                    Analyze and print to terminal
  %(prog)s tutorial.mp4 -o report.txt      Save as text report
  %(prog)s tutorial.mp4 -o report.md --md  Save as Markdown report
  %(prog)s tutorial.mp4 -o data.json --json Save as JSON
        """
    )
    parser.add_argument("video", nargs="?", default=None, help="Video file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output raw JSON")
    parser.add_argument("--md", action="store_true", dest="markdown", help="Output Markdown")
    parser.add_argument("--api-key", help="Google AI API Key")
    parser.add_argument("--model", help="Gemini model (default: gemini-2.0-flash)")
    args = parser.parse_args()

    # 无视频参数 → 启动 GUI
    if not args.video:
        try:
            from src.ui.main_window import run_gui
            run_gui()
        except ImportError as e:
            print(f"GUI unavailable ({e}). Please provide a video path for CLI mode.")
            parser.print_help()
            sys.exit(1)
        return

    # 有视频参数 → CLI 模式
    run_cli(args)


if __name__ == "__main__":
    main()
