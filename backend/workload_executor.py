import json
import shutil
import subprocess
import time
from datetime import datetime


# ==========================================================
# UBUNTU WORKLOAD RUNNER
# ==========================================================

LINUX_RUNNER = r"""
import sys
import os
import json
import time
import signal
import resource
import tempfile
import subprocess
from pathlib import Path


def run_program(command, timeout):

    before = resource.getrusage(
        resource.RUSAGE_CHILDREN
    )

    start = time.monotonic()

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        start_new_session=True
    )

    timed_out = False

    try:

        stdout, stderr = process.communicate(
            timeout=timeout
        )

    except subprocess.TimeoutExpired:

        timed_out = True

        try:

            os.killpg(
                process.pid,
                signal.SIGKILL
            )

        except ProcessLookupError:

            pass

        stdout, stderr = process.communicate()

    elapsed = time.monotonic() - start

    after = resource.getrusage(
        resource.RUSAGE_CHILDREN
    )

    cpu_time = (
        after.ru_utime - before.ru_utime
        + after.ru_stime - before.ru_stime
    )

    cpu_percent = (
        cpu_time / elapsed * 100
        if elapsed > 0
        else None
    )

    peak_memory_bytes = (
        after.ru_maxrss * 1024
    )

    return {
        "pid": process.pid,

        "exit_code": process.returncode,

        "execution_time": elapsed,

        "cpu_time_seconds": cpu_time,

        "cpu_percent": cpu_percent,

        "memory_peak_bytes": peak_memory_bytes,

        "stdout": stdout[:1000000],

        "stderr": stderr[:1000000],

        "timed_out": timed_out
    }


def main():

    payload = json.load(sys.stdin)

    language = payload["language"]

    source_code = payload["source_code"]

    timeout = payload["timeout_seconds"]

    with tempfile.TemporaryDirectory(
        prefix="sysnexa_"
    ) as directory:

        directory = Path(directory)

        # --------------------------------------------------
        # PYTHON EXECUTION
        # --------------------------------------------------

        if language == "python":

            source_file = directory / "program.py"

            source_file.write_text(
                source_code,
                encoding="utf-8"
            )

            command = [
                "python3",
                str(source_file)
            ]

        # --------------------------------------------------
        # C/C++ COMPILATION
        # --------------------------------------------------

        elif language == "cpp":

            source_file = directory / "program.cpp"

            executable = directory / "program"

            source_file.write_text(
                source_code,
                encoding="utf-8"
            )

            compile_result = subprocess.run(
                [
                    "g++",
                    str(source_file),
                    "-o",
                    str(executable)
                ],
                capture_output=True,
                text=True,
                errors="replace",
                timeout=timeout
            )

            if compile_result.returncode != 0:

                return {
                    "pid": None,

                    "exit_code": compile_result.returncode,

                    "execution_time": None,

                    "cpu_time_seconds": None,

                    "cpu_percent": None,

                    "memory_peak_bytes": None,

                    "stdout": compile_result.stdout,

                    "stderr": compile_result.stderr,

                    "timed_out": False,

                    "error": "C/C++ compilation failed."
                }

            command = [
                str(executable)
            ]

        else:

            raise ValueError(
                f"Unsupported language: {language}"
            )

        return run_program(
            command,
            timeout
        )


try:

    result = main()

    print(json.dumps(result))

except Exception as error:

    print(json.dumps({

        "pid": None,

        "exit_code": 1,

        "execution_time": None,

        "cpu_time_seconds": None,

        "cpu_percent": None,

        "memory_peak_bytes": None,

        "stdout": "",

        "stderr": str(error),

        "timed_out": isinstance(
            error,
            subprocess.TimeoutExpired
        ),

        "error": str(error)
    }))
"""


# ==========================================================
# WORKLOAD EXECUTOR
# ==========================================================

class WorkloadExecutor:

    def __init__(self, distro="Ubuntu"):

        self.use_wsl = True

        self.distro = distro

        self.wsl_executable = (
            shutil.which("wsl.exe")
            or shutil.which("wsl")
            or "wsl.exe"
        )

    # ======================================================
    # EXECUTE WORKLOAD
    # ======================================================

    def execute(
        self,
        task,
        source_code="",
        timeout_seconds=30
    ):

        timeout_seconds = int(timeout_seconds)

        if not 1 <= timeout_seconds <= 300:

            raise ValueError(
                "Execution timeout must be "
                "between 1 and 300 seconds."
            )

        workload_type = (
            task.workload_type.lower()
        )

        # --------------------------------------------------
        # RESET EXECUTION INFORMATION
        # --------------------------------------------------

        task.pid = None

        task.exit_code = None

        task.stdout = ""

        task.stderr = ""

        task.cpu_time_seconds = None

        task.cpu_percent = None

        task.memory_peak_bytes = None

        task.failure_reason = None

        task.timed_out = False

        task.transferred_bytes = None

        task.transfer_time_seconds = None

        task.transfer_speed = None

        task.transfer_destination = None

        task.transfer_metrics_error = None

        # --------------------------------------------------
        # START TASK
        # --------------------------------------------------

        self.start_task(task)

        start_time = time.monotonic()

        try:

            # ----------------------------------------------
            # FILE TRANSFER WORKLOAD
            # ----------------------------------------------

            if workload_type == "file_transfer":

                from backend.file_transfer import (
                    build_transfer_source
                )

                source_code = build_transfer_source(
                    task
                )

                language = "python"

            # ----------------------------------------------
            # PYTHON WORKLOAD
            # ----------------------------------------------

            elif workload_type == "python":

                language = "python"

            # ----------------------------------------------
            # C/C++ WORKLOAD
            # ----------------------------------------------

            elif workload_type == "cpp":

                language = "cpp"

            else:

                raise ValueError(
                    "Unsupported workload type: "
                    f"{workload_type}"
                )

            if not source_code.strip():

                raise ValueError(
                    "Workload source code is empty."
                )

            # ----------------------------------------------
            # PREPARE EXECUTION PAYLOAD
            # ----------------------------------------------

            payload = {

                "language": language,

                "source_code": source_code,

                "timeout_seconds": timeout_seconds
            }

            # ----------------------------------------------
            # EXECUTE INSIDE UBUNTU WSL
            # ----------------------------------------------

            command = [

                self.wsl_executable,

                "-d",

                self.distro,

                "--",

                "python3",

                "-c",

                LINUX_RUNNER
            ]

            result = subprocess.run(

                command,

                input=json.dumps(payload),

                capture_output=True,

                text=True,

                encoding="utf-8",

                errors="replace",

                timeout=(timeout_seconds * 2) + 20
            )

            if result.returncode != 0:

                raise RuntimeError(
                    result.stderr.strip()
                    or "Ubuntu execution failed."
                )

            if not result.stdout.strip():

                raise RuntimeError(
                    "Ubuntu returned no execution result."
                )

            # ----------------------------------------------
            # READ ACTUAL EXECUTION RESULTS
            # ----------------------------------------------

            execution_result = json.loads(
                result.stdout.strip()
            )

            task.pid = execution_result.get(
                "pid"
            )

            task.stdout = execution_result.get(
                "stdout",
                ""
            )

            task.stderr = execution_result.get(
                "stderr",
                ""
            )

            task.cpu_time_seconds = (
                execution_result.get(
                    "cpu_time_seconds"
                )
            )

            task.cpu_percent = (
                execution_result.get(
                    "cpu_percent"
                )
            )

            task.memory_peak_bytes = (
                execution_result.get(
                    "memory_peak_bytes"
                )
            )

            task.timed_out = execution_result.get(
                "timed_out",
                False
            )

            exit_code = execution_result.get(
                "exit_code",
                1
            )

            # ----------------------------------------------
            # COMPLETE TASK
            # ----------------------------------------------

            self.complete_task(
                task,
                exit_code
            )

            measured_time = execution_result.get(
                "execution_time"
            )

            task.execution_time = measured_time

            # ----------------------------------------------
            # FAILURE INFORMATION
            # ----------------------------------------------

            if task.timed_out:

                task.state = "FAILED"

                task.failure_reason = (
                    "Execution timeout exceeded."
                )

            elif exit_code != 0:

                task.state = "FAILED"

                task.failure_reason = (

                    execution_result.get("error")

                    or task.stderr

                    or f"Process exited with code {exit_code}"
                )

            else:

                task.state = "COMPLETED"

            # ----------------------------------------------
            # FILE TRANSFER METRICS
            # ----------------------------------------------

            if (
                workload_type == "file_transfer"
                and task.state == "COMPLETED"
            ):

                self.extract_transfer_metrics(
                    task
                )

            return execution_result

        # --------------------------------------------------
        # TIMEOUT HANDLING
        # --------------------------------------------------

        except subprocess.TimeoutExpired:

            task.timed_out = True

            task.failure_reason = (
                "Ubuntu execution exceeded "
                "the outer timeout."
            )

            task.stderr = task.failure_reason

            self.complete_task(
                task,
                124
            )

            task.state = "FAILED"

            task.execution_time = None

            raise RuntimeError(
                task.failure_reason
            )

        # --------------------------------------------------
        # GENERAL FAILURE HANDLING
        # --------------------------------------------------

        except Exception as error:

            task.failure_reason = str(error)

            task.stderr = str(error)

            self.complete_task(
                task,
                1
            )

            task.state = "FAILED"

            task.execution_time = None

            raise

    # ======================================================
    # START TASK
    # ======================================================

    def start_task(self, task):

        if callable(
            getattr(task, "start", None)
        ):

            task.start()

        else:

            task.start_time = datetime.now()

            task.state = "RUNNING"

    # ======================================================
    # COMPLETE TASK
    # ======================================================

    def complete_task(
        self,
        task,
        exit_code
    ):

        if callable(
            getattr(task, "complete", None)
        ):

            task.complete(exit_code)

        else:

            task.completion_time = datetime.now()

        task.exit_code = exit_code

        task.state = (

            "COMPLETED"

            if exit_code == 0

            else "FAILED"
        )

        if getattr(
            task,
            "completion_time",
            None
        ) is None:

            task.completion_time = datetime.now()

    # ======================================================
    # EXTRACT FILE TRANSFER METRICS
    # ======================================================

    def extract_transfer_metrics(
        self,
        task
    ):

        try:

            output_lines = (
                task.stdout.strip().splitlines()
            )

            if not output_lines:

                raise ValueError(
                    "File transfer returned no metrics."
                )

            transfer_result = json.loads(
                output_lines[-1]
            )

            task.transferred_bytes = (
                transfer_result.get(
                    "transferred_bytes"
                )
            )

            task.transfer_time_seconds = (
                transfer_result.get(
                    "transfer_time_seconds"
                )
            )

            task.transfer_speed = (
                transfer_result.get(
                    "transfer_speed_bytes_per_second"
                )
            )

            task.transfer_destination = (
                transfer_result.get(
                    "destination"
                )
            )

        except Exception as error:

            task.transfer_metrics_error = str(
                error
            )

    # ======================================================
    # CONVERT WINDOWS PATH TO UBUNTU PATH
    # ======================================================

    def convert_path(
        self,
        windows_path
    ):

        result = subprocess.run(

            [
                self.wsl_executable,
                "-d",
                self.distro,
                "--",
                "wslpath",
                "-a",
                windows_path
            ],

            capture_output=True,

            text=True,

            timeout=10
        )

        if result.returncode != 0:

            raise RuntimeError(
                "Could not convert Windows path "
                "to Ubuntu path."
            )

        return result.stdout.strip()