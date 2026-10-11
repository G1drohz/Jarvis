"""System resource monitor."""

from __future__ import annotations


class SystemMonitor:
    def snapshot(self) -> dict:
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(interval=0.3),
                "ram_percent": psutil.virtual_memory().percent,
                "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_percent": psutil.disk_usage("/").percent
                if hasattr(psutil, "disk_usage")
                else 0,
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
                    info = p.info
                    procs.append(info)
                except Exception:
                    continue
            procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
            lines = []
            for info in procs[:n]:
                lines.append(
                    f"{info.get('name', '?')[:24]:24}  "
                    f"CPU {info.get('cpu_percent') or 0:5.1f}%  "
                    f"MEM {info.get('memory_percent') or 0:4.1f}%"
                )
            return lines
        except Exception as e:
            return [str(e)]
