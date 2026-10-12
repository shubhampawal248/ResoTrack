from .scheduler import Scheduler
from .fcfs import FCFSScheduler
from .sjf import SJFScheduler
from .priority import PriorityScheduler


class AdaptiveScheduler(Scheduler):

    def __init__(self, history=None):
        super().__init__()
        self.name = "Adaptive"
        self.history = history if history else []

    def choose_algorithm(self):
        if not self.ready_queue:
            return "FCFS"

        # If many high-priority tasks are waiting
        high_priority_count = 0

        for process in self.ready_queue:
            if process.priority == 1:
                high_priority_count += 1

        if high_priority_count >= 2:
            return "Priority"

        # If queue has many tasks, use SJF
        if len(self.ready_queue) >= 4:
            return "SJF"

        # Otherwise FCFS
        return "FCFS"

    def select_next(self):
        if not self.ready_queue:
            return None

        algorithm = self.choose_algorithm()

        if algorithm == "Priority":
            scheduler = PriorityScheduler()

        elif algorithm == "SJF":
            scheduler = SJFScheduler()

        else:
            scheduler = FCFSScheduler()

        scheduler.add_processes(self.ready_queue)
        self.ready_queue.clear()

        return scheduler.select_next()