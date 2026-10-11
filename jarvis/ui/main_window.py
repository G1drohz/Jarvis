"""PySide6 main window for JARVIS."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from jarvis.ui.styles import DARK_QSS

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class MainWindow(QMainWindow):
    def __init__(self, agent: "Agent") -> None:
        super().__init__()
        self.agent = agent
        self.setWindowTitle(f"{settings.app.name} v{settings.app.version}")
        self.resize(settings.ui.window_width, settings.ui.window_height)
        self._build_ui()
        self.setStyleSheet(DARK_QSS)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel(settings.app.name)
        title.setObjectName("title")
        layout.addWidget(title)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setPlaceholderText("Диалог появится здесь...")
        layout.addWidget(self.chat, stretch=1)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Напиши сообщение или команду (help)...")
        self.input.returnPressed.connect(self._on_send)
        row.addWidget(self.input, stretch=1)

        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self._on_send)
        row.addWidget(send_btn)

        clear_btn = QPushButton("Очистить")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(self._on_clear)
        row.addWidget(clear_btn)

        layout.addLayout(row)

        self._append("system", f"{settings.app.name} готов. Напиши help для списка команд.")

    def _append(self, role: str, text: str) -> None:
        if role == "user":
            prefix = "Ты"
            color = "#58a6ff"
        elif role == "assistant":
            prefix = settings.app.name
            color = "#3fb950"
        else:
            prefix = "Система"
            color = "#8b949e"

        html = (
            f'<p style="margin:6px 0;">'
            f'<span style="color:{color};font-weight:600;">{prefix}:</span> '
            f'{text.replace(chr(10), "<br>")}'
            f"</p>"
        )
        self.chat.moveCursor(QTextCursor.MoveOperation.End)
        self.chat.insertHtml(html)
        self.chat.moveCursor(QTextCursor.MoveOperation.End)

    @Slot()
    def _on_send(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self._append("user", text)
        reply = self.agent.process(text)
        self._append("assistant", reply)

    @Slot()
    def _on_clear(self) -> None:
        self.agent.reset_history()
        self.chat.clear()
        self._append("system", "История очищена.")


def run_ui(agent: "Agent") -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow(agent)
    window.show()
    sys.exit(app.exec())
