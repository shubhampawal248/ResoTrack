
import streamlit as st
import pandas as pd
import psutil
import shutil
import os


def show_home():

    # ---------------------------------------------------------
    # PAGE CSS
    # ---------------------------------------------------------
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(0, 255, 200, 0.08), transparent 25%),
            radial-gradient(circle at 90% 20%, rgba(80, 100, 255, 0.10), transparent 25%),
            #080b12;
        color: #f5f7fa;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 5px;
        background: linear-gradient(90deg, #ffffff, #8fffe0, #8ca7ff, #ffffff);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientMove 5s linear infinite;
    }

    @keyframes gradientMove {
        0% { background-position: 0% center; }
        100% { background-position: 300% center; }
    }

    .hero-subtitle {
        color: #9ca8b8;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 14px;
        border-radius: 30px;
        background: rgba(0, 255, 170, 0.08);
        border: 1px solid rgba(0, 255, 170, 0.25);
        color: #71ffd1;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 20px;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #42f5a7;
        box-shadow: 0 0 12px #42f5a7;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.5); opacity: 0.5; }
        100% { transform: scale(1); opacity: 1; }
    }

    .metric-card {
        padding: 20px;
        border-radius: 18px;
        background: linear-gradient(145deg, rgba(255,255,255,0.07), rgba(255,255,255,0.025));
        border: 1px solid rgba(255,255,255,0.09);
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        transition: all 0.3s ease;
        min-height: 130px;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(120,255,220,0.35);
        box-shadow: 0 15px 40px rgba(0,0,0,0.35), 0 0 20px rgba(0,255,200,0.08);
    }

    .metric-label {
        color: #8995a6;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 750;
        color: #ffffff;
    }

    .metric-change {
        font-size: 12px;
        color: #65e6b8;
        margin-top: 8px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
        color: #f2f5f8;
    }

    .section-description {
        color: #8995a6;
        font-size: 14px;
        margin-bottom: 18px;
    }

    .workflow-card {
        padding: 18px;
        border-radius: 16px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        text-align: center;
        min-height: 125px;
        transition: 0.3s ease;
    }

    .workflow-card:hover {
        transform: translateY(-4px);
        background: rgba(255,255,255,0.055);
    }

    .workflow-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }

    .workflow-name {
        font-weight: 700;
        color: #ffffff;
        font-size: 15px;
    }

    .workflow-text {
        color: #8e99aa;
        font-size: 11px;
        margin-top: 5px;
    }

    .process-card {
        padding: 15px 18px;
        border-radius: 14px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 10px;
    }

    .process-name {
        color: #ffffff;
        font-weight: 650;
    }

    .process-info {
        color: #8793a4;
        font-size: 12px;
    }

    .dashboard-footer {
        text-align: center;
        color: #667181;
        font-size: 12px;
        margin-top: 45px;
        padding: 20px;
        border-top: 1px solid rgba(255,255,255,0.07);
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # GET LIVE SYSTEM RESOURCES
    # ---------------------------------------------------------
    cpu_percent = psutil.cpu_percent(interval=0.3)
    memory_percent = psutil.virtual_memory().percent

    try:
        disk_percent = psutil.disk_usage(os.path.abspath(os.sep)).percent
    except Exception:
        disk_percent = 0

    def resource_status(value):
        if value >= 85:
            return "● High usage"
        if value >= 65:
            return "● Elevated"
        return "● Normal"

    # ---------------------------------------------------------
    # GET SHARED TASK RECORDS
    # ---------------------------------------------------------
    task_manager = st.session_state.get("task_manager")

    if task_manager is not None:
        tasks = task_manager.get_all_tasks()
    else:
        tasks = []
        st.warning(
            "TaskManager is not initialized. Check app.py to ensure "
            "all pages use the same TaskManager."
        )

    state_counts = {
        "READY": 0,
        "RUNNING": 0,
        "COMPLETED": 0,
        "WAITING": 0,
        "FAILED": 0,
    }

    for task in tasks:
        state = str(getattr(task, "state", "UNKNOWN")).upper()

        if state in state_counts:
            state_counts[state] += 1
        elif state == "PENDING":
            state_counts["READY"] += 1

    active_tasks = state_counts["READY"] + state_counts["RUNNING"]
    running_count = state_counts["RUNNING"]

    # ---------------------------------------------------------
    # HERO SECTION
    # ---------------------------------------------------------
    st.markdown("""
    <div class="status-badge">
        <span class="status-dot"></span>
        SYSTEM MONITORIN ACTIVE
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-title">SysNexa</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Operating System and Database Resource Manager'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption("Live resource readings and current workload records.")

    # ---------------------------------------------------------
    # TOP METRICS
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    metric_values = [
        ("CPU UTILIZATION", cpu_percent, resource_status(cpu_percent)),
        ("MEMORY USAGE", memory_percent, resource_status(memory_percent)),
        ("DISK USAGE", disk_percent, resource_status(disk_percent)),
    ]

    for column, (label, value, status_text) in zip(
        [col1, col2, col3], metric_values
    ):
        with column:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value:.0f}%</div>
                <div class="metric-change">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ACTIVE TASKS</div>
            <div class="metric-value">{active_tasks:02d}</div>
            <div class="metric-change">● {running_count} Running</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SYSTEM OVERVIEW
    # ---------------------------------------------------------
    st.markdown(
        '<div class="section-title">System Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Current workload distribution and system resource utilization.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⚙️ Workload States")

        state_data = pd.DataFrame({
            "State": ["READY", "RUNNING", "COMPLETED", "WAITING", "FAILED"],
            "Tasks": [
                state_counts["READY"],
                state_counts["RUNNING"],
                state_counts["COMPLETED"],
                state_counts["WAITING"],
                state_counts["FAILED"],
            ],
        }).set_index("State")

        st.bar_chart(state_data, height=280)

    with col2:
        st.markdown("#### 📊 Resource Utilization")

        resource_data = pd.DataFrame({
            "Resource": ["CPU", "RAM", "Disk"],
            "Usage (%)": [cpu_percent, memory_percent, disk_percent],
        }).set_index("Resource")

        st.bar_chart(resource_data, height=280)

    # ---------------------------------------------------------
    # CURRENT PROCESSES
    # ---------------------------------------------------------
    st.markdown(
        '<div class="section-title">Current Processes</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Runtime workloads currently known to the process manager.'
        '</div>',
        unsafe_allow_html=True
    )

    if tasks:
        for task in tasks:
            pid = getattr(task, "pid", None)
            name = getattr(task, "workload_name", "Unnamed workload")
            state = str(getattr(task, "state", "UNKNOWN")).upper()
            priority = getattr(task, "priority", "N/A")
            task_id = getattr(task, "task_id", "N/A")

            if state == "RUNNING":
                icon = "🟢"
            elif state == "COMPLETED":
                icon = "🔵"
            elif state == "FAILED":
                icon = "🔴"
            else:
                icon = "🟡"

            displayed_pid = str(pid) if pid is not None else str(task_id)

            st.markdown(f"""
            <div class="process-card">
                <span class="process-name">
                    {icon} {displayed_pid} — {name}
                </span>
                <span class="process-info">
                    &nbsp;&nbsp; {state} &nbsp; | &nbsp; Priority {priority}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No workloads have been submitted yet.")

    # ---------------------------------------------------------
    # WORKFLOW
    # ---------------------------------------------------------
    st.markdown(
        '<div class="section-title">SysNexa Runtime Workflow</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'How a workload moves through the system.'
        '</div>',
        unsafe_allow_html=True
    )

    workflow = st.columns(6)

    steps = [
        ("📥", "Workload", "Task submitted"),
        ("📋", "READY Queue", "Waiting for selection"),
        ("🧠", "Scheduler", "Selects next task"),
        ("⚡", "Resource Check", "Checks resources"),
        ("🐧", "Linux", "Actual execution"),
        ("🗄️", "PostgreSQL", "Stores results"),
    ]

    for column, (icon, name, description) in zip(workflow, steps):
        with column:
            st.markdown(f"""
            <div class="workflow-card">
                <div class="workflow-icon">{icon}</div>
                <div class="workflow-name">{name}</div>
                <div class="workflow-text">{description}</div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # ADVANCED FEATURES
    # ---------------------------------------------------------
    st.markdown(
        '<div class="section-title">Advanced Intelligence</div>',
        unsafe_allow_html=True
    )

    feature1, feature2, feature3 = st.columns(3)

    with feature1:
        st.info(
            "🧠 **Adaptive Scheduler**\n\n"
            "Uses workload history and runtime information "
            "to support scheduling decisions."
        )

    with feature2:
        st.info(
            "⚡ **Resource-Aware Admission**\n\n"
            "Live resource readings are available. Admission control "
            "must be connected separately to enforce resource limits."
        )

    with feature3:
        st.info(
            "🔍 **Bottleneck Analysis**\n\n"
            "CPU, memory, disk and workload states are displayed. "
            "Historical bottleneck analysis requires stored measurements."
        )

    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------
    st.markdown("---")

    st.caption(
        "Resource values are sampled from the machine running Streamlit. "
        "They are not necessarily limited to the workload processes."
    )

    st.markdown("""
    <div class="dashboard-footer">
        SysNexa • Operating System & Database Resource Manager
        <br>
        Runtime Workload Management • Resource Monitoring • DBMS Analytics
    </div>
    """, unsafe_allow_html=True)
