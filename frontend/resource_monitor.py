
from datetime import datetime

import streamlit as st
import pandas as pd
import altair as alt

from backend.resource_manager import ResourceManager
from backend.monitor import ProcessMonitor


# ==========================================================
# SETTINGS
# ==========================================================

MAX_HISTORY = 60
REFRESH_SECONDS = "3s"


# ==========================================================
# FORMAT HELPERS
# ==========================================================

def format_percent(value):
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_memory(value):
    if value is None:
        return "N/A"

    try:
        return f"{float(value) / (1024 ** 2):.2f} MB"
    except (TypeError, ValueError):
        return "N/A"


def format_datetime(value):
    if value is None:
        return "N/A"

    if hasattr(value, "strftime"):
        return value.strftime("%H:%M:%S")

    return str(value)


def task_status(task):
    return str(getattr(task, "state", "UNKNOWN"))


# ==========================================================
# RESOURCE HISTORY
# ==========================================================

def save_history_reading(cpu, memory, disk):

    if any(
        value is None
        for value in (cpu, memory, disk)
    ):
        return

    if "resource_monitor_history" not in st.session_state:
        st.session_state["resource_monitor_history"] = []

    history = st.session_state["resource_monitor_history"]

    history.append({
        "Time": datetime.now(),
        "CPU": float(cpu),
        "RAM": float(memory),
        "Disk Space": float(disk),
    })

    # Retain only the latest 60 readings.
    st.session_state["resource_monitor_history"] = (
        history[-MAX_HISTORY:]
    )


def show_resource_history():

    st.subheader("Resource Usage History")

    history = st.session_state.get(
        "resource_monitor_history",
        [],
    )

    if len(history) < 2:

        st.info(
            "Collecting resource readings. "
            "The graph will appear after the next refresh."
        )
        return

    df = pd.DataFrame(history)

    graph_data = df.melt(
        id_vars="Time",
        value_vars=[
            "CPU",
            "RAM",
            "Disk Space",
        ],
        var_name="Resource",
        value_name="Usage (%)",
    )

    chart = (
        alt.Chart(graph_data)
        .mark_line(
            strokeWidth=2,
            point=True,
        )
        .encode(
            x=alt.X(
                "Time:T",
                title="Time",
                axis=alt.Axis(format="%H:%M:%S"),
            ),
            y=alt.Y(
                "Usage (%):Q",
                title="Usage (%)",
                scale=alt.Scale(
                    domain=[0, 100]
                ),
            ),
            color=alt.Color(
                "Resource:N",
                title="Resource",
                scale=alt.Scale(
                    domain=[
                        "CPU",
                        "RAM",
                        "Disk Space",
                    ],
                    range=[
                        "#60a5fa",
                        "#34d399",
                        "#fbbf24",
                    ],
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Time:T",
                    format="%H:%M:%S",
                ),
                "Resource:N",
                alt.Tooltip(
                    "Usage (%):Q",
                    format=".2f",
                ),
            ],
        )
        .properties(height=300)
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    st.caption(
        "Actual Ubuntu WSL resource readings, "
        "collected approximately every 3 seconds "
        "while this page is active. "
        "Disk Space means filesystem occupancy, "
        "not disk I/O activity."
    )


# ==========================================================
# PROCESS RESOURCE INFORMATION
# ==========================================================

def build_process_rows(tasks, process_monitor):

    rows = []

    visible_tasks = [
        task
        for task in tasks
        if task_status(task) in (
            "RUNNING",
            "COMPLETED",
            "FAILED",
        )
    ]

    for task in visible_tasks:

        status = task_status(task)

        pid = getattr(task, "pid", None)

        cpu_percent = getattr(
            task,
            "cpu_percent",
            None,
        )

        memory_peak = getattr(
            task,
            "memory_peak_bytes",
            None,
        )

        row = {
            "Task ID": getattr(
                task,
                "task_id",
                "N/A",
            ),
            "PID": (
                pid if pid is not None else "N/A"
            ),
            "Process": getattr(
                task,
                "workload_name",
                "N/A",
            ),
            "Status": status,
            "CPU Usage": format_percent(cpu_percent),
            "Peak Memory": format_memory(memory_peak),
            "Execution (s)": None,
            "Completed At": format_datetime(
                getattr(
                    task,
                    "completion_time",
                    None,
                )
            ),
        }

        execution_time = getattr(
            task,
            "execution_time",
            None,
        )

        if execution_time is not None:
            try:
                row["Execution (s)"] = round(
                    float(execution_time),
                    2,
                )
            except (TypeError, ValueError):
                pass

        # Live Linux process inspection is only
        # attempted for currently running tasks.

        if status == "RUNNING" and pid is not None:

            try:

                info = (
                    process_monitor.get_linux_process_info(
                        pid
                    )
                )

                if info and info.get("status") != "NOT FOUND":

                    if info.get("cpu_percent") is not None:
                        row["CPU Usage"] = format_percent(
                            info["cpu_percent"]
                        )

                    if info.get("memory_used") is not None:
                        row["Peak Memory"] = format_memory(
                            info["memory_used"]
                        )

            except Exception:
                # Preserve available task metadata
                # if live process inspection fails.
                pass

        rows.append(row)

    return rows


def show_process_usage(tasks, process_monitor):

    st.subheader("Process Resource Usage")

    rows = build_process_rows(
        tasks,
        process_monitor,
    )

    if not rows:

        st.info(
            "No running or completed workloads "
            "are available in the current session. "
            "Execute a workload to see its entry here."
        )
        return

    df = pd.DataFrame(rows)

    status_order = {
        "RUNNING": 0,
        "COMPLETED": 1,
        "FAILED": 2,
    }

    df["_order"] = df["Status"].map(
        status_order
    ).fillna(3)

    df = df.sort_values(
        "_order",
        kind="stable",
    ).drop(columns=["_order"])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Running processes are inspected live when "
        "their Linux PID is available. Completed "
        "processes show measurements retained by "
        "the workload executor. Missing values "
        "are displayed as N/A."
    )


# ==========================================================
# MAIN RESOURCE MONITOR
# ==========================================================

@st.fragment(run_every=REFRESH_SECONDS)
def show_resource_monitor():

    resource_manager = ResourceManager()
    process_monitor = ProcessMonitor()

    task_manager = st.session_state.get(
        "task_manager"
    )

    # ------------------------------------------------------
    # COLLECT REAL SYSTEM RESOURCES
    # ------------------------------------------------------

    try:

        resources = resource_manager.get_resources()
        monitoring_error = None

    except Exception as error:

        resources = {}
        monitoring_error = str(error)

    cpu = resources.get("cpu")
    memory = resources.get("memory")
    disk = resources.get("disk")

    tasks = (
        task_manager.get_all_tasks()
        if task_manager is not None
        else []
    )

    running_tasks = [
        task
        for task in tasks
        if task_status(task) == "RUNNING"
    ]

    completed_tasks = [
        task
        for task in tasks
        if task_status(task) == "COMPLETED"
    ]

    # Save actual resource readings.
    if not monitoring_error:
        save_history_reading(
            cpu,
            memory,
            disk,
        )

    cpu_threshold = resource_manager.cpu_threshold
    memory_threshold = resource_manager.memory_threshold
    disk_threshold = resource_manager.disk_threshold

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    st.title("⚡ Resource Monitor")

    st.caption(
        "Monitor Ubuntu WSL system resources "
        "and workload execution."
    )

    if monitoring_error:
        st.warning(
            f"Could not collect resource data: "
            f"{monitoring_error}"
        )

    # ------------------------------------------------------
    # SYSTEM RESOURCE SUMMARY
    # ------------------------------------------------------

    st.subheader("System Resource Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "CPU Utilization",
            format_percent(cpu),
        )
        st.caption("System-wide CPU usage")

    with col2:
        st.metric(
            "Memory Usage",
            format_percent(memory),
        )
        st.caption("System-wide RAM usage")

    with col3:
        st.metric(
            "Disk Usage",
            format_percent(disk),
        )
        st.caption("Root filesystem occupancy")

    with col4:
        st.metric(
            "Active Processes",
            len(running_tasks),
        )
        st.caption("Tasks marked RUNNING")

    # ------------------------------------------------------
    # RESOURCE STATUS
    # ------------------------------------------------------

    st.subheader("Resource Status")

    col1, col2 = st.columns(2)

    with col1:

        if cpu is not None:

            cpu_status = (
                "HIGH"
                if cpu >= cpu_threshold
                else "Normal"
            )

            st.write("**CPU Status**")
            st.write(
                f"Current utilization: {cpu:.1f}%"
            )
            st.write(
                f"Status: {cpu_status}"
            )

        else:
            st.info("CPU status unavailable.")

    with col2:

        if memory is not None:

            memory_status = (
                "HIGH"
                if memory >= memory_threshold
                else "Normal"
            )

            available = resources.get(
                "memory_available"
            )

            available_gb = (
                f"{available / (1024 ** 3):.2f} GB"
                if available is not None
                else "N/A"
            )

            st.write("**Memory Status**")
            st.write(
                f"Current usage: {memory:.1f}%"
            )
            st.write(
                f"Available memory: {available_gb}"
            )
            st.write(
                f"Status: {memory_status}"
            )

        else:
            st.info("Memory status unavailable.")

    # ------------------------------------------------------
    # RESOURCE THRESHOLD CHECKER
    # ------------------------------------------------------

    st.subheader("Resource Threshold Checker")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "CPU Threshold",
            f"{cpu_threshold}%",
        )

    with col2:
        st.metric(
            "Memory Threshold",
            f"{memory_threshold}%",
        )

    with col3:
        st.metric(
            "Disk Threshold",
            f"{disk_threshold}%",
        )

    if resources:

        threshold_exceeded = (
            (
                cpu is not None
                and cpu >= cpu_threshold
            )
            or (
                memory is not None
                and memory >= memory_threshold
            )
            or (
                disk is not None
                and disk >= disk_threshold
            )
        )

        if threshold_exceeded:

            st.warning(
                "At least one resource has reached "
                "its configured threshold."
            )

        else:

            st.success(
                "All measured resources are below "
                "their thresholds."
            )

    st.info(
        "These thresholds report resource usage. "
        "The scheduler must separately check resource "
        "availability before accepting new workloads."
    )

    # ------------------------------------------------------
    # ACTUAL RESOURCE HISTORY GRAPH
    # ------------------------------------------------------

    show_resource_history()

    # ------------------------------------------------------
    # RUNNING + COMPLETED WORKLOAD ENTRIES
    # ------------------------------------------------------

    st.subheader("Workload Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Tasks",
            len(tasks),
        )

    with col2:
        st.metric(
            "Running",
            len(running_tasks),
        )

    with col3:
        st.metric(
            "Completed",
            len(completed_tasks),
        )

    show_process_usage(
        tasks,
        process_monitor,
    )

    # ------------------------------------------------------
    # REFRESH
    # ------------------------------------------------------

    if st.button(
        "🔄 Refresh Resource Data",
        use_container_width=True,
    ):
        st.rerun()

    # ------------------------------------------------------
    # HOW MONITORING WORKS
    # ------------------------------------------------------

    with st.expander(
        "How Resource Monitoring Works"
    ):

        st.markdown(
            """
            **1. Workload starts**

            The selected workload is launched
            through the workload executor.

            **2. Process tracking**

            The task record stores the Linux PID
            returned by the WSL runner.

            **3. Resource collection**

            ResourceManager collects actual
            Ubuntu WSL CPU, RAM and disk-space
            measurements.

            **4. Historical monitoring**

            Resource readings are collected
            approximately every three seconds
            while the page is active.

            **5. Completed workload entries**

            Completed tasks remain visible
            while they are retained in the
            shared TaskManager session.

            **6. Threshold checking**

            Current resource usage is compared
            against configured thresholds.
            """
        )


# ==========================================================
# DIRECT EXECUTION
# ==========================================================

if __name__ == "__main__":
    show_resource_monitor()
