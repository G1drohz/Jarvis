"""Permission checks."""

from __future__ import annotations

from config.settings import PermissionsSettings


class PermissionManager:
    def __init__(self, cfg: PermissionsSettings) -> None:
        self.cfg = cfg

    def can_run_system(self) -> bool:
        return self.cfg.allow_system_commands

    def can_access_files(self) -> bool:
        return self.cfg.allow_file_access

    def can_network(self) -> bool:
        return self.cfg.allow_network

    def require(self, action: str) -> None:
        mapping = {
            "system": self.can_run_system,
            "files": self.can_access_files,
            "network": self.can_network,
        }
        checker = mapping.get(action)
        if checker is None:
            raise PermissionError(f"Unknown permission: {action}")
        if not checker():
            raise PermissionError(f"Permission denied: {action}")
