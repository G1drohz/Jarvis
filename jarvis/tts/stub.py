"""Text-to-Speech stub."""

from __future__ import annotations


class TTSEngine:
    """Placeholder. Replace with pyttsx3 / edge-tts / elevenlabs later."""

    def __init__(self, engine: str = "stub", voice: str = "jarvis") -> None:
        self.engine = engine
        self.voice = voice

    def speak(self, text: str) -> None:
        print(f"[TTS:{self.voice}] {text}")

    def save(self, text: str, path: str) -> str:
        return f"[TTS stub] would save speech of «{text[:40]}...» to {path}"
