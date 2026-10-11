"""Example plugin — registers echo command + sample scenario helper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jarvis.commands.base import Command

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class EchoCommand(Command):
    name = "echo"
    description = "Echo text / повторить текст"
    aliases = ["эхо"]

    def match(self, text: str) -> bool:
        return text.strip().lower().startswith(("echo ", "эхо "))

    def execute(self, text: str, agent: "Agent") -> str:
        parts = text.strip().split(maxsplit=1)
        return parts[1] if len(parts) > 1 else "(empty)"


def register(agent: "Agent") -> None:
    agent.commands.register(EchoCommand())
