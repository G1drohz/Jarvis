"""Placeholder — full UI is written by CI release workflow into this path before PyInstaller.

For local dev without the body, run:
  curl -o jarvis/ui/main_window_body.py https://raw.githubusercontent.com/G1drohz/Jarvis/ec6a002c20403a5e7fe429c13f04b46266f4c963/jarvis/ui/main_window.py
and strip the trailing run_ui() function.
"""

from __future__ import annotations

raise ImportError(
    "main_window_body is not embedded. "
    "Build via GitHub Actions release, or download the UI source into this file."
)
