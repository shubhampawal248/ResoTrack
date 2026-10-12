from .process import Process


class TaskManager:

    def __init__(self):
        self.tasks = []

    def create_task(
        self,
        task_id,
        workload_name,
        workload_type,
        priority=2,
        estimated_time=1.0
    ):
        process = Process(
            task_id=task_id,
            workload_name=workload_name,
            workload_type=workload_type,
            priority=priority,
            estimated_time=estimated_time
        )

        self.tasks.append(process)

        return process

    def get_task(self, task_id):

        for task in self.tasks:
            if task.task_id == task_id:
                return task

        return None

    def get_ready_tasks(self):

        return [
            task for task in self.tasks
            if task.state == "READY"
        ]

    def get_running_tasks(self):

        return [
            task for task in self.tasks
            if task.state == "RUNNING"
        ]

    def get_completed_tasks(self):

        return [
            task for task in self.tasks
            if task.state == "COMPLETED"
        ]

    def get_failed_tasks(self):

        return [
            task for task in self.tasks
            if task.state == "FAILED"
        ]

    def get_all_tasks(self):
        return self.tasks