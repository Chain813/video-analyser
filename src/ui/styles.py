# -*- coding: utf-8 -*-
"""
QSS 样式配置
=============
Premium Dark Theme 样式表，集中管理所有 UI 样式。
"""

STYLE_SHEET = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    color: #E0E0E0;
    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei";
}

QFrame#Sidebar {
    background-color: #1E1E1E;
    border-right: 1px solid #333333;
}

QFrame#MainContent {
    background-color: #121212;
}

QPushButton#PrimaryButton {
    background-color: #0078D4;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #0086F0;
}

QPushButton#PrimaryButton:disabled {
    background-color: #333333;
    color: #888888;
}

QPushButton#SecondaryButton {
    background-color: #2D2D2D;
    color: #E0E0E0;
    border: 1px solid #444444;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton#SecondaryButton:hover {
    background-color: #3D3D3D;
}

QPushButton#SecondaryButton:disabled {
    color: #666666;
}

QLineEdit, QComboBox {
    background-color: #2D2D2D;
    border: 1px solid #444444;
    padding: 8px;
    border-radius: 4px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #1E1E1E;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #444444;
    min-height: 20px;
    border-radius: 4px;
}

QFrame#StepCard {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px;
    margin-bottom: 10px;
}

QLabel#StepHeader {
    color: #0078D4;
    font-weight: bold;
    font-size: 14px;
}

QLabel#DropZone {
    border: 2px dashed #444444;
    border-radius: 10px;
    color: #888888;
    font-size: 16px;
}

QLabel#Title {
    font-size: 20px;
    font-weight: bold;
    color: #FFFFFF;
}
"""
