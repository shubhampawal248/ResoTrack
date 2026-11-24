from datetime import datetime

import streamlit as st
import pandas as pd

from backend.database_manager import DatabaseManager
from backend.fcfs import FCFSScheduler
from backend.sjf import SJFScheduler
from backend.priority import PriorityScheduler
from backend.round_robin import RoundRobinScheduler
from backend.adaptive_scheduler import AdaptiveScheduler
from backend.automatic_scheduler import AutomaticScheduler
from backend.workload_executor import WorkloadExecutor


def show_scheduler():

    st.title("SysNexa — Scheduler")

    st.caption(
        "Submit multiple workloads, preview their scheduling order, "
        "and execute Python, C/C++ and file-transfer workloads."
    )

    task_manager = st.session_state.get("task_manager")

    if task_manager is None:
        st.error("TaskManager is not initialized. Check app.py.")
        return

    # =========================================================
    # SCHEDULING CONTROLS
    # =========================================================

    st.subheader("Scheduling Controls")

    mode = st.radio(
        "Scheduling mode",
        ["Manual", "Automatic"],
        horizontal=True,
        key="scheduler_mode_choice",
    )

    algorithm = st.selectbox(
        "Scheduling algorithm",
        [
            "FCFS",
            "SJF",
            "Priority",
            "Round Robin",
            "Adaptive Scheduler",
            "Automatic Scheduler Switching",
        ],
        key="scheduler_algorithm_choice",
    )

    descriptions = {
        "FCFS":
            "The earliest-arriving READY workload is selected first.",

        "SJF":
            "The READY workload with the shortest estimated "
            "execution time is selected first.",

        "Priority":
            "Priority 1 represents the highest priority.",

        "Round Robin":
            "True time-sliced execution requires preemption support.",

        "Adaptive Scheduler":
            "Scheduling decisions depend on the adaptive scheduler's rules.",

        "Automatic Scheduler Switching":
            "The automatic scheduler chooses an algorithm.",
    }

    st.info(descriptions[algorithm])

    effective_mode = (
        "Automatic"
        if mode == "Automatic"
        or algorithm == "Automatic Scheduler Switching"
        else "Manual"
    )

    st.session_state["selected_scheduling_mode"] = effective_mode

    st.session_state["selected_algorithm"] = (
        "Automatic Scheduler Switching"
        if effective_mode == "Automatic"
        else algorithm
    )

    tasks = task_manager.get_all_tasks()

    ready_tasks = task_manager.get_ready_tasks()

    running_tasks = task_manager.get_running_tasks()

    completed_tasks = task_manager.get_completed_tasks()

    failed_tasks = task_manager.get_failed_tasks()

    # =========================================================
    # SCHEDULER STATUS
    # =========================================================

    st.subheader("Scheduler Status")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Scheduling Mode",
        st.session_state["selected_scheduling_mode"],
    )

    col2.metric(
        "Current Algorithm",
        st.session_state["selected_algorithm"],
    )

    col3.metric(
        "READY Workloads",
        len(ready_tasks)
    )

    col4.metric(
        "Running Workload",
        running_tasks[0].workload_name
        if running_tasks else "None",
    )

    # =========================================================
    # AVAILABLE ALGORITHMS
    # =========================================================

    st.subheader("Available Scheduling Algorithms")

    algorithms = [
        (
            "FCFS",
            "Selects workloads in arrival order."
        ),
        (
            "SJF",
            "Selects the shortest estimated workload first."
        ),
        (
            "Priority",
            "Selects the highest-priority workload first."
        ),
        (
            "Round Robin",
            "Uses repeated time slices when supported."
        ),
        (
            "Adaptive Scheduler",
            "Adapts scheduling decisions."
        ),
        (
            "Automatic Scheduler",
            "Chooses an algorithm automatically."
        ),
    ]

    columns = st.columns(3)

    for index, (name, description) in enumerate(algorithms):

        with columns[index % 3]:

            with st.container(border=True):

                st.markdown(f"**{name}**")

                st.write(description)

    # =========================================================
    # READY QUEUE
    # =========================================================

    st.subheader("READY Queue")

    if ready_tasks:

        ready_data = [
            {
                "Task ID": task.task_id,
                "Workload": task.workload_name,
                "Type": task.workload_type,
                "Priority": task.priority,
                "Estimated Time": task.estimated_time,
                "Arrival Time": str(task.arrival_time),
                "State": task.state,
            }
            for task in ready_tasks
        ]

        st.dataframe(
            pd.DataFrame(ready_data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No workloads are currently in the READY queue."
        )

    # =========================================================
    # SUBMISSION ORDER
    # =========================================================

    st.subheader("Submission Order")

    if tasks:

        submission_data = [
            {
                "Task ID": task.task_id,
                "Workload": task.workload_name,
                "Type": task.workload_type,
                "State": task.state,
            }
            for task in tasks
        ]

        st.dataframe(
            pd.DataFrame(submission_data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No workloads have been submitted yet.")

    # =========================================================
    # SCHEDULER HELPERS
    # =========================================================

    scheduler_classes = {
        "FCFS": FCFSScheduler,
        "SJF": SJFScheduler,
        "Priority": PriorityScheduler,
        "Round Robin": RoundRobinScheduler,
        "Adaptive Scheduler": AdaptiveScheduler,
    }

    def select_next_workload(available_tasks):

        if not available_tasks:

            return None, "None"

        if (
            effective_mode == "Automatic"
            or algorithm == "Automatic Scheduler Switching"
        ):

            scheduler = AutomaticScheduler()

            scheduler.add_processes(
                list(available_tasks)
            )

            selected_task = scheduler.select_next()

            if selected_task is None:

                return None, "Automatic"

            return (
                selected_task,
                scheduler.get_selected_algorithm()
                or "Automatic",
            )

        scheduler_class = scheduler_classes[algorithm]

        scheduler = scheduler_class()

        scheduler.add_processes(
            list(available_tasks)
        )

        return scheduler.select_next(), algorithm

    # =========================================================
    # CHECK SUPPORTED WORKLOADS
    # =========================================================

    def is_executable(task):

        # FILE TRANSFER WORKLOAD

        if task.workload_type == "file_transfer":

            operation = getattr(
                task,
                "operation",
                ""
            )

            if operation == "File Upload":

                return (
                    getattr(
                        task,
                        "uploaded_bytes",
                        None
                    ) is not None
                )

            if operation == "File Download":

                return bool(
                    getattr(
                        task,
                        "download_url",
                        ""
                    ).strip()
                )

            return False

        # PYTHON AND C/C++ WORKLOAD

        source_code = getattr(
            task,
            "source_code",
            None
        )

        return (
            task.workload_type in ("python", "cpp")
            and isinstance(source_code, str)
            and bool(source_code.strip())
        )

    # =========================================================
    # BUILD EXECUTION ORDER
    # =========================================================

    def build_execution_order(available_tasks):

        remaining = list(available_tasks)

        ordered = []

        while remaining:

            selected_task, selected_algorithm = (
                select_next_workload(remaining)
            )

            if selected_task is None:

                break

            ordered.append(
                (selected_task, selected_algorithm)
            )

            remaining = [
                task
                for task in remaining
                if task.task_id != selected_task.task_id
            ]

        return ordered

    # =========================================================
    # EXECUTION QUEUE PREVIEW
    # =========================================================

    st.subheader("Execution Queue Preview")

    runnable_tasks = [
        task
        for task in ready_tasks
        if is_executable(task)
    ]

    unsupported_tasks = [
        task
        for task in ready_tasks
        if not is_executable(task)
    ]

    preview_order = build_execution_order(
        runnable_tasks
    )

    if preview_order:

        preview_data = [
            {
                "Position": index,
                "Task ID": task.task_id,
                "Workload": task.workload_name,
                "Type": task.workload_type,
                "Algorithm": selected_algorithm,
                "Priority": task.priority,
                "Estimated Time": task.estimated_time,
                "State": task.state,
            }

            for index, (task, selected_algorithm)
            in enumerate(preview_order, start=1)
        ]

        st.dataframe(
            pd.DataFrame(preview_data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No executable Python, C/C++ or file-transfer "
            "workloads are ready."
        )

    if unsupported_tasks:

        st.warning(
            f"{len(unsupported_tasks)} READY workload(s) "
            "cannot be executed. SQL execution is not "
            "implemented here, or required workload "
            "details are missing."
        )

    # =========================================================
    # SCHEDULER CONTROL
    # =========================================================

    st.subheader("Scheduler Control")

    st.caption(
        "Submitting a workload does not execute it. "
        "Use Execute Queue to run Python, C/C++ and "
        "file-transfer workloads in the displayed order."
    )

    execute_col, history_col = st.columns(2)

    with execute_col:

        execute_clicked = st.button(
            "Execute Queue",
            type="primary",
            use_container_width=True,
            disabled=(
                not runnable_tasks
                or bool(running_tasks)
            ),
        )

    with history_col:

        clear_history_clicked = st.button(
            "Clear Selection History",
            use_container_width=True,
        )

    if clear_history_clicked:

        st.session_state[
            "scheduler_selection_order"
        ] = []

        st.rerun()

    # =========================================================
    # DATABASE HELPER
    # =========================================================

    def persist_execution(task):

        db = DatabaseManager()

        try:

            db.update_workload_status(task)

            db.save_execution_history(task)

            return True, None

        except Exception as error:

            return False, str(error)

        finally:

            db.close()

    # =========================================================
    # EXECUTE QUEUE
    # =========================================================

    if execute_clicked:

        execution_log = st.session_state.setdefault(
            "scheduler_selection_order",
            []
        )

        executor = WorkloadExecutor()

        progress = st.progress(0.0)

        status = st.empty()

        current_ready_tasks = (
            task_manager.get_ready_tasks()
        )

        queue = build_execution_order(
            [
                task
                for task in current_ready_tasks
                if is_executable(task)
            ]
        )

        total = len(queue)

        successful = 0

        unsuccessful = 0

        processed = 0

        if total == 0:

            st.warning(
                "There are no executable READY workloads."
            )

        else:

            for task, actual_algorithm in queue:

                if task.state != "READY":

                    continue

                processed += 1

                status.info(
                    f"Executing workload {processed} "
                    f"of {total}: {task.workload_name}"
                )

                execution_log.append(
                    {
                        "task_id": task.task_id,
                        "workload": task.workload_name,
                        "algorithm": actual_algorithm,
                        "type": task.workload_type,
                    }
                )

                task.scheduler_name = actual_algorithm

                execution_error = None

                # -----------------------------------------
                # ACTUAL WORKLOAD EXECUTION
                # -----------------------------------------

                try:

                    executor.execute(
                        task,
                        getattr(task, "source_code", ""),
                        timeout_seconds=int(
                            getattr(
                                task,
                                "execution_timeout",
                                30
                            )
                        ),
                    )

                except Exception as error:

                    execution_error = str(error)

                    task.state = "FAILED"

                    task.failure_reason = execution_error

                    if getattr(
                        task,
                        "completion_time",
                        None
                    ) is None:

                        task.completion_time = datetime.now()

                    st.error(
                        f"Could not execute "
                        f"{task.workload_name}: "
                        f"{execution_error}"
                    )

                # -----------------------------------------
                # SAVE EXECUTION HISTORY
                # -----------------------------------------

                saved, db_error = persist_execution(task)

                if not saved:

                    st.error(
                        f"Database save failed for "
                        f"{task.workload_name}: "
                        f"{db_error}"
                    )

                # -----------------------------------------
                # EXECUTION RESULT
                # -----------------------------------------

                if task.state == "COMPLETED":

                    successful += 1

                    st.success(
                        f"{task.workload_name} "
                        "completed successfully."
                    )

                else:

                    unsuccessful += 1

                    if execution_error is None:

                        st.error(
                            f"{task.workload_name} "
                            f"finished with state "
                            f"{task.state}."
                        )

                stdout_text = getattr(
                    task,
                    "stdout",
                    ""
                )

                stderr_text = getattr(
                    task,
                    "stderr",
                    ""
                )

                if stdout_text:

                    with st.expander(
                        f"Workload output — "
                        f"{task.workload_name}"
                    ):

                        st.code(
                            stdout_text,
                            language="text"
                        )

                if stderr_text:

                    with st.expander(
                        f"Workload errors — "
                        f"{task.workload_name}"
                    ):

                        st.code(
                            stderr_text,
                            language="text"
                        )

                progress.progress(
                    processed / total
                )

            st.session_state["last_queue_result"] = {
                "successful": successful,
                "unsuccessful": unsuccessful,
            }

            st.rerun()

    # =========================================================
    # LAST QUEUE RESULT
    # =========================================================

    last_result = st.session_state.get(
        "last_queue_result"
    )

    if last_result:

        message = (
            f"Queue finished. "
            f"Successful: {last_result['successful']}; "
            f"Unsuccessful: {last_result['unsuccessful']}."
        )

        if last_result["unsuccessful"] > 0:

            st.warning(message)

        else:

            st.success(message)

    # =========================================================
    # SELECTION / EXECUTION HISTORY
    # =========================================================

    st.subheader("Selection / Execution Order")

    selection_order = st.session_state.get(
        "scheduler_selection_order",
        []
    )

    if selection_order:

        selection_data = [
            {
                "Position": index,
                "Task ID": item.get("task_id", ""),
                "Workload": item.get("workload", ""),
                "Type": item.get("type", ""),
                "Algorithm": item.get("algorithm", ""),
            }

            for index, item in enumerate(
                selection_order,
                start=1
            )
        ]

        st.dataframe(
            pd.DataFrame(selection_data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No workloads have been selected "
            "for execution yet."
        )

    # =========================================================
    # COMPLETED WORKLOADS
    # =========================================================

    st.subheader("Completed Workloads")

    if completed_tasks:

        completed_data = [
            {
                "Task ID": task.task_id,
                "Workload": task.workload_name,
                "Type": task.workload_type,
                "PID": task.pid,
                "Exit Code": task.exit_code,
                "Execution Time (s)": task.execution_time,
                "State": task.state,
            }

            for task in completed_tasks
        ]

        st.dataframe(
            pd.DataFrame(completed_data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No completed workloads available yet.")

    # =========================================================
    # FILE TRANSFER RESULTS
    # =========================================================

    st.subheader("File Transfer Results")

    transfer_tasks = [
        task
        for task in tasks
        if task.workload_type == "file_transfer"
        and task.state in ("COMPLETED", "FAILED")
    ]

    if transfer_tasks:

        transfer_rows = []

        for task in transfer_tasks:

            transferred_bytes = getattr(
                task,
                "transferred_bytes",
                None
            )

            transfer_time = getattr(
                task,
                "transfer_time_seconds",
                None
            )

            transfer_speed = getattr(
                task,
                "transfer_speed",
                None
            )

            cpu_percent = getattr(
                task,
                "cpu_percent",
                None
            )

            memory_peak = getattr(
                task,
                "memory_peak_bytes",
                None
            )

            transfer_rows.append(
                {
                    "Task ID": task.task_id,

                    "Workload": task.workload_name,

                    "Operation": getattr(
                        task,
                        "operation",
                        "N/A"
                    ),

                    "Algorithm": getattr(
                        task,
                        "scheduler_name",
                        "N/A"
                    ),

                    "PID": getattr(
                        task,
                        "pid",
                        None
                    ),

                    "Transferred Bytes":
                        transferred_bytes,

                    "File Size (KB)": (
                        round(
                            transferred_bytes / 1024,
                            2
                        )
                        if transferred_bytes is not None
                        else None
                    ),

                    "Transfer Time (s)": (
                        round(transfer_time, 6)
                        if transfer_time is not None
                        else None
                    ),

                    "Transfer Speed (KB/s)": (
                        round(
                            transfer_speed / 1024,
                            2
                        )
                        if transfer_speed is not None
                        else None
                    ),

                    "CPU Usage (%)": (
                        round(cpu_percent, 2)
                        if cpu_percent is not None
                        else None
                    ),

                    "Peak Memory (MB)": (
                        round(
                            memory_peak / (1024 ** 2),
                            2
                        )
                        if memory_peak is not None
                        else None
                    ),

                    "Destination": getattr(
                        task,
                        "transfer_destination",
                        None
                    ),

                    "State": task.state,

                    "Metrics Error": getattr(
                        task,
                        "transfer_metrics_error",
                        None
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(transfer_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Transfer speed is calculated using actual "
            "transferred bytes divided by measured "
            "transfer duration. Upload speed measures "
            "the local WSL decoding and writing operation."
        )

    else:

        st.info(
            "No file-transfer workloads have finished yet."
        )

    # =========================================================
    # WORKLOAD OUTPUT
    # =========================================================

    finished_tasks = [
        task
        for task in tasks
        if task.state in ("COMPLETED", "FAILED")
    ]

    if finished_tasks:

        with st.expander("View Workload Output"):

            selected_task_id = st.selectbox(
                "Select workload",
                [
                    task.task_id
                    for task in finished_tasks
                ],
                format_func=lambda task_id: next(
                    (
                        task.workload_name
                        + " — "
                        + task_id
                        for task in finished_tasks
                        if task.task_id == task_id
                    ),
                    task_id
                ),
                key="scheduler_output_task",
            )

            selected_task = next(
                (
                    task
                    for task in finished_tasks
                    if task.task_id == selected_task_id
                ),
                None
            )

            if selected_task is not None:

                stdout_text = getattr(
                    selected_task,
                    "stdout",
                    ""
                )

                stderr_text = getattr(
                    selected_task,
                    "stderr",
                    ""
                )

                st.markdown("**Output**")

                if stdout_text:

                    st.code(
                        stdout_text,
                        language="text"
                    )

                else:

                    st.info("No standard output.")

                if stderr_text:

                    st.markdown("**Errors**")

                    st.code(
                        stderr_text,
                        language="text"
                    )

    # =========================================================
    # FAILED WORKLOADS
    # =========================================================

    st.subheader("Failed Workloads")

    if failed_tasks:

        failed_data = [
            {
                "Task ID": task.task_id,

                "Workload": task.workload_name,

                "Type": task.workload_type,

                "Exit Code": task.exit_code,

                "Failure Reason": getattr(
                    task,
                    "failure_reason",
                    None
                ),

                "Timed Out": getattr(
                    task,
                    "timed_out",
                    False
                ),

                "Retry Count": getattr(
                    task,
                    "retry_count",
                    0
                ),
            }

            for task in failed_tasks
        ]

        st.dataframe(
            pd.DataFrame(failed_data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No failed workloads available.")

    # =========================================================
    # FAILURE AND RECOVERY STATUS
    # =========================================================

    st.subheader("Failure & Recovery Status")

    retry_attempts = sum(
        getattr(task, "retry_count", 0)
        for task in tasks
    )

    recovered_tasks = [
        task
        for task in tasks
        if getattr(task, "retry_count", 0) > 0
        and task.state == "COMPLETED"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Failed Workloads",
        len(failed_tasks)
    )

    col2.metric(
        "Retry Attempts",
        retry_attempts
    )

    col3.metric(
        "Recovered Workloads",
        len(recovered_tasks)
    )

    st.caption(
        "Retry counts are displayed from task records. "
        "Automatic recovery requires retry logic "
        "in the execution workflow."
    )


if __name__ == "__main__":

    show_scheduler()