from .fcfs import FCFSScheduler
from .sjf import SJFScheduler
from .priority import PriorityScheduler
from .round_robin import RoundRobinScheduler
from .adaptive_scheduler import AdaptiveScheduler


class AutomaticScheduler:

    def __init__(self):
        self.selected_algorithm = "FCFS"
        self.scheduler = FCFSScheduler()

    def choose_algorithm(self, processes):

        if not processes:
            return "FCFS"

        high_priority = 0

        for process in processes:
            if process.priority == 1:
                high_priority += 1

        # Many high priority tasks
        if high_priority >= 2:
            return "Priority"

        # Many tasks waiting
        if len(processes) >= 5:
            return "Round Robin"

        # Small queue
        if len(processes) <= 2:
            return "FCFS"

        # Medium queue
        return "SJF"

    def create_scheduler(self, processes):

        algorithm = self.choose_algorithm(processes)

        self.selected_algorithm = algorithm

        if algorithm == "FCFS":
            self.scheduler = FCFSScheduler()

        elif algorithm == "SJF":
            self.scheduler = SJFScheduler()

        elif algorithm == "Priority":
            self.scheduler = PriorityScheduler()

        elif algorithm == "Round Robin":
            self.scheduler = RoundRobinScheduler()

        elif algorithm == "Adaptive":
            self.scheduler = AdaptiveScheduler()

        return self.scheduler

    def get_selected_algorithm(self):
        return self.selected_algorithm