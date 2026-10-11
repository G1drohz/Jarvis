"""Windows control helpers."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def launch_app(target: str) -> str:
    target = target.strip()
    try:
        if platform.system() == "Windows":
            os.startfile(target)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(target, shell=True)
        return f"launched: {target}"
    except Exception as e:
        # try shell
        try:
            subprocess.Popen(target, shell=True)
            return f"launched (shell): {target}"
        except Exception as e2:
            return f"launch failed: {e} / {e2}"


def run_shell(cmd: str) -> str:
    try:
        out = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT, timeout=30
        )
        return out.strip()[:2000] or "OK"
    except Exception as e:
        return f"shell error: {e}"


def send_key(name: str) -> str:
    """Best-effort media/system keys via pyautogui if available."""
    name = name.lower().strip()
    try:
        import pyautogui

        mapping = {
            "volumeup": "volumeup",
            "volumedown": "volumedown",
            "volumemute": "volumemute",
            "playpause": "playpause",
            "nexttrack": "nexttrack",
            "prevtrack": "prevtrack",
            "enter": "enter",
            "escape": "esc",
            "tab": "tab",
        }
        key = mapping.get(name, name)
        pyautogui.press(key)
        return f"key: {key}"
    except ImportError:
        # Windows nircmd / powershell fallback for volume
        if platform.system() == "Windows" and name in ("volumeup", "volumedown", "volumemute"):
            return f"key stub (install pyautogui): {name}"
        return f"key stub (install pyautogui): {name}"
    except Exception as e:
        return f"key error: {e}"


def type_text(text: str) -> str:
    try:
        import pyautogui

        pyautogui.typewrite(text, interval=0.02)
        return f"typed: {text[:40]}"
    except ImportError:
        return "type stub (install pyautogui)"
    except Exception as e:
        return f"type error: {e}"


def shutdown() -> str:
    if platform.system() == "Windows":
        subprocess.Popen(["shutdown", "/s", "/t", "5"])
        return "shutdown in 5s"
    subprocess.Popen(["shutdown", "-h", "now"])
    return "shutdown requested"


def restart() -> str:
    if platform.system() == "Windows":
        subprocess.Popen(["shutdown", "/r", "/t", "5"])
        return "restart in 5s"
    subprocess.Popen(["shutdown", "-r", "now"])
    return "restart requested"


def get_system_info() -> dict:
    return {
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
    }
