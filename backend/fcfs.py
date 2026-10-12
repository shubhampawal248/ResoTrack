from .scheduler import Scheduler


class FCFSScheduler(Scheduler):

    def __init__(self):
        super().__init__()
        self.name = "FCFS"

    def select_next(self):
        if not self.ready_queue:
            return None

        # First process that arrived is selected
        self.ready_queue.sort(
            key=lambda process: process.arrival_time
        )

        return self.ready_queue.pop(0)