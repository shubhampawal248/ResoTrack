
import time
import uuid
import threading
from datetime import datetime

import streamlit as st
import pandas as pd
import altair as alt

from backend.task_manager import TaskManager
from backend.database_manager import DatabaseManager
from backend.resource_manager import ResourceManager
from backend.load_generator import LoadGenerator
from backend.workload_executor import WorkloadExecutor

from backend.fcfs import FCFSScheduler
from backend.sjf import SJFScheduler
from backend.priority import PriorityScheduler
from backend.round_robin import RoundRobinScheduler
from backend.adaptive_scheduler import AdaptiveScheduler
from backend.automatic_scheduler import AutomaticScheduler


# ==========================================================
# CONFIGURATION
# ==========================================================

LOAD_TYPES = [
    "CPU Load",
    "Memory Load",
    "Disk Load",
    "Combined Load",
]

ALGORITHMS = [
    "FCFS",
    "SJF",
    "Priority",
    "Round Robin",
    "Adaptive Scheduler",
    "Automatic Scheduler Switching",
]

SCHEDULERS = {
    "FCFS": FCFSScheduler,
    "SJF": SJFScheduler,
    "Priority": PriorityScheduler,
    "Round Robin": RoundRobinScheduler,
    "Adaptive Scheduler": AdaptiveScheduler,
}


# ==========================================================
# SHARED TASK MANAGER
# ==========================================================

def get_task_manager():

    if "task_manager" not in st.session_state:
        st.session_state["task_manager"] = TaskManager()

    return st.session_state["task_manager"]


# ==========================================================
# GENERATE REAL PYTHON WORKLOADS
# ==========================================================

def generate_source_code(load_type, duration, memory_mb):

    duration = max(1, min(int(duration), 8))
    memory_mb = max(1, min(int(memory_mb), 16))

    common = f"""
import time
import os
import tempfile

DURATION = {duration}
MEMORY_MB = {memory_mb}

deadline = time.monotonic() + DURATION

def remaining():
    return time.monotonic() < deadline

"""

    cpu_code = """
value = 0

while remaining():
    end = min(time.monotonic() + 0.04, deadline)

    while time.monotonic() < end:
        value = (value * 17 + 31) % 1000003

    time.sleep(0.04)

print("CPU workload completed")
"""

    memory_code = """
memory = bytearray(MEMORY_MB * 1024 * 1024)

for i in range(0, len(memory), 4096):
    memory[i] = 1

while remaining():
    time.sleep(0.1)

del memory

print("Memory workload completed")
"""

    disk_code = """
with tempfile.TemporaryDirectory(
    prefix="sysnexa_sim_"
) as directory:

    path = os.path.join(directory, "sample.bin")
    block = b"0" * 4096

    while remaining():

        with open(path, "wb") as file:
            for _ in range(64):
                file.write(block)

        with open(path, "rb") as file:
            file.read()

        time.sleep(0.1)

print("Disk workload completed")
"""

    combined_code = """
memory = bytearray(MEMORY_MB * 1024 * 1024)

for i in range(0, len(memory), 4096):
    memory[i] = 1

value = 0

with tempfile.TemporaryDirectory(
    prefix="sysnexa_sim_"
) as directory:

    path = os.path.join(directory, "sample.bin")

    while remaining():

        end = min(time.monotonic() + 0.03, deadline)

        while time.monotonic() < end:
            value = (value * 17 + 31) % 1000003

        with open(path, "wb") as file:
            file.write(b"0" * 65536)

        with open(path, "rb") as file:
            file.read()

        time.sleep(0.07)

del memory

print("Combined workload completed")
"""

    programs = {
        "CPU Load": cpu_code,
        "Memory Load": memory_code,
        "Disk Load": disk_code,
        "Combined Load": combined_code,
    }

    return common + programs[load_type]


# ==========================================================
# CREATE AND SAVE WORKLOADS IN MYSQL
# ==========================================================

def create_simulator_tasks(
    count,
    duration,
    memory_mb,
    selected_loads,
    algorithm,
):

    manager = get_task_manager()
    created = []

    db = DatabaseManager()

    try:

        for index in range(count):

            load_type = selected_loads[
                index % len(selected_loads)
            ]

            task_id = (
                "SIM-"
                + datetime.now().strftime("%Y%m%d%H%M%S")
                + "-"
                + uuid.uuid4().hex[:8]
            )

            task = manager.create_task(
                task_id=task_id,
                workload_name=(
                    f"Simulator {load_type} {index + 1}"
                ),
                workload_type="python",
                priority=(index % 3) + 1,
                estimated_time=float(duration),
            )

            task.source_code = generate_source_code(
                load_type,
                duration,
                memory_mb,
            )

            task.execution_timeout = int(duration) + 12

            task.scheduling_mode = (
                "Automatic"
                if algorithm == "Automatic Scheduler Switching"
                else "Manual"
            )

            task.scheduler_name = algorithm
            task.automatic_retry = False
            task.max_retries = 0

            task.simulator_generated = True
            task.simulator_load_type = load_type

            try:
                db.insert_workload(task)

            except Exception:
                manager.tasks.remove(task)
                raise

            created.append(task)

    finally:
        db.close()

    return created


# ==========================================================
# SCHEDULING
# ==========================================================

def select_next_task(tasks, algorithm):

    if not tasks:
        return None, None

    if algorithm == "Automatic Scheduler Switching":

        scheduler = AutomaticScheduler()
        scheduler.add_processes(list(tasks))

        task = scheduler.select_next()

        selected = (
            scheduler.get_selected_algorithm()
            or "Automatic"
        )

        return task, selected

    scheduler = SCHEDULERS[algorithm]()
    scheduler.add_processes(list(tasks))

    return scheduler.select_next(), algorithm


def build_execution_order(tasks, algorithm):

    remaining = list(tasks)
    ordered = []

    while remaining:

        task, selected_algorithm = select_next_task(
            remaining,
            algorithm,
        )

        if task is None:
            raise RuntimeError(
                "Scheduler could not select a workload."
            )

        ordered.append((task, selected_algorithm))

        remaining = [
            item for item in remaining
            if item.task_id != task.task_id
        ]

    return ordered


# ==========================================================
# RESOURCE MONITORING
# ==========================================================

class ResourceSampler:

    def __init__(self):

        self.manager = ResourceManager()
        self.stop_event = threading.Event()

        self.thread = None
        self.readings = []
        self.errors = []

    def _sample(self):

        while not self.stop_event.is_set():

            try:

                resources = self.manager.get_resources()

                reading = {
                    "timestamp": datetime.now(),
                    "cpu": float(resources["cpu"]),
                    "memory": float(resources["memory"]),
                    "disk": float(resources["disk"]),
                    "memory_used": int(
                        resources["memory_used"]
                    ),
                    "memory_available": int(
                        resources["memory_available"]
                    ),
                    "disk_used": int(
                        resources["disk_used"]
                    ),
                    "disk_free": int(
                        resources["disk_free"]
                    ),
                }

                self.readings.append(reading)

            except Exception as error:
                self.errors.append(str(error))

            self.stop_event.wait(1)

    def start(self):

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._sample,
            daemon=True,
        )

        self.thread.start()

    def stop(self):

        self.stop_event.set()

        if self.thread is not None:
            self.thread.join(timeout=3)


# ==========================================================
# MYSQL EXECUTION AND RESOURCE HISTORY
# ==========================================================

def save_execution(task):

    db = DatabaseManager()

    try:
        db.update_workload_status(task)
        db.save_execution_history(task)

    finally:
        db.close()


def save_resource_readings(readings):

    if not readings:
        return

    db = DatabaseManager()

    try:

        for reading in readings:

            db.save_resource_history(
                reading["cpu"],
                reading["memory"],
                reading["disk"],
            )

    finally:
        db.close()


# ==========================================================
# EXECUTE SIMULATOR WORKLOADS
# ==========================================================

def execute_simulator_queue(tasks, algorithm):

    executor = WorkloadExecutor()

    order = build_execution_order(
        tasks,
        algorithm,
    )

    results = []
    all_readings = []

    progress = st.progress(0)
    status = st.empty()

    total = len(order)

    for index, (task, selected_algorithm) in enumerate(order):

        if task.state != "READY":
            continue

        process_name = f"P{index + 1}"

        status.info(
            f"Running {process_name}: "
            f"{task.workload_name}"
        )

        sampler = ResourceSampler()

        execution_error = None
        database_errors = []

        fallback_start = datetime.now()

        sampler.start()

        try:

            executor.execute(
                task,
                task.source_code,
                timeout_seconds=int(
                    task.execution_timeout
                ),
            )

        except Exception as error:

            execution_error = str(error)

            task.state = "FAILED"
            task.failure_reason = execution_error

            if task.completion_time is None:
                task.completion_time = datetime.now()

        finally:
            sampler.stop()

        fallback_finish = datetime.now()

        # Associate resource measurements with the
        # process active when each sample was taken.
        #
        # These are system-wide WSL measurements,
        # not exclusive per-process resource usage.

        for reading in sampler.readings:

            all_readings.append({
                **reading,
                "Process": process_name,
                "Task ID": task.task_id,
                "Workload": task.workload_name,
            })

        try:
            save_execution(task)

        except Exception as error:
            database_errors.append(str(error))

        try:
            save_resource_readings(sampler.readings)

        except Exception as error:
            database_errors.append(str(error))

        start_time = (
            task.start_time or fallback_start
        )

        finish_time = (
            task.completion_time or fallback_finish
        )

        waiting = None
        turnaround = None

        if task.arrival_time:

            waiting = max(
                0.0,
                (
                    start_time - task.arrival_time
                ).total_seconds(),
            )

            turnaround = max(
                0.0,
                (
                    finish_time - task.arrival_time
                ).total_seconds(),
            )

        results.append({
            "Process": process_name,
            "Task ID": task.task_id,
            "Workload": task.workload_name,
            "Load Type": task.simulator_load_type,
            "Algorithm": selected_algorithm,
            "Priority": task.priority,
            "PID": task.pid,
            "Start Time": start_time,
            "Completion Time": finish_time,
            "Execution Time": task.execution_time,
            "Waiting Time": waiting,
            "Turnaround Time": turnaround,
            "State": task.state,
            "Execution Error": execution_error,
            "Database Error": "; ".join(database_errors),
        })

        progress.progress(
            (index + 1) / total
        )

    status.success("Workload execution finished.")

    return results, all_readings


# ==========================================================
# SIMPLE PROCESS-WISE RESOURCE GRAPH
# ==========================================================

def show_process_resource_graph(readings):

    if not readings:
        st.info("No resource readings available.")
        return

    df = pd.DataFrame(readings)

    if "Process" not in df.columns:
        st.info(
            "Process labels are unavailable for these readings."
        )
        return

    # Average the actual system measurements collected
    # during each individual workload's execution.

    process_usage = (
        df.groupby("Process", sort=False)
        .agg(
            CPU=("cpu", "mean"),
            RAM=("memory", "mean"),
            Disk=("disk", "mean"),
        )
        .reset_index()
    )

    graph_data = process_usage.melt(
        id_vars="Process",
        value_vars=["CPU", "RAM", "Disk"],
        var_name="Resource",
        value_name="Usage (%)",
    )

    process_order = (
        process_usage["Process"].tolist()
    )

    resource_order = [
        "CPU",
        "RAM",
        "Disk",
    ]

    chart = (
        alt.Chart(graph_data)
        .mark_bar(
            size=22,
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3,
        )
        .encode(
            x=alt.X(
                "Process:N",
                title="Process",
                sort=process_order,
            ),
            xOffset=alt.XOffset(
                "Resource:N",
                sort=resource_order,
            ),
            y=alt.Y(
                "Usage (%):Q",
                title="Usage (%)",
                scale=alt.Scale(
                    domain=[0, 100]
                ),
            ),
            color=alt.Color(
                "Resource:N",
                title="Resource",
                sort=resource_order,
                scale=alt.Scale(
                    domain=resource_order,
                    range=[
                        "#60a5fa",
                        "#34d399",
                        "#fbbf24",
                    ],
                ),
            ),
            tooltip=[
                "Process:N",
                "Resource:N",
                alt.Tooltip(
                    "Usage (%):Q",
                    format=".2f",
                ),
            ],
        )
        .properties(height=300)
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    st.caption(
        "Each group shows the average Ubuntu WSL "
        "CPU usage, RAM usage and disk-space occupancy "
        "observed while that process executed. "
        "These are not exclusive per-process measurements."
    )


# ==========================================================
# SIMPLE RESOURCE GRAPH FOR SAVED MANUAL RUNS
# ==========================================================

def show_manual_resource_graph(readings):

    if not readings:
        st.info("No saved readings available.")
        return

    df = pd.DataFrame(readings)

    averages = pd.DataFrame({
        "Resource": [
            "CPU",
            "RAM",
            "Disk Space",
        ],
        "Usage (%)": [
            round(df["cpu"].mean(), 2),
            round(df["memory"].mean(), 2),
            round(df["disk"].mean(), 2),
        ],
    })

    chart = (
        alt.Chart(averages)
        .mark_bar(
            color="#60a5fa",
            size=40,
        )
        .encode(
            x=alt.X(
                "Resource:N",
                title=None,
                sort=[
                    "CPU",
                    "RAM",
                    "Disk Space",
                ],
            ),
            y=alt.Y(
                "Usage (%):Q",
                title="Average Usage (%)",
                scale=alt.Scale(
                    domain=[0, 100]
                ),
            ),
            tooltip=[
                "Resource:N",
                alt.Tooltip(
                    "Usage (%):Q",
                    format=".2f",
                ),
            ],
        )
        .properties(height=260)
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )


# ==========================================================
# SIMPLE GANTT CHART
# ==========================================================

def show_simple_gantt(results):

    if not results:
        return

    df = pd.DataFrame(results)

    df = df.dropna(
        subset=[
            "Start Time",
            "Completion Time",
        ]
    ).copy()

    if df.empty:
        return

    df["Start Time"] = pd.to_datetime(
        df["Start Time"]
    )

    df["Completion Time"] = pd.to_datetime(
        df["Completion Time"]
    )

    df = df.sort_values(
        "Start Time"
    ).reset_index(drop=True)

    base_time = df["Start Time"].min()

    df["Start (s)"] = (
        df["Start Time"] - base_time
    ).dt.total_seconds()

    df["Finish (s)"] = (
        df["Completion Time"] - base_time
    ).dt.total_seconds()

    process_order = df["Process"].tolist()

    chart = (
        alt.Chart(df)
        .mark_bar(
            size=35,
            color="#60a5fa",
            cornerRadius=3,
        )
        .encode(
            x=alt.X(
                "Start (s):Q",
                title="Time (seconds)",
                scale=alt.Scale(zero=True),
            ),
            x2="Finish (s):Q",
            y=alt.Y(
                "Process:N",
                title="Process",
                sort=process_order,
            ),
            tooltip=[
                "Process:N",
                "Workload:N",
                "Algorithm:N",
                alt.Tooltip(
                    "Start (s):Q",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Finish (s):Q",
                    format=".2f",
                ),
            ],
        )
        .properties(
            height=max(
                160,
                len(df) * 55,
            )
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )


# ==========================================================
# EXECUTION RESULTS DASHBOARD
# ==========================================================

def show_execution_results(results, readings):

    if not results:
        return

    st.subheader("Execution Results")

    df = pd.DataFrame(results)

    completed = df[
        df["State"] == "COMPLETED"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Workloads",
        len(df),
    )

    col2.metric(
        "Completed",
        len(completed),
    )

    col3.metric(
        "Failed",
        len(df) - len(completed),
    )

    # ------------------------------------------------------
    # PROCESS RESULTS
    # ------------------------------------------------------

    st.markdown("#### Process Execution Summary")

    summary = df[
        [
            "Process",
            "Workload",
            "Algorithm",
            "Execution Time",
            "Waiting Time",
            "Turnaround Time",
            "State",
        ]
    ].copy()

    summary = summary.rename(
        columns={
            "Execution Time": "Execution (s)",
            "Waiting Time": "Waiting (s)",
            "Turnaround Time": "Turnaround (s)",
        }
    )

    for column in [
        "Execution (s)",
        "Waiting (s)",
        "Turnaround (s)",
    ]:

        summary[column] = pd.to_numeric(
            summary[column],
            errors="coerce",
        ).round(2)

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------
    # SCHEDULING AVERAGES
    # ------------------------------------------------------

    if not completed.empty:

        avg_execution = pd.to_numeric(
            completed["Execution Time"],
            errors="coerce",
        ).mean()

        avg_waiting = pd.to_numeric(
            completed["Waiting Time"],
            errors="coerce",
        ).mean()

        avg_turnaround = pd.to_numeric(
            completed["Turnaround Time"],
            errors="coerce",
        ).mean()

        st.markdown("#### Scheduling Performance")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Average Execution Time",
            f"{avg_execution:.2f} s",
        )

        col2.metric(
            "Average Waiting Time",
            f"{avg_waiting:.2f} s",
        )

        col3.metric(
            "Average Turnaround Time",
            f"{avg_turnaround:.2f} s",
        )

    
    # ------------------------------------------------------
    # PROCESS-WISE RESOURCE USAGE
    # ------------------------------------------------------

    st.markdown("#### Resource Usage by Process")

    show_process_resource_graph(readings)

    # ------------------------------------------------------
    # OPTIONAL ERRORS
    # ------------------------------------------------------

    errors = [
        item
        for item in results
        if item.get("Execution Error")
        or item.get("Database Error")
    ]

    if errors:

        with st.expander("Execution and Database Errors"):

            for item in errors:

                st.write(
                    item["Process"],
                    item.get("Execution Error"),
                    item.get("Database Error"),
                )

    # No raw Resource Measurements table.
    # No overall average resource graph.


# ==========================================================
# AUTOMATIC LOAD SIMULATOR PAGE
# ==========================================================

def show_automatic_simulator():

    st.subheader("Automatic Load Simulator")

    st.write(
        "Generate workloads automatically, save them "
        "to MySQL, and execute them using the existing "
        "SysNexa scheduling system."
    )

    task_manager = get_task_manager()

    algorithm = st.selectbox(
        "Scheduling Algorithm",
        ALGORITHMS,
        key="sim_algorithm",
    )

    count = st.slider(
        "Number of Workloads",
        min_value=1,
        max_value=8,
        value=3,
        key="sim_count",
    )

    selected_loads = st.multiselect(
        "Load Types",
        LOAD_TYPES,
        default=["CPU Load"],
        key="sim_types",
    )

    col1, col2 = st.columns(2)

    with col1:

        duration = st.slider(
            "Workload Duration (seconds)",
            min_value=1,
            max_value=8,
            value=3,
            key="sim_duration",
        )

    with col2:

        memory_mb = st.slider(
            "Memory Allocation (MB)",
            min_value=1,
            max_value=16,
            value=4,
            key="sim_memory",
        )

    if "simulator_task_ids" not in st.session_state:
        st.session_state["simulator_task_ids"] = []

    if "simulator_results" not in st.session_state:
        st.session_state["simulator_results"] = []

    if "simulator_readings" not in st.session_state:
        st.session_state["simulator_readings"] = []

    # ------------------------------------------------------
    # GENERATE WORKLOADS
    # ------------------------------------------------------

    if st.button(
        "Generate and Save Workloads",
        type="primary",
        use_container_width=True,
        disabled=not selected_loads,
    ):

        try:

            tasks = create_simulator_tasks(
                count,
                duration,
                memory_mb,
                selected_loads,
                algorithm,
            )

            st.session_state["simulator_task_ids"] = [
                task.task_id
                for task in tasks
            ]

            st.session_state["simulator_results"] = []
            st.session_state["simulator_readings"] = []

            st.success(
                f"{len(tasks)} workloads saved to MySQL."
            )

        except Exception as error:

            st.error(
                f"Could not generate workloads: {error}"
            )

    generated_ids = st.session_state[
        "simulator_task_ids"
    ]

    generated_tasks = [
        task
        for task in task_manager.get_all_tasks()
        if task.task_id in generated_ids
    ]

    # ------------------------------------------------------
    # GENERATED WORKLOADS
    # ------------------------------------------------------

    if generated_tasks:

        st.markdown("#### Generated Workloads")

        preview = []

        for index, task in enumerate(
            generated_tasks,
            start=1,
        ):

            preview.append({
                "Process": f"P{index}",
                "Workload": task.workload_name,
                "Priority": task.priority,
                "State": task.state,
            })

        st.dataframe(
            pd.DataFrame(preview),
            use_container_width=True,
            hide_index=True,
        )

        ready_tasks = [
            task
            for task in generated_tasks
            if task.state == "READY"
        ]

        # --------------------------------------------------
        # SCHEDULING PREVIEW
        # --------------------------------------------------

        if ready_tasks:

            order = build_execution_order(
                ready_tasks,
                algorithm,
            )

            st.markdown("#### Scheduling Order")

            order_data = []

            for index, (task, selected) in enumerate(
                order,
                start=1,
            ):

                order_data.append({
                    "Process": f"P{index}",
                    "Workload": task.workload_name,
                    "Algorithm": selected,
                })

            st.dataframe(
                pd.DataFrame(order_data),
                use_container_width=True,
                hide_index=True,
            )

            if algorithm == "Round Robin":

                st.info(
                    "Round Robin currently selects whole "
                    "workloads. True time-sliced execution "
                    "requires preemption support."
                )

            # ----------------------------------------------
            # EXECUTE
            # ----------------------------------------------

            if st.button(
                "Execute Generated Workloads",
                type="primary",
                use_container_width=True,
            ):

                results, readings = execute_simulator_queue(
                    ready_tasks,
                    algorithm,
                )

                st.session_state["simulator_results"] = (
                    results
                )

                st.session_state["simulator_readings"] = (
                    readings
                )

                st.rerun()

    # ------------------------------------------------------
    # RESULTS
    # ------------------------------------------------------

    results = st.session_state["simulator_results"]
    readings = st.session_state["simulator_readings"]

    if results:

        show_execution_results(
            results,
            readings,
        )

    # ------------------------------------------------------
    # MYSQL VERIFICATION
    # ------------------------------------------------------

    with st.expander("MySQL Verification Commands"):

        st.code(
            "SELECT * FROM workloads;",
            language="sql",
        )

        st.code(
            "SELECT * FROM execution_history;",
            language="sql",
        )

        st.code(
            "SELECT * FROM resource_history;",
            language="sql",
        )


# ==========================================================
# MANUAL LOAD RUNTIME CONTROLLER
# ==========================================================

class RuntimeController:

    def __init__(self):

        self.generator = LoadGenerator()
        self.resource_manager = ResourceManager()

        self.stop_event = threading.Event()

        self.thread = None
        self.running = False
        self.completed_count = 0
        self.error = None
        self.current_scenario = None

    def start(
        self,
        test_name,
        scenarios,
        duration,
        memory_mb,
    ):

        if self.running:
            return False

        self.stop_event.clear()

        self.running = True
        self.completed_count = 0
        self.error = None

        self.thread = threading.Thread(
            target=self._execute,
            args=(
                test_name,
                list(scenarios),
                duration,
                memory_mb,
            ),
            daemon=True,
        )

        self.thread.start()

        return True

    def _execute(
        self,
        test_name,
        scenarios,
        duration,
        memory_mb,
    ):

        db = None

        try:

            db = DatabaseManager()

            for scenario in scenarios:

                if self.stop_event.is_set():
                    break

                self.current_scenario = scenario

                run_id = db.start_load_runtime(
                    test_name,
                    scenario,
                )

                run_status = "COMPLETED"

                try:

                    started = self.generator.start(
                        scenario=scenario,
                        duration_seconds=duration,
                        memory_mb=memory_mb,
                    )

                    if started is False:
                        raise RuntimeError(
                            "LoadGenerator could not start."
                        )

                    last_sample = 0.0

                    while self.generator.is_running():

                        if self.stop_event.is_set():
                            run_status = "STOPPED"
                            break

                        now = time.monotonic()

                        if now - last_sample >= 3:

                            resources = (
                                self.resource_manager.get_resources()
                            )

                            db.save_load_runtime_reading(
                                run_id,
                                resources["cpu"],
                                resources["memory"],
                                resources["memory_used"],
                                resources["memory_available"],
                                resources["disk"],
                                resources["disk_used"],
                                resources["disk_free"],
                            )

                            last_sample = now

                        self.stop_event.wait(0.2)

                    if self.stop_event.is_set():
                        run_status = "STOPPED"

                except Exception:
                    run_status = "FAILED"
                    raise

                finally:

                    self.generator.stop()

                    db.finish_load_runtime(
                        run_id,
                        run_status,
                    )

                if run_status == "COMPLETED":
                    self.completed_count += 1

        except Exception as error:
            self.error = str(error)

        finally:

            self.generator.stop()

            if db is not None:
                db.close()

            self.running = False
            self.current_scenario = None

    def stop(self):

        self.stop_event.set()

        self.generator.stop()

        if self.thread is not None:
            self.thread.join(timeout=10)


# ==========================================================
# MANUAL RESOURCE LOAD PAGE
# ==========================================================

def show_manual_load_runtime():

    st.subheader("Manual Resource Load")

    st.write(
        "Run CPU, Memory, Disk or Combined Load "
        "using the existing LoadGenerator."
    )

    if "runtime_controller" not in st.session_state:

        st.session_state["runtime_controller"] = (
            RuntimeController()
        )

    controller = st.session_state[
        "runtime_controller"
    ]

    scenarios = st.multiselect(
        "Select Scenarios",
        LOAD_TYPES,
        default=["CPU Load"],
        key="manual_scenarios",
    )

    duration = st.selectbox(
        "Duration (seconds)",
        [15, 30, 60, 90, 120],
        key="manual_duration",
    )

    memory_mb = st.selectbox(
        "Memory Allocation (MB)",
        [4, 8, 16, 24, 32],
        key="manual_memory",
    )

    test_name = st.text_input(
        "Test Name",
        value="Manual Load Test",
        key="manual_test_name",
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Start Runtime",
            type="primary",
            use_container_width=True,
            disabled=controller.running or not scenarios,
        ):

            controller.start(
                test_name,
                scenarios,
                duration,
                memory_mb,
            )

            st.success("Runtime started.")

    with col2:

        if st.button(
            "Stop Runtime",
            use_container_width=True,
            disabled=not controller.running,
        ):

            controller.stop()

            st.info("Stop requested.")

    if controller.running:

        st.info(
            f"Running: "
            f"{controller.current_scenario or 'Starting'}"
        )

        if st.button("Refresh Runtime Status"):
            st.rerun()

    else:

        st.metric(
            "Completed Scenarios",
            controller.completed_count,
        )

    if controller.error:
        st.error(controller.error)

    # ------------------------------------------------------
    # SAVED HISTORY
    # ------------------------------------------------------

    st.markdown("#### Saved Runtime History")

    try:

        db = DatabaseManager()

        try:

            history = db.get_load_runtime_history(
                limit=50
            )

            if history:

                history_df = pd.DataFrame(history)

                st.dataframe(
                    history_df,
                    use_container_width=True,
                    hide_index=True,
                )

                run_ids = [
                    item["run_id"]
                    for item in history
                ]

                selected_run = st.selectbox(
                    "Select Saved Runtime",
                    run_ids,
                )

                saved_readings = (
                    db.get_load_runtime_readings(
                        selected_run
                    )
                )

                if saved_readings:

                    normalized = []

                    for item in saved_readings:

                        normalized.append({
                            "cpu": float(
                                item.get("cpu_percent", 0)
                            ),
                            "memory": float(
                                item.get("memory_percent", 0)
                            ),
                            "disk": float(
                                item.get("disk_percent", 0)
                            ),
                        })

                    st.markdown(
                        "#### Saved Resource Usage"
                    )

                    show_manual_resource_graph(normalized)

            else:

                st.info(
                    "No saved runtime history yet."
                )

        finally:
            db.close()

    except Exception as error:

        st.warning(
            f"Could not load runtime history: {error}"
        )


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_load_runtime():

    st.title("SysNexa — Load Runtime Mode")

    st.caption(
        "Automatic workload scheduling, real execution, "
        "and process-wise resource monitoring."
    )

    automatic_tab, manual_tab = st.tabs([
        "Automatic Load Simulator",
        "Manual Resource Load",
    ])

    with automatic_tab:
        show_automatic_simulator()

    with manual_tab:
        show_manual_load_runtime()


if __name__ == "__main__":
    show_load_runtime()
