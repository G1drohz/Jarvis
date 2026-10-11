"""System tray icon (Luxify-style minimize to tray)."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication


def make_tray_icon() -> QIcon:
    pm = QPixmap(64, 64)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(15, 23, 42))
    p.setPen(QColor(59, 130, 246))
    p.drawRoundedRect(4, 4, 56, 56, 12, 12)
    p.setPen(QColor(96, 165, 250))
    f = QFont("Segoe UI", 28, QFont.Weight.Bold)
    p.setFont(f)
    p.drawText(pm.rect(), 0x84, "J")  # AlignHCenter | AlignVCenter
    p.end()
    return QIcon(pm)


class TrayController(QObject):
    show_window = Signal()
    quit_app = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.icon = make_tray_icon()
        self.tray = QSystemTrayIcon(self.icon, parent)
        self.tray.setToolTip("JARVIS")

        menu = QMenu()
        act_show = QAction("Открыть / Open", menu)
        act_show.triggered.connect(self.show_window.emit)
        menu.addAction(act_show)
        menu.addSeparator()
        act_quit = QAction("Выход / Quit", menu)
        act_quit.triggered.connect(self.quit_app.emit)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)
        self.tray.show()

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window.emit()

    def notify(self, title: str, message: str) -> None:
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)
