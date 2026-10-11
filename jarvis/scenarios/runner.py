"""Execute scenario actions."""

from __future__ import annotations

import time
from typing import Callable

from jarvis.safety.confirm import confirm_action, needs_confirmation
from jarvis.scenarios.models import Action, Scenario
from jarvis.tools import browser, files, windows_ctrl


class ScenarioRunner:
    def __init__(self, on_log: Callable[[str], None] | None = None) -> None:
        self.on_log = on_log or (lambda m: None)

    def run(self, scenario: Scenario) -> str:
        if scenario.require_confirm or any(
            needs_confirmation(a.type) for a in scenario.actions
        ):
            if not confirm_action("scenario", scenario.name):
                return "Отменено / Cancelled"

        results: list[str] = []
        for i, action in enumerate(scenario.actions, 1):
            try:
                msg = self._run_action(action)
                results.append(f"{i}. {msg}")
                self.on_log(msg)
            except Exception as e:
                err = f"{i}. ERROR {action.type}: {e}"
                results.append(err)
                self.on_log(err)
                break
        return "\n".join(results) if results else "OK"

    def _run_action(self, action: Action) -> str:
        t = action.type.lower()
        v = action.value

        if t in ("shutdown", "restart", "delete_file", "run_shell", "shell"):
            if not confirm_action(t if t != "shell" else "run_shell", v):
                return "cancelled"

        if t == "launch":
            return windows_ctrl.launch_app(v)
        if t == "url":
            return browser.open_url(v)
        if t == "open_path":
            return files.open_path(v)
        if t == "key":
            return windows_ctrl.send_key(v)
        if t == "type":
            return windows_ctrl.type_text(v)
        if t == "wait":
            sec = float(v or action.params.get("seconds", 1))
            time.sleep(sec)
            return f"waited {sec}s"
        if t in ("shell", "run_shell"):
            return windows_ctrl.run_shell(v)
        if t == "notify":
            return f"notify: {v}"
        if t == "shutdown":
            return windows_ctrl.shutdown()
        if t == "restart":
            return windows_ctrl.restart()
        if t == "delete_file":
            return files.delete_path(v)
        return f"unknown action: {t}"
