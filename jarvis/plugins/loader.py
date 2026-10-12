"""Plugin discovery and loading."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from config.settings import settings

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class PluginInfo:
    def __init__(self, name: str, path: str, enabled: bool = True) -> None:
        self.name = name
        self.path = path
        self.enabled = enabled
        self.error: str | None = None


class PluginLoader:
    def __init__(self) -> None:
        self.plugins: list[PluginInfo] = []

    def discover(self) -> list[PluginInfo]:
        found: list[PluginInfo] = []
        seen: set[str] = set()
        for d in settings.plugins.dirs:
            for root in self._candidate_roots(d):
                if not root.exists():
                    continue
                key = str(root.resolve())
                if key in seen:
                    continue
                seen.add(key)
                self._scan_dir(root, found)
        unique: list[PluginInfo] = []
        names: set[str] = set()
        for info in found:
            if info.name in names:
                continue
            names.add(info.name)
            unique.append(info)
        self.plugins = unique
        return unique

    def _candidate_roots(self, d: str) -> list[Path]:
        path = Path(d)
        if path.is_absolute():
            return [path]
        bases: list[Path] = []
        env = os.environ.get("JARVIS_ROOT")
        if env:
            bases.append(Path(env))
        if getattr(sys, "frozen", False):
            bases.append(Path(sys.executable).resolve().parent)
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                bases.append(Path(meipass))
        bases.append(Path(__file__).resolve().parents[2])
        return [b / path for b in bases]

    def _scan_dir(self, root: Path, found: list[PluginInfo]) -> None:
        for py in root.glob("*.py"):
            if py.name.startswith("_") or py.name == "loader.py":
                continue
            found.append(PluginInfo(name=py.stem, path=str(py)))

    def load_all(self, agent: "Agent") -> list[str]:
        logs = []
        for info in self.discover():
            if not info.enabled:
                continue
            try:
                self._load_one(info, agent)
                logs.append(f"loaded: {info.name}")
            except Exception as e:
                info.error = str(e)
                logs.append(f"failed: {info.name}: {e}")
        return logs

    def _load_one(self, info: PluginInfo, agent: "Agent") -> None:
        spec = importlib.util.spec_from_file_location(f"jarvis_plugin_{info.name}", info.path)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load spec")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        if hasattr(mod, "register") and callable(mod.register):
            mod.register(agent)
