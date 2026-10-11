from jarvis.tools.windows_ctrl import get_system_info, launch_app
from jarvis.tools.windows_ctrl import send_key as open_path  # legacy compat

# re-export list_running from old apps if needed
try:
    from jarvis.tools.windows.apps import list_running_apps
except Exception:
    def list_running_apps(limit: int = 30):
        return []

__all__ = ["get_system_info", "launch_app", "list_running_apps"]
