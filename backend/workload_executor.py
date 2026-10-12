import subprocess
import os


class WorkloadExecutor:

    def __init__(self):
        self.use_wsl = True

    def execute(self, task, file_path):

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Workload file not found: {file_path}"
            )

        workload_type = task.workload_type.lower()

        if workload_type == "python":

            command = [
                "wsl",
                "python3",
                self.convert_path(file_path)
            ]

        elif workload_type == "cpp":

            command = [
                "wsl",
                "g++",
                self.convert_path(file_path),
                "-o",
                "/tmp/sysnexa_program"
            ]

            compile_result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return None, compile_result.returncode

            command = [
                "wsl",
                "/tmp/sysnexa_program"
            ]

        else:
            raise ValueError(
                f"Unsupported workload type: {workload_type}"
            )

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return process, None

    def convert_path(self, windows_path):

        result = subprocess.run(
            ["wsl", "wslpath", "-a", windows_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Could not convert Windows path to WSL path"
            )

        return result.stdout.strip()