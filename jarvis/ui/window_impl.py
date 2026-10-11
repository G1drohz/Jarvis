"""MainWindow loader — offline, no network required."""
from __future__ import annotations

import sys


def _load():
    # Prefer full UI module (compressed offline blob)
    try:
        from jarvis.ui import _main_window_body

        return _main_window_body.MainWindow
    except Exception as e:
        err_msg = str(e)
        print("window_impl load failed:", err_msg, file=sys.stderr)

    # Fallback: minimal window (captures error string, not free var e)
    from PySide6.QtWidgets import QMainWindow, QLabel

    class MainWindow(QMainWindow):
        def __init__(self, agent):
            super().__init__()
            self.agent = agent
            self.voice = type(
                "V",
                (),
                {
                    "stt_ok": False,
                    "tts_ok": False,
                    "speak_replies": False,
                    "stt": type("S", (), {"error": err_msg})(),
                    "tts": type("T", (), {"stop": lambda self: None})(),
                    "status_message": lambda self: err_msg,
                },
            )()
            self.hud = type(
                "H",
                (),
                {
                    "close": lambda self: None,
                    "isVisible": lambda self: False,
                    "show_near_corner": lambda self: None,
                    "set_status": lambda self, t: None,
                },
            )()
            self._wake_worker = type("W", (), {})()
            self._wake_thread = type(
                "T", (), {"quit": lambda s: None, "wait": lambda s, x=0: None}
            )()
            self._voice_thread = type(
                "T", (), {"quit": lambda s: None, "wait": lambda s, x=0: None}
            )()
            self.setWindowTitle("JARVIS")
            self.setCentralWidget(
                QLabel(
                    f"UI load error:\n{err_msg}\n\n"
                    "Reinstall from https://github.com/G1drohz/Jarvis/releases"
                )
            )

    return MainWindow


MainWindow = _load()
