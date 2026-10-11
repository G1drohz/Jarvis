"""Command registry and built-in commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jarvis.commands.base import Command

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class HelpCommand(Command):
    name = "help"
    description = "Показать список команд"
    aliases = ["помощь", "?"]

    def match(self, text: str) -> bool:
        t = text.strip().lower()
        return t in {"help", "помощь", "?", "/help"}

    def execute(self, text: str, agent: "Agent") -> str:
        lines = ["Доступные команды:"]
        for cmd in agent.commands._commands:
            aliases = ", ".join(cmd.aliases) if cmd.aliases else "—"
            lines.append(f"  • {cmd.name} ({aliases}) — {cmd.description}")
        return "\n".join(lines)


class ClearCommand(Command):
    name = "clear"
    description = "Очистить историю диалога"
    aliases = ["очистить", "reset"]

    def match(self, text: str) -> bool:
        t = text.strip().lower()
        return t in {"clear", "очистить", "reset", "/clear"}

    def execute(self, text: str, agent: "Agent") -> str:
        agent.reset_history()
        return "История очищена."


class StatusCommand(Command):
    name = "status"
    description = "Показать статус JARVIS"
    aliases = ["статус"]

    def match(self, text: str) -> bool:
        t = text.strip().lower()
        return t in {"status", "статус", "/status"}

    def execute(self, text: str, agent: "Agent") -> str:
        s = agent.settings
        return (
            f"{s.app.name} v{s.app.version}\n"
            f"AI provider: {s.ai.provider}\n"
            f"Memory: {s.memory.path}\n"
            f"Debug: {s.app.debug}"
        )


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: list[Command] = [
            HelpCommand(),
            ClearCommand(),
            StatusCommand(),
        ]

    def register(self, command: Command) -> None:
        self._commands.append(command)

    def try_execute(self, text: str, agent: "Agent") -> str | None:
        for cmd in self._commands:
            if cmd.match(text):
                return cmd.execute(text, agent)
        return None
