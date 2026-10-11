"""Discord integration (open app / channel links)."""

from __future__ import annotations

import webbrowser

from jarvis.tools.windows_ctrl import launch_app


def open_discord() -> str:
    try:
        return launch_app("discord:")
    except Exception:
        webbrowser.open("https://discord.com/app")
        return "opened discord web"


def open_channel(invite_or_url: str) -> str:
    webbrowser.open(invite_or_url)
    return f"discord: {invite_or_url}"
