from .scheduler import Scheduler


class RoundRobinScheduler(Scheduler):

    def __init__(self, time_quantum=2):
        super().__init__()
        self.name = "Round Robin"
        self.time_quantum = time_quantum

    def select_next(self):
        if not self.ready_queue:
            return None

        # Select the first process
        process = self.ready_queue.pop(0)

        return process

    def return_to_queue(self, process):
        if process is not None:
            self.ready_queue.append(process)