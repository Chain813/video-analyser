# AI 视频操作步骤提取器

基于 Google Gemini 大模型的桌面工具，自动分析视频（软件操作教程、流程演示等），提取出结构化、详细的操作步骤说明。

[English Version](README_EN.md)

## ✨ 核心特性

- **结构化 JSON 输出** — 使用 Gemini `response_schema` 强制模型返回标准 JSON，100% 可解析。
- **原子化动作提取** — 每个步骤只包含一个核心动作，附带动作类型、操作对象和视觉反馈。
- **关键帧自动截取** — 根据步骤时间戳，自动从视频中截取对应画面，生成图文并茂的报告。
- **多格式导出** — 支持 TXT 纯文本、Markdown 图文报告、JSON 数据三种格式。
- **专业桌面 GUI** — 基于 PySide6 的深色模式界面，支持拖拽上传、实时预览、一键导出。
- **CLI 命令行模式** — 同时保留完整的命令行工具，适合批量处理和脚本集成。

## 📋 环境要求

- Python 3.8+
- 有效的 [Google AI API Key](https://aistudio.google.com/apikey)

## 🚀 安装步骤

```bash
pip install -r requirements.txt
```

**依赖说明：**
| 包名 | 用途 |
|---|---|
| `google-genai` | Google 官方 Gemini SDK |
| `opencv-python` | 视频元信息提取与关键帧截取 |
| `PySide6` | 专业桌面 GUI 框架 |
| `pydantic` | 数据校验 (预留) |
| `python-dotenv` | 环境变量管理 |

## ⚙️ 配置 API Key

**方式一：GUI 界面保存 (推荐)**

启动程序后在侧边栏输入 Key 并点击 "Save Config"，程序会自动生成 `.env` 文件。

**方式二：手动创建 `.env` 文件**
```bash
GOOGLE_API_KEY=your_api_key_here
```

**方式三：命令行参数**
```bash
python main.py video.mp4 --api-key "your_key"
```

## 📖 使用说明

### GUI 模式 (默认)
```bash
python main.py
```
或直接双击 `run_app.bat`。

### CLI 模式
```bash
# 终端输出文本报告
python main.py tutorial.mp4

# 保存为 Markdown 图文报告 (自动截取关键帧)
python main.py tutorial.mp4 -o report.md --md

# 导出结构化 JSON
python main.py tutorial.mp4 -o data.json --json

# 指定模型
python main.py tutorial.mp4 --model gemini-2.5-pro -o report.txt
```

## 📁 项目结构

```
video-analyser/
├── src/                          # 核心源代码
│   ├── analyzer/                 # AI 分析引擎
│   │   ├── engine.py             #   Gemini API 交互与结构化分析
│   │   └── prompts.py            #   Prompt 模板与 JSON Schema
│   ├── utils/                    # 工具函数
│   │   ├── video.py              #   视频元信息 & 关键帧截取
│   │   └── export.py             #   多格式导出 (TXT/MD/JSON)
│   └── ui/                       # 图形界面
│       ├── main_window.py        #   主窗口 (PySide6)
│       └── styles.py             #   QSS 深色主题样式表
├── main.py                       # 统一入口 (GUI/CLI)
├── run_app.bat                   # 一键启动脚本
├── build_exe.bat                 # 一键打包脚本
├── .env.example                  # 环境变量模板
├── .gitignore                    # Git 忽略规则
├── requirements.txt              # 依赖列表
├── README.md                     # 中文文档
└── README_EN.md                  # 英文文档
```

## 🙏 致谢

| 项目 | 借鉴内容 |
|---|---|
| [PouriaRouzrokh/VideoInstruct](https://github.com/PouriaRouzrokh/VideoInstruct) | 动作原子化方法论 |
| [google-gemini/cookbook](https://github.com/google-gemini/cookbook) | 结构化输出方案 |
| [YahyaBagia/recipe-video-ai](https://github.com/YahyaBagia/recipe-video-ai) | 步骤 Schema 设计 |
| [OpenGVLab/VideoChat2](https://github.com/OpenGVLab/VideoChat2) | 时空推理策略 |
| [DAMO-NLP-SG/VideoLLaMA2](https://github.com/DAMO-NLP-SG/VideoLLaMA2) | 多模态融合思路 |
