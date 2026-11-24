
import streamlit as st

from datetime import datetime
from urllib.parse import urlparse
from textwrap import dedent
from inspect import signature

from backend.database_manager import DatabaseManager
from backend.task_manager import TaskManager

from backend.file_transfer import (
    MAX_FILE_BYTES,
    ALLOWED_DOWNLOAD_HOSTS,
)


# =============================================================
# HTML RENDERING HELPERS
# =============================================================

def render_html(content):

    st.html(dedent(content).strip())


def section_title(title):

    render_html(
        f'<div class="section-title">{title}</div>'
    )


def category_card(title, description):

    render_html(f"""
        <div class="category-card">
            <div class="category-title">{title}</div>
            <div class="category-description">
                {description}
            </div>
        </div>
    """)


def runtime_card(label, value):

    render_html(f"""
        <div class="runtime-card">
            <div class="runtime-label">{label}</div>
            <div class="runtime-value">{value}</div>
        </div>
    """)


def monitoring_box(title, description):

    render_html(f"""
        <div class="ready-box">
            <div class="monitoring-title">{title}</div>
            <div class="monitoring-description">
                {description}
            </div>
        </div>
    """)


# =============================================================
# SUBMIT WORKLOAD PAGE
# =============================================================

def show_submit_workload():

    # =========================================================
    # SHARED TASK MANAGER
    # =========================================================

    if "task_manager" not in st.session_state:

        st.session_state["task_manager"] = TaskManager()

    task_manager = st.session_state["task_manager"]

    # =========================================================
    # PAGE STYLING
    # =========================================================

    render_html("""
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

        .category-card {
            background: #111827;
            border: 1px solid #273449;
            border-radius: 12px;
            padding: 18px;
            min-height: 135px;
        }

        .category-title {
            color: #f1f5f9;
            font-size: 17px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .category-description {
            color: #9ca3af;
            font-size: 13px;
            line-height: 1.5;
        }

        .runtime-card {
            background: #111827;
            border: 1px solid #273449;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            min-height: 90px;
        }

        .runtime-label {
            color: #9ca3af;
            font-size: 12px;
        }

        .runtime-value {
            color: #f1f5f9;
            font-size: 16px;
            font-weight: 600;
            margin-top: 5px;
        }

        .ready-box {
            background: rgba(59, 130, 246, 0.10);
            border: 1px solid rgba(59, 130, 246, 0.35);
            border-radius: 10px;
            padding: 16px;
            margin-top: 18px;
        }

        .monitoring-title {
            color: #60a5fa;
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .monitoring-description {
            color: #cbd5e1;
            font-size: 13px;
            line-height: 1.6;
        }

        </style>
    """)

    # =========================================================
    # PAGE HEADER
    # =========================================================

    render_html("""
        <div class="page-title">
            Submit Workload
        </div>

        <div class="page-subtitle">
            Add workloads to the READY queue.
            Execution begins only when you run the queue
            from the Scheduler page.
        </div>
    """)

    # =========================================================
    # WORKLOAD CATEGORY
    # =========================================================

    section_title("Select Workload Category")

    col1, col2 = st.columns(2)

    with col1:

        category_card(
            "💻 Program / Query Execution",
            """
            Submit Python, C/C++ or SQL workloads.
            Python and C/C++ programs execute inside
            Ubuntu through the scheduler.
            SQL execution is not connected yet.
            """
        )

    with col2:

        category_card(
            "📁 File Transfer Operation",
            """
            Submit file upload and download workloads.
            Select custom Ubuntu upload destinations
            and monitor actual transfer performance.
            """
        )

    category = st.radio(
        "Workload Category",
        [
            "Program / Query Execution",
            "File Transfer Operation"
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="submit_category",
    )

    # =========================================================
    # WORKLOAD DETAILS
    # =========================================================

    section_title("Workload Details")

    task_name = st.text_input(
        "Workload Name",
        placeholder="Example: Matrix Multiplication",
        key="submit_task_name",
    )

    uploaded_file = None
    filename = ""

    source_code = ""
    sql_query = ""

    operation = ""

    download_url = ""
    download_location = ""
    upload_location = ""

    execution_timeout = 30
    execution_type = ""
    estimated_time = 1.0

    max_file_mb = MAX_FILE_BYTES / (1024 ** 2)

    # =========================================================
    # PROGRAM / QUERY EXECUTION
    # =========================================================

    if category == "Program / Query Execution":

        execution_type = st.selectbox(
            "Execution Type",
            [
                "Python Program",
                "C/C++ Program",
                "SQL Query"
            ],
            key="submit_execution_type",
        )

        # -----------------------------------------------------
        # SQL QUERY
        # -----------------------------------------------------

        if execution_type == "SQL Query":

            st.caption(
                "SQL queries can be submitted to the READY "
                "queue, but SQL execution through the "
                "scheduler is not implemented yet."
            )

            sql_query = st.text_area(
                "SQL Query",
                placeholder="Example: SELECT * FROM workloads;",
                height=150,
                key="submit_sql_query",
            )

        # -----------------------------------------------------
        # PYTHON / C++ PROGRAM
        # -----------------------------------------------------

        else:

            source_language = (
                "python"
                if execution_type == "Python Program"
                else "cpp"
            )

            code_label = (
                "Python Source Code"
                if source_language == "python"
                else "C/C++ Source Code"
            )

            code_placeholder = (
                'print("Hello from SysNexa")'
                if source_language == "python"
                else (
                    '#include <iostream>\n\n'
                    'int main() {\n'
                    '    std::cout << "Hello from SysNexa\\n";\n'
                    '    return 0;\n'
                    '}'
                )
            )

            source_code = st.text_area(
                code_label,
                placeholder=code_placeholder,
                height=260,
                max_chars=100000,
                help=(
                    "The source code is stored with the task "
                    "and executed later by the scheduler."
                ),
                key="submit_source_code",
            )

            st.caption(
                "Your program will not run when submitted. "
                "It remains READY until you execute the queue."
            )

            execution_timeout = st.number_input(
                "Execution timeout (seconds)",
                min_value=1,
                max_value=300,
                value=30,
                step=1,
                help="Maximum permitted execution time.",
                key="submit_execution_timeout",
            )

            estimated_time = st.number_input(
                "Estimated execution time (seconds)",
                min_value=0.1,
                max_value=3600.0,
                value=1.0,
                step=0.5,
                help=(
                    "Used by SJF to determine which "
                    "workload should execute first."
                ),
                key="submit_estimated_time",
            )

    # =========================================================
    # FILE TRANSFER OPERATION
    # =========================================================

    else:

        operation = st.selectbox(
            "Transfer Operation",
            [
                "File Upload",
                "File Download"
            ],
            key="submit_transfer_operation",
        )

        # -----------------------------------------------------
        # FILE UPLOAD
        # -----------------------------------------------------

        if operation == "File Upload":

            uploader_options = {
                "label": "Select File",
                "help": (
                    f"Select a file up to {max_file_mb:g} MB "
                    "to transfer into Ubuntu WSL."
                ),
                "key": "submit_uploaded_file",
            }

            if (
                "max_upload_size"
                in signature(st.file_uploader).parameters
            ):

                uploader_options["max_upload_size"] = max(
                    1,
                    int(max_file_mb)
                )

            uploaded_file = st.file_uploader(
                **uploader_options
            )

            st.caption(
                f"Maximum permitted file size: "
                f"{max_file_mb:g} MB."
            )

            # =================================================
            # CUSTOM UPLOAD DESTINATION
            # =================================================

            destination_option = st.selectbox(
                "Select Upload Destination",
                [
                    "Default Upload Folder",
                    "Documents",
                    "Downloads",
                    "Projects",
                    "Custom Location"
                ],
                key="submit_destination_option",
            )

            destination_map = {

                "Default Upload Folder":
                    "~/sysnexa_transfers/uploads/",

                "Documents":
                    "~/Documents/",

                "Downloads":
                    "~/Downloads/",

                "Projects":
                    "~/Projects/",
            }

            if destination_option == "Custom Location":

                upload_location = st.text_input(
                    "Upload Destination (Ubuntu)",
                    placeholder="~/MyFolder/",
                    help=(
                        "Enter a directory inside your "
                        "Ubuntu home directory."
                    ),
                    key="submit_custom_upload_destination",
                )

            else:

                upload_location = destination_map[
                    destination_option
                ]

                st.text_input(
                    "Upload Destination (Ubuntu)",
                    value=upload_location,
                    disabled=True,
                    key=(
                        "submit_destination_display_"
                        + destination_option
                    ),
                )

            st.caption(
                "The selected directory will be created "
                "automatically if it does not exist."
            )

            # =================================================
            # SELECTED FILE INFORMATION
            # =================================================

            if uploaded_file is not None:

                file_size_bytes = uploaded_file.size

                file_size_kb = (
                    file_size_bytes / 1024
                )

                file_size_mb = (
                    file_size_bytes / (1024 ** 2)
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Selected File",
                        uploaded_file.name
                    )

                with col2:

                    if file_size_mb >= 1:

                        st.metric(
                            "File Size",
                            f"{file_size_mb:.2f} MB"
                        )

                    else:

                        st.metric(
                            "File Size",
                            f"{file_size_kb:.2f} KB"
                        )

                if file_size_bytes > MAX_FILE_BYTES:

                    st.error(
                        f"File exceeds the "
                        f"{max_file_mb:g} MB limit."
                    )

                else:

                    st.success(
                        "File selected successfully."
                    )

                if upload_location.strip():

                    preview_filename = (
                        uploaded_file.name
                        .replace("\\", "/")
                        .split("/")[-1]
                    )

                    expected_destination = (
                        upload_location.strip().rstrip("/")
                        + "/"
                        + preview_filename
                    )

                    st.write("**Expected File Destination:**")

                    st.code(
                        expected_destination,
                        language="text"
                    )

            st.info(
                "The file will be transferred to the selected "
                "Ubuntu directory when the scheduler executes "
                "this workload. Existing files will not be "
                "overwritten."
            )

            st.caption(
                "The selected file is held in the current "
                "Streamlit session until execution."
            )

        # -----------------------------------------------------
        # FILE DOWNLOAD
        # -----------------------------------------------------

        else:

            download_url = st.text_input(
                "Download Source URL",
                placeholder="https://www.w3.org/example.txt",
                help=(
                    "Enter an HTTPS URL from an approved "
                    "download host."
                ),
                key="submit_download_url",
            )

            download_location = (
                "~/sysnexa_transfers/downloads/"
            )

            st.text_input(
                "Save Location (Ubuntu)",
                value=download_location,
                disabled=True,
                key="submit_download_destination",
            )

            st.caption(
                "Approved download hosts: "
                + ", ".join(
                    sorted(ALLOWED_DOWNLOAD_HOSTS)
                )
            )

            st.caption(
                f"Maximum download size: "
                f"{max_file_mb:g} MB."
            )

            st.info(
                "The file will be downloaded inside Ubuntu "
                "when the scheduler executes this workload. "
                "A separate task directory will be created "
                "automatically."
            )

        # -----------------------------------------------------
        # FILE TRANSFER EXECUTION SETTINGS
        # -----------------------------------------------------

        execution_timeout = st.number_input(
            "Transfer timeout (seconds)",
            min_value=1,
            max_value=300,
            value=30,
            step=1,
            help=(
                "Maximum time allowed for the "
                "file-transfer workload."
            ),
            key="submit_transfer_timeout",
        )

        estimated_time = st.number_input(
            "Estimated transfer time (seconds)",
            min_value=0.1,
            max_value=3600.0,
            value=1.0,
            step=0.5,
            help=(
                "Scheduling estimate used by SJF. "
                "Actual transfer duration is measured "
                "automatically during execution."
            ),
            key="submit_transfer_estimated_time",
        )

        monitoring_box(
            "⚙️ Automatic File Transfer Monitoring",
            """
            The system collects actual transferred bytes,
            transfer duration, transfer speed, Linux PID,
            CPU usage, memory usage and execution status
            when the transfer runs.
            """
        )

    # =========================================================
    # SCHEDULING CONFIGURATION
    # =========================================================

    section_title("Scheduling Configuration")

    scheduling_mode = st.radio(
        "Scheduling Mode",
        ["Manual", "Automatic"],
        horizontal=True,
        help=(
            "Manual lets you select an algorithm. "
            "Automatic uses the automatic scheduler."
        ),
        key="submit_scheduling_mode",
    )

    col1, col2 = st.columns(2)

    with col1:

        priority = st.selectbox(
            "Priority",
            [1, 2, 3],
            index=1,
            help="1 = Highest Priority, 3 = Lowest Priority",
            key="submit_priority",
        )

    with col2:

        if scheduling_mode == "Manual":

            scheduler = st.selectbox(
                "Scheduling Algorithm",
                [
                    "FCFS",
                    "SJF",
                    "Priority",
                    "Round Robin",
                    "Adaptive",
                ],
                key="submit_scheduler",
            )

        else:

            scheduler = "Automatic"

            st.text_input(
                "Scheduling Algorithm",
                value="System Selected",
                disabled=True,
                key="submit_automatic_scheduler_display",
            )

    scheduler_description = {

        "FCFS":
            "Tasks are selected according to their arrival order.",

        "SJF":
            "Shorter estimated workloads are preferred.",

        "Priority":
            "Higher-priority workloads are selected first.",

        "Round Robin":
            "True time-sliced execution requires preemption support.",

        "Adaptive":
            "Scheduling decisions depend on the adaptive scheduler.",

        "Automatic":
            "The automatic scheduler chooses an algorithm.",
    }

    st.info(
        scheduler_description[scheduler]
    )

    st.caption(
        "The Scheduler page controls the algorithm actually "
        "used when the execution queue runs."
    )

    # =========================================================
    # FAILURE DETECTION AND RECOVERY
    # =========================================================

    section_title("Failure Detection & Recovery")

    col1, col2 = st.columns(2)

    with col1:

        automatic_retry = st.radio(
            "Automatic Retry",
            ["Yes", "No"],
            horizontal=True,
            help=(
                "Retry configuration is stored with the task. "
                "Automatic retry execution requires scheduler support."
            ),
            key="submit_automatic_retry",
        )

    with col2:

        max_retries = 2

        st.text_input(
            "Maximum Retries",
            value=str(max_retries),
            disabled=True,
            help="Configured maximum retry attempts.",
            key="submit_max_retries_display",
        )

    if automatic_retry == "Yes":

        st.info(
            "Retry is enabled in the task configuration. "
            "The scheduler must implement retry handling "
            "for it to take effect."
        )

    else:

        st.info(
            "Failed workloads will be recorded as FAILED "
            "by the execution handler."
        )

    # =========================================================
    # RUNTIME INFORMATION
    # =========================================================

    section_title("Runtime Information")

    col1, col2, col3 = st.columns(3)

    with col1:

        runtime_card(
            "Arrival Time",
            "Generated automatically"
        )

    with col2:

        runtime_card(
            "Process ID",
            "Generated at execution"
        )

    with col3:

        runtime_card(
            "Initial State",
            "READY"
        )

    monitoring_box(
        "⚙️ Automatic Runtime Monitoring",
        """
        PID, execution time, CPU usage, memory usage,
        start time and completion time are collected
        when supported workloads actually execute.
        These runtime measurements are not entered manually.
        """
    )

    # =========================================================
    # SUBMIT TO READY QUEUE
    # =========================================================

    st.write("")

    submit = st.button(
        "Add Workload to READY Queue",
        width="stretch",
        type="primary",
        key="submit_to_ready_queue",
    )

    if not submit:

        return

    # =========================================================
    # WORKLOAD NAME VALIDATION
    # =========================================================

    if not task_name.strip():

        st.warning(
            "Please enter a workload name."
        )

        return

    # =========================================================
    # PROGRAM VALIDATION
    # =========================================================

    if category == "Program / Query Execution":

        if execution_type in (
            "Python Program",
            "C/C++ Program"
        ):

            if not source_code.strip():

                st.warning(
                    "Please paste the program source code."
                )

                return

            workload_type = (
                "python"
                if execution_type == "Python Program"
                else "cpp"
            )

        else:

            if not sql_query.strip():

                st.warning(
                    "Please enter an SQL query."
                )

                return

            workload_type = "sql"

    # =========================================================
    # FILE TRANSFER VALIDATION
    # =========================================================

    else:

        workload_type = "file_transfer"

        # -----------------------------------------------------
        # VALIDATE FILE UPLOAD
        # -----------------------------------------------------

        if operation == "File Upload":

            if uploaded_file is None:

                st.warning(
                    "Please select a file to upload."
                )

                return

            if uploaded_file.size > MAX_FILE_BYTES:

                st.warning(
                    f"Maximum permitted file size "
                    f"is {max_file_mb:g} MB."
                )

                return

            upload_location = upload_location.strip()

            if not upload_location:

                st.warning(
                    "Please enter an upload destination."
                )

                return

            if not upload_location.startswith(
                ("~/", "/home/")
            ):

                st.warning(
                    "Enter a destination inside your "
                    "Ubuntu home directory."
                )

                return

            if ".." in upload_location.split("/"):

                st.warning(
                    "Parent-directory traversal is not allowed."
                )

                return

            filename = (
                uploaded_file.name
                .replace("\\", "/")
                .split("/")[-1]
            )

            if filename in ("", ".", ".."):

                st.warning(
                    "Invalid uploaded filename."
                )

                return

        # -----------------------------------------------------
        # VALIDATE FILE DOWNLOAD
        # -----------------------------------------------------

        elif operation == "File Download":

            download_url = download_url.strip()

            if not download_url:

                st.warning(
                    "Please enter the download source URL."
                )

                return

            try:

                parsed_url = urlparse(
                    download_url
                )

                valid_url = (
                    parsed_url.scheme == "https"
                    and parsed_url.hostname
                    in ALLOWED_DOWNLOAD_HOSTS
                    and parsed_url.username is None
                    and parsed_url.password is None
                    and parsed_url.port in (None, 443)
                )

            except ValueError:

                valid_url = False

            if not valid_url:

                st.warning(
                    "Enter a valid HTTPS URL from an "
                    "approved download host."
                )

                return

        else:

            st.warning(
                "Unsupported file-transfer operation."
            )

            return

    # =========================================================
    # CREATE AND CONFIGURE TASK
    # =========================================================

    task_id = (
        "TASK-"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        )
    )

    task = None

    try:

        task = task_manager.create_task(
            task_id=task_id,
            workload_name=task_name.strip(),
            workload_type=workload_type,
            priority=priority,
            estimated_time=float(estimated_time),
        )

        # -----------------------------------------------------
        # SCHEDULING CONFIGURATION
        # -----------------------------------------------------

        task.scheduling_mode = scheduling_mode

        task.scheduler_name = scheduler

        task.automatic_retry = (
            automatic_retry == "Yes"
        )

        task.max_retries = max_retries

        # -----------------------------------------------------
        # WORKLOAD CONFIGURATION
        # -----------------------------------------------------

        task.source_code = source_code

        task.sql_query = sql_query

        task.execution_timeout = int(
            execution_timeout
        )

        task.operation = operation

        task.download_url = download_url

        task.download_location = download_location

        task.upload_location = upload_location

        # -----------------------------------------------------
        # FILE UPLOAD CONFIGURATION
        # -----------------------------------------------------

        if (
            workload_type == "file_transfer"
            and operation == "File Upload"
            and uploaded_file is not None
        ):

            task.uploaded_filename = filename

            task.uploaded_bytes = (
                uploaded_file.getvalue()
            )

            task.uploaded_file_size = len(
                task.uploaded_bytes
            )

        # -----------------------------------------------------
        # FILE TRANSFER RUNTIME ATTRIBUTES
        # -----------------------------------------------------

        if workload_type == "file_transfer":

            task.transferred_bytes = None

            task.transfer_time_seconds = None

            task.transfer_speed = None

            task.transfer_destination = None

            task.transfer_metrics_error = None

        # -----------------------------------------------------
        # SAVE WORKLOAD TO MYSQL
        # -----------------------------------------------------

        db = DatabaseManager()

        try:

            db.insert_workload(task)

        finally:

            db.close()

        st.session_state[
            "last_submitted_task_id"
        ] = task_id

    except Exception as error:

        if (
            task is not None
            and task in task_manager.tasks
        ):

            task_manager.tasks.remove(task)

        st.error(
            f"Could not create or save workload: {error}"
        )

        return

    # =========================================================
    # CONFIRM QUEUE SUBMISSION
    # =========================================================

    st.success(
        f"Workload '{task.workload_name}' "
        "added to the READY queue."
    )

    st.success(
        "Workload record saved to MySQL successfully!"
    )

    # =========================================================
    # WORKLOAD SUMMARY
    # =========================================================

    section_title("Workload Summary")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "**Task ID:**",
            task.task_id
        )

        st.write(
            "**Category:**",
            category
        )

        st.write(
            "**Workload:**",
            task.workload_name
        )

        st.write(
            "**Priority:**",
            task.priority
        )

        st.write(
            "**Scheduling Mode:**",
            scheduling_mode
        )

    with col2:

        st.write(
            "**Scheduler:**",
            scheduler
        )

        if category == "Program / Query Execution":

            st.write(
                "**Execution Type:**",
                execution_type
            )

        else:

            st.write(
                "**Operation:**",
                operation
            )

        st.write(
            "**Automatic Retry:**",
            automatic_retry
        )

        st.write(
            "**Maximum Retries:**",
            max_retries
        )

        st.write(
            "**State:**",
            task.state
        )

    # =========================================================
    # FILE TRANSFER SUMMARY
    # =========================================================

    if workload_type == "file_transfer":

        section_title("File Transfer Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                "**Transfer Operation:**",
                operation
            )

            st.write(
                "**Execution Timeout:**",
                f"{execution_timeout} seconds"
            )

            st.write(
                "**Estimated Time:**",
                f"{estimated_time} seconds"
            )

        with col2:

            if operation == "File Upload":

                st.write(
                    "**Filename:**",
                    task.uploaded_filename
                )

                st.write(
                    "**File Size:**",
                    f"{task.uploaded_file_size / 1024:.2f} KB"
                )

                st.write(
                    "**Destination:**",
                    upload_location.rstrip("/")
                    + "/"
                    + task.uploaded_filename
                )

            else:

                st.write(
                    "**Download URL:**",
                    download_url
                )

                st.write(
                    "**Destination:**",
                    download_location + task_id + "/"
                )

        st.info(
            "Actual transferred bytes, transfer duration, "
            "transfer speed, CPU usage and memory usage "
            "will be available after execution."
        )

    # =========================================================
    # FINAL INFORMATION
    # =========================================================

    if workload_type == "sql":

        st.warning(
            "SQL workload saved, but SQL execution "
            "through the scheduler is not implemented yet."
        )

    else:

        st.info(
            "The workload has been submitted but has not "
            "been executed. Open the Scheduler page, "
            "select the scheduling algorithm and click "
            "'Execute Queue'."
        )

    st.write(
        "**Current READY queue size:**",
        len(task_manager.get_ready_tasks()),
    )


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    show_submit_workload()
