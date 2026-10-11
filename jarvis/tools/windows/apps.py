"""Windows process helpers."""

from __future__ import annotations

import subprocess


def list_running_apps(limit: int = 30) -> list[str]:
    """Return a short list of running process names (Windows)."""
    try:
        out = subprocess.check_output(
            ["tasklist", "/fo", "csv", "/nh"],
            text=True,
            encoding="cp866",
            errors="ignore",
        )
        names = []
        for line in out.splitlines():
            if not line.strip():
                continue
            # CSV: "name","pid","session",...
            part = line.split(",")[0].strip('"')
            if part and part not in names:
                names.append(part)
            if len(names) >= limit:
                break
        return names
    except Exception:
        return ["(не удалось получить список процессов)"]
