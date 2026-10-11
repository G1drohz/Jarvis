"""Luxify-style multi-page main window for JARVIS."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QFont, QTextCursor, QIcon
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
    QSizePolicy,
)

from config.settings import settings
from jarvis.ui.styles import DARK_QSS

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


# ── Sidebar nav items ──────────────────────────────────────────────
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
        self.resize(1100, 720)
        self.setMinimumSize(800, 560)
        self._listening = False
        self._nav_buttons: dict[str, SidebarButton] = {}

        self.setStyleSheet(DARK_QSS)
        self._build()

    # ── layout ─────────────────────────────────────────────────────
    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        # Content stack
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

        sub = QLabel(f"v{settings.app.version}  ·  local assistant")
        sub.setObjectName("sidebarSub")
        lay.addWidget(sub)
        lay.addSpacing(20)

        for key, label in NAV:
            btn = SidebarButton(key, label)
            btn.clicked.connect(lambda checked=False, k=key: self._switch(k))
            self._nav_buttons[key] = btn
            lay.addWidget(btn)

        lay.addStretch(1)

        # Status footer
        status_row = QHBoxLayout()
        dot = QLabel("●")
        dot.setObjectName("statusDot")
        status_row.addWidget(dot)
        st = QLabel("Online")
        st.setObjectName("statusText")
        status_row.addWidget(st)
        status_row.addStretch()
        lay.addLayout(status_row)

        return side

    def _switch(self, key: str) -> None:
        idx = list(self.pages.keys()).index(key)
        self.stack.setCurrentIndex(idx)
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

    # ── Home page ──────────────────────────────────────────────────
    def _page_home(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        t = QLabel("Home")
        t.setObjectName("pageTitle")
        title_col.addWidget(t)
        s = QLabel("История команд · управление · чат")
        s.setObjectName("pageSub")
        title_col.addWidget(s)
        header.addLayout(title_col)
        header.addStretch()

        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setObjectName("mic")
        self.mic_btn.setToolTip("Голосовой ввод (заготовка)")
        self.mic_btn.clicked.connect(self._toggle_mic)
        header.addWidget(self.mic_btn)
        lay.addLayout(header)

        # History + chat split
        body = QHBoxLayout()
        body.setSpacing(14)

        # Left: command history
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

        # Right: chat
        chat_card = QFrame()
        chat_card.setObjectName("card")
        chat_lay = QVBoxLayout(chat_card)
        chat_lay.setContentsMargins(14, 12, 14, 12)
        cl = QLabel("Диалог")
        cl.setStyleSheet("font-weight: 600; color: #9ca3af; font-size: 12px;")
        chat_lay.addWidget(cl)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setPlaceholderText("Диалог появится здесь…")
        chat_lay.addWidget(self.chat, stretch=1)

        # Input row
        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Напиши сообщение или команду (help)…")
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
        ctrl.setSpacing(20)

        self.chk_prefix = QCheckBox("Prefix mode")
        self.chk_silent = QCheckBox("Silent mode")
        self.chk_avatar = QCheckBox("Avatar anim")
        self.chk_top = QCheckBox("Always on top")
        self.chk_top.toggled.connect(self._toggle_top)

        for c in (self.chk_prefix, self.chk_silent, self.chk_avatar, self.chk_top):
            ctrl.addWidget(c)

        ctrl.addStretch()
        vol_lbl = QLabel("Vol")
        vol_lbl.setStyleSheet("color: #6b7280;")
        ctrl.addWidget(vol_lbl)
        self.vol = QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(80)
        self.vol.setFixedWidth(120)
        ctrl.addWidget(self.vol)

        lay.addWidget(controls)

        self._append("system", f"{settings.app.name} готов. Напиши help или выбери раздел слева.")
        return page

    # ── Commands page ──────────────────────────────────────────────
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

        # Tree-like list (collections)
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

        # Command detail
        right = QFrame()
        right.setObjectName("card")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(16, 14, 16, 14)
        right_lay.addWidget(QLabel("Команда"))

        self.cmd_name = QLineEdit()
        self.cmd_name.setPlaceholderText("Название команды / фраза")
        right_lay.addWidget(self.cmd_name)

        self.cmd_actions = QTextEdit()
        self.cmd_actions.setPlaceholderText(
            "Действия (пока текстовый черновик):\n"
            "1. launch: notepad\n"
            "2. type: Hello\n"
            "3. key: enter"
        )
        right_lay.addWidget(self.cmd_actions, stretch=1)

        btns = QHBoxLayout()
        save = QPushButton("Сохранить")
        btns.addWidget(save)
        ai_btn = QPushButton("✦ Создать с AI")
        ai_btn.setObjectName("secondary")
        btns.addWidget(ai_btn)
        btns.addStretch()
        right_lay.addLayout(btns)

        body.addWidget(right, stretch=2)
        lay.addLayout(body, stretch=1)
        return page

    # ── AI page ────────────────────────────────────────────────────
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

        s = QLabel("Чат с моделью  ·  можно прикреплять файлы позже")
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
        attach = QPushButton("+")
        attach.setObjectName("secondary")
        attach.setFixedWidth(44)
        attach.setToolTip("Прикрепить (скоро)")
        row.addWidget(attach)
        lay.addLayout(row)

        self._ai_append("system", "AI-чат. Модель переключается сверху. Без ключа работает stub.")
        return page

    # ── Settings page ──────────────────────────────────────────────
    def _page_settings(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        t = QLabel("Settings")
        t.setObjectName("pageTitle")
        lay.addWidget(t)
        s = QLabel("Интерфейс · AI · права · голос")
        s.setObjectName("pageSub")
        lay.addWidget(s)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.setSpacing(14)

        # Interface
        cl.addWidget(self._section("Интерфейс"))
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Тема"))
        theme = QComboBox()
        theme.addItems(["Тёмная", "Светлая (скоро)"])
        row1.addWidget(theme)
        row1.addStretch()
        cl.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Язык"))
        lang = QComboBox()
        lang.addItems(["Русский", "English"])
        row2.addWidget(lang)
        row2.addStretch()
        cl.addLayout(row2)

        # AI
        cl.addWidget(self._section("AI"))
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Провайдер"))
        prov = QComboBox()
        prov.addItems(["stub", "openai"])
        prov.setCurrentText(settings.ai.provider)
        row3.addWidget(prov)
        row3.addStretch()
        cl.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Модель"))
        model = QLineEdit(settings.ai.model)
        model.setFixedWidth(180)
        row4.addWidget(model)
        row4.addStretch()
        cl.addLayout(row4)

        # Permissions
        cl.addWidget(self._section("Права"))
        cl.addWidget(QCheckBox("Системные команды"))
        cl.addWidget(QCheckBox("Доступ к файлам"))
        cl.addWidget(QCheckBox("Сеть"))

        # Voice
        cl.addWidget(self._section("Голос"))
        cl.addWidget(QCheckBox("STT включён"))
        cl.addWidget(QCheckBox("TTS включён"))

        cl.addStretch()
        lay.addWidget(card, stretch=1)
        return page

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: 700; color: #93c5fd; font-size: 13px; margin-top: 8px;")
        return lbl

    # ── helpers ────────────────────────────────────────────────────
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

        # also push to history list
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

    @Slot()
    def _toggle_mic(self) -> None:
        self._listening = not self._listening
        self.mic_btn.setProperty("listening", self._listening)
        self.mic_btn.style().unpolish(self.mic_btn)
        self.mic_btn.style().polish(self.mic_btn)
        if self._listening:
            self._append("system", "Микрофон: слушаю… (STT пока заготовка)")
        else:
            self._append("system", "Микрофон выключен.")

    @Slot(bool)
    def _toggle_top(self, checked: bool) -> None:
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        self.show()  # re-apply flags


def run_ui(agent: "Agent") -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow(agent)
    window.show()
    sys.exit(app.exec())
