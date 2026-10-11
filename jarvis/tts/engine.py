"""Text-to-Speech engine (pyttsx3 offline)."""

from __future__ import annotations

import threading
from typing import Callable

from config.settings import TTSSettings, settings as app_settings


class TTSEngine:
    """Speak text using system voices (SAPI5 on Windows)."""

    def __init__(self, cfg: TTSSettings | None = None) -> None:
        self.cfg = cfg or app_settings.tts
        self._engine = None
        self._available = False
        self._error: str | None = None
        self._lock = threading.Lock()
        self._init()

    def _init(self) -> None:
        if (self.cfg.engine or "").lower() == "stub":
            self._error = "TTS engine set to stub"
            return
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.cfg.rate)
            self._engine.setProperty("volume", self.cfg.volume)
            self._pick_voice()
            self._available = True
        except Exception as e:
            self._error = f"TTS init error: {e}"

    def _pick_voice(self) -> None:
        if self._engine is None:
            return
        prefer = (self.cfg.voice or "auto").lower()
        voices = self._engine.getProperty("voices") or []
        if not voices:
            return

        # Prefer Russian / English male-ish voices when possible
        keywords = {
            "jarvis": ["david", "mark", "male", "en-us", "english"],
            "male": ["david", "mark", "male", "paul"],
            "female": ["zira", "female", "irina", "helena"],
            "auto": ["irina", "elena", "russian", "ru-ru", "david", "zira"],
        }
        targets = keywords.get(prefer, keywords["auto"])

        chosen = None
        for v in voices:
            name = (getattr(v, "name", "") or "").lower()
            vid = (getattr(v, "id", "") or "").lower()
            blob = name + " " + vid
            for kw in targets:
                if kw in blob:
                    chosen = v.id
                    break
            if chosen:
                break

        if chosen:
            self._engine.setProperty("voice", chosen)

    @property
    def available(self) -> bool:
        return self._available

    @property
    def error(self) -> str | None:
        return self._error

    def speak(self, text: str, blocking: bool = False) -> None:
        """Speak text. Non-blocking by default (background thread)."""
        text = (text or "").strip()
        if not text:
            return
        if not self._available or self._engine is None:
            print(f"[TTS unavailable] {text[:80]}")
            return

        def _run() -> None:
            with self._lock:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    print(f"[TTS error] {e}")

        if blocking:
            _run()
        else:
            t = threading.Thread(target=_run, daemon=True)
            t.start()

    def stop(self) -> None:
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass

    def list_voices(self) -> list[str]:
        if self._engine is None:
            return []
        voices = self._engine.getProperty("voices") or []
        return [getattr(v, "name", str(v.id)) for v in voices]


def create_tts(cfg: TTSSettings | None = None) -> TTSEngine:
    return TTSEngine(cfg)
