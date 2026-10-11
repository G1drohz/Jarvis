"""MainWindow loader — embeds fetch of last known-good UI module."""
from __future__ import annotations

import sys
from pathlib import Path

_CACHE = Path(__file__).with_name("_main_window_cache.py")
_RAW_URL = (
    "https://raw.githubusercontent.com/G1drohz/Jarvis/"
    "ec6a002c20403a5e7fe429c13f04b46266f4c963/jarvis/ui/main_window.py"
)


def _fetch() -> str:
    if _CACHE.exists():
        return _CACHE.read_text(encoding="utf-8")
    import urllib.request

    with urllib.request.urlopen(_RAW_URL, timeout=30) as r:
        text = r.read().decode("utf-8")
    # strip run_ui to avoid double-bootstrap; keep MainWindow class only
    if "def run_ui" in text:
        text = text[: text.rfind("def run_ui")].rstrip() + "\n"
    _CACHE.write_text(text, encoding="utf-8")
    return text


def _load():
    try:
        code = _fetch()
        ns = {"__name__": "jarvis.ui.window_impl"}
        exec(compile(code, str(_CACHE), "exec"), ns)
        return ns["MainWindow"]
    except Exception as e:
        print("window_impl load failed:", e, file=sys.stderr)
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
                        "stt": type("S", (), {"error": str(e)})(),
                        "tts": type("T", (), {"stop": lambda self: None})(),
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
                    QLabel(f"UI load error: {e}\nNeed internet once to cache UI module.")
                )

        return MainWindow


MainWindow = _load()
