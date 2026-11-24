
import time
from datetime import datetime

import pandas as pd
import streamlit as st

from backend.database_manager import DatabaseManager
from backend.resource_manager import ResourceManager


# ============================================================
# RESOURCE MANAGER AND THRESHOLDS
# ============================================================

resource_manager = ResourceManager()

CPU_THRESHOLD = resource_manager.cpu_threshold
MEMORY_THRESHOLD = resource_manager.memory_threshold
DISK_THRESHOLD = resource_manager.disk_threshold


# ============================================================
# COLLECT UBUNTU WSL RESOURCE DATA
# ============================================================

def collect_resource_data():

    manager = ResourceManager()

    resources = manager.get_resources()

    cpu_percent = float(resources["cpu"])
    memory_percent = float(resources["memory"])
    disk_percent = float(resources["disk"])

    return cpu_percent, memory_percent, disk_percent


# ============================================================
# SAVE RESOURCE DATA TO MYSQL
# ============================================================

def save_resource_data(cpu, memory, disk):

    db = DatabaseManager()

    try:

        db.save_resource_history(
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
        )

    finally:

        db.close()


# ============================================================
# LOAD DATABASE DATA
# ============================================================

def load_data():

    db = DatabaseManager()

    try:

        start_time = time.perf_counter()

        resources = db.get_resource_history(
            limit=100
        )

        resource_query_time_ms = (
            time.perf_counter() - start_time
        ) * 1000

        executions = db.get_execution_history()

        return (
            resources,
            executions,
            resource_query_time_ms,
        )

    finally:

        db.close()


# ============================================================
# BOTTLENECK ANALYSIS
# ============================================================

def analyse_bottleneck(cpu, memory, disk):

    resource_values = {
        "CPU": (
            cpu,
            CPU_THRESHOLD,
        ),
        "Memory": (
            memory,
            MEMORY_THRESHOLD,
        ),
        "Disk Space": (
            disk,
            DISK_THRESHOLD,
        ),
    }

    overloaded = []

    for resource_name, (
        value,
        threshold,
    ) in resource_values.items():

        if value is not None and value >= threshold:

            overloaded.append(resource_name)

    if overloaded:

        return (
            "Possible resource pressure detected: "
            + ", ".join(overloaded),
            overloaded,
        )

    available_values = [
        value
        for value, _ in resource_values.values()
        if value is not None
    ]

    if not available_values:

        return (
            "No resource readings are available.",
            [],
        )

    return (
        "No configured resource threshold "
        "has been exceeded.",
        [],
    )


# ============================================================
# FORMAT RESOURCE VALUES
# ============================================================

def format_percent(value):

    if value is None:
        return "N/A"

    return f"{float(value):.1f}%"


# ============================================================
# COLLECT AND SAVE CURRENT UBUNTU MEASUREMENTS
# ============================================================

def refresh_current_resources():

    cpu, memory, disk = collect_resource_data()

    current_reading = {
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "timestamp": datetime.now(),
    }

    # Keep the latest confirmed Ubuntu reading.
    st.session_state[
        "bottleneck_current_reading"
    ] = current_reading

    # Save the same measurements to MySQL.
    save_resource_data(
        cpu,
        memory,
        disk,
    )

    return current_reading


# ============================================================
# CURRENT SYSTEM ANALYSIS
# ============================================================

def show_current_analysis(
    current_reading,
    db_read_time_ms,
):

    st.header("Current System Analysis")

    if current_reading is None:

        st.info(
            "No current Ubuntu readings available. "
            "Click Refresh Monitoring Data."
        )

        return

    cpu = current_reading["cpu"]
    memory = current_reading["memory"]
    disk = current_reading["disk"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "CPU Utilization",
        format_percent(cpu),
    )

    col2.metric(
        "Memory Utilization",
        format_percent(memory),
    )

    col3.metric(
        "Disk Space Used",
        format_percent(disk),
    )

    col4.metric(
        "DB Read Time",
        (
            f"{db_read_time_ms:.2f} ms"
            if db_read_time_ms is not None
            else "N/A"
        ),
    )

    st.caption(
        "Measurement Source: Ubuntu WSL"
    )

    st.caption(
        "Last collected reading: "
        + current_reading[
            "timestamp"
        ].strftime("%Y-%m-%d %H:%M:%S")
    )


# ============================================================
# BOTTLENECK RESULT
# ============================================================

def show_bottleneck_result(
    current_reading,
    analysis_requested,
):

    st.header("Bottleneck Result")

    if not analysis_requested:

        st.info(
            "Click Run Bottleneck Analysis "
            "to evaluate current Ubuntu resources."
        )

        return

    if current_reading is None:

        st.warning(
            "Collect resource measurements "
            "before running analysis."
        )

        return

    cpu = current_reading["cpu"]
    memory = current_reading["memory"]
    disk = current_reading["disk"]

    result, overloaded = analyse_bottleneck(
        cpu,
        memory,
        disk,
    )

    if overloaded:

        st.warning(result)

        st.write(
            "Resources exceeding their configured "
            "thresholds: "
            + ", ".join(overloaded)
        )

        st.write(
            "Review resource history and workload "
            "execution records before concluding "
            "that a resource is the actual bottleneck."
        )

    else:

        st.success(result)

    # --------------------------------------------------------
    # RESOURCE COMPARISON
    # --------------------------------------------------------

    comparison = pd.DataFrame({
        "Resource": [
            "CPU",
            "Memory",
            "Disk Space",
        ],
        "Current Usage": [
            format_percent(cpu),
            format_percent(memory),
            format_percent(disk),
        ],
        "Threshold": [
            f"{CPU_THRESHOLD}%",
            f"{MEMORY_THRESHOLD}%",
            f"{DISK_THRESHOLD}%",
        ],
        "Status": [
            (
                "HIGH"
                if cpu >= CPU_THRESHOLD
                else "Normal"
            ),
            (
                "HIGH"
                if memory >= MEMORY_THRESHOLD
                else "Normal"
            ),
            (
                "HIGH"
                if disk >= DISK_THRESHOLD
                else "Normal"
            ),
        ],
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# RESOURCE HISTORY
# ============================================================

def show_resource_history(resources):

    st.header("Resource History")

    if not resources:

        st.info(
            "Resource history will appear "
            "after collecting measurements."
        )

        return

    resource_df = pd.DataFrame(resources)

    expected_columns = [
        "recorded_at",
        "cpu_percent",
        "memory_percent",
        "disk_percent",
    ]

    available_columns = [
        column
        for column in expected_columns
        if column in resource_df.columns
    ]

    if not available_columns:

        st.info(
            "Resource history columns are unavailable."
        )

        return

    # Previous Windows readings may still exist
    # in the resource_history table.

    st.caption(
        "Historical records are retrieved from MySQL. "
        "Older records may contain Windows measurements "
        "collected before the Ubuntu monitoring update."
    )

    display_df = resource_df[
        available_columns
    ].copy()

    display_df = display_df.rename(
        columns={
            "recorded_at": "Time",
            "cpu_percent": "CPU (%)",
            "memory_percent": "RAM (%)",
            "disk_percent": "Disk Space (%)",
        }
    )

    for column in [
        "CPU (%)",
        "RAM (%)",
        "Disk Space (%)",
    ]:

        if column in display_df.columns:

            display_df[column] = pd.to_numeric(
                display_df[column],
                errors="coerce",
            ).round(2)

    with st.expander("View Saved Resource Records"):

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # SIMPLE RESOURCE HISTORY GRAPH
    # --------------------------------------------------------

    if "Time" not in display_df.columns:
        return

    chart_df = display_df.copy()

    chart_df["Time"] = pd.to_datetime(
        chart_df["Time"],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=["Time"]
    )

    chart_df = chart_df.sort_values("Time")

    chart_columns = [
        column
        for column in [
            "CPU (%)",
            "RAM (%)",
            "Disk Space (%)",
        ]
        if column in chart_df.columns
    ]

    if chart_columns and not chart_df.empty:

        st.subheader("Saved Resource Usage Trend")

        st.line_chart(
            chart_df.set_index("Time")[
                chart_columns
            ]
        )

        st.caption(
            "Disk Space represents filesystem occupancy, "
            "not disk read/write activity."
        )


# ============================================================
# WORKLOAD EXECUTION HISTORY
# ============================================================

def show_workload_analysis(executions):

    st.header("Workload Bottleneck Analysis")

    if not executions:

        st.info(
            "No execution-history records "
            "are available yet."
        )

        return

    execution_df = pd.DataFrame(executions)

    expected_columns = [
        "task_id",
        "pid",
        "execution_time_seconds",
        "cpu_time_seconds",
        "cpu_percent",
        "peak_memory_mb",
        "exit_code",
        "result_status",
        "executed_at",
    ]

    display_columns = [
        column
        for column in expected_columns
        if column in execution_df.columns
    ]

    if not display_columns:

        st.info(
            "Execution history columns "
            "are unavailable."
        )

        return

    display_df = execution_df[
        display_columns
    ].copy()

    display_df = display_df.rename(
        columns={
            "task_id": "Task ID",
            "pid": "PID",
            "execution_time_seconds": "Execution (s)",
            "cpu_time_seconds": "CPU Time (s)",
            "cpu_percent": "CPU (%)",
            "peak_memory_mb": "Peak Memory (MB)",
            "exit_code": "Exit Code",
            "result_status": "Status",
            "executed_at": "Executed At",
        }
    )

    numeric_columns = [
        "Execution (s)",
        "CPU Time (s)",
        "CPU (%)",
        "Peak Memory (MB)",
    ]

    for column in numeric_columns:

        if column in display_df.columns:

            display_df[column] = pd.to_numeric(
                display_df[column],
                errors="coerce",
            ).round(2)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # SELECT INDIVIDUAL WORKLOAD
    # --------------------------------------------------------

    if "Task ID" in display_df.columns:

        task_ids = (
            display_df["Task ID"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if task_ids:

            selected_task = st.selectbox(
                "Select Workload",
                task_ids,
                key="bottleneck_selected_task",
            )

            selected_rows = display_df[
                display_df["Task ID"].astype(str)
                == selected_task
            ]

            st.subheader(
                "Selected Workload Details"
            )

            st.dataframe(
                selected_rows,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "These measurements describe "
                "individual recorded workload runs. "
                "Missing measurements are not "
                "treated as zero."
            )


# ============================================================
# DATABASE PERFORMANCE
# ============================================================

def show_database_performance(db_read_time_ms):

    st.header("Database Performance")

    if db_read_time_ms is None:

        st.info(
            "Database retrieval time is unavailable."
        )

        return

    st.metric(
        "Resource History Retrieval Time",
        f"{db_read_time_ms:.2f} ms",
    )

    st.caption(
        "This is the measured time required to retrieve "
        "resource-history records from MySQL. "
        "It does not represent arbitrary SQL query "
        "execution time, active database locks, "
        "or buffer hit ratio."
    )


# ============================================================
# BOTTLENECK DETECTION RULES
# ============================================================

def show_detection_rules():

    st.header("Bottleneck Detection Rules")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "CPU Threshold",
        f"{CPU_THRESHOLD}%",
    )

    col2.metric(
        "Memory Threshold",
        f"{MEMORY_THRESHOLD}%",
    )

    col3.metric(
        "Disk Space Threshold",
        f"{DISK_THRESHOLD}%",
    )

    st.caption(
        "These thresholds are obtained from the same "
        "ResourceManager used by Resource Monitor. "
        "High resource usage indicates possible "
        "resource pressure, but does not alone "
        "prove a performance bottleneck."
    )


# ============================================================
# MAIN BOTTLENECK ANALYSIS PAGE
# ============================================================

def show_bottleneck_analysis():

    st.title("🔍 Bottleneck Analysis")

    st.write(
        "Analyse Ubuntu WSL resource usage "
        "and workload execution records "
        "to identify possible bottlenecks."
    )

    # --------------------------------------------------------
    # ANALYSIS CONTROLS
    # --------------------------------------------------------

    st.header("Analysis Controls")

    col1, col2 = st.columns(2)

    with col1:

        refresh_clicked = st.button(
            "🔄 Refresh Monitoring Data",
            use_container_width=True,
        )

    with col2:

        analyse_clicked = st.button(
            "🔍 Run Bottleneck Analysis",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------------

    if "bottleneck_current_reading" not in st.session_state:

        st.session_state[
            "bottleneck_current_reading"
        ] = None

    if "bottleneck_analysis_requested" not in st.session_state:

        st.session_state[
            "bottleneck_analysis_requested"
        ] = False

    # --------------------------------------------------------
    # COLLECT FRESH UBUNTU RESOURCE MEASUREMENTS
    # --------------------------------------------------------

    if (
        refresh_clicked
        or analyse_clicked
        or st.session_state[
            "bottleneck_current_reading"
        ] is None
    ):

        st.session_state[
            "bottleneck_current_reading"
        ] = None

        st.session_state[
            "bottleneck_analysis_requested"
        ] = False

        try:

            with st.spinner(
                "Collecting Ubuntu WSL measurements..."
            ):

                refresh_current_resources()

            if refresh_clicked:

                st.success(
                    "Ubuntu resource readings "
                    "collected and saved to MySQL."
                )

        except Exception as error:

            st.error(
                f"Resource collection or saving failed: "
                f"{error}"
            )

    if analyse_clicked:

        st.session_state[
            "bottleneck_analysis_requested"
        ] = True

    current_reading = st.session_state[
        "bottleneck_current_reading"
    ]

    # --------------------------------------------------------
    # LOAD MYSQL HISTORY
    # --------------------------------------------------------

    resources = []
    executions = []
    db_read_time_ms = None

    try:

        (
            resources,
            executions,
            db_read_time_ms,
        ) = load_data()

    except Exception as error:

        st.error(
            f"Could not retrieve MySQL history: {error}"
        )

        st.info(
            "Check your MySQL connection and "
            "resource_history and execution_history tables."
        )

    # --------------------------------------------------------
    # CURRENT SYSTEM ANALYSIS
    # --------------------------------------------------------

    show_current_analysis(
        current_reading,
        db_read_time_ms,
    )

    # --------------------------------------------------------
    # BOTTLENECK RESULT
    # --------------------------------------------------------

    show_bottleneck_result(
        current_reading,
        st.session_state[
            "bottleneck_analysis_requested"
        ],
    )

    # --------------------------------------------------------
    # RESOURCE HISTORY
    # --------------------------------------------------------

    show_resource_history(resources)

    # --------------------------------------------------------
    # WORKLOAD EXECUTION HISTORY
    # --------------------------------------------------------

    show_workload_analysis(executions)

    # --------------------------------------------------------
    # DATABASE PERFORMANCE
    # --------------------------------------------------------

    show_database_performance(
        db_read_time_ms
    )

    # --------------------------------------------------------
    # DETECTION THRESHOLDS
    # --------------------------------------------------------

    show_detection_rules()


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    show_bottleneck_analysis()
