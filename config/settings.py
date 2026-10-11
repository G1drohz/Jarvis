from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


def _root() -> Path:
    env = os.environ.get("JARVIS_ROOT")
    if env:
        return Path(env)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


ROOT = _root()
CONFIG_PATH = ROOT / "config" / "default.yaml"
if not CONFIG_PATH.exists():
    # bundled config next to exe or in _MEIPASS
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        alt = Path(meipass) / "config" / "default.yaml"
        if alt.exists():
            CONFIG_PATH = alt


class AppSettings(BaseModel):
    name: str = "JARVIS"
    version: str = "0.2.1"
    debug: bool = True
    language: str = "ru"


class AISettings(BaseModel):
    provider: str = "stub"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1024
    api_key: str | None = None
    ollama_base: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"


class MemorySettings(BaseModel):
    path: str = "data/jarvis_memory.db"


class UISettings(BaseModel):
    theme: str = "dark"
    window_width: int = 1200
    window_height: int = 780
    hud_enabled: bool = True
    start_in_tray: bool = False


class PermissionsSettings(BaseModel):
    allow_system_commands: bool = False
    allow_file_access: bool = True
    allow_network: bool = True
    require_confirm_for: list[str] = Field(
        default_factory=lambda: ["shutdown", "restart", "delete_file", "run_shell"]
    )


class STTSettings(BaseModel):
    enabled: bool = True
    engine: str = "auto"
    language: str = "ru-RU"
    phrase_time_limit: int = 8
    ambient_duration: float = 0.5
    vosk_model_path: str = ""


class TTSSettings(BaseModel):
    enabled: bool = True
    engine: str = "pyttsx3"
    voice: str = "auto"
    rate: int = 175
    volume: float = 0.9


class VoiceSettings(BaseModel):
    speak_replies: bool = True
    wake_word: str = "джарвис"
    wake_word_en: str = "jarvis"
    continuous: bool = True
    wake_cooldown_sec: float = 1.5


class VisionSettings(BaseModel):
    enabled: bool = True


class PluginsSettings(BaseModel):
    auto_load: bool = True
    dirs: list[str] = Field(default_factory=lambda: ["jarvis/plugins", "data/plugins"])


class CommandsSettings(BaseModel):
    store_path: str = "data/commands.json"


class Settings(BaseModel):
    app: AppSettings = Field(default_factory=AppSettings)
    ai: AISettings = Field(default_factory=AISettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    ui: UISettings = Field(default_factory=UISettings)
    permissions: PermissionsSettings = Field(default_factory=PermissionsSettings)
    stt: STTSettings = Field(default_factory=STTSettings)
    tts: TTSSettings = Field(default_factory=TTSSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    vision: VisionSettings = Field(default_factory=VisionSettings)
    plugins: PluginsSettings = Field(default_factory=PluginsSettings)
    commands: CommandsSettings = Field(default_factory=CommandsSettings)


_ENV_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "grok": "XAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


def load_settings(path: Path | None = None) -> Settings:
    path = path or CONFIG_PATH
    data: dict[str, Any] = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    ai = data.setdefault("ai", {})
    provider = (ai.get("provider") or "stub").lower()
    for prov, env_name in _ENV_KEY_MAP.items():
        key = os.getenv(env_name)
        if key and provider == prov:
            ai["api_key"] = key
    if not ai.get("api_key") and os.getenv("OPENAI_API_KEY"):
        ai["api_key"] = os.getenv("OPENAI_API_KEY")

    return Settings(**data)


settings = load_settings()
