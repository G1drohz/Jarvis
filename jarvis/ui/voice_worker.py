"""Background STT / wake-word workers."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot

from jarvis.voice.controller import VoiceController
from jarvis.voice.wake import WakeWordListener


class VoiceWorker(QObject):
    status = Signal(str)
    finished = Signal(str, str)
    failed = Signal(str)

    def __init__(self, voice: VoiceController) -> None:
        super().__init__()
        self.voice = voice
        self._busy = False

    @property
    def busy(self) -> bool:
        return self._busy

    @Slot()
    def run_once(self) -> None:
        if self._busy:
            return
        self._busy = True
        try:

            def on_status(s: str) -> None:
                self.status.emit(s)

            user_text, reply = self.voice.process_voice(on_status=on_status)
            self.finished.emit(user_text, reply)
        except Exception as e:
            self.failed.emit(str(e))
        finally:
            self._busy = False
            self.status.emit("done")


class WakeWorker(QObject):
    status = Signal(str)
    command = Signal(str)
    failed = Signal(str)

    def __init__(self, voice: VoiceController) -> None:
        super().__init__()
        self.voice = voice
        self._listener: WakeWordListener | None = None

    @Slot()
    def start_loop(self) -> None:
        if not self.voice.stt_ok:
            self.failed.emit(self.voice.stt.error or "STT unavailable")
            return

        def on_cmd(text: str) -> None:
            self.command.emit(text)

        def on_status(s: str) -> None:
            self.status.emit(s)

        self._listener = WakeWordListener(self.voice.stt, on_cmd, on_status)
        self._listener.run_forever()

    @Slot()
    def stop_loop(self) -> None:
        if self._listener:
            self._listener.stop()


def start_voice_thread(voice: VoiceController) -> tuple[QThread, VoiceWorker]:
    thread = QThread()
    worker = VoiceWorker(voice)
    worker.moveToThread(thread)
    thread.start()
    return thread, worker


def start_wake_thread(voice: VoiceController) -> tuple[QThread, WakeWorker]:
    thread = QThread()
    worker = WakeWorker(voice)
    worker.moveToThread(thread)
    thread.start()
    return thread, worker
