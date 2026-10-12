"""MainWindow loader.

UI body is jarvis.ui.main_window_body (written by CI from known-good source).
All jarvis.* imports below are intentional so PyInstaller freezes them.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ── Force-include subpackages in frozen builds ─────────────────────
import jarvis.monitor  # noqa: F401
import jarvis.monitor.system  # noqa: F401
import jarvis.scenarios  # noqa: F401
import jarvis.scenarios.models  # noqa: F401
import jarvis.scenarios.store  # noqa: F401
import jarvis.scenarios.runner  # noqa: F401
import jarvis.ai  # noqa: F401
import jarvis.ai.base  # noqa: F401
import jarvis.ai.providers  # noqa: F401
import jarvis.i18n  # noqa: F401
import jarvis.i18n.loader  # noqa: F401
import jarvis.ui.hud  # noqa: F401
import jarvis.ui.styles  # noqa: F401
import jarvis.ui.voice_worker  # noqa: F401
import jarvis.ui.tray  # noqa: F401
import jarvis.voice  # noqa: F401
import jarvis.voice.controller  # noqa: F401
import jarvis.voice.wake  # noqa: F401
import jarvis.stt  # noqa: F401
import jarvis.stt.engine  # noqa: F401
import jarvis.tts  # noqa: F401
import jarvis.tts.engine  # noqa: F401
import jarvis.tts.models  # noqa: F401
import jarvis.plugins  # noqa: F401
import jarvis.plugins.loader  # noqa: F401
import jarvis.safety  # noqa: F401
import jarvis.safety.confirm  # noqa: F401
import jarvis.tools  # noqa: F401
import jarvis.tools.browser  # noqa: F401
import jarvis.tools.files  # noqa: F401
import jarvis.tools.windows  # noqa: F401
import jarvis.tools.windows_ctrl  # noqa: F401
import jarvis.vision  # noqa: F401
import jarvis.vision.engine  # noqa: F401
import jarvis.integrations  # noqa: F401
import jarvis.integrations.steam  # noqa: F401
import jarvis.integrations.discord  # noqa: F401
import jarvis.integrations.github_int  # noqa: F401
import jarvis.memory  # noqa: F401
import jarvis.memory.sqlite_store  # noqa: F401
import jarvis.commands  # noqa: F401
import jarvis.commands.registry  # noqa: F401
import jarvis.core  # noqa: F401
import jarvis.core.agent  # noqa: F401
import jarvis.permissions  # noqa: F401
import config.settings  # noqa: F401

_BODY = Path(__file__).with_name("main_window_body.py")
_CACHE = Path(__file__).with_name("_main_window_cache.py")
_RAW_URL = (
    "https://raw.githubusercontent.com/G1drohz/Jarvis/"
    "ec6a002c20403a5e7fe429c13f04b46266f4c963/jarvis/ui/main_window.py"
)


def _exec_file(path: Path):
    code = path.read_text(encoding="utf-8")
    if "def run_ui" in code:
        code = code[: code.rfind("def run_ui")].rstrip() + "\n"
    ns = {"__name__": "jarvis.ui.main_window_body", "__file__": str(path)}
    exec(compile(code, str(path), "exec"), ns)
    return ns["MainWindow"]


def _ensure_body() -> Path:
    if _BODY.exists() and _BODY.stat().st_size > 1000:
        return _BODY
    if _CACHE.exists() and _CACHE.stat().st_size > 1000:
        return _CACHE
    import urllib.request

    with urllib.request.urlopen(_RAW_URL, timeout=45) as r:
        text = r.read().decode("utf-8")
    if "def run_ui" in text:
        text = text[: text.rfind("def run_ui")].rstrip() + "\n"
    _BODY.write_text(text, encoding="utf-8")
    return _BODY


def _load():
    err_msg = "unknown"
    try:
        # Preferred: real package module (if present as .py in tree)
        try:
            from jarvis.ui.main_window_body import MainWindow as MW  # type: ignore

            return MW
        except Exception:
            pass
        path = _ensure_body()
        return _exec_file(path)
    except Exception as e:
        err_msg = str(e)
        print("window_impl load failed:", err_msg, file=sys.stderr)

    from PySide6.QtWidgets import QLabel, QMainWindow

    class MainWindow(QMainWindow):
        def __init__(self, agent):
            super().__init__()
            self.agent = agent
            msg = err_msg

            class _V:
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

            self.voice = _V()

            class _H:
                def close(self):
                    return None

                def isVisible(self):
                    return False

                def show_near_corner(self):
                    return None

                def set_status(self, t):
                    return None

            self.hud = _H()
            self._wake_worker = type("W", (), {})()
            self._wake_thread = type(
                "T", (), {"quit": lambda s: None, "wait": lambda s, x=0: None}
            )()
            self._voice_thread = type(
                "T", (), {"quit": lambda s: None, "wait": lambda s, x=0: None}
            )()
            self.setWindowTitle("JARVIS")
            self.resize(720, 220)
            self.setCentralWidget(
                QLabel(
                    "Не удалось загрузить интерфейс:\n"
                    + msg
                    + "\n\nСкачай JARVIS-Setup-0.3.3.exe:\n"
                    "https://github.com/G1drohz/Jarvis/releases/latest"
                )
            )

    return MainWindow


MainWindow = _load()
