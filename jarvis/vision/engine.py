"""Screen capture + optional AI description."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

from config.settings import settings


class VisionEngine:
    def __init__(self) -> None:
        self.enabled = settings.vision.enabled

    def capture_screen(self, path: str | None = None) -> str:
        if not self.enabled:
            return ""
        out = Path(path or f"data/screenshots/screen_{datetime.now():%Y%m%d_%H%M%S}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            from PIL import ImageGrab

            img = ImageGrab.grab()
            img.save(str(out))
            return str(out)
        except Exception as e:
            return f"capture error: {e}"

    def describe_image(self, path: str, ai_chat=None) -> str:
        if ai_chat is None:
            return f"[Vision] Screenshot saved: {path}. Connect multimodal AI for description."
        # Text-only fallback: ask AI about context
        return ai_chat(
            [
                {
                    "role": "user",
                    "content": f"User captured screen to {path}. Briefly say you received a screenshot and ask what to analyze.",
                }
            ]
        )
