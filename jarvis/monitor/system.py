"""System resource monitor."""

from __future__ import annotations

import os


class SystemMonitor:
    def _disk_path(self) -> str:
        if os.name == "nt":
            return os.environ.get("SystemDrive", "C:") + "\\"
        return "/"

    def snapshot(self) -> dict:
        try:
            import psutil

            vm = psutil.virtual_memory()
            try:
                disk = psutil.disk_usage(self._disk_path()).percent
            except Exception:
                disk = 0.0
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.2),
                "ram_percent": vm.percent,
                "ram_used_gb": round(vm.used / (1024**3), 2),
                "ram_total_gb": round(vm.total / (1024**3), 2),
                "disk_percent": disk,
                "processes": len(psutil.pids()),
            }
        except Exception as e:
            return {"error": str(e)}

    def top_processes(self, n: int = 8) -> list[str]:
        try:
            import psutil

            procs = []
            for p in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
                try:
                    procs.append(p.info)
                except Exception:
                    continue
            procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
            lines = []
            for info in procs[:n]:
                lines.append(
                    f"{str(info.get('name', '?'))[:24]:24}  "
                    f"CPU {info.get('cpu_percent') or 0:5.1f}%  "
                    f"MEM {info.get('memory_percent') or 0:4.1f}%"
                )
            return lines
        except Exception as e:
            return [str(e)]
