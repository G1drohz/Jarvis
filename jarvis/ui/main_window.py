"""Luxify-style multi-page JARVIS UI — re-export run_ui from app bootstrap."""

# Keep full MainWindow implementation; run_ui comes from app.py for tray support.
from jarvis.ui.window import MainWindow  # noqa: F401
from jarvis.ui.app import run_ui  # noqa: F401

__all__ = ["MainWindow", "run_ui"]
