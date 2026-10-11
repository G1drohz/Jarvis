"""MainWindow loader — offline first, network fallback, no free-var bugs."""
from __future__ import annotations

import sys
from pathlib import Path

_CACHE = Path(__file__).with_name("_main_window_cache.py")
_RAW_URL = (
    "https://raw.githubusercontent.com/G1drohz/Jarvis/"
    "ec6a002c20403a5e7fe429c13f04b46266f4c963/jarvis/ui/main_window.py"
)


def _exec_source(code: str, label: str):
    ns = {"__name__": "jarvis.ui.window_impl"}
    exec(compile(code, label, "exec"), ns)
    return ns["MainWindow"]


def _from_cache_or_network() -> type:
    if _CACHE.exists():
        return _exec_source(_CACHE.read_text(encoding="utf-8"), str(_CACHE))

    import urllib.request

    with urllib.request.urlopen(_RAW_URL, timeout=30) as r:
        text = r.read().decode("utf-8")
    if "def run_ui" in text:
        text = text[: text.rfind("def run_ui")].rstrip() + "\n"
    try:
        _CACHE.write_text(text, encoding="utf-8")
    except OSError:
        pass
    return _exec_source(text, "main_window_remote")


def _load():
    errors: list[str] = []

    # 1) Local compressed / plain body module
    try:
        from jarvis.ui import _main_window_body

        return _main_window_body.MainWindow
    except Exception as e:
        errors.append(f"body: {e}")

    # 2) Cache or download last known-good UI
    try:
        return _from_cache_or_network()
    except Exception as e:
        errors.append(f"cache/net: {e}")

    err_msg = " | ".join(errors)
    print("window_impl load failed:", err_msg, file=sys.stderr)

    from PySide6.QtWidgets import QMainWindow, QLabel

    class MainWindow(QMainWindow):
        def __init__(self, agent):
            super().__init__()
            self.agent = agent
            msg = err_msg  # bind to local, never free var from except

            class _Voice:
                stt_ok = False
                tts_ok = False
                speak_replies = False

                class stt:
                    error = msg

                class tts:
                    @staticmethod
                    def stop():
                        return None

                def status_message(self):
                    return msg

            self.voice = _Voice()

            class _Hud:
                def close(self):
                    return None

                def isVisible(self):
                    return False

                def show_near_corner(self):
                    return None

                def set_status(self, t):
                    return None

            self.hud = _Hud()
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
                    "UI failed to load:\n"
                    + msg
                    + "\n\nDownload latest from:\n"
                    "https://github.com/G1drohz/Jarvis/releases"
                )
            )

    return MainWindow


MainWindow = _load()
