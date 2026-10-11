"""Compact always-on-top HUD overlay."""

from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class HUDWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("JARVIS HUD")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedSize(280, 100)
        self.setStyleSheet(
            """
            QWidget {
                background-color: rgba(15, 23, 42, 230);
                border: 1px solid #3b82f6;
                border-radius: 14px;
            }
            QLabel#title {
                color: #60a5fa;
                font-weight: 700;
                font-size: 14px;
            }
            QLabel#status {
                color: #e5e7eb;
                font-size: 12px;
            }
            """
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        self.title = QLabel("JARVIS")
        self.title.setObjectName("title")
        lay.addWidget(self.title)
        self.status = QLabel("Online")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

    @Slot(str)
    def set_status(self, text: str) -> None:
        self.status.setText(text)

    def show_near_corner(self) -> None:
        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            self.move(screen.right() - self.width() - 24, screen.bottom() - self.height() - 48)
        self.show()
