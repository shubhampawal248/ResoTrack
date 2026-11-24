
import streamlit as st
import pandas as pd

from backend.database_manager import DatabaseManager


# =============================================================
# FORMAT HELPERS
# =============================================================

def format_value(value, suffix="", decimals=None):

    if value is None or pd.isna(value):
        return "N/A"

    if decimals is not None:
        return f"{float(value):.{decimals}f}{suffix}"

    return f"{value}{suffix}"


def format_datetime(value):

    if value is None or pd.isna(value):
        return "N/A"

    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    return str(value)


def display_workload_type(workload_type, operation=None):

    workload_type = str(workload_type).lower()

    type_map = {
        "python": "Python Program",
        "python program": "Python Program",
        "cpp": "C/C++ Program",
        "c++": "C/C++ Program",
        "c/c++ program": "C/C++ Program",
        "sql": "SQL Query",
        "sql query": "SQL Query",
        "file_upload": "File Upload",
        "file_download": "File Download",
        "file_transfer": "File Transfer",
    }

    if workload_type == "file_transfer":

        if operation in ("File Upload", "File Download"):
            return operation

    return type_map.get(workload_type, workload_type)


# =============================================================
# FETCH PERMANENT MYSQL HISTORY
# =============================================================

def fetch_database_history():

    db = DatabaseManager()

    try:

        workloads = db.get_workloads()

        executions = db.get_execution_history()

        return workloads, executions

    finally:

        db.close()


# =============================================================
# PREPARE WORKLOAD HISTORY
# =============================================================

def prepare_history_records(workloads, executions):

    # Current session information is supplementary.
    # MySQL remains the primary source.

    task_manager = st.session_state.get("task_manager")

    session_tasks = (
        task_manager.get_all_tasks()
        if task_manager else []
    )

    session_task_map = {
        task.task_id: task
        for task in session_tasks
    }

    # Store the latest execution record for each task.
    # This prevents counting one task multiple times.

    latest_executions = {}

    for execution in executions:

        task_id = execution["task_id"]

        existing = latest_executions.get(task_id)

        if (
            existing is None
            or execution["execution_id"]
            > existing["execution_id"]
        ):

            latest_executions[task_id] = execution

    history_records = []

    for workload in workloads:

        task_id = workload["task_id"]

        execution = latest_executions.get(
            task_id, {}
        )

        session_task = session_task_map.get(
            task_id
        )

        state = workload.get("status", "UNKNOWN")

        # -----------------------------------------------------
        # PERMANENT DATABASE INFORMATION
        # -----------------------------------------------------

        execution_time = execution.get(
            "execution_time_seconds"
        )

        cpu_time = execution.get(
            "cpu_time_seconds"
        )

        cpu_percent = execution.get(
            "cpu_percent"
        )

        memory_mb = execution.get(
            "peak_memory_mb"
        )

        pid = execution.get("pid")

        exit_code = execution.get("exit_code")

        submitted_at = workload.get(
            "submitted_at"
        )

        executed_at = execution.get(
            "executed_at"
        )

        # -----------------------------------------------------
        # ADDITIONAL SESSION INFORMATION
        # -----------------------------------------------------

        scheduler = "N/A"

        retry_count = None

        start_time = None

        completion_time = None

        operation = None

        transfer_destination = None

        transferred_bytes = None

        transfer_speed = None

        transfer_time = None

        if session_task is not None:

            scheduler = getattr(
                session_task,
                "scheduler_name",
                None
            ) or "N/A"

            retry_count = getattr(
                session_task,
                "retry_count",
                None
            )

            start_time = getattr(
                session_task,
                "start_time",
                None
            )

            completion_time = getattr(
                session_task,
                "completion_time",
                None
            )

            operation = getattr(
                session_task,
                "operation",
                None
            )

            transfer_destination = getattr(
                session_task,
                "transfer_destination",
                None
            )

            transferred_bytes = getattr(
                session_task,
                "transferred_bytes",
                None
            )

            transfer_speed = getattr(
                session_task,
                "transfer_speed",
                None
            )

            transfer_time = getattr(
                session_task,
                "transfer_time_seconds",
                None
            )

        # -----------------------------------------------------
        # FAILURE AND RECOVERY STATUS
        # -----------------------------------------------------

        if state == "FAILED":

            recovery_status = "Failed"

        elif (
            state == "COMPLETED"
            and retry_count is not None
            and retry_count > 0
        ):

            recovery_status = "Recovered"

        else:

            recovery_status = "N/A"

        workload_type = display_workload_type(
            workload.get("workload_type"),
            operation
        )

        # -----------------------------------------------------
        # CREATE HISTORY RECORD
        # -----------------------------------------------------

        history_records.append({

            "Task ID": task_id,

            "Workload": workload.get(
                "workload_name"
            ),

            "Type": workload_type,

            "Algorithm": scheduler,

            "PID": pid,

            "Priority": workload.get(
                "priority"
            ),

            "Submitted At": submitted_at,

            "Start Time": start_time,

            "Completion Time": completion_time,

            "Execution Recorded At": executed_at,

            "Execution Time": execution_time,

            "CPU Time": cpu_time,

            "CPU Usage": cpu_percent,

            "Memory Used": memory_mb,

            "State": state,

            "Exit Code": exit_code,

            "Retry Count": retry_count,

            "Recovery Status": recovery_status,

            "Transfer Destination": transfer_destination,

            "Transferred Bytes": transferred_bytes,

            "Transfer Speed": transfer_speed,

            "Transfer Time": transfer_time,

        })

    return history_records


# =============================================================
# HTML RENDERING
# =============================================================

def section_title(title):

    st.html(
        f'<div class="section-title">{title}</div>'
    )


def stat_card(label, value, description):

    st.html(f"""
        <div class="stat-card">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-description">
                {description}
            </div>
        </div>
    """)


# =============================================================
# MAIN HISTORY PAGE
# =============================================================

def show_history():

    # =========================================================
    # PAGE STYLING
    # =========================================================

    st.html("""
        <style>

        .history-title {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .history-subtitle {
            color: #9ca3af;
            font-size: 16px;
            margin-bottom: 28px;
        }

        .section-title {
            font-size: 21px;
            font-weight: 600;
            margin-top: 28px;
            margin-bottom: 14px;
        }

        .stat-card {
            background: linear-gradient(
                145deg, #111827, #0f172a
            );
            border: 1px solid #263244;
            border-radius: 14px;
            padding: 20px;
            min-height: 145px;
        }

        .stat-label {
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .stat-value {
            color: #f1f5f9;
            font-size: 29px;
            font-weight: 700;
        }

        .stat-description {
            color: #9ca3af;
            font-size: 12px;
            margin-top: 7px;
        }

        .info-card {
            background: #111827;
            border: 1px solid #263244;
            border-radius: 14px;
            padding: 20px;
            line-height: 1.7;
            color: #d1d5db;
        }

        .failure-card {
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.30);
            border-radius: 14px;
            padding: 20px;
            line-height: 1.7;
            color: #d1d5db;
        }

        .status-note {
            background: #111827;
            border-left: 4px solid #4f46e5;
            padding: 14px 18px;
            border-radius: 8px;
            color: #d1d5db;
            margin-top: 15px;
        }

        </style>
    """)

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.html("""
        <div class="history-title">
            📚 Workload History
        </div>

        <div class="history-subtitle">
            Review permanently stored workloads,
            execution results, runtime performance
            and recovery information.
        </div>
    """)

    # =========================================================
    # REFRESH HISTORY
    # =========================================================

    if st.button(
        "🔄 Refresh History",
        width="stretch",
        key="refresh_workload_history"
    ):

        st.rerun()

    # =========================================================
    # FETCH DATA FROM MYSQL
    # =========================================================

    try:

        workloads, executions = fetch_database_history()

    except Exception as error:

        st.error(
            f"Could not retrieve MySQL history: {error}"
        )

        return

    history_records = prepare_history_records(
        workloads,
        executions
    )

    history_df = pd.DataFrame(
        history_records
    )

    st.success(
        f"Hgit statusistory loaded successfully. "
        
    )

    # =========================================================
    # EXECUTION OVERVIEW
    # =========================================================

    section_title("Execution Overview")

    completed_count = 0

    failed_count = 0

    retry_attempts = "N/A"

    avg_execution = "N/A"

    avg_cpu = "N/A"

    if not history_df.empty:

        completed_df = history_df[
            history_df["State"] == "COMPLETED"
        ]

        failed_df = history_df[
            history_df["State"] == "FAILED"
        ]

        completed_count = len(completed_df)

        failed_count = len(failed_df)

        # Calculate average execution time using saved data.

        execution_samples = pd.to_numeric(
            completed_df["Execution Time"],
            errors="coerce"
        ).dropna()

        if not execution_samples.empty:

            avg_execution = (
                f"{execution_samples.mean():.2f} s"
            )

        # Calculate average CPU usage using saved data.

        cpu_samples = pd.to_numeric(
            completed_df["CPU Usage"],
            errors="coerce"
        ).dropna()

        if not cpu_samples.empty:

            avg_cpu = (
                f"{cpu_samples.mean():.1f}%"
            )

        # Retry counts are not permanently saved.

        retry_samples = pd.to_numeric(
            history_df["Retry Count"],
            errors="coerce"
        ).dropna()

        if not retry_samples.empty:

            retry_attempts = int(
                retry_samples.sum()
            )

    stats = [

        (
            "COMPLETED TASKS",
            completed_count,
            "Completed workloads in MySQL"
        ),

        (
            "FAILED TASKS",
            failed_count,
            "Failed workloads in MySQL"
        ),

        (
            "RETRY ATTEMPTS",
            retry_attempts,
            "Current session records only"
        ),

        (
            "AVG EXECUTION",
            avg_execution,
            "Completed tasks with measurements"
        ),

        (
            "AVG CPU USAGE",
            avg_cpu,
            "Completed tasks with measurements"
        ),

    ]

    columns = st.columns(5)

    for column, stat in zip(columns, stats):

        label, value, description = stat

        with column:

            stat_card(
                label,
                value,
                description
            )

    # =========================================================
    # FILTER EXECUTION HISTORY
    # =========================================================

    section_title("Filter Execution History")

    type_options = ["All"]

    algorithm_options = ["All"]

    if not history_df.empty:

        type_options += sorted(
            history_df["Type"]
            .dropna()
            .unique()
            .tolist()
        )

        algorithm_options += sorted(
            history_df["Algorithm"]
            .dropna()
            .unique()
            .tolist()
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        workload_type = st.selectbox(
            "Workload Type",
            type_options,
            key="history_type_filter"
        )

    with col2:

        algorithm = st.selectbox(
            "Algorithm",
            algorithm_options,
            key="history_algorithm_filter"
        )

    with col3:

        state = st.selectbox(
            "State",
            [
                "All",
                "READY",
                "RUNNING",
                "COMPLETED",
                "FAILED"
            ],
            key="history_state_filter"
        )

    with col4:

        search_task = st.text_input(
            "Search Task",
            placeholder="Task ID or workload name",
            key="history_search_filter"
        )

    filtered_df = history_df.copy()

    if not filtered_df.empty:

        if workload_type != "All":

            filtered_df = filtered_df[
                filtered_df["Type"] == workload_type
            ]

        if algorithm != "All":

            filtered_df = filtered_df[
                filtered_df["Algorithm"] == algorithm
            ]

        if state != "All":

            filtered_df = filtered_df[
                filtered_df["State"] == state
            ]

        if search_task.strip():

            query = search_task.strip()

            mask = (

                filtered_df["Task ID"]
                .astype(str)
                .str.contains(
                    query,
                    case=False,
                    na=False,
                    regex=False
                )

                |

                filtered_df["Workload"]
                .astype(str)
                .str.contains(
                    query,
                    case=False,
                    na=False,
                    regex=False
                )

            )

            filtered_df = filtered_df[mask]

    # =========================================================
    # EXECUTION RECORDS
    # =========================================================

    section_title("Execution Records")

    if filtered_df.empty:

        st.info(
            "No matching workload records found."
        )

    else:

        display_df = filtered_df.copy()

        display_df["Execution Time"] = (
            display_df["Execution Time"].apply(
                lambda value: format_value(
                    value, " s", 3
                )
            )
        )

        display_df["CPU Time"] = (
            display_df["CPU Time"].apply(
                lambda value: format_value(
                    value, " s", 3
                )
            )
        )

        display_df["CPU Usage"] = (
            display_df["CPU Usage"].apply(
                lambda value: format_value(
                    value, "%", 2
                )
            )
        )

        display_df["Memory Used"] = (
            display_df["Memory Used"].apply(
                lambda value: format_value(
                    value, " MB", 2
                )
            )
        )

        date_columns = [

            "Submitted At",

            "Start Time",

            "Completion Time",

            "Execution Recorded At"

        ]

        for column in date_columns:

            display_df[column] = (
                display_df[column].apply(
                    format_datetime
                )
            )

        for column in [
            "PID", "Exit Code", "Retry Count"
        ]:

            display_df[column] = (
                display_df[column].apply(
                    lambda value: format_value(
                        value, "", 0
                    )
                )
            )

        table_columns = [

            "Task ID",

            "Workload",

            "Type",

            "Algorithm",

            "PID",

            "Priority",

            "State",

            "Execution Time",

            "CPU Time",

            "CPU Usage",

            "Memory Used",

            "Exit Code",

            "Submitted At",

            "Start Time",

            "Completion Time",

            "Execution Recorded At",

            "Retry Count",

            "Recovery Status"

        ]

        st.dataframe(

            display_df[table_columns],

            width="stretch",

            hide_index=True

        )

        st.caption(
            f"Showing {len(filtered_df)} of "
            f"{len(history_df)} saved workloads."
        )

    # =========================================================
    # FAILURE AND RECOVERY HISTORY
    # =========================================================

    section_title("⚠️ Failure & Recovery History")

    st.html("""
        <div class="failure-card">

            <strong>Failure Detection</strong><br>

            Failed workload states and exit codes
            are retrieved from MySQL.

            <br><br>

            <strong>Recovery Information</strong><br>

            Retry counts are displayed when they
            are available in the current session.
            Historical retry counts are not yet
            permanently stored.

        </div>
    """)

    if not history_df.empty:

        retry_values = pd.to_numeric(
            history_df["Retry Count"],
            errors="coerce"
        ).fillna(0)

        failure_df = history_df[

            (history_df["State"] == "FAILED")

            |

            (retry_values > 0)

        ].copy()

        if failure_df.empty:

            st.info(
                "No failed workloads or known retries found."
            )

        else:

            failure_columns = [

                "Task ID",

                "Workload",

                "PID",

                "State",

                "Exit Code",

                "Retry Count",

                "Recovery Status",

                "Execution Recorded At"

            ]

            failure_df["Retry Count"] = (
                failure_df["Retry Count"].apply(
                    lambda value: format_value(
                        value, "", 0
                    )
                )
            )

            st.dataframe(

                failure_df[failure_columns],

                width="stretch",

                hide_index=True

            )

    else:

        st.info(
            "No failure records available."
        )

    # =========================================================
    # SELECTED WORKLOAD DETAILS
    # =========================================================

    section_title("Workload Details")

    if not history_df.empty:

        task_ids = history_df[
            "Task ID"
        ].tolist()

        selected_task_id = st.selectbox(

            "Select a workload",

            task_ids,

            key="history_selected_workload"

        )

        selected_record = history_df[

            history_df["Task ID"]
            == selected_task_id

        ].iloc[0]

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                "**Task ID:**",
                selected_record["Task ID"]
            )

            st.write(
                "**Workload:**",
                selected_record["Workload"]
            )

            st.write(
                "**Workload Type:**",
                selected_record["Type"]
            )

            st.write(
                "**Scheduling Algorithm:**",
                selected_record["Algorithm"]
            )

            st.write(
                "**Priority:**",
                selected_record["Priority"]
            )

            st.write(
                "**State:**",
                selected_record["State"]
            )

            st.write(
                "**PID:**",
                format_value(
                    selected_record["PID"],
                    "", 0
                )
            )

        with col2:

            st.write(
                "**Execution Time:**",
                format_value(
                    selected_record["Execution Time"],
                    " s", 3
                )
            )

            st.write(
                "**CPU Time:**",
                format_value(
                    selected_record["CPU Time"],
                    " s", 3
                )
            )

            st.write(
                "**CPU Usage:**",
                format_value(
                    selected_record["CPU Usage"],
                    "%", 2
                )
            )

            st.write(
                "**Peak Memory:**",
                format_value(
                    selected_record["Memory Used"],
                    " MB", 2
                )
            )

            st.write(
                "**Exit Code:**",
                format_value(
                    selected_record["Exit Code"],
                    "", 0
                )
            )

            st.write(
                "**Submitted At:**",
                format_datetime(
                    selected_record["Submitted At"]
                )
            )

            st.write(
                "**Execution Recorded At:**",
                format_datetime(
                    selected_record[
                        "Execution Recorded At"
                    ]
                )
            )

        # -----------------------------------------------------
        # ALL SAVED EXECUTION ATTEMPTS
        # -----------------------------------------------------

        selected_executions = [

            execution

            for execution in executions

            if execution["task_id"]
            == selected_task_id

        ]

        with st.expander(
            "View Saved Execution Records"
        ):

            if selected_executions:

                st.dataframe(

                    pd.DataFrame(
                        selected_executions
                    ),

                    width="stretch",

                    hide_index=True

                )

            else:

                st.info(
                    "No execution measurements have "
                    "been saved for this workload."
                )

        # -----------------------------------------------------
        # FILE TRANSFER DETAILS
        # -----------------------------------------------------

        if selected_record["Type"] in (

            "File Transfer",

            "File Upload",

            "File Download"

        ):

            section_title("File Transfer Details")

            transfer_speed = selected_record[
                "Transfer Speed"
            ]

            if (
                transfer_speed is not None
                and not pd.isna(transfer_speed)
            ):

                transfer_speed = (
                    float(transfer_speed) / 1024
                )

            else:

                transfer_speed = None

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Destination:**",
                    format_value(
                        selected_record[
                            "Transfer Destination"
                        ]
                    )
                )

                st.write(
                    "**Transferred Bytes:**",
                    format_value(
                        selected_record[
                            "Transferred Bytes"
                        ],
                        " bytes", 0
                    )
                )

            with col2:

                st.write(
                    "**Transfer Time:**",
                    format_value(
                        selected_record[
                            "Transfer Time"
                        ],
                        " s", 6
                    )
                )

                st.write(
                    "**Transfer Speed:**",
                    format_value(
                        transfer_speed,
                        " KB/s", 2
                    )
                )

            st.caption(
                "Transfer-specific measurements are "
                "currently available only during "
                "the session that executed the transfer."
            )

    else:

        st.info(
            "No saved workloads available."
        )

    # =========================================================
    # STORED RUNTIME INFORMATION
    # =========================================================

    section_title("Stored Runtime Information")

    col1, col2 = st.columns(2)

    with col1:

        st.html("""
            <div class="info-card">

                <strong>
                    Permanent MySQL Information
                </strong>

                <br><br>

                • Task ID and workload name<br>

                • Workload type and priority<br>

                • Process ID and execution status<br>

                • Submission and execution record time<br>

                • Execution time and CPU time<br>

                • CPU usage and peak memory<br>

                • Exit code

            </div>
        """)

    with col2:

        st.html("""
            <div class="info-card">

                <strong>
                    Additional Session Information
                </strong>

                <br><br>

                • Scheduling algorithm<br>

                • Actual start and completion time<br>

                • Retry count and recovery status<br>

                • File transfer destination<br>

                • Transfer duration and speed<br>

                • Transferred bytes

                <br><br>

                These additional fields are not yet
                permanently stored in MySQL.

            </div>
        """)

    # =========================================================
    # ADAPTIVE SCHEDULING INFORMATION
    # =========================================================

    section_title(
        "🧠 Historical Data for Adaptive Scheduling"
    )

    st.html("""
        <div class="info-card">

            <strong>
                How History Supports Adaptive Scheduling
            </strong>

            <br><br>

            SysNexa retrieves historical workload
            information from MySQL.

            Previous execution durations, CPU usage
            and memory measurements can help evaluate
            workload performance and support future
            adaptive scheduling decisions.

            <br><br>

            Historical records remain available
            after restarting the application.

        </div>
    """)

    # =========================================================
    # DEVELOPMENT STATUS
    # =========================================================

    st.html("""
        <div class="status-note">

            <strong>Storage Status:</strong><br>

            Workload History is connected to the
            permanent MySQL database.

            Current session information is used
            only for additional fields that are
            not yet stored in the database.

            Missing historical measurements are
            displayed as N/A instead of fabricated values.

        </div>
    """)


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    show_history()
