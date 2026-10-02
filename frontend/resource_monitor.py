import streamlit as st


def show_resource_monitor():

    # ---------------- PAGE STYLE ----------------
    st.markdown("""
    <style>

    .resource-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .resource-subtitle {
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .resource-card {
        background: #111827;
        border: 1px solid #263244;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .resource-label {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .resource-value {
        font-size: 28px;
        font-weight: 700;
    }

    .resource-status {
        color: #9ca3af;
        font-size: 13px;
        margin-top: 5px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .info-box {
        background: #111827;
        border: 1px solid #263244;
        border-radius: 12px;
        padding: 18px;
        color: #d1d5db;
        line-height: 1.6;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    st.markdown(
        '<div class="resource-title">⚡ Resource Monitor</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="resource-subtitle">'
        'Monitor real-time system resources used by running workloads.'
        '</div>',
        unsafe_allow_html=True
    )

    # ---------------- RESOURCE SUMMARY ----------------
    st.markdown(
        '<div class="section-title">System Resource Summary</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="resource-card">
            <div class="resource-label">CPU Utilization</div>
            <div class="resource-value">-- %</div>
            <div class="resource-status">Waiting for runtime data</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="resource-card">
            <div class="resource-label">Memory Usage</div>
            <div class="resource-value">-- %</div>
            <div class="resource-status">Waiting for runtime data</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="resource-card">
            <div class="resource-label">Disk Usage</div>
            <div class="resource-value">-- %</div>
            <div class="resource-status">Waiting for runtime data</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="resource-card">
            <div class="resource-label">Active Process</div>
            <div class="resource-value">--</div>
            <div class="resource-status">No process running</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- RESOURCE STATUS ----------------
    st.markdown(
        '<div class="section-title">Resource Status</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-box">
            <strong>CPU Status</strong><br>
            Current CPU utilization will be collected automatically
            from the Linux environment using the monitoring module.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-box">
            <strong>Memory Status</strong><br>
            Current memory usage and available memory will be
            collected automatically during runtime.
        </div>
        """, unsafe_allow_html=True)

    # ---------------- RESOURCE THRESHOLDS ----------------
    st.markdown(
        '<div class="section-title">Resource Threshold Checker</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("CPU Threshold", "90%")

    with col2:
        st.metric("Memory Threshold", "85%")

    with col3:
        st.metric("Disk Threshold", "90%")

    st.info(
        "If resource utilization becomes too high, the Resource Manager "
        "can keep a new workload in the READY/WAITING state instead of "
        "starting it immediately."
    )

    # ---------------- RESOURCE HISTORY ----------------
    st.markdown(
        '<div class="section-title">Resource Usage History</div>',
        unsafe_allow_html=True
    )

    st.info(
        "CPU, memory and disk usage graphs will appear here after "
        "runtime monitoring is connected."
    )

    # ---------------- CURRENT PROCESS ----------------
    st.markdown(
        '<div class="section-title">Current Process Resource Usage</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        [],
        column_config={
            "Task ID": "Task ID",
            "PID": "PID",
            "Process": "Process",
            "CPU Usage": "CPU Usage",
            "Memory Used": "Memory Used",
            "Disk Read": "Disk Read",
            "Disk Write": "Disk Write",
            "Timestamp": "Timestamp"
        },
        use_container_width=True
    )

    # ---------------- REFRESH ----------------
    if st.button("🔄 Refresh Resource Data", use_container_width=True):
        st.info(
            "Runtime monitoring is not connected yet. "
            "After Ubuntu/WSL and psutil are configured, "
            "this button will refresh the actual resource readings."
        )

    # ---------------- PROJECT NOTE ----------------
    st.markdown(
        '<div class="section-title">How Resource Monitoring Works</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-box">

    <strong>1. Workload starts</strong><br>
    The selected workload is executed in the Linux environment.

    <br><br>

    <strong>2. Linux creates the process</strong><br>
    Linux assigns a real Process ID (PID).

    <br><br>

    <strong>3. Monitoring starts</strong><br>
    Python uses the process information and <b>psutil</b>
    to collect CPU, memory and disk information.

    <br><br>

    <strong>4. Resource Manager checks thresholds</strong><br>
    If resource usage is too high, a new workload can remain
    in READY/WAITING until resources become available.

    <br><br>

    <strong>5. Data is stored</strong><br>
    Runtime resource measurements can later be stored in PostgreSQL
    for history and analysis.

    </div>
    """, unsafe_allow_html=True)