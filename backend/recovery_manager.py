class RecoveryManager:

    def __init__(self, max_retries=2):
        self.max_retries = max_retries

    def can_retry(self, task):

        return task.retry_count < self.max_retries

    def recover(self, task):

        if self.can_retry(task):

            task.reset_for_retry()

            return True

        return False

    def get_status(self, task):

        if task.state == "COMPLETED":
            return "RECOVERED"

        if task.state == "FAILED":
            if task.retry_count >= self.max_retries:
                return "FAILED - MAX RETRIES"

            return "FAILED"

        return "NOT APPLICABLE"