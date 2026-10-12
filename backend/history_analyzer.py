class HistoryAnalyzer:

    def __init__(self, database_manager=None):
        self.database_manager = database_manager

    def get_workload_history(self, workload_name):

        if self.database_manager is None:
            return []

        return self.database_manager.get_workload_history(
            workload_name
        )

    def calculate_average(self, values):

        if not values:
            return 0

        return sum(values) / len(values)

    def get_estimated_time(self, workload_name):

        history = self.get_workload_history(workload_name)

        if not history:
            # No previous history
            return 1.0

        execution_times = []

        for record in history:

            if record.get("execution_time") is not None:
                execution_times.append(
                    float(record["execution_time"])
                )

        if not execution_times:
            return 1.0

        return self.calculate_average(execution_times)