@echo off
title 视频分析器 - 自动打包工具
echo ======================================================
echo           正在将项目打包为独立 EXE 文件
echo ======================================================
echo.

:: 1. 安装打包工具
echo [1/3] 正在安装 PyInstaller...
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 2. 执行打包
echo [2/3] 正在执行打包流程 (这可能需要 1-3 分钟)...
echo 请稍候...

:: --noconsole: 不显示黑窗口
:: --onefile: 打包为单个文件
:: --collect-all: 收集所有依赖
pyinstaller --noconsole --onefile --name "VideoAnalyser" --collect-all PySide6 --clean main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败。
    pause
    exit
)

:: 3. 完成
echo.
echo [3/3] 打包成功！
echo ======================================================
echo  您的程序位于: [dist\VideoAnalyser.exe]
echo  请将该 .exe 文件与 .env 文件放在同一目录下使用。
echo ======================================================
pause
exit
