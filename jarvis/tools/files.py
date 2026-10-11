"""File system helpers."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from config.settings import settings


def open_path(path: str) -> str:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"not found: {p}"
    try:
        os.startfile(str(p))  # type: ignore[attr-defined]
        return f"opened: {p}"
    except AttributeError:
        import subprocess

        subprocess.Popen(["xdg-open", str(p)])
        return f"opened: {p}"
    except Exception as e:
        return f"open error: {e}"


def list_dir(path: str = ".", limit: int = 50) -> list[str]:
    p = Path(path).expanduser()
    if not p.exists():
        return []
    items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    return [("📁 " if i.is_dir() else "📄 ") + i.name for i in items[:limit]]


def delete_path(path: str) -> str:
    if not settings.permissions.allow_file_access:
        return "file access denied"
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"not found: {p}"
    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return f"deleted: {p}"
    except Exception as e:
        return f"delete error: {e}"


def search_files(root: str, pattern: str, limit: int = 30) -> list[str]:
    root_p = Path(root).expanduser()
    if not root_p.exists():
        return []
    hits = []
    for p in root_p.rglob(pattern):
        hits.append(str(p))
        if len(hits) >= limit:
            break
    return hits
