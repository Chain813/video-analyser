# AI Video Operation Extractor

A desktop tool powered by Google Gemini that analyzes videos (software tutorials, process demos, etc.) and extracts structured, step-by-step operational instructions.

[中文版 (Chinese Version)](README.md)

## ✨ Key Features

- **Structured JSON Output** — Uses Gemini `response_schema` for 100% parsable JSON.
- **Atomic Action Extraction** — Each step captures a single action with type, target, and visual feedback.
- **Auto Keyframe Capture** — Automatically screenshots the video at each step's timestamp for visual reports.
- **Multi-format Export** — TXT plain text, Markdown with embedded screenshots, and raw JSON.
- **Professional Desktop GUI** — PySide6-based dark-mode interface with drag-and-drop and one-click export.
- **CLI Mode** — Full command-line support for scripting and batch processing.

## 📋 Requirements

- Python 3.8+
- A valid [Google AI API Key](https://aistudio.google.com/apikey)

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

**Option 1: Save via GUI (Recommended)**

Launch the app, enter your Key in the sidebar, and click "Save Config".

**Option 2: Create a `.env` file**
```bash
GOOGLE_API_KEY=your_api_key_here
```

**Option 3: CLI argument**
```bash
python main.py video.mp4 --api-key "your_key"
```

## 📖 Usage

### GUI Mode (Default)
```bash
python main.py
```

### CLI Mode
```bash
# Print text report to terminal
python main.py tutorial.mp4

# Export Markdown report with keyframes
python main.py tutorial.mp4 -o report.md --md

# Export structured JSON
python main.py tutorial.mp4 -o data.json --json

# Use a specific model
python main.py tutorial.mp4 --model gemini-2.5-pro
```

## 📁 Project Structure

```
video-analyser/
├── src/
│   ├── analyzer/
│   │   ├── engine.py             # Gemini API interaction
│   │   └── prompts.py            # Prompt templates & JSON Schema
│   ├── utils/
│   │   ├── video.py              # Video metadata & keyframe extraction
│   │   └── export.py             # Multi-format export (TXT/MD/JSON)
│   └── ui/
│       ├── main_window.py        # PySide6 main window
│       └── styles.py             # QSS dark theme
├── main.py                       # Unified entry (GUI/CLI)
├── run_app.bat                   # One-click launcher
├── build_exe.bat                 # One-click EXE builder
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md                     # Chinese docs
└── README_EN.md                  # English docs
```

## 🙏 Acknowledgments

- [PouriaRouzrokh/VideoInstruct](https://github.com/PouriaRouzrokh/VideoInstruct)
- [google-gemini/cookbook](https://github.com/google-gemini/cookbook)
- [YahyaBagia/recipe-video-ai](https://github.com/YahyaBagia/recipe-video-ai)
- [OpenGVLab/VideoChat2](https://github.com/OpenGVLab/VideoChat2)
- [DAMO-NLP-SG/VideoLLaMA2](https://github.com/DAMO-NLP-SG/VideoLLaMA2)
