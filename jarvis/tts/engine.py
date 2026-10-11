"""Text-to-Speech: Jarvis neural voice (edge-tts) + offline pyttsx3 fallback."""

from __future__ import annotations

import asyncio
import os
import tempfile
import threading
from pathlib import Path
from typing import TYPE_CHECKING

from config.settings import TTSSettings, settings as app_settings

if TYPE_CHECKING:
    pass

# Jarvis-style neural voices (Microsoft Edge TTS — free, no key)
JARVIS_VOICES = {
    # British male — closest free "butler / AI assistant" tone
    "jarvis": "en-GB-RyanNeural",
    "jarvis_en": "en-GB-RyanNeural",
    "jarvis_ru": "ru-RU-DmitryNeural",
    "en": "en-GB-RyanNeural",
    "ru": "ru-RU-DmitryNeural",
    "male_en": "en-GB-RyanNeural",
    "male_ru": "ru-RU-DmitryNeural",
    "female_en": "en-GB-SoniaNeural",
    "female_ru": "ru-RU-SvetlanaNeural",
}


class TTSEngine:
    """Speak text. Prefers edge-tts Jarvis voice; falls back to SAPI5/pyttsx3."""

    def __init__(self, cfg: TTSSettings | None = None) -> None:
        self.cfg = cfg or app_settings.tts
        self._engine = None  # pyttsx3
        self._backend = "none"
        self._available = False
        self._error: str | None = None
        self._lock = threading.Lock()
        self._edge_voice = JARVIS_VOICES["jarvis"]
        self._init()

    def _init(self) -> None:
        engine_name = (self.cfg.engine or "auto").lower()
        if engine_name == "stub":
            self._error = "TTS engine set to stub"
            return

        # Resolve preferred Jarvis voice from config
        prefer = (self.cfg.voice or "jarvis").lower()
        lang = (getattr(app_settings.app, "language", "ru") or "ru").lower()

        if prefer in ("jarvis", "auto", ""):
            self._edge_voice = JARVIS_VOICES["jarvis_ru" if lang.startswith("ru") else "jarvis_en"]
        elif prefer in JARVIS_VOICES:
            self._edge_voice = JARVIS_VOICES[prefer]
        else:
            # allow raw edge voice id
            self._edge_voice = self.cfg.voice if "Neural" in (self.cfg.voice or "") else JARVIS_VOICES["jarvis"]

        # Try edge-tts first (neural Jarvis-like voice)
        if engine_name in ("auto", "edge", "jarvis", "edge-tts"):
            try:
                import edge_tts  # noqa: F401

                self._backend = "edge"
                self._available = True
                return
            except Exception as e:
                if engine_name in ("edge", "jarvis", "edge-tts"):
                    self._error = f"edge-tts unavailable: {e}"
                    # fall through to pyttsx3

        # Offline fallback: pyttsx3 / SAPI5
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.cfg.rate)
            self._engine.setProperty("volume", self.cfg.volume)
            self._pick_sapi_voice()
            self._backend = "pyttsx3"
            self._available = True
        except Exception as e:
            self._error = self._error or f"TTS init error: {e}"

    def _pick_sapi_voice(self) -> None:
        if self._engine is None:
            return
        prefer = (self.cfg.voice or "jarvis").lower()
        voices = self._engine.getProperty("voices") or []
        if not voices:
            return

        keywords = {
            "jarvis": ["david", "mark", "george", "ryan", "male", "en-gb", "english"],
            "male": ["david", "mark", "male", "paul", "dmitry"],
            "female": ["zira", "female", "irina", "helena", "svetlana"],
            "auto": ["david", "mark", "george", "irina", "dmitry", "russian"],
        }
        targets = keywords.get(prefer, keywords["jarvis"])

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

    @property
    def backend(self) -> str:
        return self._backend

    def _speak_edge(self, text: str) -> None:
        import edge_tts

        async def _gen(path: str) -> None:
            communicate = edge_tts.Communicate(text, self._edge_voice)
            await communicate.save(path)

        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            asyncio.run(_gen(path))
            self._play_mp3(path)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def _play_mp3(self, path: str) -> None:
        # 1) pygame
        try:
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(float(self.cfg.volume))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
            return
        except Exception:
            pass

        # 2) Windows Media Player via PowerShell
        try:
            import subprocess

            ps = (
                f'$p = New-Object -ComObject WMPlayer.OCX; '
                f'$p.URL = (Resolve-Path "{path}").Path; '
                f'$p.controls.play(); '
                f'while ($p.playState -ne 1) {{ Start-Sleep -Milliseconds 100 }}; '
                f'$p.close()'
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                check=False,
                capture_output=True,
                timeout=120,
            )
            return
        except Exception:
            pass

        # 3) playsound
        try:
            from playsound import playsound

            playsound(path)
        except Exception as e:
            print(f"[TTS play error] {e}")

    def _speak_sapi(self, text: str) -> None:
        if self._engine is None:
            return
        self._engine.say(text)
        self._engine.runAndWait()

    def speak(self, text: str, blocking: bool = False) -> None:
        text = (text or "").strip()
        if not text:
            return
        if not self._available:
            print(f"[TTS unavailable] {text[:80]}")
            return

        def _run() -> None:
            with self._lock:
                try:
                    if self._backend == "edge":
                        self._speak_edge(text)
                    else:
                        self._speak_sapi(text)
                except Exception as e:
                    print(f"[TTS error] {e}")
                    # one-shot fallback
                    if self._backend == "edge" and self._engine is None:
                        try:
                            import pyttsx3

                            self._engine = pyttsx3.init()
                            self._speak_sapi(text)
                        except Exception:
                            pass

        if blocking:
            _run()
        else:
            threading.Thread(target=_run, daemon=True).start()

    def stop(self) -> None:
        try:
            import pygame

            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass

    def list_voices(self) -> list[str]:
        out = [f"edge:{k} → {v}" for k, v in JARVIS_VOICES.items()]
        if self._engine is not None:
            voices = self._engine.getProperty("voices") or []
            out.extend(getattr(v, "name", str(v.id)) for v in voices)
        return out


def create_tts(cfg: TTSSettings | None = None) -> TTSEngine:
    return TTSEngine(cfg)
