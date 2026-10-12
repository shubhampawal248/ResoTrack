import psutil
from datetime import datetime


class ProcessMonitor:

    def get_process_info(self, pid):

        try:
            process = psutil.Process(pid)

            return {
                "pid": pid,
                "name": process.name(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_percent": process.memory_percent(),
                "memory_used": process.memory_info().rss,
                "timestamp": datetime.now()
            }

        except psutil.NoSuchProcess:

            return {
                "pid": pid,
                "status": "NOT FOUND"
            }

    def is_process_running(self, pid):

        try:
            process = psutil.Process(pid)
            return process.is_running()

        except psutil.NoSuchProcess:
            return False

    def get_system_info(self):

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": memory.percent,
            "memory_used": memory.used,
            "memory_available": memory.available,
            "disk_percent": disk.percent,
            "disk_used": disk.used,
            "disk_free": disk.free,
            "timestamp": datetime.now()
        }