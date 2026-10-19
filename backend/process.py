from datetime import datetime
import time


class Process:

    def __init__(
        self,
        task_id,
        workload_name,
        workload_type="program",
        priority=2,
        estimated_time=1.0
    ):
        self.task_id = task_id
        self.workload_name = workload_name
        self.workload_type = workload_type
        self.priority = priority
        self.estimated_time = estimated_time

        self.arrival_time = datetime.now()
        self.start_time = None
        self.completion_time = None

        self.state = "READY"
        self.pid = None
        self.exit_code = None
        self.retry_count = 0

        self.execution_time = None
        self.cpu_time_seconds = None
        self.cpu_percent = None
        self.memory_peak_bytes = None
        self.stdout = ""
        self.stderr = ""
        self.failure_reason = None
        self.timed_out = False
        self._start_monotonic = None

    def start(self, pid=None):
        self.state = "RUNNING"
        self.start_time = datetime.now()
        self._start_monotonic = time.monotonic()
        self.pid = pid

    def complete(self, exit_code=0):
        self.completion_time = datetime.now()
        self.exit_code = exit_code

        if self._start_monotonic is not None:
            self.execution_time = max(
                0.0,
                time.monotonic() - self._start_monotonic
            )

        if exit_code == 0:
            self.state = "COMPLETED"
        else:
            self.state = "FAILED"

    def reset_for_retry(self):
        self.state = "READY"
        self.start_time = None
        self.completion_time = None
        self.pid = None
        self.exit_code = None
        self.execution_time = None
        self.cpu_time_seconds = None
        self.cpu_percent = None
        self.memory_peak_bytes = None
        self.stdout = ""
        self.stderr = ""
        self.failure_reason = None
        self.timed_out = False
        self._start_monotonic = None
        self.retry_count += 1

    def get_waiting_time(self):
        if self.start_time is None:
            return None

        return (self.start_time - self.arrival_time).total_seconds()

    def get_turnaround_time(self):
        if self.completion_time is None:
            return None

        return (self.completion_time - self.arrival_time).total_seconds()

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "workload_name": self.workload_name,
            "workload_type": self.workload_type,
            "priority": self.priority,
            "state": self.state,
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "exit_code": self.exit_code,
            "retry_count": self.retry_count,
            "estimated_time": self.estimated_time,
            "execution_time": self.execution_time,
            "cpu_time_seconds": self.cpu_time_seconds,
            "cpu_percent": self.cpu_percent,
            "memory_peak_bytes": self.memory_peak_bytes,
            "failure_reason": self.failure_reason,
            "timed_out": self.timed_out,
        }
