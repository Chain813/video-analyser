# -*- coding: utf-8 -*-
"""
视频元信息与关键帧提取模块
===========================
使用 OpenCV 获取视频物理属性信息，
并支持按时间戳截取关键帧图片。
"""

import os
import cv2


def get_video_info(video_path: str) -> dict:
    """获取视频的详细元信息。

    Args:
        video_path: 视频文件路径。

    Returns:
        dict: 包含 duration_sec, fps, total_frames, width, height, codec, file_size_mb。

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
    """将秒数格式化为 MM:SS 字符串。"""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"


def parse_timestamp(ts_str: str) -> float:
    """将 MM:SS 格式的时间戳解析为秒数。"""
    try:
        parts = ts_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return 0.0


def extract_keyframes(video_path: str, timestamps: list, output_dir: str) -> list:
    """根据时间戳列表从视频中截取关键帧图片。

    Args:
        video_path: 视频文件路径。
        timestamps: MM:SS 格式的时间戳字符串列表。
        output_dir: 截图保存目录。

    Returns:
        list[str]: 生成的截图文件路径列表。
    """
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    saved_paths = []

    for i, ts in enumerate(timestamps):
        seconds = parse_timestamp(ts)
        frame_num = int(seconds * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if ret:
            filename = f"step_{i + 1:02d}_{ts.replace(':', '-')}.png"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            saved_paths.append(filepath)

    cap.release()
    return saved_paths
