# -*- coding: utf-8 -*-
"""
视频操作分析器 - 专业桌面 GUI (Pro 版)
=======================================
基于 PySide6 构建的现代深色模式界面。
集成异步分析、拖拽上传、关键帧截取、多格式导出。
"""

import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QScrollArea, QFrame,
    QLineEdit, QComboBox, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from src.analyzer.engine import analyze_video
from src.utils.video import get_video_info, format_timestamp, extract_keyframes
from src.utils.export import format_result_text, export_markdown, export_json
from src.ui.styles import STYLE_SHEET


# ---------------------------------------------------------------------------
# 异步分析线程
# ---------------------------------------------------------------------------

class AnalysisWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, video_path, api_key, model):
        super().__init__()
        self.video_path = video_path
        self.api_key = api_key
        self.model = model

    def run(self):
        try:
            self.progress.emit("正在连接 Gemini 服务...")
            result = analyze_video(self.video_path, self.api_key, self.model)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------------------------------------------------------
# UI 组件：操作步骤卡片
# ---------------------------------------------------------------------------

class StepCard(QFrame):
    def __init__(self, step_data):
        super().__init__()
        self.setObjectName("StepCard")
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        ts = step_data.get("timestamp", "00:00")
        action = step_data.get("action_type", "操作")
        target = step_data.get("target_object", "")

        header_label = QLabel(f"[{ts}] {action}")
        header_label.setObjectName("StepHeader")
        header_layout.addWidget(header_label)

        if target:
            target_label = QLabel(f"-> {target}")
            target_label.setStyleSheet("color: #AAAAAA; font-style: italic;")
            header_layout.addWidget(target_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)

        detail_label = QLabel(step_data.get("detail", ""))
        detail_label.setWordWrap(True)
        detail_label.setStyleSheet("color: #E0E0E0; font-size: 13px;")
        layout.addWidget(detail_label)

        visual = step_data.get("visual_change", "")
        if visual:
            v_label = QLabel(f"[Feedback] {visual}")
            v_label.setStyleSheet("color: #00A36C; font-size: 12px;")
            v_label.setWordWrap(True)
            layout.addWidget(v_label)


# ---------------------------------------------------------------------------
# 主窗口
# ---------------------------------------------------------------------------

class VideoAnalyserGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 视频操作步骤提取器 v3.0 (Pro)")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(STYLE_SHEET)
        self.setAcceptDrops(True)

        self.current_video = None
        self.last_result = None
        self.api_key = os.environ.get("GOOGLE_API_KEY", "")

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- 侧边栏 ----
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(280)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(15)

        title = QLabel("Zenith Pro")
        title.setObjectName("Title")
        side_layout.addWidget(title)

        side_layout.addWidget(QLabel("Google AI API Key"))
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.Password)
        self.api_input.setPlaceholderText("在此输入 API Key...")
        self.api_input.setText(self.api_key)
        side_layout.addWidget(self.api_input)

        self.btn_save_key = QPushButton("Save Config")
        self.btn_save_key.setObjectName("SecondaryButton")
        self.btn_save_key.clicked.connect(self.save_api_key)
        side_layout.addWidget(self.btn_save_key)

        side_layout.addWidget(QLabel("Gemini Model"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gemini-2.0-flash", "gemini-2.0-pro"])
        side_layout.addWidget(self.model_combo)

        side_layout.addStretch()

        self.stats_label = QLabel("Ready")
        self.stats_label.setStyleSheet("color: #888888; font-size: 12px;")
        side_layout.addWidget(self.stats_label)

        main_layout.addWidget(sidebar)

        # ---- 内容区 ----
        content_frame = QFrame()
        content_frame.setObjectName("MainContent")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # 左侧：上传与操作
        left_column = QVBoxLayout()

        self.drop_zone = QLabel("Drag & Drop Video Here\nor Click Below to Select")
        self.drop_zone.setObjectName("DropZone")
        self.drop_zone.setAlignment(Qt.AlignCenter)
        self.drop_zone.setMinimumHeight(280)
        self.drop_zone.setWordWrap(True)
        left_column.addWidget(self.drop_zone)

        self.btn_select = QPushButton("Select Video File")
        self.btn_select.setObjectName("SecondaryButton")
        self.btn_select.clicked.connect(self.select_video)
        left_column.addWidget(self.btn_select)

        left_column.addSpacing(15)

        self.btn_analyze = QPushButton("Start AI Analysis")
        self.btn_analyze.setObjectName("PrimaryButton")
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self.start_analysis)
        left_column.addWidget(self.btn_analyze)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        left_column.addWidget(self.progress_bar)

        self.status_msg = QLabel("")
        self.status_msg.setStyleSheet("color: #0078D4;")
        self.status_msg.setWordWrap(True)
        left_column.addWidget(self.status_msg)

        left_column.addStretch()
        content_layout.addLayout(left_column, 2)

        # 右侧：结果展示
        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("Analysis Results"))

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.results_container)
        right_column.addWidget(self.scroll_area)

        # 导出按钮组
        export_row = QHBoxLayout()

        self.btn_export_txt = QPushButton("Export TXT")
        self.btn_export_txt.setObjectName("SecondaryButton")
        self.btn_export_txt.setEnabled(False)
        self.btn_export_txt.clicked.connect(self.export_txt)
        export_row.addWidget(self.btn_export_txt)

        self.btn_export_md = QPushButton("Export Markdown")
        self.btn_export_md.setObjectName("SecondaryButton")
        self.btn_export_md.setEnabled(False)
        self.btn_export_md.clicked.connect(self.export_md)
        export_row.addWidget(self.btn_export_md)

        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_json.setObjectName("SecondaryButton")
        self.btn_export_json.setEnabled(False)
        self.btn_export_json.clicked.connect(self.export_json_file)
        export_row.addWidget(self.btn_export_json)

        right_column.addLayout(export_row)

        content_layout.addLayout(right_column, 3)

        main_layout.addWidget(content_frame)

    # ---- 事件处理 ----

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.load_video(files[0])

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_path:
            self.load_video(file_path)

    def load_video(self, file_path):
        try:
            info = get_video_info(file_path)
            self.current_video = file_path
            duration = format_timestamp(info["duration_sec"])
            self.drop_zone.setText(
                f"Selected: {os.path.basename(file_path)}\n"
                f"Duration: {duration} | Resolution: {info['width']}x{info['height']}"
            )
            self.drop_zone.setStyleSheet("border: 2px solid #0078D4; color: #E0E0E0;")
            self.btn_analyze.setEnabled(True)
            self.status_msg.setText("Ready")
        except Exception as e:
            self.status_msg.setText(f"Load failed: {str(e)}")

    def save_api_key(self):
        new_key = self.api_input.text().strip()
        if not new_key:
            self.status_msg.setText("Please enter a valid API Key")
            return
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(f"GOOGLE_API_KEY={new_key}\n")
            self.status_msg.setText("API Key saved to .env")
            os.environ["GOOGLE_API_KEY"] = new_key
        except Exception as e:
            self.status_msg.setText(f"Save failed: {str(e)}")

    def start_analysis(self):
        api_key = self.api_input.text().strip()
        if not api_key:
            self.status_msg.setText("Please enter API Key first")
            return

        self.set_ui_state(False)
        self.clear_results()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.worker = AnalysisWorker(
            self.current_video, api_key, self.model_combo.currentText()
        )
        self.worker.progress.connect(lambda m: self.status_msg.setText(m))
        self.worker.error.connect(self.on_analysis_error)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.start()

    def on_analysis_error(self, err_msg):
        self.set_ui_state(True)
        self.status_msg.setText(f"Error: {err_msg}")
        self.progress_bar.setVisible(False)

    def on_analysis_finished(self, result):
        self.set_ui_state(True)
        self.progress_bar.setVisible(False)
        self.last_result = result
        self.render_results(result)
        self.btn_export_txt.setEnabled(True)
        self.btn_export_md.setEnabled(True)
        self.btn_export_json.setEnabled(True)

        step_count = len(result.get("steps", []))
        self.status_msg.setText(f"Done! {step_count} steps extracted.")

    def clear_results(self):
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def render_results(self, result):
        if result.get("summary"):
            summary_box = QFrame()
            summary_box.setStyleSheet(
                "background-color: #2D2D2D; border-radius: 8px; padding: 10px;"
            )
            sum_layout = QVBoxLayout(summary_box)
            sum_title = QLabel("Summary")
            sum_title.setStyleSheet("font-weight: bold; color: #FFFFFF;")
            sum_content = QLabel(result["summary"])
            sum_content.setWordWrap(True)
            sum_layout.addWidget(sum_title)
            sum_layout.addWidget(sum_content)
            self.results_layout.addWidget(summary_box)

        for step in result.get("steps", []):
            card = StepCard(step)
            self.results_layout.addWidget(card)

        tips = result.get("tips", [])
        if tips:
            tips_box = QFrame()
            tips_box.setStyleSheet(
                "background-color: #1A2A1A; border: 1px solid #2A4A2A;"
                "border-radius: 8px; margin-top: 10px;"
            )
            tips_layout = QVBoxLayout(tips_box)
            tips_layout.addWidget(QLabel("Tips & Notes"))
            for t in tips:
                t_label = QLabel(f"  {t}")
                t_label.setWordWrap(True)
                tips_layout.addWidget(t_label)
            self.results_layout.addWidget(tips_box)

    def set_ui_state(self, enabled):
        self.btn_analyze.setEnabled(enabled)
        self.btn_select.setEnabled(enabled)
        self.api_input.setEnabled(enabled)
        self.model_combo.setEnabled(enabled)

    # ---- 导出逻辑 ----

    def export_txt(self):
        if not self.last_result:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export TXT", "report.txt", "Text (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(format_result_text(self.last_result))
            self.status_msg.setText(f"Saved: {os.path.basename(path)}")

    def export_md(self):
        if not self.last_result:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Markdown", "report.md", "Markdown (*.md)")
        if path:
            video_name = os.path.basename(self.current_video) if self.current_video else ""
            # 截取关键帧到报告同级目录
            keyframe_dir = None
            if self.current_video:
                keyframe_dir = os.path.join(os.path.dirname(path), "keyframes")
                timestamps = [s.get("timestamp", "00:00") for s in self.last_result.get("steps", [])]
                extract_keyframes(self.current_video, timestamps, keyframe_dir)
                self.status_msg.setText(f"Keyframes saved to: keyframes/")

            content = export_markdown(self.last_result, video_name, keyframe_dir)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_msg.setText(f"Saved: {os.path.basename(path)} (with keyframes)")

    def export_json_file(self):
        if not self.last_result:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export JSON", "data.json", "JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(export_json(self.last_result))
            self.status_msg.setText(f"Saved: {os.path.basename(path)}")


def run_gui():
    app = QApplication(sys.argv)
    window = VideoAnalyserGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
