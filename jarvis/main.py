"""JARVIS application entry point (dev + frozen exe)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _app_root() -> Path:
    """Project root in dev; folder next to exe when frozen."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _prepare_env() -> Path:
    root = _app_root()
    # Writable data next to exe (or in project)
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "screenshots").mkdir(exist_ok=True)
    (data / "plugins").mkdir(exist_ok=True)

    # Make imports work
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Config path override for frozen builds
    os.environ.setdefault("JARVIS_ROOT", str(root))
    return root


def main() -> None:
    root = _prepare_env()

    # High-DPI
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass

    from config.settings import settings
    from jarvis.core.agent import Agent
    from jarvis.ui.main_window import run_ui

    # Point memory/commands under app root when frozen
    if getattr(sys, "frozen", False):
        settings.memory.path = str(root / "data" / "jarvis_memory.db")
        settings.commands.store_path = str(root / "data" / "commands.json")

    agent = Agent()
    run_ui(agent)


if __name__ == "__main__":
    main()
