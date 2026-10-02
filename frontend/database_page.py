import streamlit as st


def show_database_monitor():

    # ============================================================
    # PAGE STYLING
    # ============================================================

    st.markdown("""
    <style>

    .db-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .db-subtitle {
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
        font-size: 13px;
        margin-bottom: 10px;
    }

    .stat-value {
        font-size: 27px;
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
        margin-top: 20px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # HEADER
    # ============================================================

    st.markdown(
        '<div class="db-title">🗄️ Database Monitor</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="db-subtitle">'
        'Monitor PostgreSQL queries, database performance, locks, '
        'and buffer efficiency.'
        '</div>',
        unsafe_allow_html=True
    )

    # ============================================================
    # DATABASE STATUS
    # ============================================================

    st.markdown(
        '<div class="section-title">Database Status</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">DATABASE</div>
            <div class="stat-value">PostgreSQL</div>
            <div class="stat-description">Configured database</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">CONNECTION</div>
            <div class="stat-value">--</div>
            <div class="stat-description">Waiting for backend</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">ACTIVE QUERIES</div>
            <div class="stat-value">--</div>
            <div class="stat-description">Runtime database data</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">ACTIVE LOCKS</div>
            <div class="stat-value">--</div>
            <div class="stat-description">Current lock entries</div>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # QUERY EXECUTION
    # ============================================================

    st.markdown(
        '<div class="section-title">Query Execution</div>',
        unsafe_allow_html=True
    )

    query = st.text_area(
        "SQL Query",
        placeholder="Enter a SQL query...",
        height=130
    )

    if st.button(
        "▶ Execute Query",
        use_container_width=True
    ):
        if query.strip():
            st.info(
                "Query execution will be connected to PostgreSQL "
                "after the database backend is implemented."
            )
        else:
            st.warning("Please enter a SQL query.")

    # ============================================================
    # QUERY PERFORMANCE
    # ============================================================

    st.markdown(
        '<div class="section-title">Database Performance</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Query Execution Time",
            "--"
        )

    with col2:
        st.metric(
            "Active Locks",
            "--"
        )

    with col3:
        st.metric(
            "Buffer Hit Ratio",
            "--"
        )

    st.info(
        "These metrics will be collected from PostgreSQL after "
        "the database monitoring backend is connected."
    )

    # ============================================================
    # RECENT QUERIES
    # ============================================================

    st.markdown(
        '<div class="section-title">Recent Queries</div>',
        unsafe_allow_html=True
    )

    query_columns = [
        "Query ID",
        "Query",
        "Execution Time",
        "Timestamp",
        "Status"
    ]

    st.dataframe(
        [],
        column_config={
            "Query ID": st.column_config.TextColumn("Query ID"),
            "Query": st.column_config.TextColumn("Query"),
            "Execution Time": st.column_config.TextColumn(
                "Execution Time"
            ),
            "Timestamp": st.column_config.TextColumn("Timestamp"),
            "Status": st.column_config.TextColumn("Status")
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div class="empty-card">
        <div class="empty-icon">🗃️</div>
        <strong>No query history available</strong><br>
        Executed SQL queries will appear here after PostgreSQL
        integration is completed.
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # DATABASE INFORMATION
    # ============================================================

    st.markdown(
        '<div class="section-title">Database Monitoring Metrics</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">

        <strong>⏱️ Query Execution Time</strong><br><br>

        Measures how long a SQL query takes to execute.

        <br><br>

        A higher execution time can indicate that a query
        or database operation requires further analysis.

        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">

        <strong>🔒 Active Locks</strong><br><br>

        Shows currently detected PostgreSQL lock entries.

        <br><br>

        Lock information helps identify possible database
        contention between transactions or operations.

        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">

        <strong>📦 Buffer Hit Ratio</strong><br><br>

        Indicates how often PostgreSQL can satisfy data
        requests from its buffer cache instead of requiring
        disk reads.

        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">

        <strong>🔗 OS–DBMS Connection</strong><br><br>

        Database performance information can be correlated
        with OS resource information for bottleneck analysis.

        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # OS + DATABASE CORRELATION
    # ============================================================

    st.markdown(
        '<div class="section-title">OS–DBMS Performance Correlation</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">

    SysNexa can combine operating-system and database information.

    <br><br>

    <strong>OS metrics:</strong>
    CPU usage, memory usage and disk activity.

    <br><br>

    <strong>Database metrics:</strong>
    query execution time, active locks and buffer hit ratio.

    <br><br>

    These measurements can be used together by the
    <strong>Bottleneck Analyzer</strong> to identify possible
    performance issues.

    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # REFRESH BUTTON
    # ============================================================

    st.markdown("")

    if st.button(
        "🔄 Refresh Database Metrics",
        use_container_width=True
    ):
        st.info(
            "Database metrics will be refreshed from PostgreSQL "
            "after the database backend is implemented."
        )

    # ============================================================
    # DEVELOPMENT STATUS
    # ============================================================

    st.markdown("""
    <div class="status-note">
        <strong>Development Status:</strong>
        Frontend ready. PostgreSQL connection, query execution,
        lock monitoring and performance metrics will be connected
        through the backend.
    </div>
    """, unsafe_allow_html=True)