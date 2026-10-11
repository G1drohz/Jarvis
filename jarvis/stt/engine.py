"""Speech-to-Text: auto | google | vosk | sphinx."""

from __future__ import annotations

from typing import Callable

from config.settings import STTSettings, settings as app_settings


class STTEngine:
    def __init__(self, cfg: STTSettings | None = None) -> None:
        self.cfg = cfg or app_settings.stt
        self._recognizer = None
        self._mic = None
        self._sr = None
        self._vosk_model = None
        self._available = False
        self._error: str | None = None
        self._backend = "none"
        self._init()

    def _init(self) -> None:
        engine = (self.cfg.engine or "auto").lower()
        if engine in ("auto", "vosk") and self.cfg.vosk_model_path:
            if self._try_vosk():
                return
        if engine in ("auto", "google", "sphinx"):
            if self._try_speech_recognition(engine if engine != "auto" else "google"):
                return
        if engine == "vosk":
            self._error = self._error or "Vosk model path empty or failed"
        if not self._available:
            self._error = self._error or "No STT backend available"

    def _try_speech_recognition(self, preferred: str) -> bool:
        try:
            import speech_recognition as sr

            self._sr = sr
            self._recognizer = sr.Recognizer()
            self._recognizer.dynamic_energy_threshold = True
            self._mic = sr.Microphone()
            self._backend = preferred if preferred != "auto" else "google"
            self._available = True
            return True
        except ImportError as e:
            self._error = f"SpeechRecognition/PyAudio: {e}"
        except OSError as e:
            self._error = f"Microphone: {e}"
        except Exception as e:
            self._error = f"STT init: {e}"
        return False

    def _try_vosk(self) -> bool:
        try:
            from vosk import Model, KaldiRecognizer
            import json
            import speech_recognition as sr

            self._vosk_model = Model(self.cfg.vosk_model_path)
            self._sr = sr
            self._recognizer = sr.Recognizer()
            self._mic = sr.Microphone(sample_rate=16000)
            self._backend = "vosk"
            self._available = True
            self._KaldiRecognizer = KaldiRecognizer
            self._json = json
            return True
        except Exception as e:
            self._error = f"Vosk: {e}"
            return False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def backend(self) -> str:
        return self._backend

    def listen_once(self, on_status: Callable[[str], None] | None = None) -> str:
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
                source, phrase_time_limit=self.cfg.phrase_time_limit
            )

        status("recognizing")
        if self._backend == "vosk":
            return self._recognize_vosk(audio)
        return self._recognize_sr(audio)

    def _recognize_sr(self, audio) -> str:
        lang = self.cfg.language or "ru-RU"
        try:
            if self._backend == "sphinx":
                text = self._recognizer.recognize_sphinx(audio, language=lang)
            else:
                text = self._recognizer.recognize_google(audio, language=lang)
            return (text or "").strip()
        except self._sr.UnknownValueError:
            raise RuntimeError("Не удалось распознать / Unrecognized")
        except self._sr.RequestError as e:
            raise RuntimeError(f"STT service: {e}")
        except Exception as e:
            raise RuntimeError(f"STT: {e}")

    def _recognize_vosk(self, audio) -> str:
        raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
        rec = self._KaldiRecognizer(self._vosk_model, 16000)
        rec.AcceptWaveform(raw)
        result = self._json.loads(rec.FinalResult())
        return (result.get("text") or "").strip()


def create_stt(cfg: STTSettings | None = None) -> STTEngine:
    return STTEngine(cfg)
