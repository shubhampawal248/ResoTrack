class BottleneckAnalyzer:

    def __init__(
        self,
        cpu_threshold=90,
        memory_threshold=85,
        disk_threshold=90,
        query_time_threshold=2.0
    ):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.query_time_threshold = query_time_threshold

    def analyze_resources(self, resources):

        bottlenecks = []

        if resources.get("cpu", 0) >= self.cpu_threshold:
            bottlenecks.append("High CPU Usage")

        if resources.get("memory", 0) >= self.memory_threshold:
            bottlenecks.append("High Memory Usage")

        if resources.get("disk", 0) >= self.disk_threshold:
            bottlenecks.append("High Disk Usage")

        return bottlenecks

    def analyze_database(self, query_time=None, active_locks=0):

        bottlenecks = []

        if query_time is not None:
            if query_time >= self.query_time_threshold:
                bottlenecks.append(
                    "Slow Database Query"
                )

        if active_locks > 5:
            bottlenecks.append(
                "High Database Lock Activity"
            )

        return bottlenecks

    def get_result(self, resources):

        bottlenecks = self.analyze_resources(resources)

        if not bottlenecks:
            return "No major bottleneck detected"

        return ", ".join(bottlenecks)