# AI Video Operation Extractor

A CLI tool powered by Google Gemini that automatically analyzes videos (software tutorials, process demos, etc.) and extracts structured, detailed operational step-by-step instructions.

[中文版 (Chinese Version)](README.md)

## ✨ Key Features

- **Structured JSON Output** — Leveraging the [Gemini Cookbook](https://github.com/google-gemini/cookbook) recommendation, using `response_schema` to force 100% parsable JSON output.
- **Atomic Action Extraction** — Inspired by [VideoInstruct](https://github.com/PouriaRouzrokh/VideoInstruct), each step captures a single core action with type, target object, and visual feedback.
- **Multi-dimensional Analysis** — Automatically identifies software/tools used and extracts hidden tips and notes from the video.
- **Flexible Formats** — Supports both human-readable text reports and raw JSON data.

## 📋 Requirements

- Python 3.8+
- A valid [Google AI API Key](https://aistudio.google.com/apikey) (supporting Gemini multimodal models)

## 🚀 Installation

```bash
# 1. Clone or download this project
# 2. Install dependencies
pip install -r requirements.txt
```

**Dependency Overview:**
| Package | Purpose |
|---|---|
| `google-genai` | Official Google SDK for video upload and multimodal analysis |
| `opencv-python` | Extracts video metadata (duration, resolution, fps, codec) |
| `pydantic` | Data validation framework (reserved for future use) |
| `python-dotenv` | Loads environment variables from `.env` files |

## ⚙️ Configuration

**Option 1: Environment Variable (Recommended)**
Create a `.env` file in the root directory:
```bash
GOOGLE_API_KEY=your_real_api_key_here
```

**Option 2: Command Line Argument**
```bash
python main.py video.mp4 --api-key "your_api_key_here"
```

## 📖 Usage

```bash
python main.py <video_path> [options]
```

### Available Options

| Option | Description |
|---|---|
| `-o`, `--output` | Output file path (prints to terminal if not specified) |
| `--json` | Output raw JSON format (default is human-readable text) |
| `--api-key` | Directly pass the Google AI API Key |
| `--model` | Specify Gemini model (default: `gemini-2.0-flash`) |

### Examples

```bash
# Basic analysis -> Terminal output
python main.py tutorial.mp4

# Save as a text report
python main.py tutorial.mp4 -o report.txt

# Export structured JSON (for programmatic use)
python main.py tutorial.mp4 -o data.json --json

# Use a more powerful model for higher precision
python main.py tutorial.mp4 --model gemini-2.5-pro -o report.txt
```

### Output Example

**Text Mode** (`python main.py video.mp4`):
```
📋 Video Summary
   This video demonstrates how to perform Buffer Analysis in ArcGIS Pro.

🛠️  Tools Involved
   ArcGIS Pro, Spatial Analyst

📝 Operation Steps (Total: 5)
────────────────────────────────────────────────────────────
[00:03] Step 1 (Double-click) → ArcGIS Pro Icon
       Double-click the ArcGIS Pro shortcut on the desktop to launch the app.
       💡 Visual: Splash screen appears, showing the recent projects list.

[00:15] Step 2 (Click) → New Map Button
       Click "Map" on the start page to create a new blank map project.
       💡 Visual: Map view opens with the default world topographic map.
...

💡 Tips & Notes
   1. Buffer radius is recommended to use meters in a projected coordinate system.
   2. Ensure data coordinate systems are consistent before analysis.
```

## 📁 Project Structure

```
P2/
├── main.py              # CLI Entry: Arg parsing, workflow orchestration, output
├── ai_analyzer.py       # AI Core: Prompt engineering, JSON Schema, Gemini API
├── video_processor.py   # Video Utils: OpenCV metadata extraction
├── requirements.txt     # Dependencies
└── README.md            # Documentation (Chinese)
└── README_EN.md         # Documentation (English)
```

## 🙏 Acknowledgments & References

This project design is inspired by several excellent open-source works:
- [PouriaRouzrokh/VideoInstruct](https://github.com/PouriaRouzrokh/VideoInstruct)
- [google-gemini/cookbook](https://github.com/google-gemini/cookbook)
- [YahyaBagia/recipe-video-ai](https://github.com/YahyaBagia/recipe-video-ai)
- [OpenGVLab/VideoChat2](https://github.com/OpenGVLab/VideoChat2)
- [DAMO-NLP-SG/VideoLLaMA2](https://github.com/DAMO-NLP-SG/VideoLLaMA2)
