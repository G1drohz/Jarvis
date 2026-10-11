"""Example plugin."""

from __future__ import annotations

from jarvis.commands.base import Command
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class EchoCommand(Command):
    name = "echo"
    description = "Повторить текст (пример плагина)"
    aliases = ["эхо"]

    def match(self, text: str) -> bool:
        return text.strip().lower().startswith(("echo ", "эхо "))

    def execute(self, text: str, agent: "Agent") -> str:
        # strip the command word
        parts = text.strip().split(maxsplit=1)
        return parts[1] if len(parts) > 1 else "(пусто)"


def register(agent: "Agent") -> None:
    """Called by plugin loader (future)."""
    agent.commands.register(EchoCommand())
