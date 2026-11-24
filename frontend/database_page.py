
import re
import time

import pandas as pd
import streamlit as st

from backend.database_manager import DatabaseManager


def show_database_monitor():

    st.title("🗄️ Database Monitor")
    st.caption(
        "Monitor MySQL queries, query history, and workload execution."
    )

    db = DatabaseManager()

    # ---------------------------------------------------------
    # DATABASE CONNECTION AND INITIALIZATION
    # ---------------------------------------------------------
    try:
        db.create_tables()
        connection_status = "Connected"
        connection_error = None

    except Exception as error:
        connection_status = "Disconnected"
        connection_error = str(error)

    col1, col2 = st.columns(2)

    col1.metric("Database", "MySQL")
    col2.metric("Connection", connection_status)

    if connection_error:
        st.error(f"MySQL connection failed: {connection_error}")
        st.info(
            "Check that MySQL is running and your DB_HOST, DB_PORT, "
            "DB_NAME, DB_USER, and DB_PASSWORD settings are correct."
        )
        db.close()
        return

    # ---------------------------------------------------------
    # QUERY EXECUTION
    # ---------------------------------------------------------
    st.subheader("Execute a Read-Only SQL Query")

    query = st.text_area(
        "SQL Query",
        placeholder="Example: SELECT * FROM workloads;",
        height=120,
        key="database_monitor_query",
    )

    st.caption(
        "For safety, this interface accepts SELECT and SHOW queries. "
        "Only one SQL statement can be submitted at a time."
    )

    def is_read_only_query(sql):
        # Remove leading whitespace and SQL comments.
        sql = sql.strip()

        while sql:
            if sql.startswith("--"):
                newline = sql.find("\n")
                if newline == -1:
                    return ""
                sql = sql[newline + 1:].lstrip()

            elif sql.startswith("#"):
                newline = sql.find("\n")
                if newline == -1:
                    return ""
                sql = sql[newline + 1:].lstrip()

            elif sql.startswith("/*"):
                end = sql.find("*/")
                if end == -1:
                    return ""
                sql = sql[end + 2:].lstrip()

            else:
                break

        # Allow a single optional trailing semicolon.
        sql = sql.rstrip()
        if sql.endswith(";"):
            sql = sql[:-1].rstrip()

        # Reject multiple statements and SQL that is not SELECT or SHOW.
        if ";" in sql:
            return ""

        match = re.match(r"^(SELECT|SHOW)\b", sql, re.IGNORECASE)
        if not match:
            return ""

        return sql

    if st.button(
        "▶ Execute Query",
        type="primary",
        use_container_width=True,
    ):
        clean_query = is_read_only_query(query)

        if not query.strip():
            st.warning("Please enter a SQL query.")

        elif not clean_query:
            st.error(
                "Only a single SELECT or SHOW query is allowed."
            )

        else:
            cursor = None
            started = time.perf_counter()

            try:
                connection = db.connect()
                cursor = connection.cursor(dictionary=True)

                cursor.execute(clean_query)
                rows = cursor.fetchall()
                elapsed_ms = (time.perf_counter() - started) * 1000

                db.save_query_history(
                    query_text=clean_query,
                    execution_time_ms=elapsed_ms,
                    status="SUCCESS",
                    rows_returned=len(rows),
                )

                st.success(
                    f"Query executed successfully in {elapsed_ms:.3f} ms. "
                    f"Rows returned: {len(rows)}."
                )

                if rows:
                    st.dataframe(
                        pd.DataFrame(rows),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("The query returned no rows.")

            except Exception as error:
                elapsed_ms = (time.perf_counter() - started) * 1000

                st.error(f"Query failed: {error}")

                # Attempt to preserve failed-query history.
                try:
                    db.save_query_history(
                        query_text=query.strip(),
                        execution_time_ms=elapsed_ms,
                        status="FAILED",
                        rows_returned=0,
                        error_message=str(error),
                    )
                except Exception as history_error:
                    st.warning(
                        "Could not save query history: "
                        f"{history_error}"
                    )

            finally:
                if cursor is not None:
                    cursor.close()

    # ---------------------------------------------------------
    # QUERY HISTORY
    # ---------------------------------------------------------
    st.subheader("Recent Queries")

    try:
        history = db.get_query_history(limit=50)

        if history:
            history_df = pd.DataFrame(history)
            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No query history is available yet.")

    except Exception as error:
        st.warning(f"Could not load query history: {error}")

    # ---------------------------------------------------------
    # SCHEDULER EXECUTION HISTORY
    # ---------------------------------------------------------
    st.subheader("Scheduler Execution History")

    try:
        executions = db.get_execution_history()

        if executions:
            st.dataframe(
                pd.DataFrame(executions),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "No workload execution records are available yet. "
                "Execute a workload from the Scheduler page first."
            )

    except Exception as error:
        st.warning(
            f"Could not load scheduler history: {error}"
        )

    # ---------------------------------------------------------
    # RESOURCE HISTORY
    # ---------------------------------------------------------
    st.subheader("Latest OS Resource Readings")

    try:
        readings = db.get_resource_history(limit=20)

        if readings:
            resource_df = pd.DataFrame(readings)
            st.dataframe(
                resource_df,
                use_container_width=True,
                hide_index=True,
            )

            chart_df = resource_df[
                ["recorded_at", "cpu_percent", "memory_percent",
                 "disk_percent"]
            ].copy()

            chart_df["recorded_at"] = pd.to_datetime(
                chart_df["recorded_at"]
            )

            chart_df = (
                chart_df
                .sort_values("recorded_at")
                .set_index("recorded_at")
            )

            st.line_chart(
                chart_df[
                    ["cpu_percent", "memory_percent", "disk_percent"]
                ]
            )
        else:
            st.info(
                "No OS resource readings have been saved yet."
            )

    except Exception as error:
        st.warning(
            f"Could not load resource history: {error}"
        )

    # ---------------------------------------------------------
    # REFRESH
    # ---------------------------------------------------------
    if st.button("🔄 Refresh Database Metrics"):
        st.rerun()

    db.close()

