"""Speech-to-Text stub."""

from __future__ import annotations


class STTEngine:
    """Placeholder. Replace with whisper / vosk / etc later."""

    def __init__(self, engine: str = "stub") -> None:
        self.engine = engine

    def transcribe(self, audio_path: str) -> str:
        return f"[STT stub] would transcribe: {audio_path}"

    def listen_once(self) -> str:
        return "[STT stub] no microphone integration yet"
