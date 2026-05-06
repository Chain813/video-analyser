# -*- coding: utf-8 -*-
"""
视频元信息提取模块
==================
使用 OpenCV 获取视频的物理属性信息。
"""

import os
import cv2


def get_video_info(video_path: str) -> dict:
    """获取视频的详细元信息。

    Args:
        video_path: 视频文件路径。

    Returns:
        dict: 包含以下键值的字典：
            - duration_sec (float): 视频时长（秒）
            - fps (float): 帧率
            - total_frames (int): 总帧数
            - width (int): 视频宽度（像素）
            - height (int): 视频高度（像素）
            - codec (str): 视频编码格式
            - file_size_mb (float): 文件大小（MB）

    Raises:
        FileNotFoundError: 视频文件不存在或无法打开。
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"无法打开视频文件: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 获取编码格式 (fourcc → 可读字符串)
    fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc_int >> (8 * i)) & 0xFF) for i in range(4)])

    cap.release()

    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)

    return {
        "duration_sec": duration,
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "codec": codec.strip(),
        "file_size_mb": round(file_size_mb, 2),
    }


def format_timestamp(seconds: float) -> str:
    """将秒数格式化为 MM:SS 字符串。

    Args:
        seconds: 秒数。

    Returns:
        str: 格式化的时间字符串，如 "03:45"。
    """
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"
