from datetime import datetime


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

    def start(self, pid=None):
        self.state = "RUNNING"
        self.start_time = datetime.now()
        self.pid = pid

    def complete(self, exit_code=0):
        self.completion_time = datetime.now()
        self.exit_code = exit_code

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
            "estimated_time": self.estimated_time
        }