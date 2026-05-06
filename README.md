# AI 视频操作步骤提取器

基于 Google Gemini 大模型的命令行工具，自动分析视频（软件操作教程、流程演示等），提取出结构化、详细的操作步骤说明。

[English Version](README_EN.md)

## ✨ 核心特性

- **结构化 JSON 输出** — 借鉴 [Gemini Cookbook](https://github.com/google-gemini/cookbook) 官方推荐方案，使用 `response_schema` 强制模型返回标准 JSON，100% 可解析。
- **原子化动作提取** — 受 [VideoInstruct](https://github.com/PouriaRouzrokh/VideoInstruct) 启发，每个步骤只包含一个核心动作，附带动作类型、操作对象和视觉反馈。
- **多维度分析** — 不仅提取步骤，还自动识别视频中使用的软件/工具，并萃取隐含的技巧与注意事项。
- **灵活的输出格式** — 支持人类可读的文本报告和原始 JSON 两种模式。

## 📋 环境要求

- Python 3.8+
- 有效的 [Google AI API Key](https://aistudio.google.com/apikey)（支持 Gemini 多模态模型）

## 🚀 安装步骤

```bash
# 1. 克隆或下载本项目
# 2. 安装依赖
pip install -r requirements.txt
```

**依赖说明：**
| 包名 | 用途 |
|---|---|
| `google-genai` | Google 官方 Gemini SDK，负责视频上传与多模态分析 |
| `opencv-python` | 提取视频元信息（时长、分辨率、帧率、编码格式） |
| `pydantic` | 数据校验框架（预留扩展用） |

## ⚙️ 配置 API Key

**方式一：环境变量（推荐）**
```powershell
# PowerShell
$env:GOOGLE_API_KEY="您的_API_KEY"
```
```bash
# Linux / macOS
export GOOGLE_API_KEY="您的_API_KEY"
```

**方式二：命令行参数**
```bash
python main.py video.mp4 --api-key "您的_API_KEY"
```

## 📖 使用说明

```bash
python main.py <视频路径> [选项]
```

### 可用选项

| 选项 | 说明 |
|---|---|
| `-o`, `--output` | 输出文件路径（不指定则打印到终端） |
| `--json` | 输出原始 JSON 格式（默认输出人类可读文本） |
| `--api-key` | 直接传入 Google AI API Key |
| `--model` | 指定模型（默认 `gemini-2.0-flash`） |

### 使用示例

```bash
# 基本分析 → 终端显示
python main.py tutorial.mp4

# 保存为文本报告
python main.py tutorial.mp4 -o report.txt

# 导出结构化 JSON（适合程序化处理）
python main.py tutorial.mp4 -o data.json --json

# 使用更强大的模型获取更高精度
python main.py tutorial.mp4 --model gemini-2.5-pro -o report.txt
```

### 输出示例

**文本模式** (`python main.py video.mp4`)：
```
📋 视频概述
   本视频演示了如何在 ArcGIS Pro 中创建缓冲区分析

🛠️  涉及工具
   ArcGIS Pro, Spatial Analyst

📝 操作步骤 (共 5 步)
────────────────────────────────────────────────────────────
[00:03] 步骤 1 (双击) → ArcGIS Pro 图标
       在桌面双击 ArcGIS Pro 快捷方式启动应用程序
       💡 变化: 软件启动界面出现，显示最近项目列表

[00:15] 步骤 2 (点击) → 新建地图按钮
       在起始页中点击"Map"创建一个新的空白地图项目
       💡 变化: 地图视图打开，显示默认的世界底图
...

💡 技巧与注意事项
   1. 缓冲区半径建议使用投影坐标系的米为单位
   2. 分析前请确认数据的坐标系一致性
```

**JSON 模式** (`python main.py video.mp4 --json`)：
```json
{
  "summary": "本视频演示了如何在 ArcGIS Pro 中创建缓冲区分析",
  "software_or_tools": ["ArcGIS Pro", "Spatial Analyst"],
  "steps": [
    {
      "step_id": 1,
      "timestamp": "00:03",
      "action_type": "双击",
      "target_object": "ArcGIS Pro 图标",
      "detail": "在桌面双击 ArcGIS Pro 快捷方式启动应用程序",
      "visual_change": "软件启动界面出现，显示最近项目列表"
    }
  ],
  "tips": ["缓冲区半径建议使用投影坐标系的米为单位"]
}
```

## 📁 项目结构

```
P2/
├── main.py              # CLI 主入口：参数解析、流程编排、结果输出
├── ai_analyzer.py       # AI 核心：Prompt 工程、JSON Schema、Gemini API 调用
├── video_processor.py   # 视频处理：OpenCV 元信息提取
├── requirements.txt     # Python 依赖
└── README.md            # 本文件
```

## 🙏 致谢与技术参考

本项目的设计借鉴了以下优秀的开源工作：

| 项目 | 借鉴内容 |
|---|---|
| [PouriaRouzrokh/VideoInstruct](https://github.com/PouriaRouzrokh/VideoInstruct) | "指令推理"型 Prompt 设计、动作原子化方法论 |
| [google-gemini/cookbook](https://github.com/google-gemini/cookbook) | `response_schema` 结构化输出、长视频上下文缓存 |
| [YahyaBagia/recipe-video-ai](https://github.com/YahyaBagia/recipe-video-ai) | 步骤 Schema 定义、工具/对象字段拆分 |
| [OpenGVLab/VideoChat2](https://github.com/OpenGVLab/VideoChat2) | 时空推理、关键帧采样策略（未来扩展） |
| [DAMO-NLP-SG/VideoLLaMA2](https://github.com/DAMO-NLP-SG/VideoLLaMA2) | 音视频多模态融合思路（未来扩展） |
