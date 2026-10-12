class FailureDetector:

    def check_process(self, process):

        exit_code = process.poll()

        # Process is still running
        if exit_code is None:
            return {
                "finished": False,
                "success": False,
                "exit_code": None
            }

        # Exit code 0 = success
        if exit_code == 0:
            return {
                "finished": True,
                "success": True,
                "exit_code": 0
            }

        # Non-zero = failure
        return {
            "finished": True,
            "success": False,
            "exit_code": exit_code
        }