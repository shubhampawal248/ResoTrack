```python
import subprocess
import pandas as pd
from io import StringIO


class ResourceManager:
    def __init__(
        self,
        cpu_threshold=90,
        memory_threshold=85,
        disk_threshold=90
    ):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold

    def _run_ubuntu(self, command):
        """Run a command inside the Ubuntu WSL distribution."""
        result = subprocess.run(
            [
                "wsl.exe",
                "-d", "Ubuntu",
                "--",
                "bash", "-lc", command
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Ubuntu command failed: "
                + result.stderr.strip()
            )

        return result.stdout.strip()

    def get_resources(self):
        """Collect live CPU, RAM and disk measurements from Ubuntu."""

        script = r'''
python3 - <<'PY'
import os
import time

def read_cpu():
    with open("/proc/stat", "r") as f:
        values = list(map(int, f.readline().split()[1:]))

    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return idle, sum(values)

idle1, total1 = read_cpu()
time.sleep(0.5)
idle2, total2 = read_cpu()

total_delta = total2 - total1
idle_delta = idle2 - idle1

if total_delta > 0:
    cpu = (1 - idle_delta / total_delta) * 100
else:
    cpu = 0.0

memory = {}

with open("/proc/meminfo", "r") as f:
    for line in f:
        key, value = line.split(":", 1)
        memory[key] = int(value.strip().split()[0]) * 1024

memory_total = memory["MemTotal"]
memory_available = memory.get(
    "MemAvailable",
    memory.get("MemFree", 0)
)
memory_used = memory_total - memory_available

disk = os.statvfs("/")
disk_total = disk.f_blocks * disk.f_frsize
disk_free = disk.f_bavail * disk.f_frsize
disk_used = disk_total - disk_free

memory_percent = (
    memory_used / memory_total * 100
    if memory_total else 0
)

disk_percent = (
    disk_used / (disk_used + disk_free) * 100
    if disk_used + disk_free else 0
)

# CSV columns:
# cpu,memory,memory_used,memory_available,memory_total,
# disk,disk_used,disk_free,disk_total
print(
    f"{cpu:.2f},{memory_percent:.2f},"
    f"{memory_used},{memory_available},{memory_total},"
    f"{disk_percent:.2f},{disk_used},{disk_free},{disk_total}"
)
PY
'''

        output = self._run_ubuntu(script)

        # Parse Ubuntu's CSV output using Pandas.
        columns = [
            "cpu",
            "memory",
            "memory_used",
            "memory_available",
            "memory_total",
            "disk",
            "disk_used",
            "disk_free",
            "disk_total"
        ]

        df = pd.read_csv(
            StringIO(output),
            header=None,
            names=columns
        )

        if len(df) != 1:
            raise RuntimeError(
                "Unexpected resource data returned by Ubuntu."
            )

        row = df.iloc[0]

        return {
            "cpu": float(row["cpu"]),
            "memory": float(row["memory"]),
            "memory_used": int(row["memory_used"]),
            "memory_available": int(row["memory_available"]),
            "memory_total": int(row["memory_total"]),
            "disk": float(row["disk"]),
            "disk_used": int(row["disk_used"]),
            "disk_free": int(row["disk_free"]),
            "disk_total": int(row["disk_total"])
        }

    def resources_available(self):
        resources = self.get_resources()

        return not (
            resources["cpu"] >= self.cpu_threshold
            or resources["memory"] >= self.memory_threshold
            or resources["disk"] >= self.disk_threshold
        )

    def get_status(self):
        resources = self.get_resources()

        available = not (
            resources["cpu"] >= self.cpu_threshold
            or resources["memory"] >= self.memory_threshold
            or resources["disk"] >= self.disk_threshold
        )

        return {
            "resources": resources,
            "available": available
        }
```