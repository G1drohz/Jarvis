"""AI provider abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from config.settings import AISettings


class AIProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send chat messages and return assistant text."""


class StubProvider(AIProvider):
    """Offline stub for development without API key."""

    def chat(self, messages: list[dict[str, str]]) -> str:
        last = messages[-1]["content"] if messages else ""
        return (
            f"[stub] Я получил: «{last[:120]}». "
            "Подключи OPENAI_API_KEY и поставь provider: openai в config, "
            "чтобы получить настоящие ответы."
        )


def get_provider(cfg: AISettings) -> AIProvider:
    if cfg.provider == "openai" and cfg.api_key:
        from jarvis.ai.openai_provider import OpenAIProvider
        return OpenAIProvider(cfg)
    return StubProvider()
