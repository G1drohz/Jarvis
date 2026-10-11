"""Speech-to-Text engine (SpeechRecognition + microphone)."""

from __future__ import annotations

from typing import Callable

from config.settings import STTSettings, settings as app_settings


class STTEngine:
    """Listen from default microphone and return recognized text."""

    def __init__(self, cfg: STTSettings | None = None) -> None:
        self.cfg = cfg or app_settings.stt
        self._recognizer = None
        self._mic = None
        self._available = False
        self._error: str | None = None
        self._init()

    def _init(self) -> None:
        try:
            import speech_recognition as sr

            self._sr = sr
            self._recognizer = sr.Recognizer()
            self._recognizer.dynamic_energy_threshold = True
            self._mic = sr.Microphone()
            self._available = True
        except ImportError as e:
            self._error = (
                f"Нет модуля: {e}. Установи: pip install SpeechRecognition PyAudio"
            )
        except OSError as e:
            self._error = f"Микрофон / PyAudio: {e}"
        except Exception as e:
            self._error = f"STT init error: {e}"

    @property
    def available(self) -> bool:
        return self._available

    @property
    def error(self) -> str | None:
        return self._error

    def listen_once(
        self,
        on_status: Callable[[str], None] | None = None,
    ) -> str:
        """Record one phrase and return text. Raises RuntimeError on failure."""
        if not self._available or self._recognizer is None or self._mic is None:
            raise RuntimeError(self._error or "STT unavailable")

        def status(msg: str) -> None:
            if on_status:
                on_status(msg)

        with self._mic as source:
            status("calibrating")
            self._recognizer.adjust_for_ambient_noise(
                source, duration=self.cfg.ambient_duration
            )
            status("listening")
            audio = self._recognizer.listen(
                source,
                phrase_time_limit=self.cfg.phrase_time_limit,
            )

        status("recognizing")
        return self._recognize(audio)

    def _recognize(self, audio) -> str:
        engine = (self.cfg.engine or "google").lower()
        lang = self.cfg.language or "ru-RU"

        try:
            if engine == "sphinx":
                text = self._recognizer.recognize_sphinx(audio, language=lang)
            else:
                # google web speech (needs internet)
                text = self._recognizer.recognize_google(audio, language=lang)
            return (text or "").strip()
        except self._sr.UnknownValueError:
            raise RuntimeError("Не удалось распознать речь")
        except self._sr.RequestError as e:
            raise RuntimeError(f"Сервис распознавания недоступен: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка распознавания: {e}")


def create_stt(cfg: STTSettings | None = None) -> STTEngine:
    return STTEngine(cfg)
