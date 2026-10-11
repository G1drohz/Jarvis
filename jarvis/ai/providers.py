"""Concrete AI providers."""

from __future__ import annotations

import httpx

from config.settings import AISettings
from jarvis.ai.base import AIProvider


class OpenAICompatibleProvider(AIProvider):
    def __init__(
        self,
        cfg: AISettings,
        base_url: str,
        name: str = "openai",
        default_model: str | None = None,
    ) -> None:
        self.cfg = cfg
        self.base_url = base_url.rstrip("/")
        self.name = name
        self.model = cfg.model or default_model or "gpt-4o-mini"

    def chat(self, messages: list[dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.max_tokens,
        }
        try:
            with httpx.Client(timeout=90.0) as client:
                r = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[{self.name} error] {type(e).__name__}: {e}"


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self, cfg: AISettings) -> None:
        self.cfg = cfg
        self.base = cfg.ollama_base.rstrip("/")
        self.model = cfg.ollama_model or cfg.model or "llama3.2"

    def chat(self, messages: list[dict[str, str]]) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False}
        try:
            with httpx.Client(timeout=120.0) as client:
                r = client.post(f"{self.base}/api/chat", json=payload)
                r.raise_for_status()
                data = r.json()
                return (data.get("message") or {}).get("content", "").strip()
        except Exception as e:
            return f"[ollama error] {type(e).__name__}: {e}"


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, cfg: AISettings) -> None:
        self.cfg = cfg
        self.model = cfg.model if "gemini" in (cfg.model or "") else "gemini-1.5-flash"

    def chat(self, messages: list[dict[str, str]]) -> str:
        # Convert to Gemini contents format
        contents = []
        system = ""
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
                continue
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        if system and contents:
            contents[0]["parts"][0]["text"] = system + "\n\n" + contents[0]["parts"][0]["text"]

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.cfg.api_key}"
        )
        try:
            with httpx.Client(timeout=90.0) as client:
                r = client.post(url, json={"contents": contents})
                r.raise_for_status()
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            return f"[gemini error] {type(e).__name__}: {e}"


class ClaudeProvider(AIProvider):
    name = "claude"

    def __init__(self, cfg: AISettings) -> None:
        self.cfg = cfg
        self.model = cfg.model if "claude" in (cfg.model or "") else "claude-3-5-sonnet-20241022"

    def chat(self, messages: list[dict[str, str]]) -> str:
        system = ""
        conv = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                conv.append({"role": m["role"], "content": m["content"]})
        headers = {
            "x-api-key": self.cfg.api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": self.cfg.max_tokens,
            "messages": conv,
        }
        if system:
            payload["system"] = system
        try:
            with httpx.Client(timeout=90.0) as client:
                r = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                )
                r.raise_for_status()
                data = r.json()
                return data["content"][0]["text"].strip()
        except Exception as e:
            return f"[claude error] {type(e).__name__}: {e}"
