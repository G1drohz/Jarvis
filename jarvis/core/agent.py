"""Core JARVIS agent."""

from __future__ import annotations

from typing import Any

from config.settings import settings
from jarvis.ai.base import get_provider
from jarvis.commands.registry import CommandRegistry
from jarvis.memory.sqlite_store import MemoryStore
from jarvis.permissions.manager import PermissionManager


class Agent:
    """Main agent that ties AI, memory, commands and permissions together."""

    def __init__(self) -> None:
        self.settings = settings
        self.memory = MemoryStore(settings.memory.path)
        self.permissions = PermissionManager(settings.permissions)
        self.commands = CommandRegistry()
        self.ai = get_provider(settings.ai)
        self._history: list[dict[str, str]] = []

    def process(self, user_input: str) -> str:
        """Process a single user message and return assistant reply."""
        user_input = user_input.strip()
        if not user_input:
            return ""

        # Try command first
        cmd_result = self.commands.try_execute(user_input, self)
        if cmd_result is not None:
            self._remember("user", user_input)
            self._remember("assistant", cmd_result)
            return cmd_result

        # Fallback to AI
        self._remember("user", user_input)
        messages = self._build_messages()
        reply = self.ai.chat(messages)
        self._remember("assistant", reply)
        return reply

    def _remember(self, role: str, content: str) -> None:
        self._history.append({"role": role, "content": content})
        self.memory.add_message(role, content)

    def _build_messages(self) -> list[dict[str, str]]:
        system = (
            f"You are {self.settings.app.name}, a helpful local AI assistant. "
            "Be concise, practical and friendly. You run on the user's machine."
        )
        messages = [{"role": "system", "content": system}]
        # last N turns from memory
        recent = self.memory.get_recent(20)
        messages.extend(recent)
        return messages

    def reset_history(self) -> None:
        self._history.clear()
        self.memory.clear_messages()
