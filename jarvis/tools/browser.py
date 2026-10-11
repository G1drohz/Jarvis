"""Browser helpers."""

from __future__ import annotations

import webbrowser


def open_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"opened: {url}"


def search(query: str, engine: str = "google") -> str:
    engines = {
        "google": f"https://www.google.com/search?q={query}",
        "yandex": f"https://yandex.ru/search/?text={query}",
        "duckduckgo": f"https://duckduckgo.com/?q={query}",
    }
    url = engines.get(engine, engines["google"])
    # naive encode spaces
    url = url.replace(" ", "+")
    return open_url(url)
