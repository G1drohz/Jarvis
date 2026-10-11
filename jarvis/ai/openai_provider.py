"""OpenAI-compatible chat provider (uses httpx)."""

from __future__ import annotations

import httpx

from config.settings import AISettings
from jarvis.ai.base import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, cfg: AISettings) -> None:
        self.cfg = cfg
        self.base_url = "https://api.openai.com/v1"

    def chat(self, messages: list[dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.max_tokens,
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                r = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[AI error] {type(e).__name__}: {e}"
