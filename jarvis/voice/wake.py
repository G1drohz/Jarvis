"""Wake-word loop: continuous listen → detect «джарвис»/«jarvis» → capture command."""

from __future__ import annotations

import time
from typing import Callable

from config.settings import settings
from jarvis.stt.engine import STTEngine


class WakeWordListener:
    """Simple STT-based wake word (not Porcupine). Works with continuous flag."""

    def __init__(
        self,
        stt: STTEngine,
        on_command: Callable[[str], None],
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        self.stt = stt
        self.on_command = on_command
        self.on_status = on_status or (lambda s: None)
        self._running = False
        self._words = [
            settings.voice.wake_word.lower(),
            settings.voice.wake_word_en.lower(),
            "jarvis",
            "джарвис",
        ]

    def stop(self) -> None:
        self._running = False

    def run_forever(self) -> None:
        self._running = True
        cooldown = settings.voice.wake_cooldown_sec
        while self._running:
            try:
                self.on_status("wake_listen")
                text = self.stt.listen_once(on_status=None)
                if not text:
                    continue
                low = text.lower()
                if any(w in low for w in self._words if w):
                    # strip wake word and use remainder, or listen again
                    cmd = low
                    for w in self._words:
                        cmd = cmd.replace(w, " ").strip(" ,.")
                    if not cmd:
                        self.on_status("wake_triggered")
                        cmd = self.stt.listen_once(on_status=None)
                    if cmd:
                        self.on_command(cmd)
                    time.sleep(cooldown)
            except Exception:
                time.sleep(0.8)
