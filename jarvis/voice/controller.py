"""Voice controller: STT + TTS + optional continuous listen."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from config.settings import settings
from jarvis.stt.engine import STTEngine, create_stt
from jarvis.tts.engine import TTSEngine, create_tts

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class VoiceController:
    """High-level voice API used by the UI."""

    def __init__(self, agent: "Agent") -> None:
        self.agent = agent
        self.stt = create_stt(settings.stt)
        self.tts = create_tts(settings.tts)
        self.speak_replies = settings.voice.speak_replies

    @property
    def stt_ok(self) -> bool:
        return self.stt.available

    @property
    def tts_ok(self) -> bool:
        return self.tts.available

    def status_message(self) -> str:
        parts = []
        if self.stt_ok:
            parts.append(f"STT: OK ({settings.stt.engine}, {settings.stt.language})")
        else:
            parts.append(f"STT: {self.stt.error or 'off'}")
        if self.tts_ok:
            parts.append(f"TTS: OK ({settings.tts.engine})")
        else:
            parts.append(f"TTS: {self.tts.error or 'off'}")
        return " · ".join(parts)

    def listen_once(
        self,
        on_status: Callable[[str], None] | None = None,
    ) -> str:
        """Listen for one phrase and return recognized text."""
        if not settings.stt.enabled:
            raise RuntimeError("STT выключен в настройках")
        return self.stt.listen_once(on_status=on_status)

    def process_voice(
        self,
        on_status: Callable[[str], None] | None = None,
    ) -> tuple[str, str]:
        """Listen → agent.process → optional speak. Returns (user_text, reply)."""
        text = self.listen_once(on_status=on_status)
        if not text:
            return "", ""
        reply = self.agent.process(text)
        if self.speak_replies and settings.tts.enabled and reply:
            self.tts.speak(reply)
        return text, reply

    def speak(self, text: str) -> None:
        if settings.tts.enabled:
            self.tts.speak(text)
