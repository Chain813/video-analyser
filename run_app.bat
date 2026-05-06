@echo off
title 视频操作分析器 - 一键启动器
echo ======================================================
echo           AI 视频操作步骤提取器 (GUI 版)
echo ======================================================
echo.

:: 1. 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python 环境，请先安装 Python 3.8 或更高版本。
    pause
    exit
)

:: 2. 检查并安装依赖
echo [1/2] 正在检查依赖环境...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% neq 0 (
    echo [警告] 依赖安装可能失败，尝试直接运行...
)

:: 3. 启动 GUI
echo [2/2] 正在启动图形界面，请稍候...
echo ------------------------------------------------------
python main.py
echo ------------------------------------------------------

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序运行出错。请检查 API Key 是否正确或网络是否连通。
    pause
)

exit
