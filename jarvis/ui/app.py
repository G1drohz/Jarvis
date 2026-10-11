"""Application bootstrap: MainWindow + system tray (Luxify-style)."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from jarvis.ui.tray import TrayController, make_tray_icon
from jarvis.ui.window_impl import MainWindow

if TYPE_CHECKING:
    from jarvis.core.agent import Agent


def run_ui(agent: "Agent") -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("JARVIS")
    app.setOrganizationName("JARVIS")
    app.setFont(QFont("Segoe UI", 10))
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(agent)
    window.setWindowIcon(make_tray_icon())
    window._force_quit = False
    _orig_close = window.closeEvent

    def close_event(event) -> None:  # noqa: N802
        if getattr(window, "_force_quit", False) or not QSystemTrayIcon.isSystemTrayAvailable():
            _orig_close(event)
            return
        event.ignore()
        window.hide()
        tray = getattr(window, "_tray", None)
        if tray:
            tray.notify("JARVIS", "Работаю в трее / Running in tray")

    window.closeEvent = close_event  # type: ignore[method-assign]

    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = TrayController(window)
        window._tray = tray

        def show_win() -> None:
            window.showNormal()
            window.raise_()
            window.activateWindow()

        def quit_app() -> None:
            window._force_quit = True
            try:
                from PySide6.QtCore import QMetaObject

                QMetaObject.invokeMethod(
                    window._wake_worker, "stop_loop", Qt.ConnectionType.QueuedConnection
                )
                window._wake_thread.quit()
                window._voice_thread.quit()
                window._wake_thread.wait(1000)
                window._voice_thread.wait(1000)
            except Exception:
                pass
            try:
                if window.voice.tts_ok:
                    window.voice.tts.stop()
            except Exception:
                pass
            try:
                window.hud.close()
            except Exception:
                pass
            app.quit()

        tray.show_window.connect(show_win)
        tray.quit_app.connect(quit_app)
    else:
        window._tray = None
        app.setQuitOnLastWindowClosed(True)

    window.show()
    sys.exit(app.exec())
