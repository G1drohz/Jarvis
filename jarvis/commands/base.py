"""Base command interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class Command(ABC):
    name: str = ""
    description: str = ""
    aliases: list[str] = []

    @abstractmethod
    def match(self, text: str) -> bool:
        """Return True if this command should handle the text."""

    @abstractmethod
    def execute(self, text: str, agent: "Agent") -> str:
        """Run the command and return a reply string."""
