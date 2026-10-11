"""GitHub integration (open repos / issues via browser)."""

from __future__ import annotations

import webbrowser


def open_repo(owner: str, repo: str) -> str:
    url = f"https://github.com/{owner}/{repo}"
    webbrowser.open(url)
    return f"opened {url}"


def open_url(path: str) -> str:
    if not path.startswith("http"):
        path = "https://github.com/" + path.lstrip("/")
    webbrowser.open(path)
    return f"opened {path}"
