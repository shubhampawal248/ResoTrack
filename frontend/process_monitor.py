
import streamlit as st


def show_process_monitor():
    # ==========================================
    # GET SHARED TASK RECORDS
    # ==========================================
    task_manager = st.session_state.get("task_manager")

    if task_manager is not None:
        tasks = task_manager.get_all_tasks()
    else:
        tasks = []

    total_processes = len(tasks)
    ready_count = sum(task.state == "READY" for task in tasks)
    running_count = sum(task.state == "RUNNING" for task in tasks)
    completed_count = sum(task.state == "COMPLETED" for task in tasks)
    failed_count = sum(task.state == "FAILED" for task in tasks)

    retry_attempts = sum(
        getattr(task, "retry_count", 0) for task in tasks
    )

    recovered_count = sum(
        task.state == "COMPLETED"
        and getattr(task, "retry_count", 0) > 0
        for task in tasks
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
        'Monitor submitted workloads and their individual resource usage.'
        '</div>',
        unsafe_allow_html=True
    )

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

    for col, (label, value) in zip(columns, summary_cards):
        with col:
            st.markdown(f"""
            <div class="status-card">
                <div class="status-label">{label}</div>
                <div class="status-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # CURRENT RUNNING PROCESS
    # ==========================================
    st.markdown(
        '<div class="section-title">Current Running Process</div>',
        unsafe_allow_html=True
    )

    running_tasks = [
        task for task in tasks if task.state == "RUNNING"
    ]

    if running_tasks:
        for task in running_tasks:
            st.info(
                f"Workload: {task.workload_name} | "
                f"Task ID: {task.task_id} | "
                f"PID: {getattr(task, 'pid', None) or 'Not assigned'}"
            )
    else:
        st.info("No process is currently running.")

    # ==========================================
    # PROCESS TABLE
    # ==========================================
    st.markdown(
        '<div class="section-title">Process List</div>',
        unsafe_allow_html=True
    )

    process_data = []

    for task in tasks:
        memory_bytes = getattr(task, "memory_peak_bytes", None)

        process_data.append({
            "Task ID": task.task_id,
            "Workload": task.workload_name,
            "Type": getattr(task, "workload_type", "Unknown"),
            "PID": getattr(task, "pid", None),
            "State": task.state,
            "Priority": getattr(task, "priority", None),
            "Arrival Time": getattr(task, "arrival_time", None),
            "Start Time": getattr(task, "start_time", None),
            "Completion Time": getattr(task, "completion_time", None),
            "Execution Time (s)": (
                round(task.execution_time, 3)
                if getattr(task, "execution_time", None) is not None
                else None
            ),
            "CPU Time (s)": (
                round(task.cpu_time_seconds, 3)
                if getattr(task, "cpu_time_seconds", None) is not None
                else None
            ),
            "CPU Usage (%)": (
                round(task.cpu_percent, 1)
                if getattr(task, "cpu_percent", None) is not None
                else None
            ),
            "Peak Memory (MB)": (
                round(memory_bytes / (1024 ** 2), 2)
                if memory_bytes is not None
                else None
            ),
            "Exit Code": getattr(task, "exit_code", None),
            "Retry Count": getattr(task, "retry_count", 0)
        })

    if process_data:
        st.dataframe(
            process_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.caption("No workloads have been submitted.")

    # ==========================================
    # INDIVIDUAL TASK USAGE CARDS
    # ==========================================
    st.markdown(
        '<div class="section-title">Individual Task Usage</div>',
        unsafe_allow_html=True
    )

    if tasks:
        for index, task in enumerate(tasks, start=1):
            execution_time = getattr(task, "execution_time", None)
            cpu_time = getattr(task, "cpu_time_seconds", None)
            cpu_percent = getattr(task, "cpu_percent", None)
            memory_peak = getattr(task, "memory_peak_bytes", None)
            pid = getattr(task, "pid", None)
            exit_code = getattr(task, "exit_code", None)

            memory_mb = (
                memory_peak / (1024 ** 2)
                if memory_peak is not None
                else None
            )

            state = getattr(task, "state", "UNKNOWN")

            with st.container(border=True):
                # Task heading and status
                header_col, status_col = st.columns([3, 1])

                with header_col:
                    st.subheader(
                        f"Task {index}: {task.workload_name}"
                    )
                    st.caption(f"Task ID: {task.task_id}")

                with status_col:
                    if state == "COMPLETED":
                        st.success(state)
                    elif state == "RUNNING":
                        st.info(state)
                    elif state == "FAILED":
                        st.error(state)
                    else:
                        st.warning(state)

                # Resource metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "CPU Usage",
                        f"{cpu_percent:.1f}%"
                        if cpu_percent is not None
                        else "N/A"
                    )

                with col2:
                    st.metric(
                        "Peak Memory",
                        f"{memory_mb:.2f} MB"
                        if memory_mb is not None
                        else "N/A"
                    )

                with col3:
                    st.metric(
                        "Execution Time",
                        f"{execution_time:.3f} s"
                        if execution_time is not None
                        else "N/A"
                    )

                with col4:
                    st.metric(
                        "CPU Time",
                        f"{cpu_time:.3f} s"
                        if cpu_time is not None
                        else "N/A"
                    )

                st.divider()

                # Additional process information
                info_col1, info_col2, info_col3 = st.columns(3)

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

                # Program output
                stdout = getattr(task, "stdout", "")
                stderr = getattr(task, "stderr", "")
                failure_reason = getattr(task, "failure_reason", None)

                if stdout:
                    with st.expander("View Program Output"):
                        st.code(stdout, language="text")

                if stderr:
                    with st.expander("View Program Errors"):
                        st.code(stderr, language="text")

                if failure_reason:
                    st.error(f"Failure reason: {failure_reason}")

    else:
        st.info("No workloads submitted yet.")

    # ==========================================
    # FAILURE DETECTION & RECOVERY
    # ==========================================
    st.markdown(
        '<div class="section-title">Failure Detection & Recovery</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="failure-box">
        <strong style="color:#f87171; font-size:15px;">
            Failure Monitoring
        </strong>
        <br><br>
        <span style="color:#cbd5e1; font-size:13px;">
            Failed tasks are identified from their recorded process state.
            Automatic failure detection and retry depend on runtime integration.
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.write("**Recovery Status**")

    recovery_col1, recovery_col2, recovery_col3 = st.columns(3)

    with recovery_col1:
        st.metric("Failed Operations", failed_count)

    with recovery_col2:
        st.metric("Retry Attempts", retry_attempts)

    with recovery_col3:
        st.metric("Recovered Operations", recovered_count)

    st.caption(
        "These values use the task records currently held in memory. "
        "This page displays recorded retry information but does not "
        "perform task retries itself."
    )

    # ==========================================
    # FAILURE DETAILS
    # ==========================================
    st.markdown(
        '<div class="section-title">Failure Details</div>',
        unsafe_allow_html=True
    )

    failure_data = []

    for task in tasks:
        if task.state == "FAILED":
            failure_data.append({
                "Task ID": task.task_id,
                "Workload": task.workload_name,
                "PID": getattr(task, "pid", None),
                "Exit Code": getattr(task, "exit_code", None),
                "Failure Reason": (
                    getattr(task, "failure_reason", None)
                    or getattr(task, "stderr", "")
                    or "Not recorded"
                ),
                "Retry Count": getattr(task, "retry_count", 0),
                "Recovery Status": "Failed"
            })

    if failure_data:
        st.dataframe(
            failure_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.caption(
            "Failure information will appear here when a task "
            "is marked FAILED."
        )

    # ==========================================
    # REFRESH
    # ==========================================
    if st.button(
        "Refresh Process Status",
        use_container_width=True
    ):
        st.rerun()

    # ==========================================
    # RUNTIME MONITORING NOTE
    # ==========================================
    st.markdown("""
    <div class="info-box">
        <strong style="color:#60a5fa; font-size:15px;">
            Runtime Process Monitoring
        </strong>
        <br><br>
        <span style="color:#cbd5e1; font-size:13px;">
            Each task card displays the metrics recorded for that task,
            including Linux PID, exit status, execution time, CPU time,
            average CPU usage and sampled peak memory.
            Metrics depend on the executor recording those values.
        </span>
    </div>
    """, unsafe_allow_html=True)
