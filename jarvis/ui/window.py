"""Main window implementation (split for packaging)."""

from __future__ import annotations

# Re-export original module content by loading from legacy path if needed.
# For simplicity the full MainWindow lives here as a thin import bridge.

import importlib.util
from pathlib import Path

# Prefer the historical implementation file if present as main_window_impl
_impl = Path(__file__).with_name("_main_window_impl.py")
if _impl.exists():
    spec = importlib.util.spec_from_file_location("jarvis.ui._main_window_impl", _impl)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    MainWindow = mod.MainWindow
else:
    # Fallback: define minimal placeholder (should not happen)
    from PySide6.QtWidgets import QMainWindow

    class MainWindow(QMainWindow):
        def __init__(self, agent):
            super().__init__()
            self.agent = agent
            self.setWindowTitle("JARVIS")
