"""Steam integration (launch games via steam://)."""

from __future__ import annotations

import webbrowser


def launch_app(app_id: str) -> str:
    webbrowser.open(f"steam://run/{app_id}")
    return f"steam launch: {app_id}"


def open_store(query: str = "") -> str:
    url = "https://store.steampowered.com/"
    if query:
        url = f"https://store.steampowered.com/search/?term={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"steam store: {query or 'home'}"
