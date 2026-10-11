"""Luxify-style multi-page main window for JARVIS with voice control."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot, QMetaObject, Q_ARG
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSlider,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from jarvis.ui.styles import DARK_QSS
from jarvis.ui.voice_worker import start_voice_thread
from jarvis.voice.controller import VoiceController

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


NAV = [
    ("home", "🏠  Home"),
    ("commands", "⚡  Commands"),
    ("ai", "✦  JARVIS AI"),
    ("settings", "⚙  Settings"),
]


class SidebarButton(QPushButton):
    def __init__(self, key: str, label: str, parent=None):
        super().__init__(label, parent)
        self.key = key
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("active", False)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    def __init__(self, agent: "Agent") -> None:
        super().__init__()
        self.agent = agent
        self.setWindowTitle(f"{settings.app.name} v{settings.app.version}")
        self.resize(
            settings.ui.window_width or 1100,
            settings.ui.window_height or 720,
        )
        self.setMinimumSize(800, 560)
        self._listening = False
        self._nav_buttons: dict[str, SidebarButton] = {}

        # Voice
        self.voice = VoiceController(agent)
        agent.voice = self.voice
        self._voice_thread, self._voice_worker = start_voice_thread(self.voice)
        self._voice_worker.status.connect(self._on_voice_status)
        self._voice_worker.finished.connect(self._on_voice_finished)
        self._voice_worker.failed.connect(self._on_voice_failed)

        self.setStyleSheet(DARK_QSS)
        self._build()

        # Show voice status on startup
        self._append("system", self.voice.status_message())

    def closeEvent(self, event) -> None:  # noqa: N802
        self._voice_thread.quit()
        self._voice_thread.wait(2000)
        if self.voice.tts_ok:
            self.voice.tts.stop()
        super().closeEvent(event)

    # ── layout ─────────────────────────────────────────────────────
    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        root_layout.addWidget(self.stack, stretch=1)

        self.pages = {
            "home": self._page_home(),
            "commands": self._page_commands(),
            "ai": self._page_ai(),
            "settings": self._page_settings(),
        }
        for key in ("home", "commands", "ai", "settings"):
            self.stack.addWidget(self.pages[key])

        self._switch("home")

    def _build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(220)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(14, 20, 14, 16)
        lay.setSpacing(4)

        title = QLabel(settings.app.name)
        title.setObjectName("sidebarTitle")
        lay.addWidget(title)

        sub = QLabel(f"v{settings.app.version}  ·  voice ready")
        sub.setObjectName("sidebarSub")
        lay.addWidget(sub)
        lay.addSpacing(20)

        for key, label in NAV:
            btn = SidebarButton(key, label)
            btn.clicked.connect(lambda checked=False, k=key: self._switch(k))
            self._nav_buttons[key] = btn
            lay.addWidget(btn)

        lay.addStretch(1)

        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDot")
        status_row.addWidget(self.status_dot)
        self.status_label = QLabel("Online")
        self.status_label.setObjectName("statusText")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        lay.addLayout(status_row)

        return side

    def _switch(self, key: str) -> None:
        idx = list(self.pages.keys()).index(key)
        self.stack.setCurrentIndex(idx)
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

    # ── Home ───────────────────────────────────────────────────────
    def _page_home(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        header = QHBoxLayout()
        title_col = QVBoxLayout()
        t = QLabel("Home")
        t.setObjectName("pageTitle")
        title_col.addWidget(t)
        s = QLabel("Голос · история · чат")
        s.setObjectName("pageSub")
        title_col.addWidget(s)
        header.addLayout(title_col)
        header.addStretch()

        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setObjectName("mic")
        self.mic_btn.setToolTip("Нажми и говори (распознавание речи)")
        self.mic_btn.clicked.connect(self._on_mic)
        header.addWidget(self.mic_btn)
        lay.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(14)

        hist_card = QFrame()
        hist_card.setObjectName("card")
        hist_lay = QVBoxLayout(hist_card)
        hist_lay.setContentsMargins(14, 12, 14, 12)
        hl = QLabel("История команд")
        hl.setStyleSheet("font-weight: 600; color: #9ca3af; font-size: 12px;")
        hist_lay.addWidget(hl)
        self.history_list = QListWidget()
        self.history_list.setMinimumWidth(240)
        hist_lay.addWidget(self.history_list)
        body.addWidget(hist_card, stretch=1)

        chat_card = QFrame()
        chat_card.setObjectName("card")
        chat_lay = QVBoxLayout(chat_card)
        chat_lay.setContentsMargins(14, 12, 14, 12)
        cl = QLabel("Диалог")
        cl.setStyleSheet("font-weight: 600; color: #9ca3af; font-size: 12px;")
        chat_lay.addWidget(cl)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        chat_lay.addWidget(self.chat, stretch=1)

        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Напиши или нажми 🎤 и говори…")
        self.input.returnPressed.connect(self._on_send)
        input_row.addWidget(self.input, stretch=1)

        send = QPushButton("Отправить")
        send.clicked.connect(self._on_send)
        input_row.addWidget(send)

        clear = QPushButton("Очистить")
        clear.setObjectName("secondary")
        clear.clicked.connect(self._on_clear)
        input_row.addWidget(clear)
        chat_lay.addLayout(input_row)

        body.addWidget(chat_card, stretch=2)
        lay.addLayout(body, stretch=1)

        # Control panel
        controls = QFrame()
        controls.setObjectName("card")
        ctrl = QHBoxLayout(controls)
        ctrl.setContentsMargins(16, 12, 16, 12)
        ctrl.setSpacing(16)

        self.chk_speak = QCheckBox("Озвучивать ответы")
        self.chk_speak.setChecked(settings.voice.speak_replies)
        self.chk_speak.toggled.connect(self._toggle_speak)

        self.chk_silent = QCheckBox("Silent (без TTS)")
        self.chk_silent.toggled.connect(self._toggle_silent)

        self.chk_top = QCheckBox("Always on top")
        self.chk_top.toggled.connect(self._toggle_top)

        for c in (self.chk_speak, self.chk_silent, self.chk_top):
            ctrl.addWidget(c)

        ctrl.addStretch()
        vol_lbl = QLabel("TTS Vol")
        vol_lbl.setStyleSheet("color: #6b7280;")
        ctrl.addWidget(vol_lbl)
        self.vol = QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(int(settings.tts.volume * 100))
        self.vol.setFixedWidth(120)
        self.vol.valueChanged.connect(self._on_vol)
        ctrl.addWidget(self.vol)

        lay.addWidget(controls)

        self._append(
            "system",
            f"{settings.app.name} готов. Нажми 🎤 или напиши help.",
        )
        return page

    # ── Commands ───────────────────────────────────────────────────
    def _page_commands(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        t = QLabel("Commands")
        t.setObjectName("pageTitle")
        lay.addWidget(t)
        s = QLabel("Коллекции → папки → команды  ·  редактор (заготовка)")
        s.setObjectName("pageSub")
        lay.addWidget(s)

        body = QHBoxLayout()
        body.setSpacing(14)

        left = QFrame()
        left.setObjectName("card")
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(12, 12, 12, 12)
        left_lay.addWidget(QLabel("Коллекции"))
        self.cmd_list = QListWidget()
        for name in ("Windows", "Browser", "Media", "System", "Custom"):
            self.cmd_list.addItem(QListWidgetItem(f"📁  {name}"))
        left_lay.addWidget(self.cmd_list)
        add_col = QPushButton("+ Коллекция")
        add_col.setObjectName("secondary")
        left_lay.addWidget(add_col)
        body.addWidget(left, stretch=1)

        right = QFrame()
        right.setObjectName("card")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(16, 14, 16, 14)
        right_lay.addWidget(QLabel("Команда"))

        self.cmd_name = QLineEdit()
        self.cmd_name.setPlaceholderText("Название / голосовая фраза")
        right_lay.addWidget(self.cmd_name)

        self.cmd_actions = QTextEdit()
        self.cmd_actions.setPlaceholderText(
            "Действия:\n1. launch: notepad\n2. type: Hello\n3. key: enter"
        )
        right_lay.addWidget(self.cmd_actions, stretch=1)

        btns = QHBoxLayout()
        btns.addWidget(QPushButton("Сохранить"))
        ai_btn = QPushButton("✦ Создать с AI")
        ai_btn.setObjectName("secondary")
        btns.addWidget(ai_btn)
        btns.addStretch()
        right_lay.addLayout(btns)

        body.addWidget(right, stretch=2)
        lay.addLayout(body, stretch=1)
        return page

    # ── AI ─────────────────────────────────────────────────────────
    def _page_ai(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        header = QHBoxLayout()
        t = QLabel("JARVIS AI")
        t.setObjectName("pageTitle")
        header.addWidget(t)
        header.addStretch()
        self.model_combo = QComboBox()
        self.model_combo.addItems(["stub (offline)", "gpt-4o-mini", "gpt-4o"])
        self.model_combo.setFixedWidth(160)
        header.addWidget(self.model_combo)
        lay.addLayout(header)

        s = QLabel("Чат с моделью")
        s.setObjectName("pageSub")
        lay.addWidget(s)

        self.ai_chat = QTextEdit()
        self.ai_chat.setReadOnly(True)
        lay.addWidget(self.ai_chat, stretch=1)

        row = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Спроси что угодно…")
        self.ai_input.returnPressed.connect(self._on_ai_send)
        row.addWidget(self.ai_input, stretch=1)
        send = QPushButton("Отправить")
        send.clicked.connect(self._on_ai_send)
        row.addWidget(send)
        lay.addLayout(row)

        self._ai_append("system", "AI-чат. Без ключа — stub.")
        return page

    # ── Settings ───────────────────────────────────────────────────
    def _page_settings(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        t = QLabel("Settings")
        t.setObjectName("pageTitle")
        lay.addWidget(t)
        s = QLabel("Интерфейс · AI · голос · права")
        s.setObjectName("pageSub")
        lay.addWidget(s)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.setSpacing(12)

        cl.addWidget(self._section("Голос"))
        stt_info = QLabel(
            f"STT: {'OK' if self.voice.stt_ok else self.voice.stt.error}\n"
            f"TTS: {'OK' if self.voice.tts_ok else self.voice.tts.error}\n"
            f"Язык STT: {settings.stt.language}  ·  движок: {settings.stt.engine}"
        )
        stt_info.setStyleSheet("color: #9ca3af; font-size: 12px;")
        stt_info.setWordWrap(True)
        cl.addWidget(stt_info)

        cl.addWidget(QLabel(f"Wake word (скоро): «{settings.voice.wake_word}»"))

        cl.addWidget(self._section("AI"))
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Провайдер"))
        prov = QComboBox()
        prov.addItems(["stub", "openai"])
        prov.setCurrentText(settings.ai.provider)
        row3.addWidget(prov)
        row3.addStretch()
        cl.addLayout(row3)

        cl.addWidget(self._section("Права"))
        cl.addWidget(QCheckBox("Системные команды"))
        cl.addWidget(QCheckBox("Доступ к файлам"))
        cl.addWidget(QCheckBox("Сеть"))

        cl.addStretch()
        lay.addWidget(card, stretch=1)
        return page

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: 700; color: #93c5fd; font-size: 13px; margin-top: 8px;")
        return lbl

    # ── chat helpers ───────────────────────────────────────────────
    def _append(self, role: str, text: str) -> None:
        if role == "user":
            prefix, color = "Ты", "#60a5fa"
        elif role == "assistant":
            prefix, color = settings.app.name, "#34d399"
        else:
            prefix, color = "Система", "#6b7280"

        html = (
            f'<p style="margin:8px 0;">'
            f'<span style="color:{color};font-weight:600;">{prefix}:</span> '
            f'{text.replace(chr(10), "<br>")}'
            f"</p>"
        )
        self.chat.moveCursor(QTextCursor.MoveOperation.End)
        self.chat.insertHtml(html)
        self.chat.moveCursor(QTextCursor.MoveOperation.End)

        if role in ("user", "assistant"):
            short = text if len(text) < 60 else text[:57] + "…"
            self.history_list.insertItem(0, QListWidgetItem(f"{prefix}: {short}"))

    def _ai_append(self, role: str, text: str) -> None:
        if role == "user":
            prefix, color = "Ты", "#60a5fa"
        elif role == "assistant":
            prefix, color = "AI", "#a78bfa"
        else:
            prefix, color = "Система", "#6b7280"
        html = (
            f'<p style="margin:8px 0;">'
            f'<span style="color:{color};font-weight:600;">{prefix}:</span> '
            f'{text.replace(chr(10), "<br>")}'
            f"</p>"
        )
        self.ai_chat.moveCursor(QTextCursor.MoveOperation.End)
        self.ai_chat.insertHtml(html)
        self.ai_chat.moveCursor(QTextCursor.MoveOperation.End)

    # ── text input ─────────────────────────────────────────────────
    @Slot()
    def _on_send(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self._append("user", text)
        reply = self.agent.process(text)
        self._append("assistant", reply)
        if self.voice.speak_replies and settings.tts.enabled and reply:
            self.voice.speak(reply)

    @Slot()
    def _on_ai_send(self) -> None:
        text = self.ai_input.text().strip()
        if not text:
            return
        self.ai_input.clear()
        self._ai_append("user", text)
        reply = self.agent.process(text)
        self._ai_append("assistant", reply)

    @Slot()
    def _on_clear(self) -> None:
        self.agent.reset_history()
        self.chat.clear()
        self.history_list.clear()
        self._append("system", "История очищена.")

    # ── voice ──────────────────────────────────────────────────────
    @Slot()
    def _on_mic(self) -> None:
        if self._voice_worker.busy or self._listening:
            return
        if not self.voice.stt_ok:
            self._append(
                "system",
                f"Микрофон недоступен: {self.voice.stt.error}\n"
                "Установи: pip install SpeechRecognition\n"
                "Windows PyAudio: pip install pipwin && pipwin install pyaudio",
            )
            return

        self._listening = True
        self.mic_btn.setProperty("listening", True)
        self.mic_btn.style().unpolish(self.mic_btn)
        self.mic_btn.style().polish(self.mic_btn)
        self.status_label.setText("Слушаю…")
        self.status_dot.setStyleSheet("color: #ef4444;")

        # Invoke worker on its thread
        QMetaObject.invokeMethod(
            self._voice_worker,
            "run_once",
            Qt.ConnectionType.QueuedConnection,
        )

    @Slot(str)
    def _on_voice_status(self, status: str) -> None:
        labels = {
            "calibrating": "Калибровка…",
            "listening": "Слушаю…",
            "recognizing": "Распознаю…",
            "done": "Online",
        }
        self.status_label.setText(labels.get(status, status))
        if status == "listening":
            self.status_dot.setStyleSheet("color: #ef4444;")
        elif status == "recognizing":
            self.status_dot.setStyleSheet("color: #f59e0b;")
        elif status == "done":
            self.status_dot.setStyleSheet("color: #22c55e;")
            self._listening = False
            self.mic_btn.setProperty("listening", False)
            self.mic_btn.style().unpolish(self.mic_btn)
            self.mic_btn.style().polish(self.mic_btn)

    @Slot(str, str)
    def _on_voice_finished(self, user_text: str, reply: str) -> None:
        if user_text:
            self._append("user", user_text)
        if reply:
            self._append("assistant", reply)

    @Slot(str)
    def _on_voice_failed(self, err: str) -> None:
        self._append("system", f"Голос: {err}")

    @Slot(bool)
    def _toggle_speak(self, checked: bool) -> None:
        self.voice.speak_replies = checked
        if checked:
            self.chk_silent.setChecked(False)

    @Slot(bool)
    def _toggle_silent(self, checked: bool) -> None:
        if checked:
            self.voice.speak_replies = False
            self.chk_speak.setChecked(False)
        else:
            self.voice.speak_replies = self.chk_speak.isChecked()

    @Slot(int)
    def _on_vol(self, value: int) -> None:
        if self.voice.tts_ok and self.voice.tts._engine is not None:
            self.voice.tts._engine.setProperty("volume", value / 100.0)

    @Slot(bool)
    def _toggle_top(self, checked: bool) -> None:
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        self.show()


def run_ui(agent: "Agent") -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow(agent)
    window.show()
    sys.exit(app.exec())
