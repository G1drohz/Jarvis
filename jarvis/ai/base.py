"""AI provider abstraction + factory."""

from __future__ import annotations

from abc import ABC, abstractmethod

from config.settings import AISettings, settings as app_settings


class AIProvider(ABC):
    name: str = "base"

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        ...


class StubProvider(AIProvider):
    name = "stub"

    def chat(self, messages: list[dict[str, str]]) -> str:
        last = messages[-1]["content"] if messages else ""
        return (
            f"[stub] Received: «{last[:140]}». "
            "Set ai.provider + API key (or Ollama) for real answers."
        )


def get_provider(cfg: AISettings | None = None) -> AIProvider:
    cfg = cfg or app_settings.ai
    p = (cfg.provider or "stub").lower()

    if p == "openai" and cfg.api_key:
        from jarvis.ai.providers import OpenAICompatibleProvider

        return OpenAICompatibleProvider(
            cfg, base_url="https://api.openai.com/v1", name="openai"
        )
    if p == "grok" and cfg.api_key:
        from jarvis.ai.providers import OpenAICompatibleProvider

        return OpenAICompatibleProvider(
            cfg, base_url="https://api.x.ai/v1", name="grok", default_model="grok-2"
        )
    if p == "deepseek" and cfg.api_key:
        from jarvis.ai.providers import OpenAICompatibleProvider

        return OpenAICompatibleProvider(
            cfg,
            base_url="https://api.deepseek.com/v1",
            name="deepseek",
            default_model="deepseek-chat",
        )
    if p == "ollama":
        from jarvis.ai.providers import OllamaProvider

        return OllamaProvider(cfg)
    if p == "gemini" and cfg.api_key:
        from jarvis.ai.providers import GeminiProvider

        return GeminiProvider(cfg)
    if p == "claude" and cfg.api_key:
        from jarvis.ai.providers import ClaudeProvider

        return ClaudeProvider(cfg)

    return StubProvider()


PROVIDERS = ["stub", "openai", "gemini", "claude", "grok", "deepseek", "ollama"]
