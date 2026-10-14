"""MainWindow entry — real package module (no network/exec)."""

from __future__ import annotations

# Side-effect imports so PyInstaller freezes these packages
import jarvis.monitor  # noqa: F401
import jarvis.monitor.system  # noqa: F401
import jarvis.scenarios.models  # noqa: F401
import jarvis.scenarios.store  # noqa: F401
import jarvis.ai.base  # noqa: F401
import jarvis.i18n  # noqa: F401
import jarvis.ui.hud  # noqa: F401
import jarvis.ui.styles  # noqa: F401
import jarvis.ui.voice_worker  # noqa: F401
import jarvis.voice.controller  # noqa: F401

from jarvis.ui.main_window_body import MainWindow

__all__ = ["MainWindow"]
