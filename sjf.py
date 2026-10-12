from .scheduler import Scheduler


class SJFScheduler(Scheduler):

    def __init__(self):
        super().__init__()
        self.name = "SJF"

    def select_next(self):
        if not self.ready_queue:
            return None

        # Select process with smallest estimated execution time
        self.ready_queue.sort(
            key=lambda process: process.estimated_time
        )

        return self.ready_queue.pop(0)