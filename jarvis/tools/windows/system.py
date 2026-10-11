"""Windows system helpers (safe stubs + basic ops)."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def get_system_info() -> dict:
    return {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
    }


def open_path(path: str) -> str:
    """Open a file or folder with the default application (Windows)."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Путь не найден: {p}"
    try:
        os.startfile(str(p))  # type: ignore[attr-defined]
        return f"Открыто: {p}"
    except Exception as e:
        return f"Ошибка открытия: {e}"
