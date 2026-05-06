# -*- coding: utf-8 -*-
"""
AI 分析引擎
===========
负责与 Google Gemini API 交互，执行视频的结构化分析。
Prompt 和 Schema 配置从 prompts.py 中导入，实现关注点分离。
"""

import json
import time
from typing import Optional

from google import genai
from google.genai import types

from src.analyzer.prompts import (
    DEFAULT_MODEL, RESPONSE_SCHEMA, SYSTEM_PROMPT, USER_PROMPT
)


def analyze_video(video_path: str, api_key: str, model: Optional[str] = None) -> dict:
    """使用 Gemini 分析视频，提取结构化操作步骤。

    Args:
        video_path: 视频文件的本地路径。
        api_key: Google AI API Key。
        model: 可选，指定使用的模型名称。

    Returns:
        dict: 包含 summary, software_or_tools, steps, tips 的结构化字典。

    Raises:
        RuntimeError: 视频上传或处理失败时抛出。
    """
    use_model = model or DEFAULT_MODEL
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
            temperature=0.1,
        ),
    )

    # ---- 阶段 4: 解析 JSON ----
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
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
        pass

    print("[Done] 分析完成！")
    return result
