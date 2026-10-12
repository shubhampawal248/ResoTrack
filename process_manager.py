class ProcessManager:

    def __init__(self):
        self.running_processes = {}

    def register_process(self, task, process):

        task.start(process.pid)

        self.running_processes[task.task_id] = process

    def get_process(self, task_id):

        return self.running_processes.get(task_id)

    def is_running(self, task_id):

        process = self.get_process(task_id)

        if process is None:
            return False

        return process.poll() is None

    def remove_process(self, task_id):

        if task_id in self.running_processes:
            del self.running_processes[task_id]

    def get_running_processes(self):

        return self.running_processes