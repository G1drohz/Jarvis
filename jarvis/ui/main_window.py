"""Luxify-style multi-page JARVIS UI v0.2."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot, QMetaObject, QTimer
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
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
from jarvis.ai.base import PROVIDERS
from jarvis.i18n import t, set_language, get_language
from jarvis.monitor.system import SystemMonitor
from jarvis.scenarios.models import Action, Scenario
from jarvis.ui.hud import HUDWindow
from jarvis.ui.styles import DARK_QSS
from jarvis.ui.voice_worker import start_voice_thread, start_wake_thread
from jarvis.voice.controller import VoiceController

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


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
        self.resize(settings.ui.window_width, settings.ui.window_height)
        self.setMinimumSize(900, 600)
        self._listening = False
        self._nav_buttons: dict[str, SidebarButton] = {}
        self._current_collection_id = "custom"
        self.monitor = SystemMonitor()

        self.voice = VoiceController(agent)
        agent.voice = self.voice
        self._voice_thread, self._voice_worker = start_voice_thread(self.voice)
        self._voice_worker.status.connect(self._on_voice_status)
        self._voice_worker.finished.connect(self._on_voice_finished)
        self._voice_worker.failed.connect(self._on_voice_failed)

        self._wake_thread, self._wake_worker = start_wake_thread(self.voice)
        self._wake_worker.status.connect(self._on_wake_status)
        self._wake_worker.command.connect(self._on_wake_command)
        self._wake_worker.failed.connect(self._on_voice_failed)

        self.hud = HUDWindow()
        if settings.ui.hud_enabled:
            self.hud.show_near_corner()

        self.setStyleSheet(DARK_QSS)
        self._build()
        self._append("system", self.voice.status_message())
        self._append(
            "system",
            t(
                "app.ready",
                name=settings.app.name,
                wake=settings.voice.wake_word,
            ),
        )

        if settings.voice.continuous and self.voice.stt_ok:
            QMetaObject.invokeMethod(
                self._wake_worker, "start_loop", Qt.ConnectionType.QueuedConnection
            )

        self._mon_timer = QTimer(self)
        self._mon_timer.timeout.connect(self._refresh_monitor)
        self._mon_timer.start(2000)

    def closeEvent(self, event) -> None:  # noqa: N802
        QMetaObject.invokeMethod(
            self._wake_worker, "stop_loop", Qt.ConnectionType.QueuedConnection
        )
        self._wake_thread.quit()
        self._voice_thread.quit()
        self._wake_thread.wait(1500)
        self._voice_thread.wait(1500)
        if self.voice.tts_ok:
            self.voice.tts.stop()
        self.hud.close()
        super().closeEvent(event)

    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())
        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        layout.addWidget(self.stack, stretch=1)

        self.page_keys = ["home", "commands", "ai", "monitor", "plugins", "settings"]
        self.pages = {
            "home": self._page_home(),
            "commands": self._page_commands(),
            "ai": self._page_ai(),
            "monitor": self._page_monitor(),
            "plugins": self._page_plugins(),
            "settings": self._page_settings(),
        }
        for k in self.page_keys:
            self.stack.addWidget(self.pages[k])
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
        sub = QLabel(f"v{settings.app.version}")
        sub.setObjectName("sidebarSub")
        lay.addWidget(sub)
        lay.addSpacing(16)

        nav = [
            ("home", t("nav.home")),
            ("commands", t("nav.commands")),
            ("ai", t("nav.ai")),
            ("monitor", t("nav.monitor")),
            ("plugins", t("nav.plugins")),
            ("settings", t("nav.settings")),
        ]
        for key, label in nav:
            btn = SidebarButton(key, label)
            btn.clicked.connect(lambda checked=False, k=key: self._switch(k))
            self._nav_buttons[key] = btn
            lay.addWidget(btn)

        lay.addStretch(1)
        row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDot")
        row.addWidget(self.status_dot)
        self.status_label = QLabel(t("status.online"))
        self.status_label.setObjectName("statusText")
        row.addWidget(self.status_label)
        row.addStretch()
        lay.addLayout(row)
        return side

    def _switch(self, key: str) -> None:
        self.stack.setCurrentIndex(self.page_keys.index(key))
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

    # ── Home ───────────────────────────────────────────────────────
    def _page_home(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(14)

        header = QHBoxLayout()
        col = QVBoxLayout()
        t1 = QLabel(t("home.title"))
        t1.setObjectName("pageTitle")
        col.addWidget(t1)
        t2 = QLabel(t("home.sub"))
        t2.setObjectName("pageSub")
        col.addWidget(t2)
        header.addLayout(col)
        header.addStretch()
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setObjectName("mic")
        self.mic_btn.clicked.connect(self._on_mic)
        header.addWidget(self.mic_btn)
        lay.addLayout(header)

        body = QHBoxLayout()
        hist_card = QFrame()
        hist_card.setObjectName("card")
        hl = QVBoxLayout(hist_card)
        hl.setContentsMargins(14, 12, 14, 12)
        hl.addWidget(QLabel(t("home.history")))
        self.history_list = QListWidget()
        hl.addWidget(self.history_list)
        body.addWidget(hist_card, 1)

        chat_card = QFrame()
        chat_card.setObjectName("card")
        cl = QVBoxLayout(chat_card)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.addWidget(QLabel(t("home.chat")))
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        cl.addWidget(self.chat, 1)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(
            t("home.placeholder", wake=settings.voice.wake_word)
        )
        self.input.returnPressed.connect(self._on_send)
        row.addWidget(self.input, 1)
        send = QPushButton(t("home.send"))
        send.clicked.connect(self._on_send)
        row.addWidget(send)
        clear = QPushButton(t("home.clear"))
        clear.setObjectName("secondary")
        clear.clicked.connect(self._on_clear)
        row.addWidget(clear)
        cl.addLayout(row)
        body.addWidget(chat_card, 2)
        lay.addLayout(body, 1)

        controls = QFrame()
        controls.setObjectName("card")
        ctrl = QHBoxLayout(controls)
        ctrl.setContentsMargins(16, 12, 16, 12)

        self.chk_speak = QCheckBox(t("home.speak"))
        self.chk_speak.setChecked(settings.voice.speak_replies)
        self.chk_speak.toggled.connect(lambda v: setattr(self.voice, "speak_replies", v))
        self.chk_wake = QCheckBox(t("home.wake"))
        self.chk_wake.setChecked(settings.voice.continuous)
        self.chk_wake.toggled.connect(self._toggle_wake)
        self.chk_top = QCheckBox(t("home.ontop"))
        self.chk_top.toggled.connect(self._toggle_top)
        self.chk_hud = QCheckBox("HUD")
        self.chk_hud.setChecked(settings.ui.hud_enabled)
        self.chk_hud.toggled.connect(self._toggle_hud)

        for c in (self.chk_speak, self.chk_wake, self.chk_top, self.chk_hud):
            ctrl.addWidget(c)
        ctrl.addStretch()
        self.vol = QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(int(settings.tts.volume * 100))
        self.vol.setFixedWidth(100)
        self.vol.valueChanged.connect(self._on_vol)
        ctrl.addWidget(QLabel("TTS"))
        ctrl.addWidget(self.vol)
        lay.addWidget(controls)
        return page

    # ── Commands editor ────────────────────────────────────────────
    def _page_commands(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(12)

        lay.addWidget(self._title(t("cmds.title"), t("cmds.sub")))

        body = QHBoxLayout()
        left = QFrame()
        left.setObjectName("card")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 12, 12, 12)
        ll.addWidget(QLabel(t("cmds.collections")))
        self.col_list = QListWidget()
        self.sc_list = QListWidget()
        self._reload_collections()
        self.col_list.currentRowChanged.connect(self._on_col_changed)
        self.sc_list.currentRowChanged.connect(self._on_sc_changed)
        ll.addWidget(self.col_list, 1)
        ll.addWidget(QLabel("Scenarios"))
        ll.addWidget(self.sc_list, 2)
        body.addWidget(left, 1)

        right = QFrame()
        right.setObjectName("card")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 14, 16, 14)
        rl.addWidget(QLabel(t("cmds.editor")))
        self.cmd_phrase = QLineEdit()
        self.cmd_phrase.setPlaceholderText(t("cmds.phrase"))
        rl.addWidget(self.cmd_phrase)
        self.cmd_name = QLineEdit()
        self.cmd_name.setPlaceholderText("Name")
        rl.addWidget(self.cmd_name)
        rl.addWidget(QLabel(t("cmds.actions")))
        self.cmd_actions = QTextEdit()
        self.cmd_actions.setPlaceholderText(
            "launch: notepad.exe\n"
            "url: https://youtube.com\n"
            "key: volumeup\n"
            "wait: 1\n"
            "type: Hello\n"
            "open_path: C:\\Users"
        )
        rl.addWidget(self.cmd_actions, 1)

        btns = QHBoxLayout()
        save = QPushButton(t("cmds.save"))
        save.clicked.connect(self._save_scenario)
        btns.addWidget(save)
        run = QPushButton(t("cmds.run"))
        run.setObjectName("secondary")
        run.clicked.connect(self._run_scenario)
        btns.addWidget(run)
        exp = QPushButton(t("cmds.export"))
        exp.setObjectName("ghost")
        exp.clicked.connect(self._export_cmds)
        btns.addWidget(exp)
        imp = QPushButton(t("cmds.import"))
        imp.setObjectName("ghost")
        imp.clicked.connect(self._import_cmds)
        btns.addWidget(imp)
        btns.addStretch()
        rl.addLayout(btns)
        body.addWidget(right, 2)
        lay.addLayout(body, 1)
        return page

    def _reload_collections(self) -> None:
        self.col_list.clear()
        for c in self.agent.scenarios.collections:
            self.col_list.addItem(QListWidgetItem(f"📁 {c.name}"))
        if self.agent.scenarios.collections:
            self.col_list.setCurrentRow(0)

    def _on_col_changed(self, row: int) -> None:
        self.sc_list.clear()
        if row < 0 or row >= len(self.agent.scenarios.collections):
            return
        col = self.agent.scenarios.collections[row]
        self._current_collection_id = col.id
        for sc in col.scenarios:
            self.sc_list.addItem(QListWidgetItem(f"⚡ {sc.name}  «{sc.phrase}»"))

    def _on_sc_changed(self, row: int) -> None:
        col_row = self.col_list.currentRow()
        if col_row < 0 or row < 0:
            return
        col = self.agent.scenarios.collections[col_row]
        if row >= len(col.scenarios):
            return
        sc = col.scenarios[row]
        self.cmd_name.setText(sc.name)
        self.cmd_phrase.setText(sc.phrase)
        lines = [f"{a.type}: {a.value}" for a in sc.actions]
        self.cmd_actions.setPlainText("\n".join(lines))

    def _parse_actions(self) -> list[Action]:
        actions = []
        for line in self.cmd_actions.toPlainText().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                typ, _, val = line.partition(":")
                actions.append(Action(type=typ.strip(), value=val.strip()))
            else:
                actions.append(Action(type="notify", value=line))
        return actions

    @Slot()
    def _save_scenario(self) -> None:
        name = self.cmd_name.text().strip() or "Untitled"
        phrase = self.cmd_phrase.text().strip()
        actions = self._parse_actions()
        sc = Scenario(
            id=self.agent.scenarios.new_id(),
            name=name,
            phrase=phrase,
            actions=actions,
        )
        self.agent.scenarios.add_scenario(self._current_collection_id, sc)
        self._reload_collections()
        self._append("system", f"Saved scenario: {name}")

    @Slot()
    def _run_scenario(self) -> None:
        actions = self._parse_actions()
        sc = Scenario(
            id="tmp",
            name=self.cmd_name.text() or "tmp",
            phrase=self.cmd_phrase.text(),
            actions=actions,
        )
        result = self.agent.runner.run(sc)
        self._append("assistant", result)

    @Slot()
    def _export_cmds(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export", "commands.json", "JSON (*.json)")
        if path:
            self.agent.scenarios.export(Path(path))
            self._append("system", f"Exported → {path}")

    @Slot()
    def _import_cmds(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "JSON (*.json)")
        if path:
            n = self.agent.scenarios.import_file(Path(path))
            self._reload_collections()
            self._append("system", f"Imported {n} scenarios")

    # ── AI ─────────────────────────────────────────────────────────
    def _page_ai(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(12)
        header = QHBoxLayout()
        header.addWidget(self._title_widget(t("ai.title")))
        header.addStretch()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(PROVIDERS)
        self.provider_combo.setCurrentText(settings.ai.provider)
        self.provider_combo.currentTextChanged.connect(self._on_provider)
        header.addWidget(self.provider_combo)
        lay.addLayout(header)
        sub = QLabel(t("ai.sub"))
        sub.setObjectName("pageSub")
        lay.addWidget(sub)
        self.ai_chat = QTextEdit()
        self.ai_chat.setReadOnly(True)
        lay.addWidget(self.ai_chat, 1)
        row = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.returnPressed.connect(self._on_ai_send)
        row.addWidget(self.ai_input, 1)
        send = QPushButton(t("home.send"))
        send.clicked.connect(self._on_ai_send)
        row.addWidget(send)
        lay.addLayout(row)
        return page

    # ── Monitor ────────────────────────────────────────────────────
    def _page_monitor(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.addWidget(self._title(t("mon.title"), t("mon.sub")))
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        self.mon_label = QLabel("…")
        self.mon_label.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")
        cl.addWidget(self.mon_label)
        self.mon_procs = QTextEdit()
        self.mon_procs.setReadOnly(True)
        cl.addWidget(self.mon_procs, 1)
        lay.addWidget(card, 1)
        return page

    def _refresh_monitor(self) -> None:
        if not hasattr(self, "mon_label"):
            return
        snap = self.monitor.snapshot()
        if "error" in snap:
            self.mon_label.setText(str(snap["error"]))
            return
        self.mon_label.setText(
            f"CPU {snap.get('cpu_percent', 0):5.1f}%    "
            f"RAM {snap.get('ram_percent', 0):5.1f}% "
            f"({snap.get('ram_used_gb')} / {snap.get('ram_total_gb')} GB)    "
            f"Processes: {snap.get('processes', 0)}"
        )
        self.mon_procs.setPlainText("\n".join(self.monitor.top_processes()))
        if self.hud.isVisible():
            self.hud.set_status(
                f"CPU {snap.get('cpu_percent', 0):.0f}% · RAM {snap.get('ram_percent', 0):.0f}%"
            )

    # ── Plugins ────────────────────────────────────────────────────
    def _page_plugins(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.addWidget(self._title(t("pl.title"), t("pl.sub")))
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 12, 14, 12)
        self.plugin_list = QListWidget()
        for p in self.agent.plugins.discover():
            status = p.error or "OK"
            self.plugin_list.addItem(QListWidgetItem(f"🧩 {p.name}  —  {status}"))
        cl.addWidget(self.plugin_list)
        reload_btn = QPushButton("Reload plugins")
        reload_btn.setObjectName("secondary")
        reload_btn.clicked.connect(self._reload_plugins)
        cl.addWidget(reload_btn)
        lay.addWidget(card, 1)
        return page

    @Slot()
    def _reload_plugins(self) -> None:
        logs = self.agent.plugins.load_all(self.agent)
        self.plugin_list.clear()
        for p in self.agent.plugins.plugins:
            self.plugin_list.addItem(
                QListWidgetItem(f"🧩 {p.name}  —  {p.error or 'OK'}")
            )
        self._append("system", "Plugins: " + "; ".join(logs))

    # ── Settings ───────────────────────────────────────────────────
    def _page_settings(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.addWidget(self._title(t("set.title"), t("set.sub")))
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.setSpacing(12)

        row = QHBoxLayout()
        row.addWidget(QLabel("Language / Язык"))
        lang = QComboBox()
        lang.addItems(["ru", "en"])
        lang.setCurrentText(get_language())
        lang.currentTextChanged.connect(self._on_lang)
        row.addWidget(lang)
        row.addStretch()
        cl.addLayout(row)

        cl.addWidget(QLabel(self.voice.status_message()))
        cl.addWidget(
            QLabel(
                f"AI: {settings.ai.provider} / {settings.ai.model}\n"
                f"Confirm: {', '.join(settings.permissions.require_confirm_for)}"
            )
        )
        cl.addStretch()
        lay.addWidget(card, 1)
        return page

    # ── helpers ────────────────────────────────────────────────────
    def _title(self, title: str, sub: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        t1 = QLabel(title)
        t1.setObjectName("pageTitle")
        l.addWidget(t1)
        t2 = QLabel(sub)
        t2.setObjectName("pageSub")
        l.addWidget(t2)
        return w

    def _title_widget(self, title: str) -> QLabel:
        t1 = QLabel(title)
        t1.setObjectName("pageTitle")
        return t1

    def _append(self, role: str, text: str) -> None:
        if role == "user":
            prefix, color = t("you"), "#60a5fa"
        elif role == "assistant":
            prefix, color = settings.app.name, "#34d399"
        else:
            prefix, color = t("system"), "#6b7280"
        html = (
            f'<p style="margin:8px 0;">'
            f'<span style="color:{color};font-weight:600;">{prefix}:</span> '
            f'{text.replace(chr(10), "<br>")}</p>'
        )
        self.chat.moveCursor(QTextCursor.MoveOperation.End)
        self.chat.insertHtml(html)
        self.chat.moveCursor(QTextCursor.MoveOperation.End)
        if role in ("user", "assistant"):
            short = text if len(text) < 55 else text[:52] + "…"
            self.history_list.insertItem(0, QListWidgetItem(f"{prefix}: {short}"))

    def _ai_append(self, role: str, text: str) -> None:
        color = {"user": "#60a5fa", "assistant": "#a78bfa"}.get(role, "#6b7280")
        prefix = {"user": t("you"), "assistant": "AI"}.get(role, t("system"))
        html = (
            f'<p style="margin:8px 0;"><span style="color:{color};font-weight:600;">'
            f"{prefix}:</span> {text.replace(chr(10), '<br>')}</p>"
        )
        self.ai_chat.moveCursor(QTextCursor.MoveOperation.End)
        self.ai_chat.insertHtml(html)

    @Slot()
    def _on_send(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self._append("user", text)
        reply = self.agent.process(text)
        self._append("assistant", reply)
        if self.voice.speak_replies and reply:
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

    @Slot()
    def _on_mic(self) -> None:
        if self._voice_worker.busy or self._listening:
            return
        if not self.voice.stt_ok:
            self._append("system", f"STT: {self.voice.stt.error}")
            return
        self._listening = True
        self.mic_btn.setProperty("listening", True)
        self.mic_btn.style().unpolish(self.mic_btn)
        self.mic_btn.style().polish(self.mic_btn)
        QMetaObject.invokeMethod(
            self._voice_worker, "run_once", Qt.ConnectionType.QueuedConnection
        )

    @Slot(str)
    def _on_voice_status(self, status: str) -> None:
        labels = {
            "calibrating": t("voice.calibrating"),
            "listening": t("voice.listening"),
            "recognizing": t("voice.recognizing"),
            "done": t("status.online"),
        }
        self.status_label.setText(labels.get(status, status))
        if status == "done":
            self._listening = False
            self.mic_btn.setProperty("listening", False)
            self.mic_btn.style().unpolish(self.mic_btn)
            self.mic_btn.style().polish(self.mic_btn)
            self.status_dot.setStyleSheet("color: #22c55e;")
        elif status == "listening":
            self.status_dot.setStyleSheet("color: #ef4444;")

    @Slot(str, str)
    def _on_voice_finished(self, user_text: str, reply: str) -> None:
        if user_text:
            self._append("user", user_text)
        if reply:
            self._append("assistant", reply)

    @Slot(str)
    def _on_voice_failed(self, err: str) -> None:
        self._append("system", err)

    @Slot(str)
    def _on_wake_status(self, status: str) -> None:
        if status == "wake_listen":
            self.status_label.setText(t("voice.wake"))
            self.hud.set_status(t("voice.wake"))
        elif status == "wake_triggered":
            self.status_label.setText(t("voice.listening"))

    @Slot(str)
    def _on_wake_command(self, text: str) -> None:
        self._append("user", text)
        reply = self.agent.process(text)
        self._append("assistant", reply)
        if self.voice.speak_replies and reply:
            self.voice.speak(reply)

    @Slot(bool)
    def _toggle_wake(self, on: bool) -> None:
        self.voice.wake_enabled = on
        if on and self.voice.stt_ok:
            QMetaObject.invokeMethod(
                self._wake_worker, "start_loop", Qt.ConnectionType.QueuedConnection
            )
        else:
            QMetaObject.invokeMethod(
                self._wake_worker, "stop_loop", Qt.ConnectionType.QueuedConnection
            )

    @Slot(bool)
    def _toggle_top(self, on: bool) -> None:
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, on)
        self.show()

    @Slot(bool)
    def _toggle_hud(self, on: bool) -> None:
        if on:
            self.hud.show_near_corner()
        else:
            self.hud.hide()

    @Slot(int)
    def _on_vol(self, value: int) -> None:
        if self.voice.tts_ok and self.voice.tts._engine:
            self.voice.tts._engine.setProperty("volume", value / 100.0)

    @Slot(str)
    def _on_provider(self, name: str) -> None:
        self.agent.set_provider(name)
        self._ai_append("system", f"Provider → {name}")

    @Slot(str)
    def _on_lang(self, lang: str) -> None:
        set_language(lang)
        settings.app.language = lang
        self._append("system", f"Language → {lang} (restart UI labels on next launch)")


def run_ui(agent: "Agent") -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow(agent)
    window.show()
    sys.exit(app.exec())
