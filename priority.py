from .scheduler import Scheduler


class PriorityScheduler(Scheduler):

    def __init__(self):
        super().__init__()
        self.name = "Priority"

    def select_next(self):
        if not self.ready_queue:
            return None

        # Lower number means higher priority
        self.ready_queue.sort(
            key=lambda process: (
                process.priority,
                process.arrival_time
            )
        )

        return self.ready_queue.pop(0)