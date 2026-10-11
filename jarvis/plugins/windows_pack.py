"""Built-in Windows voice commands pack."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jarvis.commands.base import Command
from jarvis.tools import windows_ctrl, browser

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class LaunchNotepad(Command):
    name = "notepad"
    description = "Open Notepad"
    aliases = ["блокнот"]

    def match(self, text: str) -> bool:
        t = text.lower()
        return "notepad" in t or "блокнот" in t

    def execute(self, text: str, agent: "Agent") -> str:
        return windows_ctrl.launch_app("notepad.exe")


class OpenYouTube(Command):
    name = "youtube"
    description = "Open YouTube"

    def match(self, text: str) -> bool:
        t = text.lower()
        return "youtube" in t or "ютуб" in t or "ютюб" in t

    def execute(self, text: str, agent: "Agent") -> str:
        return browser.open_url("https://youtube.com")


def register(agent: "Agent") -> None:
    agent.commands.register(LaunchNotepad())
    agent.commands.register(OpenYouTube())
