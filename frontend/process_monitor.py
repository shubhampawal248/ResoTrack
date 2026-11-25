import streamlit as st
from types import SimpleNamespace
from backend.database_manager import DatabaseManager


# ==========================================
# GET PERSISTENT PROCESS RECORDS
# ==========================================

def get_persistent_processes():

    task_manager = st.session_state.get("task_manager")

    session_tasks = (
        task_manager.get_all_tasks()
        if task_manager is not None
        else []
    )

    records = {}
    db = None

    try:

        db = DatabaseManager()

        workloads = db.get_workloads()
        executions = db.get_execution_history()

        latest_executions = {}

        for execution in executions:

            task_id = execution["task_id"]

            previous = latest_executions.get(task_id)

            if (
                previous is None
                or execution["execution_id"]
                > previous["execution_id"]
            ):
                latest_executions[task_id] = execution

        for workload in workloads:

            task_id = workload["task_id"]

            execution = latest_executions.get(task_id, {})

            state = workload.get("status")

            if state not in ("COMPLETED", "FAILED"):
                continue

            memory_mb = execution.get("peak_memory_mb")

            task = SimpleNamespace(

                task_id=task_id,

                workload_name=workload.get(
                    "workload_name", "Unknown"
                ),

                workload_type=workload.get(
                    "workload_type", "Unknown"
                ),

                priority=workload.get("priority"),

                state=state,

                pid=execution.get("pid"),

                arrival_time=workload.get("submitted_at"),

                start_time=None,

                completion_time=None,

                execution_recorded_at=execution.get(
                    "executed_at"
                ),

                execution_time=execution.get(
                    "execution_time_seconds"
                ),

                cpu_time_seconds=execution.get(
                    "cpu_time_seconds"
                ),

                cpu_percent=execution.get("cpu_percent"),

                memory_peak_bytes=(
                    float(memory_mb) * 1024 ** 2
                    if memory_mb is not None
                    else None
                ),

                exit_code=execution.get("exit_code"),

                retry_count=None,

                stdout="",

                stderr="",

                failure_reason=None
            )

            records[task_id] = task

    except Exception as error:

        st.warning(
            f"Could not retrieve saved processes: {error}"
        )

    finally:

        if db is not None:
            db.close()

    # Merge current session without duplicates

    for task in session_tasks:

        records[task.task_id] = task

    return list(reversed(list(records.values())))


# ==========================================
# FORMAT VALUES
# ==========================================

def format_number(value, decimals=2):

    if value is None:
        return None

    try:
        return round(float(value), decimals)

    except (ValueError, TypeError):
        return None


def format_metric(value, unit="", decimals=2):

    value = format_number(value, decimals)

    if value is None:
        return "N/A"

    return f"{value:.{decimals}f}{unit}"


# ==========================================
# PROCESS MONITOR
# ==========================================

def show_process_monitor():

    tasks = get_persistent_processes()

    task_manager = st.session_state.get("task_manager")

    session_tasks = (
        task_manager.get_all_tasks()
        if task_manager is not None
        else []
    )

    session_ids = {
        task.task_id for task in session_tasks
    }

    total_processes = len(tasks)

    ready_count = sum(
        task.state == "READY" for task in tasks
    )

    running_count = sum(
        task.state == "RUNNING" for task in tasks
    )

    completed_count = sum(
        task.state == "COMPLETED" for task in tasks
    )

    failed_count = sum(
        task.state == "FAILED" for task in tasks
    )

    retry_attempts = sum(
        getattr(task, "retry_count", 0) or 0
        for task in session_tasks
    )

    recovered_count = sum(
        task.state == "COMPLETED"
        and (getattr(task, "retry_count", 0) or 0) > 0
        for task in session_tasks
    )

    # ==========================================
    # PAGE STYLING
    # ==========================================

    st.markdown("""
    <style>

    .page-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .page-subtitle {
        color: #9ca3af;
        font-size: 15px;
        margin-bottom: 28px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 14px;
    }

    .status-card {
        background: #111827;
        border: 1px solid #273449;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }

    .status-label {
        color: #9ca3af;
        font-size: 12px;
    }

    .status-value {
        font-size: 20px;
        font-weight: 600;
        margin-top: 5px;
    }

    .info-box {
        background: rgba(59, 130, 246, 0.10);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 10px;
        padding: 16px;
        margin-top: 18px;
    }

    .failure-box {
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 10px;
        padding: 16px;
        margin-top: 18px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # PAGE HEADER
    # ==========================================

    st.markdown(
        '<div class="page-title">Process Monitor</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Monitor current and previously executed workloads '
        'with their individual resource usage.'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "Refresh Process Status",
        width="stretch"
    ):
        st.rerun()

    # ==========================================
    # PROCESS SUMMARY
    # ==========================================

    st.markdown(
        '<div class="section-title">Process Summary</div>',
        unsafe_allow_html=True
    )

    summary_cards = [
        ("Total Processes", total_processes),
        ("READY", ready_count),
        ("RUNNING", running_count),
        ("COMPLETED", completed_count),
        ("FAILED", failed_count)
    ]

    columns = st.columns(5)

    for col, (label, value) in zip(
        columns, summary_cards
    ):

        with col:

            st.markdown(f"""
            <div class="status-card">
                <div class="status-label">{label}</div>
                <div class="status-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.caption(
        "Process records are combined from MySQL "
        "and the current application session."
    )

    # ==========================================
    # CURRENT RUNNING PROCESSES
    # ==========================================

    st.markdown(
        '<div class="section-title">'
        'Current Running Process</div>',
        unsafe_allow_html=True
    )

    running_tasks = [
        task for task in session_tasks
        if task.state == "RUNNING"
    ]

    if running_tasks:

        for task in running_tasks:

            st.info(
                f"Workload: {task.workload_name} | "
                f"Task ID: {task.task_id} | "
                f"PID: "
                f"{getattr(task, 'pid', None) or 'Not assigned'}"
            )

    else:

        st.info("No process is currently running.")

    # ==========================================
    # PROCESS FILTERS
    # ==========================================

    st.markdown(
        '<div class="section-title">Process List</div>',
        unsafe_allow_html=True
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        selected_state = st.selectbox(
            "Process State",
            [
                "All",
                "READY",
                "RUNNING",
                "COMPLETED",
                "FAILED"
            ],
            key="process_monitor_state"
        )

    with filter_col2:

        selected_source = st.selectbox(
            "Record Source",
            [
                "All Processes",
                "Current Session",
                "Previous Sessions"
            ],
            key="process_monitor_source"
        )

    with filter_col3:

        search = st.text_input(
            "Search Workload",
            placeholder="Name or Task ID",
            key="process_monitor_search"
        )

    filtered_tasks = []

    for task in tasks:

        if (
            selected_state != "All"
            and task.state != selected_state
        ):
            continue

        if (
            selected_source == "Current Session"
            and task.task_id not in session_ids
        ):
            continue

        if (
            selected_source == "Previous Sessions"
            and task.task_id in session_ids
        ):
            continue

        if search:

            search_value = search.lower().strip()

            if (
                search_value not in str(
                    task.workload_name
                ).lower()

                and search_value not in str(
                    task.task_id
                ).lower()
            ):
                continue

        filtered_tasks.append(task)

    # ==========================================
    # PROCESS TABLE
    # ==========================================

    process_data = []

    for task in filtered_tasks:

        memory_bytes = getattr(
            task, "memory_peak_bytes", None
        )

        process_data.append({

            "Task ID": task.task_id,

            "Workload": task.workload_name,

            "Type": getattr(
                task, "workload_type", "Unknown"
            ),

            "PID": getattr(task, "pid", None),

            "State": task.state,

            "Priority": getattr(task, "priority", None),

            "Arrival Time": getattr(
                task, "arrival_time", None
            ),

            "Start Time": getattr(
                task, "start_time", None
            ),

            "Completion Time": getattr(
                task, "completion_time", None
            ),

            "Execution Recorded At": getattr(
                task, "execution_recorded_at", None
            ),

            "Execution Time (s)": format_number(
                getattr(task, "execution_time", None),
                3
            ),

            "CPU Time (s)": format_number(
                getattr(task, "cpu_time_seconds", None),
                3
            ),

            "CPU Usage (%)": format_number(
                getattr(task, "cpu_percent", None),
                1
            ),

            "Peak Memory (MB)": (
                round(float(memory_bytes) / 1024 ** 2, 2)
                if memory_bytes is not None
                else None
            ),

            "Exit Code": getattr(
                task, "exit_code", None
            ),

            "Retry Count": getattr(
                task, "retry_count", None
            ),

            "Source": (
                "Current Session"
                if task.task_id in session_ids
                else "MySQL History"
            )
        })

    if process_data:

        st.dataframe(
            process_data,
            width="stretch",
            hide_index=True
        )

        st.caption(
            f"Showing {len(process_data)} "
            f"of {total_processes} processes."
        )

    else:

        st.info("No matching processes found.")

    # ==========================================
    # INDIVIDUAL TASK USAGE
    # ==========================================

    st.markdown(
        '<div class="section-title">'
        'Individual Task Usage</div>',
        unsafe_allow_html=True
    )

    if filtered_tasks:

        for index, task in enumerate(
            filtered_tasks, start=1
        ):

            execution_time = getattr(
                task, "execution_time", None
            )

            cpu_time = getattr(
                task, "cpu_time_seconds", None
            )

            cpu_percent = getattr(
                task, "cpu_percent", None
            )

            memory_peak = getattr(
                task, "memory_peak_bytes", None
            )

            pid = getattr(task, "pid", None)

            exit_code = getattr(
                task, "exit_code", None
            )

            memory_mb = (
                float(memory_peak) / 1024 ** 2
                if memory_peak is not None
                else None
            )

            state = getattr(
                task, "state", "UNKNOWN"
            )

            with st.container(border=True):

                header_col, status_col = st.columns(
                    [3, 1]
                )

                with header_col:

                    st.subheader(
                        f"Task {index}: "
                        f"{task.workload_name}"
                    )

                    st.caption(
                        f"Task ID: {task.task_id}"
                    )

                    st.caption(
                        "Source: "
                        + (
                            "Current Session"
                            if task.task_id in session_ids
                            else "MySQL History"
                        )
                    )

                with status_col:

                    if state == "COMPLETED":
                        st.success(state)

                    elif state == "RUNNING":
                        st.info(state)

                    elif state == "FAILED":
                        st.error(state)

                    else:
                        st.warning(state)

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "CPU Usage",
                        format_metric(
                            cpu_percent, "%", 1
                        )
                    )

                with col2:

                    st.metric(
                        "Peak Memory",
                        format_metric(
                            memory_mb, " MB", 2
                        )
                    )

                with col3:

                    st.metric(
                        "Execution Time",
                        format_metric(
                            execution_time, " s", 3
                        )
                    )

                with col4:

                    st.metric(
                        "CPU Time",
                        format_metric(
                            cpu_time, " s", 3
                        )
                    )

                st.divider()

                info_col1, info_col2, info_col3 = (
                    st.columns(3)
                )

                with info_col1:

                    st.write(
                        f"**Linux PID:** "
                        f"{pid if pid is not None else 'N/A'}"
                    )

                with info_col2:

                    st.write(
                        f"**Priority:** "
                        f"{getattr(task, 'priority', 'N/A')}"
                    )

                with info_col3:

                    st.write(
                        f"**Exit Code:** "
                        f"{exit_code if exit_code is not None else 'N/A'}"
                    )

                stdout = getattr(task, "stdout", "")

                stderr = getattr(task, "stderr", "")

                failure_reason = getattr(
                    task, "failure_reason", None
                )

                if stdout:

                    with st.expander(
                        "View Program Output"
                    ):

                        st.code(
                            stdout,
                            language="text"
                        )

                if stderr:

                    with st.expander(
                        "View Program Errors"
                    ):

                        st.code(
                            stderr,
                            language="text"
                        )

                if failure_reason:

                    st.error(
                        f"Failure reason: {failure_reason}"
                    )

    else:

        st.info("No matching workloads available.")

    # ==========================================
    # FAILURE DETECTION AND RECOVERY
    # ==========================================

    st.markdown(
        '<div class="section-title">'
        'Failure Detection & Recovery</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="failure-box">

        <strong style="color:#f87171; font-size:15px;">
            Failure Monitoring
        </strong>

        <br><br>

        <span style="color:#cbd5e1; font-size:13px;">

            Failed workloads are identified using
            their recorded process states.

            Previous failed workloads are retrieved
            from MySQL.

            Retry and recovery information depends
            on the current runtime session.

        </span>

    </div>
    """, unsafe_allow_html=True)

    st.write("**Recovery Status**")

    recovery_col1, recovery_col2, recovery_col3 = (
        st.columns(3)
    )

    with recovery_col1:

        st.metric(
            "Failed Operations",
            failed_count
        )

    with recovery_col2:

        st.metric(
            "Retry Attempts (Session)",
            retry_attempts
        )

    with recovery_col3:

        st.metric(
            "Recovered Operations (Session)",
            recovered_count
        )

    st.caption(
        "Failure counts include saved historical workloads. "
        "Retry and recovery counts use current-session "
        "information only."
    )

    # ==========================================
    # FAILURE DETAILS
    # ==========================================

    st.markdown(
        '<div class="section-title">'
        'Failure Details</div>',
        unsafe_allow_html=True
    )

    failure_data = []

    for task in tasks:

        if task.state == "FAILED":

            failure_data.append({

                "Task ID": task.task_id,

                "Workload": task.workload_name,

                "PID": getattr(
                    task, "pid", None
                ),

                "Exit Code": getattr(
                    task, "exit_code", None
                ),

                "Failure Reason": (
                    getattr(
                        task, "failure_reason", None
                    )
                    or getattr(task, "stderr", "")
                    or "Not recorded"
                ),

                "Retry Count": getattr(
                    task, "retry_count", None
                ),

                "Recovery Status": "Failed",

                "Source": (
                    "Current Session"
                    if task.task_id in session_ids
                    else "MySQL History"
                )
            })

    if failure_data:

        st.dataframe(
            failure_data,
            width="stretch",
            hide_index=True
        )

    else:

        st.success("No failed workloads recorded.")

    # ==========================================
    # RUNTIME MONITORING NOTE
    # ==========================================

    st.markdown("""
    <div class="info-box">

        <strong style="color:#60a5fa; font-size:15px;">
            Persistent Process Monitoring
        </strong>

        <br><br>

        <span style="color:#cbd5e1; font-size:13px;">

            Current workloads are retrieved from
            TaskManager.

            Previously completed and failed workloads
            are retrieved from MySQL.

            Saved process records remain available
            after browser refresh and application restart.

            Historical PID values represent recorded
            Linux processes, not currently running processes.

            Metrics that were not saved remain unavailable.

        </span>

    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":

    show_process_monitor()