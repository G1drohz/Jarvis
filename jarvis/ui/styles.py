"""Dark theme stylesheet for JARVIS UI."""

DARK_QSS = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 14px;
}
QTextEdit, QLineEdit {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px;
    color: #e6edf3;
    selection-background-color: #1f6feb;
}
QPushButton {
    background-color: #238636;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #2ea043;
}
QPushButton:pressed {
    background-color: #196c2e;
}
QPushButton#secondary {
    background-color: #21262d;
    border: 1px solid #30363d;
}
QPushButton#secondary:hover {
    background-color: #30363d;
}
QLabel#title {
    font-size: 20px;
    font-weight: 700;
    color: #58a6ff;
}
QScrollBar:vertical {
    background: #0d1117;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""
