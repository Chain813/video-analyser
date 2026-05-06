# -*- coding: utf-8 -*-
"""
AI 视频分析核心模块
===================
借鉴 PouriaRouzrokh/VideoInstruct 的"动作原子化"策略，
以及 Google Gemini Cookbook 官方推荐的结构化 JSON 输出能力，
实现高精度的视频操作步骤提取。

核心特性:
  - 强制 JSON Schema 输出 (response_mime_type="application/json")
  - 多维度提取: 视频摘要 + 所需工具 + 原子化步骤
  - 每个步骤包含: 时间戳、动作类型、操作对象、详细描述、视觉反馈
"""

import json
import time
from typing import Optional

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 模型配置
# ---------------------------------------------------------------------------
MODEL = "gemini-2.0-flash"

# ---------------------------------------------------------------------------
# 结构化输出 JSON Schema
# ---------------------------------------------------------------------------
# 借鉴 YahyaBagia/recipe-video-ai 的 Zod Schema 思路，
# 将每一步拆解为最小可描述的"原子动作"。
# 借鉴 Gemini Cookbook 官方推荐的 response_schema 特性，
# 确保 100% 稳定的 JSON 输出。

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "用一两句话概括视频的核心内容和最终目标"
        },
        "software_or_tools": {
            "type": "array",
            "items": {"type": "string"},
            "description": "视频中涉及的软件名称或工具（如 ArcGIS Pro、Photoshop、Excel 等）"
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {
                        "type": "integer",
                        "description": "步骤序号，从 1 开始"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "动作发生的时间点，格式 MM:SS"
                    },
                    "action_type": {
                        "type": "string",
                        "description": "动作类型，例如：点击、双击、右键点击、拖拽、输入、选择、滚动、快捷键"
                    },
                    "target_object": {
                        "type": "string",
                        "description": "操作的 UI 元素或对象名称（如：文件菜单、图层面板、搜索框）"
                    },
                    "detail": {
                        "type": "string",
                        "description": "完整的操作描述，应当足够详细让读者能够复现"
                    },
                    "visual_change": {
                        "type": "string",
                        "description": "该操作完成后屏幕上发生的可观察变化"
                    }
                },
                "required": ["step_id", "timestamp", "action_type", "detail"]
            }
        },
        "tips": {
            "type": "array",
            "items": {"type": "string"},
            "description": "视频中提及或隐含的注意事项、技巧、易错点"
        }
    },
    "required": ["summary", "steps"]
}

# ---------------------------------------------------------------------------
# 增强型系统 Prompt
# ---------------------------------------------------------------------------
# 融合 VideoInstruct 的"指令推理"逻辑和 recipe-video-ai 的原子化方法论。

SYSTEM_PROMPT = """\
你是一位专业的软件操作教程分析师，拥有丰富的 UI 交互理解经验。

## 核心任务
分析视频中的操作过程，提取出每一个**原子级别**的操作步骤。

## 分析方法论

### 第一步：整体理解（推理阶段）
在开始逐帧分析前，先通读整段视频，理解：
- 这个视频的**最终目的**是什么？
- 使用了哪些**软件或工具**？
- 操作的整体**流程框架**是什么？

### 第二步：原子化提取（执行阶段）
逐一识别每个界面交互动作。遵循以下规则：
1. **原子化**：一个步骤 = 一个动作。不要将"打开菜单并选择选项"合并为一步。
2. **精确定位**：时间戳必须精确到发生操作的那一秒 (MM:SS)。
3. **指明对象**：必须明确指出操作的 UI 元素名称（按钮文字、菜单项名称、面板标题等）。
4. **视觉验证**：描述操作后屏幕上发生了什么变化（弹出窗口、颜色变化、数据更新等）。
5. **跳过空白**：忽略无操作的等待、加载和过渡画面。

### 第三步：知识萃取（总结阶段）
提取视频中隐含的技巧、注意事项或容易犯错的地方，放入 tips 字段。

## 输出要求
严格按照 JSON Schema 输出，所有文本使用**中文**。\
"""

USER_PROMPT = "请分析这个视频中的所有操作步骤。先理解视频的整体目的，再逐一提取每个原子级操作。"


# ---------------------------------------------------------------------------
# 核心分析函数
# ---------------------------------------------------------------------------

def analyze_video(video_path: str, api_key: str, model: Optional[str] = None) -> dict:
    """使用 Gemini 分析视频，提取结构化操作步骤。

    借鉴 Gemini Cookbook 官方的 response_mime_type + response_schema 方案，
    确保返回值始终是合法的、可解析的 JSON 对象。

    Args:
        video_path: 视频文件的本地路径。
        api_key: Google AI API Key。
        model: 可选，指定使用的模型名称。默认使用 gemini-2.0-flash。

    Returns:
        dict: 包含 summary, software_or_tools, steps, tips 的结构化字典。

    Raises:
        RuntimeError: 视频上传或处理失败时抛出。
    """
    use_model = model or MODEL
    client = genai.Client(api_key=api_key)

    # ---- 阶段 1: 上传视频 ----
    print("[Upload] 正在上传视频到 Gemini...")
    video_file = client.files.upload(file=video_path)
    print(f"   上传完成: {video_file.name}")

    # ---- 阶段 2: 等待处理 ----
    while video_file.state.name == "PROCESSING":
        print("   [Processing] 视频处理中...")
        time.sleep(3)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name != "ACTIVE":
        raise RuntimeError(f"视频处理失败，状态: {video_file.state.name}")

    # ---- 阶段 3: 结构化分析 ----
    print("[Analysis] 正在进行结构化分析...")
    response = client.models.generate_content(
        model=use_model,
        contents=[
            video_file,
            USER_PROMPT,
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            max_output_tokens=8192,
            temperature=0.1,  # 低温度确保输出稳定
        ),
    )

    # ---- 阶段 4: 解析 JSON ----
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        # 兜底：如果 Schema 强制失败，尝试从文本中提取
        print("[Warning] JSON 解析失败，尝试原始文本回退...")
        result = {
            "summary": "（解析失败，以下为原始输出）",
            "steps": [],
            "_raw_text": response.text
        }

    # ---- 阶段 5: 清理远端文件 ----
    try:
        client.files.delete(name=video_file.name)
    except Exception:
        pass  # 清理失败不影响主流程

    print("[Done] 分析完成！")
    return result


def format_result_text(result: dict) -> str:
    """将结构化 JSON 结果格式化为人类可读的文本报告。

    Args:
        result: analyze_video 返回的字典。

    Returns:
        str: 格式化的多行文本。
    """
    lines = []

    # 摘要
    if result.get("summary"):
        lines.append("📋 视频概述")
        lines.append(f"   {result['summary']}")
        lines.append("")

    # 涉及工具
    tools = result.get("software_or_tools", [])
    if tools:
        lines.append("🛠️  涉及工具")
        lines.append(f"   {', '.join(tools)}")
        lines.append("")

    # 操作步骤
    steps = result.get("steps", [])
    if steps:
        lines.append(f"📝 操作步骤 (共 {len(steps)} 步)")
        lines.append("─" * 60)
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
                header += f" → {target}"

            lines.append(header)
            lines.append(f"       {detail}")
            if visual:
                lines.append(f"       💡 变化: {visual}")
            lines.append("")

    # 技巧与提示
    tips = result.get("tips", [])
    if tips:
        lines.append("💡 技巧与注意事项")
        for i, tip in enumerate(tips, 1):
            lines.append(f"   {i}. {tip}")
        lines.append("")

    # 原始文本兜底
    if result.get("_raw_text"):
        lines.append("⚠️ 原始输出 (JSON 解析失败)")
        lines.append(result["_raw_text"])

    return "\n".join(lines)
