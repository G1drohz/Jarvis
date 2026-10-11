"""Background worker so STT does not freeze the Qt UI."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot

from jarvis.voice.controller import VoiceController


class VoiceWorker(QObject):
    """Runs listen + process in a QThread."""

    status = Signal(str)          # calibrating | listening | recognizing | done | error
    finished = Signal(str, str)   # user_text, reply
    failed = Signal(str)          # error message

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


def start_voice_thread(voice: VoiceController) -> tuple[QThread, VoiceWorker]:
    thread = QThread()
    worker = VoiceWorker(voice)
    worker.moveToThread(thread)
    thread.start()
    return thread, worker
