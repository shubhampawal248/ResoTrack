
import subprocess
import uuid
import threading


class LoadGenerator:

    SCENARIOS = [
        "CPU Load",
        "Memory Load",
        "Disk Load",
        "Combined Load"
    ]

    def __init__(self):
        self.process = None
        self.stop_file = None
        self.lock = threading.Lock()
        self.last_exit_code = None

    def start(self, scenario="CPU Load", duration_seconds=30, memory_mb=16):

        with self.lock:

            if self.process is not None and self.process.poll() is None:
                return False

            if scenario not in self.SCENARIOS:
                raise ValueError("Invalid load scenario")

            duration_seconds = max(1, min(int(duration_seconds), 120))
            memory_mb = max(1, min(int(memory_mb), 32))

            token = uuid.uuid4().hex
            self.stop_file = f"/tmp/sysnexa_load_{token}.stop"
            log_file = f"/tmp/sysnexa_load_{token}.log"

            worker_code = r'''
import sys
import time
import os
import traceback

scenario = sys.argv[1]
duration = int(sys.argv[2])
memory_mb = int(sys.argv[3])
stop_file = sys.argv[4]
log_file = sys.argv[5]

memory_block = None
disk_file = f"/tmp/sysnexa_disk_{os.getpid()}.dat"

try:
    with open(log_file, "w") as log:
        log.write(f"Scenario: {scenario}\n")
        log.write(f"Requested duration: {duration} seconds\n")
        log.write("Worker started\n")

    if scenario in ("Memory Load", "Combined Load"):
        memory_block = bytearray(memory_mb * 1024 * 1024)

    start_time = time.monotonic()
    deadline = start_time + duration

    while time.monotonic() < deadline:

        if os.path.exists(stop_file):
            with open(log_file, "a") as log:
                log.write("Stop request received\n")
            break

        # CPU workload
        if scenario in ("CPU Load", "Combined Load"):
            busy_until = time.monotonic() + 0.05

            while time.monotonic() < busy_until:
                if os.path.exists(stop_file):
                    break
                sum(range(1000))

        # Small disk workload
        if scenario in ("Disk Load", "Combined Load"):
            with open(disk_file, "wb") as file:
                file.write(b"SysNexa test data" * 4096)

            with open(disk_file, "rb") as file:
                file.read()

        time.sleep(0.20)

    elapsed = time.monotonic() - start_time

    with open(log_file, "a") as log:
        log.write(f"Worker finished after {elapsed:.2f} seconds\n")

except Exception:
    with open(log_file, "a") as log:
        traceback.print_exc(file=log)
    raise

finally:
    if memory_block is not None:
        del memory_block

    if os.path.exists(disk_file):
        os.remove(disk_file)

    if os.path.exists(stop_file):
        os.remove(stop_file)
'''

            command = [
                "wsl.exe",
                "-d", "Ubuntu",
                "--",
                "python3", "-u", "-c",
                worker_code,
                scenario,
                str(duration_seconds),
                str(memory_mb),
                self.stop_file,
                log_file
            ]

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.last_exit_code = None

            print("SysNexa worker started.")
            print("Process ID:", self.process.pid)
            print("Scenario:", scenario)
            print("Requested duration:", duration_seconds)
            print("Worker log:", log_file)

            self.log_file = log_file

            return True

    def is_running(self):

        with self.lock:

            if self.process is None:
                return False

            exit_code = self.process.poll()

            if exit_code is not None:
                self.last_exit_code = exit_code
                print("SysNexa worker exited. Exit code:", exit_code)
                return False

            return True

    def get_worker_log(self):

        with self.lock:
            log_file = getattr(self, "log_file", None)

        if not log_file:
            return "No worker log available."

        try:
            result = subprocess.run(
                [
                    "wsl.exe",
                    "-d", "Ubuntu",
                    "--",
                    "cat", log_file
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.stdout or result.stderr or "Worker log is empty."

        except Exception as error:
            return f"Could not read worker log: {error}"

    def stop(self):

        with self.lock:

            process = self.process
            stop_file = self.stop_file

            if process is None:
                return

            if process.poll() is not None:
                self.last_exit_code = process.returncode
                self.process = None
                self.stop_file = None
                return

            try:
                subprocess.run(
                    [
                        "wsl.exe",
                        "-d", "Ubuntu",
                        "--",
                        "touch", stop_file
                    ],
                    capture_output=True,
                    timeout=5
                )

                process.wait(timeout=5)

            except subprocess.TimeoutExpired:
                process.terminate()

                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()

            except Exception as error:
                print("Error stopping worker:", error)

                if process.poll() is None:
                    process.terminate()

            finally:
                self.last_exit_code = process.poll()

                if self.process is process:
                    self.process = None
                    self.stop_file = None
