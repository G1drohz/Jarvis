"""TTS: offline Piper (Jarvis-like) → pyttsx3 → online edge-tts."""

from __future__ import annotations

import asyncio
import os
import tempfile
import threading
import wave
from pathlib import Path

from config.settings import TTSSettings, settings as app_settings
from jarvis.tts.models import MODELS, ensure_model, resolve_voice_key

# Online Microsoft voices (optional fallback)
EDGE_VOICES = {
    "jarvis": "en-GB-RyanNeural",
    "jarvis_en": "en-GB-RyanNeural",
    "jarvis_ru": "ru-RU-DmitryNeural",
    "en": "en-GB-RyanNeural",
    "ru": "ru-RU-DmitryNeural",
}


class TTSEngine:
    """Jarvis voice: offline neural (Piper) first, then system, then online."""

    def __init__(self, cfg: TTSSettings | None = None) -> None:
        self.cfg = cfg or app_settings.tts
        self._engine = None
        self._piper = None
        self._piper_path: Path | None = None
        self._backend = "none"
        self._available = False
        self._error: str | None = None
        self._lock = threading.Lock()
        self._edge_voice = EDGE_VOICES["jarvis_en"]
        self._voice_key = "jarvis_en"
        self._init()

    def _init(self) -> None:
        engine_name = (self.cfg.engine or "auto").lower()
        if engine_name == "stub":
            self._error = "TTS engine set to stub"
            return

        prefer = (self.cfg.voice or "jarvis").lower()
        lang = (getattr(app_settings.app, "language", "ru") or "ru").lower()
        self._voice_key = resolve_voice_key(prefer, lang)
        self._edge_voice = EDGE_VOICES.get(
            prefer if prefer in EDGE_VOICES else ("jarvis_ru" if self._voice_key == "jarvis_ru" else "jarvis_en"),
            EDGE_VOICES["jarvis_en"],
        )

        # 1) Offline Piper neural (preferred for cinematic / offline)
        if engine_name in ("auto", "piper", "jarvis", "offline"):
            if self._try_piper():
                return
            if engine_name in ("piper", "offline"):
                # keep trying fallbacks but record error
                pass

        # 2) Offline system SAPI
        if engine_name in ("auto", "pyttsx3", "sapi", "jarvis", "offline"):
            if self._try_sapi():
                return

        # 3) Online edge-tts
        if engine_name in ("auto", "edge", "edge-tts", "jarvis"):
            try:
                import edge_tts  # noqa: F401

                self._backend = "edge"
                self._available = True
                return
            except Exception as e:
                self._error = f"edge-tts unavailable: {e}"

        if not self._available:
            self._error = self._error or "No TTS backend available"

    def _try_piper(self) -> bool:
        try:
            from piper import PiperVoice  # type: ignore

            path = ensure_model(self._voice_key)
            self._piper = PiperVoice.load(str(path))
            self._piper_path = path
            self._backend = "piper"
            self._available = True
            return True
        except Exception as e:
            self._error = f"Piper offline voice: {e}"
            self._piper = None
            return False

    def _try_sapi(self) -> bool:
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            # Slightly slower = more formal / butler-like
            rate = int(getattr(self.cfg, "rate", 175) or 175)
            self._engine.setProperty("rate", max(120, rate - 15))
            self._engine.setProperty("volume", self.cfg.volume)
            self._pick_sapi_voice()
            self._backend = "pyttsx3"
            self._available = True
            return True
        except Exception as e:
            self._error = f"SAPI: {e}"
            return False

    def _pick_sapi_voice(self) -> None:
        if self._engine is None:
            return
        voices = self._engine.getProperty("voices") or []
        targets = [
            "george", "hazel", "david", "mark", "ryan", "male",
            "en-gb", "english", "dmitry", "irina",
        ]
        if self._voice_key == "jarvis_en":
            targets = ["george", "hazel", "david", "en-gb", "english", "male"]
        chosen = None
        for v in voices:
            blob = f"{getattr(v, 'name', '')} {getattr(v, 'id', '')}".lower()
            if any(k in blob for k in targets):
                chosen = v.id
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

    def _speak_piper(self, text: str) -> None:
        if self._piper is None:
            raise RuntimeError("Piper not loaded")

        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            with wave.open(path, "wb") as wav_file:
                # piper-tts API variants
                try:
                    self._piper.synthesize(text, wav_file)
                except TypeError:
                    # newer API: synthesize returns audio chunks
                    audio = self._piper.synthesize(text)
                    if hasattr(audio, "audio_int16_bytes"):
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(getattr(self._piper.config, "sample_rate", 22050))
                        wav_file.writeframes(audio.audio_int16_bytes)
                    else:
                        for chunk in audio:
                            if wav_file.getnframes() == 0:
                                wav_file.setnchannels(1)
                                wav_file.setsampwidth(2)
                                wav_file.setframerate(getattr(chunk, "sample_rate", 22050))
                            wav_file.writeframes(chunk.audio_int16_bytes)
            self._play_wav(path)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def _play_wav(self, path: str) -> None:
        try:
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(float(self.cfg.volume))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(40)
            return
        except Exception:
            pass
        try:
            import winsound

            winsound.PlaySound(path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"[TTS play] {e}")

    def _speak_edge(self, text: str) -> None:
        import edge_tts

        async def _gen(p: str) -> None:
            await edge_tts.Communicate(text, self._edge_voice).save(p)

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
        except Exception as e:
            print(f"[TTS play] {e}")

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
                    if self._backend == "piper":
                        self._speak_piper(text)
                    elif self._backend == "edge":
                        self._speak_edge(text)
                    else:
                        self._speak_sapi(text)
                except Exception as e:
                    print(f"[TTS error] {e}")
                    # cascade fallback
                    try:
                        if self._backend == "piper":
                            if self._try_sapi():
                                self._speak_sapi(text)
                                return
                            import edge_tts  # noqa: F401

                            self._backend = "edge"
                            self._speak_edge(text)
                    except Exception as e2:
                        print(f"[TTS fallback] {e2}")

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
        out = [f"piper offline: {k} → {v['id']}" for k, v in MODELS.items()]
        out += [f"edge online: {k} → {v}" for k, v in EDGE_VOICES.items()]
        return out

    def ensure_offline_models(self, on_status=None) -> str:
        """Pre-download both EN/RU offline voices."""
        paths = []
        for key in ("jarvis_en", "jarvis_ru"):
            try:
                paths.append(str(ensure_model(key, on_status=on_status)))
            except Exception as e:
                paths.append(f"{key}: FAIL {e}")
        # reload piper if needed
        if self._backend != "piper":
            self._try_piper()
        return "; ".join(paths)


def create_tts(cfg: TTSSettings | None = None) -> TTSEngine:
    return TTSEngine(cfg)
