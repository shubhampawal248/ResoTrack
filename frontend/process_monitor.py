import streamlit as st


def show_process_monitor():

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
        'Monitor submitted workloads and their runtime process states.'
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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">Total Processes</div>
            <div class="status-value">0</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">READY</div>
            <div class="status-value">0</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">RUNNING</div>
            <div class="status-value">0</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">COMPLETED</div>
            <div class="status-value">0</div>
        </div>
        """, unsafe_allow_html=True)


    # ==========================================
    # CURRENT RUNNING PROCESS
    # ==========================================
    st.markdown(
        '<div class="section-title">Current Running Process</div>',
        unsafe_allow_html=True
    )

    st.info(
        "No process is currently running."
    )


    # ==========================================
    # PROCESS TABLE
    # ==========================================
    st.markdown(
        '<div class="section-title">Process List</div>',
        unsafe_allow_html=True
    )

    process_data = {
        "Task ID": [],
        "Workload": [],
        "PID": [],
        "State": [],
        "Priority": [],
        "Arrival Time": [],
        "Start Time": [],
        "Completion Time": [],
        "Execution Time": []
    }

    st.dataframe(
        process_data,
        use_container_width=True,
        hide_index=True
    )


    # ==========================================
    # PROCESS DETAILS
    # ==========================================
    st.markdown(
        '<div class="section-title">Process Details</div>',
        unsafe_allow_html=True
    )

    selected_process = st.selectbox(
        "Select Process",
        ["No process available"]
    )

    if selected_process == "No process available":
        st.caption(
            "Process details will appear here when workloads are submitted."
        )


    # ==========================================
    # REFRESH
    # ==========================================
    if st.button(
        "🔄 Refresh Process Status",
        use_container_width=True
    ):
        st.info(
            "Live process monitoring will be connected to the backend."
        )


    # ==========================================
    # RUNTIME MONITORING NOTE
    # ==========================================
    st.markdown("""
    <div class="info-box">
        <strong style="color:#60a5fa; font-size:15px;">
            ⚙️ Runtime Process Monitoring
        </strong>
        <br><br>
        <span style="color:#cbd5e1; font-size:13px;">
            Process ID, process state, start time, completion time
            and execution time will be collected automatically
            when workloads are executed in the Linux environment.
            These values are not entered manually.
        </span>
    </div>
    """, unsafe_allow_html=True)