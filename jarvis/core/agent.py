"""Core JARVIS agent — AI, commands, scenarios, plugins, vision."""

from __future__ import annotations

from config.settings import settings
from jarvis.ai.base import get_provider
from jarvis.commands.registry import CommandRegistry
from jarvis.memory.sqlite_store import MemoryStore
from jarvis.permissions.manager import PermissionManager
from jarvis.plugins.loader import PluginLoader
from jarvis.scenarios.runner import ScenarioRunner
from jarvis.scenarios.store import ScenarioStore
from jarvis.vision.engine import VisionEngine


class Agent:
    def __init__(self) -> None:
        self.settings = settings
        self.memory = MemoryStore(settings.memory.path)
        self.permissions = PermissionManager(settings.permissions)
        self.commands = CommandRegistry()
        self.ai = get_provider(settings.ai)
        self.scenarios = ScenarioStore()
        self.runner = ScenarioRunner()
        self.vision = VisionEngine()
        self.plugins = PluginLoader()
        self._history: list[dict[str, str]] = []
        self.voice = None

        if settings.plugins.auto_load:
            self.plugins.load_all(self)

    def process(self, user_input: str) -> str:
        user_input = user_input.strip()
        if not user_input:
            return ""

        # 1) Built-in / plugin text commands
        cmd_result = self.commands.try_execute(user_input, self)
        if cmd_result is not None:
            self._remember("user", user_input)
            self._remember("assistant", cmd_result)
            return cmd_result

        # 2) Scenario by phrase
        sc = self.scenarios.find_by_phrase(user_input)
        if sc is not None:
            result = self.runner.run(sc)
            self._remember("user", user_input)
            self._remember("assistant", result)
            return result

        # 3) Vision keywords
        low = user_input.lower()
        if any(k in low for k in ("скрин", "screenshot", "что на экране", "what on screen", "анализ экрана")):
            path = self.vision.capture_screen()
            reply = self.vision.describe_image(path, ai_chat=self.ai.chat)
            self._remember("user", user_input)
            self._remember("assistant", reply)
            return reply

        # 4) AI fallback
        self._remember("user", user_input)
        messages = self._build_messages()
        reply = self.ai.chat(messages)
        self._remember("assistant", reply)
        return reply

    def _remember(self, role: str, content: str) -> None:
        self._history.append({"role": role, "content": content})
        self.memory.add_message(role, content)

    def _build_messages(self) -> list[dict[str, str]]:
        lang = settings.app.language
        system = (
            f"You are {self.settings.app.name}, a local AI assistant on the user's PC. "
            f"Reply in {'Russian' if lang == 'ru' else 'English'}. "
            "Be concise and practical. You can control apps via commands/scenarios."
        )
        messages = [{"role": "system", "content": system}]
        messages.extend(self.memory.get_recent(20))
        return messages

    def reset_history(self) -> None:
        self._history.clear()
        self.memory.clear_messages()

    def set_provider(self, name: str) -> None:
        settings.ai.provider = name
        self.ai = get_provider(settings.ai)
