"""Confirm dangerous actions before execution."""

from __future__ import annotations

from config.settings import settings
from jarvis.i18n import t


DANGEROUS = {
    "shutdown",
    "restart",
    "delete_file",
    "run_shell",
    "format",
    "kill_process",
}


def needs_confirmation(action_type: str) -> bool:
    action_type = action_type.lower().strip()
    required = set(settings.permissions.require_confirm_for) | DANGEROUS
    return action_type in required


def confirm_action(action_type: str, detail: str = "") -> bool:
    """Show Qt dialog if available; otherwise refuse dangerous actions."""
    if not needs_confirmation(action_type):
        return True
    try:
        from PySide6.QtWidgets import QMessageBox, QApplication

        if QApplication.instance() is None:
            return False
        body = t("confirm.body", action=f"{action_type}\n{detail}".strip())
        box = QMessageBox()
        box.setWindowTitle(t("confirm.title"))
        box.setText(body)
        box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)
        return box.exec() == QMessageBox.StandardButton.Yes
    except Exception:
        return False
