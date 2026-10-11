"""Entry point for JARVIS."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import settings
from jarvis.core.agent import Agent
from jarvis.ui.main_window import run_ui


def main() -> None:
    print(f"{settings.app.name} v{settings.app.version} starting...")
    agent = Agent()
    run_ui(agent)


if __name__ == "__main__":
    main()
