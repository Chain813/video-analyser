# -*- coding: utf-8 -*-
"""
结果格式化与导出模块
====================
支持将分析结果输出为纯文本、Markdown 图文报告等多种格式。
"""

import json
import os
from datetime import datetime


def format_result_text(result: dict) -> str:
    """将结构化 JSON 结果格式化为人类可读的纯文本报告。"""
    lines = []

    if result.get("summary"):
        lines.append("视频概述")
        lines.append(f"   {result['summary']}")
        lines.append("")

    tools = result.get("software_or_tools", [])
    if tools:
        lines.append("涉及工具")
        lines.append(f"   {', '.join(tools)}")
        lines.append("")

    steps = result.get("steps", [])
    if steps:
        lines.append(f"操作步骤 (共 {len(steps)} 步)")
        lines.append("-" * 60)
        for s in steps:
            step_id = s.get("step_id", "?")
            ts = s.get("timestamp", "--:--")
            action = s.get("action_type", "")
            target = s.get("target_object", "")
            detail = s.get("detail", "")
            visual = s.get("visual_change", "")

            header = f"[{ts}] 步骤 {step_id}"
            if action:
                header += f" ({action})"
            if target:
                header += f" -> {target}"

            lines.append(header)
            lines.append(f"       {detail}")
            if visual:
                lines.append(f"       变化: {visual}")
            lines.append("")

    tips = result.get("tips", [])
    if tips:
        lines.append("技巧与注意事项")
        for i, tip in enumerate(tips, 1):
            lines.append(f"   {i}. {tip}")
        lines.append("")

    if result.get("_raw_text"):
        lines.append("原始输出 (JSON 解析失败)")
        lines.append(result["_raw_text"])

    return "\n".join(lines)


def export_markdown(result: dict, video_name: str = "",
                    keyframe_dir: str = None) -> str:
    """将分析结果导出为 Markdown 格式的图文报告。

    Args:
        result: analyze_video 返回的字典。
        video_name: 视频文件名（用于报告标题）。
        keyframe_dir: 关键帧截图目录。如果提供，将在步骤中嵌入截图。

    Returns:
        str: Markdown 格式的报告内容。
    """
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append(f"# 视频操作步骤分析报告")
    lines.append("")
    if video_name:
        lines.append(f"**视频文件**: `{video_name}`  ")
    lines.append(f"**生成时间**: {now}  ")
    lines.append("")

    # 摘要
    if result.get("summary"):
        lines.append("## 概述")
        lines.append("")
        lines.append(f"> {result['summary']}")
        lines.append("")

    # 工具
    tools = result.get("software_or_tools", [])
    if tools:
        lines.append("## 涉及工具")
        lines.append("")
        for t in tools:
            lines.append(f"- {t}")
        lines.append("")

    # 步骤
    steps = result.get("steps", [])
    if steps:
        lines.append(f"## 操作步骤 ({len(steps)} 步)")
        lines.append("")
        for s in steps:
            step_id = s.get("step_id", "?")
            ts = s.get("timestamp", "--:--")
            action = s.get("action_type", "")
            target = s.get("target_object", "")
            detail = s.get("detail", "")
            visual = s.get("visual_change", "")

            title = f"### 步骤 {step_id} `[{ts}]`"
            if action:
                title += f" — {action}"
            if target:
                title += f" → {target}"
            lines.append(title)
            lines.append("")
            lines.append(detail)
            lines.append("")

            if visual:
                lines.append(f"**视觉反馈**: {visual}")
                lines.append("")

            # 嵌入关键帧截图
            if keyframe_dir:
                img_name = f"step_{step_id:02d}_{ts.replace(':', '-')}.png"
                img_path = os.path.join(keyframe_dir, img_name)
                if os.path.isfile(img_path):
                    lines.append(f"![步骤 {step_id} 截图]({img_name})")
                    lines.append("")

            lines.append("---")
            lines.append("")

    # 技巧
    tips = result.get("tips", [])
    if tips:
        lines.append("## 技巧与注意事项")
        lines.append("")
        for i, tip in enumerate(tips, 1):
            lines.append(f"{i}. {tip}")
        lines.append("")

    return "\n".join(lines)


def export_json(result: dict) -> str:
    """将结果导出为美化的 JSON 字符串。"""
    return json.dumps(result, ensure_ascii=False, indent=2)
