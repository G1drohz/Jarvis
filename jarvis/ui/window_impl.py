"""MainWindow — load from embedded cache only (no free-var bugs)."""
from __future__ import annotations

import sys
from pathlib import Path

# Packed next to this file by CI / first-run download
_CACHE = Path(__file__).with_name("_main_window_cache.py")
_RAW_URL = (
    "https://raw.githubusercontent.com/G1drohz/Jarvis/"
    "ec6a002c20403a5e7fe429c13f04b46266f4c963/jarvis/ui/main_window.py"
)


def _prepare_cache() -> Path:
    if _CACHE.exists() and _CACHE.stat().st_size > 1000:
        return _CACHE
    # Try download once (dev / first portable run)
    try:
        import urllib.request

        with urllib.request.urlopen(_RAW_URL, timeout=45) as r:
            text = r.read().decode("utf-8")
        if "def run_ui" in text:
            text = text[: text.rfind("def run_ui")].rstrip() + "\n"
        _CACHE.write_text(text, encoding="utf-8")
    except Exception as ex:
        raise RuntimeError(
            f"UI module missing and download failed: {ex}. "
            "Reinstall JARVIS-Setup from GitHub Releases."
        ) from ex
    return _CACHE


def _load():
    err_msg = "unknown"
    try:
        path = _prepare_cache()
        code = path.read_text(encoding="utf-8")
        ns = {"__name__": "jarvis.ui.window_impl"}
        exec(compile(code, str(path), "exec"), ns)
        return ns["MainWindow"]
    except Exception as e:
        err_msg = str(e)
        print("window_impl load failed:", err_msg, file=sys.stderr)

    from PySide6.QtWidgets import QLabel, QMainWindow

    class MainWindow(QMainWindow):
        def __init__(self, agent):
            super().__init__()
            self.agent = agent
            msg = err_msg  # local bind — never use exception var e here

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
            self.resize(640, 200)
            self.setCentralWidget(
                QLabel(
                    "Не удалось загрузить интерфейс:\n"
                    + msg
                    + "\n\nСкачай заново:\n"
                    "https://github.com/G1drohz/Jarvis/releases/latest"
                )
            )

    return MainWindow


MainWindow = _load()
