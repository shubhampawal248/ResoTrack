import streamlit as st


def show_history():

    # ============================================================
    # PAGE STYLING
    # ============================================================

    st.markdown("""
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
        background: linear-gradient(145deg, #111827, #0f172a);
        border: 1px solid #263244;
        border-radius: 14px;
        padding: 20px;
        min-height: 125px;
    }

    .stat-label {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 10px;
    }

    .stat-value {
        font-size: 29px;
        font-weight: 700;
    }

    .stat-description {
        color: #6b7280;
        font-size: 12px;
        margin-top: 7px;
    }

    .info-card {
        background: #111827;
        border: 1px solid #263244;
        border-radius: 14px;
        padding: 20px;
        line-height: 1.7;
    }

    .empty-card {
        background: #0f172a;
        border: 1px dashed #374151;
        border-radius: 14px;
        padding: 35px;
        text-align: center;
        color: #9ca3af;
    }

    .empty-icon {
        font-size: 35px;
        margin-bottom: 10px;
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
    """, unsafe_allow_html=True)

    # ============================================================
    # HEADER
    # ============================================================

    st.markdown(
        '<div class="history-title">📚 Workload History</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="history-subtitle">'
        'Review previously executed workloads, scheduling decisions, '
        'and runtime performance.'
        '</div>',
        unsafe_allow_html=True
    )

    # ============================================================
    # SUMMARY CARDS
    # ============================================================

    st.markdown(
        '<div class="section-title">Execution Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">COMPLETED TASKS</div>
            <div class="stat-value">--</div>
            <div class="stat-description">Historical records</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">AVG EXECUTION</div>
            <div class="stat-value">--</div>
            <div class="stat-description">Across completed tasks</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">AVG CPU USAGE</div>
            <div class="stat-value">--</div>
            <div class="stat-description">Runtime measurements</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">AVG MEMORY</div>
            <div class="stat-value">--</div>
            <div class="stat-description">Runtime measurements</div>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # FILTERS
    # ============================================================

    st.markdown(
        '<div class="section-title">Filter Execution History</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        workload_type = st.selectbox(
            "Workload Type",
            [
                "All",
                "Python Program",
                "C/C++ Program",
                "SQL Query",
                "File Upload",
                "File Download"
            ]
        )

    with col2:
        algorithm = st.selectbox(
            "Algorithm",
            [
                "All",
                "FCFS",
                "SJF",
                "Priority",
                "Round Robin",
                "Adaptive"
            ]
        )

    with col3:
        state = st.selectbox(
            "State",
            [
                "All",
                "COMPLETED",
                "FAILED"
            ]
        )

    with col4:
        search_task = st.text_input(
            "Search Task",
            placeholder="e.g. TASK-001"
        )

    # ============================================================
    # HISTORY TABLE
    # ============================================================

    st.markdown(
        '<div class="section-title">Execution Records</div>',
        unsafe_allow_html=True
    )

    history_columns = [
        "Task ID",
        "Workload",
        "Type",
        "Algorithm",
        "PID",
        "Priority",
        "Arrival Time",
        "Start Time",
        "Completion Time",
        "Execution Time",
        "CPU Usage",
        "Memory Used",
        "State"
    ]

    # Empty table for now.
    # Later this will be replaced with PostgreSQL data.

    st.dataframe(
        [],
        column_config={
            "Task ID": st.column_config.TextColumn("Task ID"),
            "Workload": st.column_config.TextColumn("Workload"),
            "Type": st.column_config.TextColumn("Type"),
            "Algorithm": st.column_config.TextColumn("Algorithm"),
            "PID": st.column_config.TextColumn("PID"),
            "Priority": st.column_config.NumberColumn("Priority"),
            "Arrival Time": st.column_config.TextColumn("Arrival"),
            "Start Time": st.column_config.TextColumn("Start"),
            "Completion Time": st.column_config.TextColumn("Completed"),
            "Execution Time": st.column_config.TextColumn("Execution"),
            "CPU Usage": st.column_config.TextColumn("CPU"),
            "Memory Used": st.column_config.TextColumn("Memory"),
            "State": st.column_config.TextColumn("State")
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div class="empty-card">
        <div class="empty-icon">🗂️</div>
        <strong>No execution history available</strong><br>
        Completed workload records will appear here after the
        runtime and PostgreSQL modules are connected.
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # SELECTED WORKLOAD DETAILS
    # ============================================================

    st.markdown(
        '<div class="section-title">Workload Details</div>',
        unsafe_allow_html=True
    )

    selected_task = st.selectbox(
        "Select a workload",
        ["No completed workload available"]
    )

    if selected_task == "No completed workload available":

        st.markdown("""
        <div class="info-card">
            <strong>📌 No workload selected</strong><br><br>
            Once a workload is completed, you will be able to
            select it here and view its complete execution details.
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # WHAT WILL BE STORED
    # ============================================================

    st.markdown(
        '<div class="section-title">Stored Runtime Information</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">

        <strong>Process Information</strong><br><br>

        • Process / Task ID<br>
        • Linux PID<br>
        • Workload type<br>
        • Process priority<br>
        • Process state<br>
        • Arrival time<br>
        • Start time<br>
        • Completion time

        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">

        <strong>Performance Information</strong><br><br>

        • Execution time<br>
        • CPU utilization<br>
        • Memory usage<br>
        • Disk activity<br>
        • Scheduling algorithm<br>
        • Waiting time<br>
        • Turnaround time

        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # ADAPTIVE SCHEDULER SECTION
    # ============================================================

    st.markdown(
        '<div class="section-title">🧠 Historical Data for Adaptive Scheduling</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">

    <strong>How History supports the Adaptive Scheduler</strong>

    <br><br>

    When a workload runs for the first time, there is no previous
    performance history available.

    <br><br>

    After execution, SysNexa records information such as:

    <br><br>

    <b>CPU usage → Memory usage → Execution time → Resource behavior</b>

    <br><br>

    This information is stored in PostgreSQL and can be used during
    future executions as historical input for adaptive scheduling.

    <br><br>

    <strong>First execution:</strong>
    No historical data → use available task information/default policy.

    <br>

    <strong>Future execution:</strong>
    Historical data available → adaptive scheduler can consider
    previous workload behavior.

    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # REFRESH BUTTON
    # ============================================================

    st.markdown("")

    if st.button(
        "🔄 Refresh History",
        use_container_width=True
    ):
        st.info(
            "History will be refreshed from PostgreSQL once the "
            "database backend is connected."
        )

    # ============================================================
    # CURRENT DEVELOPMENT STATUS
    # ============================================================

    st.markdown("""
    <div class="status-note">
        <strong>Development Status:</strong>
        Frontend ready. PostgreSQL and runtime monitoring will
        provide the actual historical data later.
    </div>
    """, unsafe_allow_html=True)