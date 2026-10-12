from abc import ABC, abstractmethod


class Scheduler(ABC):

    def __init__(self):
        self.ready_queue = []

    def add_process(self, process):
        process.state = "READY"
        self.ready_queue.append(process)

    def add_processes(self, processes):
        for process in processes:
            self.add_process(process)

    @abstractmethod
    def select_next(self):
        pass

    def has_processes(self):
        return len(self.ready_queue) > 0

    def queue_size(self):
        return len(self.ready_queue)

    def get_queue(self):
        return self.ready_queue

    def clear_queue(self):
        self.ready_queue.clear()