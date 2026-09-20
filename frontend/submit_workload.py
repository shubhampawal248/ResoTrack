import streamlit as st
from datetime import datetime


def show_submit_workload():

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

    .category-card {
        background: #111827;
        border: 1px solid #273449;
        border-radius: 12px;
        padding: 18px;
        min-height: 120px;
    }

    .category-title {
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
    }

    .runtime-label {
        color: #9ca3af;
        font-size: 12px;
    }

    .runtime-value {
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

    </style>
    """, unsafe_allow_html=True)


    # ==========================================
    # PAGE HEADER
    # ==========================================
    st.markdown(
        '<div class="page-title">Submit Workload</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Submit and configure a workload for runtime scheduling and execution.'
        '</div>',
        unsafe_allow_html=True
    )


    # ==========================================
    # WORKLOAD CATEGORY
    # ==========================================
    st.markdown(
        '<div class="section-title">Select Workload Category</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="category-card">
            <div class="category-title">
                💻 Program / Query Execution
            </div>
            <div class="category-description">
                Execute Python, C/C++ programs or SQL queries
                through the runtime workload manager.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="category-card">
            <div class="category-title">
                📁 File Transfer Operation
            </div>
            <div class="category-description">
                Manage file upload and download operations
                as schedulable workloads.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    category = st.radio(
        "Workload Category",
        [
            "Program / Query Execution",
            "File Transfer Operation"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )


    # ==========================================
    # WORKLOAD DETAILS
    # ==========================================
    st.markdown(
        '<div class="section-title">Workload Details</div>',
        unsafe_allow_html=True
    )

    task_name = st.text_input(
        "Workload Name",
        placeholder="Example: Matrix Multiplication"
    )


    # ==========================================
    # DEFAULT VALUES
    # ==========================================
    uploaded_file = None
    sql_query = ""
    operation = ""
    download_url = ""
    download_location = ""


    # ==========================================
    # PROGRAM / QUERY EXECUTION
    # ==========================================
    if category == "Program / Query Execution":

        execution_type = st.selectbox(
            "Execution Type",
            [
                "Python Program",
                "C/C++ Program",
                "SQL Query"
            ]
        )

        if execution_type == "SQL Query":

            sql_query = st.text_area(
                "SQL Query",
                placeholder="Example: SELECT * FROM processes;",
                height=150
            )

        else:

            if execution_type == "Python Program":
                file_types = ["py"]
            else:
                file_types = ["c", "cpp", "cc"]

            uploaded_file = st.file_uploader(
                "Upload Program",
                type=file_types,
                help="Upload the source file that should be executed."
            )


    # ==========================================
    # FILE TRANSFER OPERATION
    # ==========================================
    else:

        operation = st.selectbox(
            "Transfer Operation",
            [
                "File Upload",
                "File Download"
            ]
        )

        if operation == "File Upload":

            uploaded_file = st.file_uploader(
                "Select File",
                help="Select the file that should be uploaded."
            )

            st.caption(
                "The selected file will be handled as a schedulable workload."
            )

        else:

            download_url = st.text_input(
                "Download Source",
                placeholder="Enter the file URL"
            )

            download_location = st.text_input(
                "Save Location",
                value="workloads/transfers/downloads/",
                help="Directory where the downloaded file will be stored."
            )

            st.caption(
                "The downloaded file will be stored in the specified directory."
            )


    # ==========================================
    # SCHEDULING CONFIGURATION
    # ==========================================
    st.markdown(
        '<div class="section-title">Scheduling Configuration</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        priority = st.selectbox(
            "Priority",
            [1, 2, 3],
            index=1,
            help="1 = Highest Priority, 3 = Lowest Priority"
        )

    with col2:

        scheduler = st.selectbox(
            "Scheduling Algorithm",
            [
                "FCFS",
                "SJF",
                "Priority",
                "Round Robin",
                "Adaptive"
            ]
        )


    # ==========================================
    # SCHEDULER DESCRIPTION
    # ==========================================
    scheduler_description = {

        "FCFS":
        "Tasks are selected according to their arrival order.",

        "SJF":
        "Workloads with shorter estimated execution time are preferred.",

        "Priority":
        "Higher-priority workloads are selected before lower-priority workloads.",

        "Round Robin":
        "Ready workloads are handled using a time-slice based queue.",

        "Adaptive":
        "Scheduling decisions can use workload history and current system conditions."
    }

    st.info(scheduler_description[scheduler])


    # ==========================================
    # RUNTIME INFORMATION
    # ==========================================
    st.markdown(
        '<div class="section-title">Runtime Information</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="runtime-card">
            <div class="runtime-label">Arrival Time</div>
            <div class="runtime-value">Automatic</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="runtime-card">
            <div class="runtime-label">Process ID</div>
            <div class="runtime-value">Linux Generated</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="runtime-card">
            <div class="runtime-label">Initial State</div>
            <div class="runtime-value">READY</div>
        </div>
        """, unsafe_allow_html=True)


    # ==========================================
    # AUTOMATIC RUNTIME MONITORING
    # ==========================================
    st.markdown("""
    <div class="ready-box">
        <strong style="color:#60a5fa; font-size:15px;">
            ⚙️ Automatic Runtime Monitoring
        </strong>
        <br><br>
        <span style="color:#cbd5e1; font-size:13px;">
            CPU utilization, memory usage, execution time,
            process ID, start time and completion time will be
            collected automatically during runtime.
            These values are not entered manually.
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.write("")


    # ==========================================
    # SUBMIT BUTTON
    # ==========================================
    submit = st.button(
        "🚀 Submit Workload",
        use_container_width=True,
        type="primary"
    )


    # ==========================================
    # VALIDATION AND TASK CREATION
    # ==========================================
    if submit:

        # --------------------------------------
        # Workload name
        # --------------------------------------
        if not task_name.strip():

            st.warning("Please enter a workload name.")
            return


        # --------------------------------------
        # Program / Query validation
        # --------------------------------------
        if category == "Program / Query Execution":

            if execution_type == "SQL Query":

                if not sql_query.strip():

                    st.warning("Please enter an SQL query.")
                    return

            else:

                if uploaded_file is None:

                    st.warning("Please upload a program file.")
                    return


        # --------------------------------------
        # File Transfer validation
        # --------------------------------------
        else:

            if operation == "File Upload":

                if uploaded_file is None:

                    st.warning("Please select a file to upload.")
                    return

            else:

                if not download_url.strip():

                    st.warning("Please enter the download source URL.")
                    return


        # --------------------------------------
        # Temporary Task Creation
        # --------------------------------------
        task_id = "TASK-" + datetime.now().strftime("%H%M%S")


        st.success(
            f"Workload '{task_name}' submitted successfully."
        )


        # ==========================================
        # TASK SUMMARY
        # ==========================================
        st.markdown(
            '<div class="section-title">Workload Summary</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write("**Task ID:**", task_id)

            st.write(
                "**Category:**",
                category
            )

            st.write(
                "**Workload:**",
                task_name
            )

            st.write(
                "**Priority:**",
                priority
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
                "**State:**",
                "READY"
            )


        st.info(
            "The workload has entered the READY state. "
            "The backend scheduler will select it for execution."
        )