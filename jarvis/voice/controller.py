"""Voice controller: STT + TTS + wake word."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from config.settings import settings
from jarvis.stt.engine import STTEngine, create_stt
from jarvis.tts.engine import TTSEngine, create_tts

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


class VoiceController:
    def __init__(self, agent: "Agent") -> None:
        self.agent = agent
        self.stt = create_stt(settings.stt)
        self.tts = create_tts(settings.tts)
        self.speak_replies = settings.voice.speak_replies
        self.wake_enabled = settings.voice.continuous

    @property
    def stt_ok(self) -> bool:
        return self.stt.available

    @property
    def tts_ok(self) -> bool:
        return self.tts.available

    def status_message(self) -> str:
        parts = []
        if self.stt_ok:
            parts.append(f"STT: {self.stt.backend} ({settings.stt.language})")
        else:
            parts.append(f"STT: {self.stt.error or 'off'}")
        if self.tts_ok:
            backend = getattr(self.tts, "backend", "ok")
            voice = settings.tts.voice
            parts.append(f"TTS: {backend} ({voice})")
        else:
            parts.append(f"TTS: {self.tts.error or 'off'}")
        wake = settings.voice.wake_word
        parts.append(f"Wake: «{wake}» {'ON' if self.wake_enabled else 'OFF'}")
        return " · ".join(parts)

    def listen_once(self, on_status: Callable[[str], None] | None = None) -> str:
        if not settings.stt.enabled:
            raise RuntimeError("STT disabled")
        return self.stt.listen_once(on_status=on_status)

    def process_voice(
        self, on_status: Callable[[str], None] | None = None
    ) -> tuple[str, str]:
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
