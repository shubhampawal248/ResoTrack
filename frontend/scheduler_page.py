import streamlit as st


def show_scheduler():

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

    .algorithm-card {
        background: #111827;
        border: 1px solid #273449;
        border-radius: 12px;
        padding: 18px;
        min-height: 135px;
    }

    .algorithm-title {
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .algorithm-description {
        color: #9ca3af;
        font-size: 13px;
        line-height: 1.5;
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
        font-size: 17px;
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
        '<div class="page-title">Scheduler</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Manage the order in which READY workloads are selected for execution.'
        '</div>',
        unsafe_allow_html=True
    )


    # ==========================================
    # CURRENT SCHEDULER STATUS
    # ==========================================
    st.markdown(
        '<div class="section-title">Scheduler Status</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">Current Algorithm</div>
            <div class="status-value">Not Selected</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">READY Workloads</div>
            <div class="status-value">0</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">Running Workload</div>
            <div class="status-value">None</div>
        </div>
        """, unsafe_allow_html=True)


    # ==========================================
    # ALGORITHM SELECTION
    # ==========================================
    st.markdown(
        '<div class="section-title">Select Scheduling Algorithm</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="algorithm-card">
            <div class="algorithm-title">🔵 FCFS</div>
            <div class="algorithm-description">
                First Come First Serve selects workloads according
                to their arrival order in the READY queue.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="algorithm-card">
            <div class="algorithm-title">🟣 SJF</div>
            <div class="algorithm-description">
                Shortest Job First prefers workloads with the
                shortest estimated execution time.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="algorithm-card">
            <div class="algorithm-title">🟠 Priority</div>
            <div class="algorithm-description">
                Higher-priority workloads are selected before
                lower-priority workloads.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="algorithm-card">
            <div class="algorithm-title">🟢 Round Robin</div>
            <div class="algorithm-description">
                READY workloads are handled in a rotating queue
                using a configured time slice.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="algorithm-card">
        <div class="algorithm-title">🧠 Adaptive Scheduler</div>
        <div class="algorithm-description">
            Uses workload history, current system conditions and
            scheduling information to make adaptive decisions.
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ==========================================
    # SELECT ALGORITHM
    # ==========================================
    st.markdown(
        '<div class="section-title">Scheduling Configuration</div>',
        unsafe_allow_html=True
    )

    algorithm = st.selectbox(
        "Scheduling Algorithm",
        [
            "FCFS",
            "SJF",
            "Priority",
            "Round Robin",
            "Adaptive"
        ]
    )

    if algorithm == "Round Robin":

        time_quantum = st.number_input(
            "Time Quantum",
            min_value=1,
            value=2,
            step=1,
            help="Time slice used by the application-level Round Robin scheduler."
        )

        st.caption(
            f"Current time quantum: {time_quantum}"
        )


    # ==========================================
    # ALGORITHM INFORMATION
    # ==========================================
    descriptions = {

        "FCFS":
        "The next workload is selected according to arrival order.",

        "SJF":
        "The workload with the shortest estimated execution time is selected.",

        "Priority":
        "The workload with the highest priority is selected first. Priority 1 is highest.",

        "Round Robin":
        "Workloads are handled using a rotating READY queue and a time quantum.",

        "Adaptive":
        "The scheduler can use previous workload history and current system conditions."
    }

    st.info(descriptions[algorithm])


    # ==========================================
    # READY QUEUE
    # ==========================================
    st.markdown(
        '<div class="section-title">READY Queue</div>',
        unsafe_allow_html=True
    )

    st.info(
        "No workloads are currently available in the READY queue."
    )


    # ==========================================
    # SCHEDULER ACTION
    # ==========================================
    st.markdown(
        '<div class="section-title">Scheduler Control</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "▶️ Select Next Workload",
        use_container_width=True,
        type="primary"
    ):
        st.warning(
            "Backend scheduler is not connected yet."
        )


    # ==========================================
    # IMPORTANT PROJECT NOTE
    # ==========================================
    st.markdown("""
    <div class="info-box">
        <strong style="color:#60a5fa; font-size:15px;">
            ⚙️ Runtime Scheduling
        </strong>
        <br><br>
        <span style="color:#cbd5e1; font-size:13px;">
            The application scheduler selects the next workload
            from the READY queue. The selected workload is then
            passed to the workload executor for execution in
            the Linux environment.
        </span>
    </div>
    """, unsafe_allow_html=True)