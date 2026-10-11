from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "default.yaml"


class AppSettings(BaseModel):
    name: str = "JARVIS"
    version: str = "0.1.1"
    debug: bool = True


class AISettings(BaseModel):
    provider: str = "stub"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1024
    api_key: str | None = None


class MemorySettings(BaseModel):
    path: str = "data/jarvis_memory.db"


class UISettings(BaseModel):
    theme: str = "dark"
    window_width: int = 1100
    window_height: int = 720


class PermissionsSettings(BaseModel):
    allow_system_commands: bool = False
    allow_file_access: bool = True
    allow_network: bool = True


class STTSettings(BaseModel):
    enabled: bool = True
    engine: str = "google"
    language: str = "ru-RU"
    phrase_time_limit: int = 8
    ambient_duration: float = 0.5


class TTSSettings(BaseModel):
    enabled: bool = True
    engine: str = "pyttsx3"
    voice: str = "auto"
    rate: int = 175
    volume: float = 0.9


class VoiceSettings(BaseModel):
    speak_replies: bool = True
    wake_word: str = "джарвис"
    continuous: bool = False


class VisionSettings(BaseModel):
    enabled: bool = False


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


def load_settings(path: Path | None = None) -> Settings:
    path = path or CONFIG_PATH
    data: dict[str, Any] = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        data.setdefault("ai", {})["api_key"] = api_key
        data.setdefault("ai", {})["provider"] = data.get("ai", {}).get("provider", "openai")

    return Settings(**data)


settings = load_settings()
