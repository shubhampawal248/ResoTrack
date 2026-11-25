
import os
import uuid
from contextlib import contextmanager

import mysql.connector


class DatabaseManager:

    def __init__(self):

        self.host = os.getenv("DB_HOST", "127.0.0.1")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.database = os.getenv("DB_NAME", "sysnexa")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "singh")

        self.connection = None

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def _new_connection(self):

        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def connect(self):

        if (
            self.connection is None
            or not self.connection.is_connected()
        ):
            self.connection = self._new_connection()

        return self.connection

    def close(self):

        if self.connection is not None:
            self.connection.close()
            self.connection = None

    # =========================================================
    # COMMON DATABASE WRITE OPERATION
    # =========================================================

    def _write(self, query, parameters=()):

        connection = self.connect()
        cursor = connection.cursor()

        try:

            cursor.execute(query, parameters)

            result = {
                "rowcount": cursor.rowcount,
                "lastrowid": cursor.lastrowid
            }

            connection.commit()

            return result

        except Exception:

            connection.rollback()
            raise

        finally:

            cursor.close()

    # =========================================================
    # COMMON DATABASE READ OPERATION
    # =========================================================

    def _read(self, query, parameters=()):

        connection = self._new_connection()
        cursor = None

        try:

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, parameters)

            return cursor.fetchall()

        finally:

            if cursor is not None:
                cursor.close()

            connection.close()

    # =========================================================
    # TRANSACTION MANAGEMENT
    # =========================================================

    @contextmanager
    def transaction(self):

        connection = self._new_connection()
        cursor = None

        try:

            connection.start_transaction()

            cursor = connection.cursor()

            yield cursor

            connection.commit()

        except Exception:

            connection.rollback()
            raise

        finally:

            if cursor is not None:
                cursor.close()

            connection.close()

    # =========================================================
    # CREATE ALL REQUIRED TABLES
    # =========================================================

    def create_tables(self):

        connection = self.connect()
        cursor = connection.cursor()

        try:

            # WORKLOAD TABLE

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workloads (
                    task_id VARCHAR(100) PRIMARY KEY,
                    workload_name VARCHAR(150) NOT NULL,
                    workload_type VARCHAR(50),
                    priority INT DEFAULT 1,
                    status VARCHAR(30) DEFAULT 'READY',
                    submitted_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)

            # EXECUTION HISTORY TABLE

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    execution_id INT AUTO_INCREMENT PRIMARY KEY,
                    task_id VARCHAR(100) NOT NULL,
                    pid INT,
                    execution_time_seconds DECIMAL(10,3),
                    cpu_time_seconds DECIMAL(10,3),
                    cpu_percent DECIMAL(5,2),
                    peak_memory_mb DECIMAL(12,2),
                    exit_code INT,
                    result_status VARCHAR(30),
                    executed_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (task_id)
                        REFERENCES workloads(task_id)

                ) ENGINE=InnoDB
            """)

            # RESOURCE HISTORY TABLE

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resource_history (
                    reading_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    cpu_percent DECIMAL(5,2),
                    memory_percent DECIMAL(5,2),
                    disk_percent DECIMAL(5,2),
                    recorded_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)

            # QUERY HISTORY TABLE

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    query_id INT AUTO_INCREMENT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    execution_time_ms DECIMAL(12,3),
                    status VARCHAR(20) NOT NULL,
                    rows_returned INT DEFAULT 0,
                    error_message TEXT,
                    executed_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)

            # LOAD RUNTIME RUNS TABLE

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS load_runtime_runs (
                    run_id INT AUTO_INCREMENT PRIMARY KEY,
                    test_name VARCHAR(150) NOT NULL,
                    scenario_name VARCHAR(100) NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    duration_seconds INT,
                    average_cpu DECIMAL(5,2),
                    peak_cpu DECIMAL(5,2),
                    average_memory DECIMAL(5,2),
                    peak_memory DECIMAL(5,2),
                    average_disk DECIMAL(5,2),
                    peak_disk DECIMAL(5,2),
                    status VARCHAR(30) DEFAULT 'RUNNING'
                ) ENGINE=InnoDB
            """)

            # LOAD RUNTIME READINGS TABLE

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS load_runtime_readings (
                    reading_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    run_id INT NOT NULL,

                    cpu_percent DECIMAL(5,2),

                    memory_percent DECIMAL(5,2),
                    memory_used BIGINT,
                    memory_available BIGINT,

                    disk_percent DECIMAL(5,2),
                    disk_used BIGINT,
                    disk_free BIGINT,

                    recorded_at DATETIME
                        DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (run_id)
                        REFERENCES load_runtime_runs(run_id)
                        ON DELETE CASCADE

                ) ENGINE=InnoDB
            """)

            # TRANSACTION DEMONSTRATION TABLE

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_demo (
                    demo_id VARCHAR(100) PRIMARY KEY,
                    description VARCHAR(200) NOT NULL,
                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)

            # NEW: ACTUAL WORKLOAD TRANSACTION HISTORY

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workload_transaction_history (
                    transaction_id VARCHAR(100) PRIMARY KEY,
                    task_id VARCHAR(100) NOT NULL,
                    workload_name VARCHAR(150),
                    workload_type VARCHAR(50),
                    execution_id INT,
                    transaction_status VARCHAR(30) NOT NULL,
                    workload_status VARCHAR(30),
                    error_message TEXT,
                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP,

                    INDEX idx_transaction_task (task_id),
                    INDEX idx_transaction_status (transaction_status)

                ) ENGINE=InnoDB
            """)

            connection.commit()

            # SUPPORT OLDER DATABASE SCHEMAS

            cursor.execute("""
                SHOW COLUMNS FROM load_runtime_runs
            """)

            run_columns = {
                row[0] for row in cursor.fetchall()
            }

            if "test_name" not in run_columns:

                cursor.execute("""
                    ALTER TABLE load_runtime_runs
                    ADD COLUMN test_name VARCHAR(150)
                    NOT NULL DEFAULT 'Runtime_Test'
                """)

            cursor.execute("""
                SHOW COLUMNS FROM load_runtime_readings
            """)

            reading_columns = {
                row[0] for row in cursor.fetchall()
            }

            new_reading_columns = {
                "memory_used": "BIGINT",
                "memory_available": "BIGINT",
                "disk_used": "BIGINT",
                "disk_free": "BIGINT"
            }

            for column_name, column_type in (
                new_reading_columns.items()
            ):

                if column_name not in reading_columns:

                    cursor.execute(f"""
                        ALTER TABLE load_runtime_readings
                        ADD COLUMN {column_name} {column_type}
                    """)

            connection.commit()

        except Exception:

            connection.rollback()
            raise

        finally:

            cursor.close()

    # =========================================================
    # VERIFY TRANSACTIONAL STORAGE ENGINE
    # =========================================================

    def verify_transaction_support(self):

        connection = self._new_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute("""
                SELECT TABLE_NAME, ENGINE
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME IN (
                    'workloads',
                    'execution_history',
                    'transaction_demo',
                    'workload_transaction_history'
                )
            """, (self.database,))

            rows = cursor.fetchall()

            engines = {
                row["TABLE_NAME"]: row["ENGINE"]
                for row in rows
            }

            required_tables = (
                "workloads",
                "execution_history",
                "transaction_demo",
                "workload_transaction_history"
            )

            for table in required_tables:

                engine = engines.get(table)

                if not engine or engine.lower() != "innodb":

                    raise RuntimeError(
                        f"{table} must use InnoDB "
                        "for transaction support."
                    )

            return engines

        finally:

            cursor.close()
            connection.close()

    # =========================================================
    # INSERT NEW WORKLOAD
    # =========================================================

    def insert_workload(self, task):

        self._write("""
            INSERT INTO workloads (
                task_id,
                workload_name,
                workload_type,
                priority,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            task.task_id,
            task.workload_name,
            task.workload_type,
            task.priority,
            task.state
        ))

    # =========================================================
    # UPDATE WORKLOAD STATUS
    # =========================================================

    def update_workload_status(self, task):

        result = self._write("""
            UPDATE workloads
            SET status = %s
            WHERE task_id = %s
        """, (
            task.state,
            task.task_id
        ))

        return result["rowcount"]

    # =========================================================
    # PREPARE EXECUTION VALUES
    # =========================================================

    def _execution_values(self, task):

        memory_mb = (
            task.memory_peak_bytes / (1024 * 1024)
            if task.memory_peak_bytes is not None
            else None
        )

        return (
            task.task_id,
            task.pid,
            task.execution_time,
            task.cpu_time_seconds,
            task.cpu_percent,
            memory_mb,
            task.exit_code,
            task.state
        )

    # =========================================================
    # EXECUTION HISTORY INSERT QUERY
    # =========================================================

    def _execution_insert_query(self):

        return """
            INSERT INTO execution_history (
                task_id,
                pid,
                execution_time_seconds,
                cpu_time_seconds,
                cpu_percent,
                peak_memory_mb,
                exit_code,
                result_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

    # =========================================================
    # SAVE EXECUTION HISTORY
    # =========================================================

    def save_execution_history(self, task):

        self._write(
            self._execution_insert_query(),
            self._execution_values(task)
        )

    # =========================================================
    # NEW: INSERT WORKLOAD TRANSACTION RECORD
    # =========================================================

    def _insert_transaction_record(
        self,
        cursor,
        transaction_id,
        task,
        execution_id,
        transaction_status,
        error_message=None
    ):

        cursor.execute("""
            INSERT INTO workload_transaction_history (
                transaction_id,
                task_id,
                workload_name,
                workload_type,
                execution_id,
                transaction_status,
                workload_status,
                error_message
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            transaction_id,
            task.task_id,
            task.workload_name,
            task.workload_type,
            execution_id,
            transaction_status,
            task.state,
            error_message
        ))

    # =========================================================
    # NEW: ATOMIC WORKLOAD EXECUTION TRANSACTION
    # =========================================================

    def save_execution_transaction(self, task):

        transaction_id = f"WTXN-{uuid.uuid4().hex}"

        execution_id = None

        try:

            self.verify_transaction_support()

            with self.transaction() as cursor:

                # STEP 1: LOCK WORKLOAD RECORD

                cursor.execute("""
                    SELECT task_id
                    FROM workloads
                    WHERE task_id = %s
                    FOR UPDATE
                """, (task.task_id,))

                workload = cursor.fetchone()

                if workload is None:

                    raise ValueError(
                        f"Workload {task.task_id} does not exist."
                    )

                # STEP 2: UPDATE WORKLOAD STATUS

                cursor.execute("""
                    UPDATE workloads
                    SET status = %s
                    WHERE task_id = %s
                """, (
                    task.state,
                    task.task_id
                ))

                # STEP 3: SAVE EXECUTION HISTORY

                cursor.execute(
                    self._execution_insert_query(),
                    self._execution_values(task)
                )

                execution_id = cursor.lastrowid

                # STEP 4: SAVE ACTUAL TRANSACTION RECORD

                self._insert_transaction_record(
                    cursor=cursor,
                    transaction_id=transaction_id,
                    task=task,
                    execution_id=execution_id,
                    transaction_status="COMMITTED",
                    error_message=None
                )

            # COMMIT COMPLETED SUCCESSFULLY

            return {
                "status": "COMMITTED",
                "transaction_id": transaction_id,
                "task_id": task.task_id,
                "execution_id": execution_id
            }

        except Exception as error:

            # CHECK WHETHER COMMIT ACTUALLY SUCCEEDED
            # IN CASE THE CONNECTION FAILED DURING COMMIT

            try:

                existing_records = self._read("""
                    SELECT transaction_status, execution_id
                    FROM workload_transaction_history
                    WHERE transaction_id = %s
                """, (transaction_id,))

                if (
                    existing_records
                    and existing_records[0]["transaction_status"]
                    == "COMMITTED"
                ):

                    return {
                        "status": "COMMITTED",
                        "transaction_id": transaction_id,
                        "task_id": task.task_id,
                        "execution_id":
                            existing_records[0]["execution_id"]
                    }

            except Exception:

                # Verification may fail if MySQL is unavailable.

                pass

            # SAVE FAILED ATTEMPT IN A SEPARATE TRANSACTION

            try:

                with self.transaction() as cursor:

                    self._insert_transaction_record(
                        cursor=cursor,
                        transaction_id=transaction_id,
                        task=task,
                        execution_id=None,
                        transaction_status="SAVE FAILED",
                        error_message=str(error)
                    )

            except Exception as logging_error:

                raise RuntimeError(
                    f"Workload database save failed: {error}. "
                    f"Transaction logging also failed: "
                    f"{logging_error}"
                ) from error

            raise

    # =========================================================
    # NEW: FETCH ACTUAL WORKLOAD TRANSACTION HISTORY
    # =========================================================

    def get_workload_transaction_history(self):

        return self._read("""
            SELECT
                transaction_id,
                task_id,
                workload_name,
                workload_type,
                execution_id,
                transaction_status,
                workload_status,
                error_message,
                created_at
            FROM workload_transaction_history
            ORDER BY created_at DESC, transaction_id DESC
        """)

    # =========================================================
    # NEW: FETCH TRANSACTION SUMMARY
    # =========================================================

    def get_workload_transaction_summary(self):

        records = self._read("""
            SELECT
                COUNT(*) AS total_transactions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN transaction_status = 'COMMITTED'
                            THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS committed_transactions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN transaction_status = 'SAVE FAILED'
                            THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS failed_transactions

            FROM workload_transaction_history
        """)

        if records:

            return {
                "total_transactions":
                    int(records[0]["total_transactions"]),

                "committed_transactions":
                    int(records[0]["committed_transactions"]),

                "failed_transactions":
                    int(records[0]["failed_transactions"])
            }

        return {
            "total_transactions": 0,
            "committed_transactions": 0,
            "failed_transactions": 0
        }

    # =========================================================
    # ACTUAL COMMIT AND ROLLBACK DEMONSTRATION
    # =========================================================

    def demonstrate_transaction(self, force_failure=False):

        self.verify_transaction_support()

        transaction_id = f"TXN-{uuid.uuid4().hex}"

        first_id = transaction_id + "-1"
        second_id = transaction_id + "-2"

        steps = []
        error_message = None

        try:

            with self.transaction() as cursor:

                steps.append("START TRANSACTION")

                # FIRST DATABASE OPERATION

                cursor.execute("""
                    INSERT INTO transaction_demo (
                        demo_id,
                        description
                    )
                    VALUES (%s, %s)
                """, (
                    first_id,
                    "First transaction operation"
                ))

                steps.append(
                    "First INSERT executed successfully"
                )

                # SECOND DATABASE OPERATION

                if force_failure:

                    # Intentionally reuse the primary key.
                    # MySQL raises a duplicate-key error.

                    cursor.execute("""
                        INSERT INTO transaction_demo (
                            demo_id,
                            description
                        )
                        VALUES (%s, %s)
                    """, (
                        first_id,
                        "Duplicate primary key test"
                    ))

                else:

                    cursor.execute("""
                        INSERT INTO transaction_demo (
                            demo_id,
                            description
                        )
                        VALUES (%s, %s)
                    """, (
                        second_id,
                        "Second transaction operation"
                    ))

                steps.append(
                    "Second INSERT executed successfully"
                )

            transaction_status = "COMMITTED"

            steps.append("COMMIT executed successfully")

        except mysql.connector.IntegrityError as error:

            if not force_failure or error.errno != 1062:
                raise

            transaction_status = "ROLLED BACK"

            error_message = str(error)

            steps.append(
                "Second INSERT failed: Duplicate primary key"
            )

            steps.append("ROLLBACK completed")

        # VERIFY ACTUAL DATABASE RESULT
        # USING A SEPARATE CONNECTION

        verification_connection = self._new_connection()

        verification_cursor = (
            verification_connection.cursor(dictionary=True)
        )

        try:

            verification_cursor.execute("""
                SELECT *
                FROM transaction_demo
                WHERE demo_id IN (%s, %s)
                ORDER BY demo_id
            """, (
                first_id,
                second_id
            ))

            records = verification_cursor.fetchall()

        finally:

            verification_cursor.close()
            verification_connection.close()

        expected_records = (
            0 if force_failure else 2
        )

        verified = len(records) == expected_records

        return {
            "transaction_id": transaction_id,
            "status": transaction_status,
            "steps": steps,
            "error": error_message,
            "records_saved": len(records),
            "expected_records": expected_records,
            "verified": verified,
            "records": records
        }

    # =========================================================
    # FETCH TRANSACTION DEMONSTRATION RECORDS
    # =========================================================

    def get_transaction_demo_history(self, limit=50):

        limit = max(1, min(int(limit), 500))

        return self._read("""
            SELECT *
            FROM transaction_demo
            ORDER BY created_at DESC, demo_id DESC
            LIMIT %s
        """, (limit,))

    # =========================================================
    # SAVE RESOURCE MONITORING DATA
    # =========================================================

    def save_resource_history(
        self,
        cpu_percent,
        memory_percent,
        disk_percent
    ):

        self._write("""
            INSERT INTO resource_history (
                cpu_percent,
                memory_percent,
                disk_percent
            )
            VALUES (%s, %s, %s)
        """, (
            cpu_percent,
            memory_percent,
            disk_percent
        ))

    # =========================================================
    # SAVE DATABASE QUERY HISTORY
    # =========================================================

    def save_query_history(
        self,
        query_text,
        execution_time_ms,
        status,
        rows_returned=0,
        error_message=None
    ):

        self._write("""
            INSERT INTO query_history (
                query_text,
                execution_time_ms,
                status,
                rows_returned,
                error_message
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            query_text,
            execution_time_ms,
            status,
            rows_returned,
            error_message
        ))

    # =========================================================
    # FETCH QUERY HISTORY
    # =========================================================

    def get_query_history(self, limit=50):

        limit = max(1, min(int(limit), 500))

        return self._read("""
            SELECT *
            FROM query_history
            ORDER BY executed_at DESC, query_id DESC
            LIMIT %s
        """, (limit,))

    # =========================================================
    # FETCH ALL WORKLOADS
    # =========================================================

    def get_workloads(self):

        return self._read("""
            SELECT *
            FROM workloads
            ORDER BY submitted_at DESC
        """)

    # =========================================================
    # FETCH EXECUTION HISTORY
    # =========================================================

    def get_execution_history(self, task_id=None):

        if task_id is None:

            return self._read("""
                SELECT *
                FROM execution_history
                ORDER BY executed_at DESC
            """)

        return self._read("""
            SELECT *
            FROM execution_history
            WHERE task_id = %s
            ORDER BY executed_at DESC
        """, (task_id,))

    # =========================================================
    # FETCH RESOURCE HISTORY
    # =========================================================

    def get_resource_history(self, limit=100):

        limit = max(1, min(int(limit), 1000))

        return self._read("""
            SELECT *
            FROM resource_history
            ORDER BY recorded_at DESC
            LIMIT %s
        """, (limit,))

    # =========================================================
    # START LOAD RUNTIME
    # =========================================================

    def start_load_runtime(self, test_name, scenario_name):

        result = self._write("""
            INSERT INTO load_runtime_runs (
                test_name,
                scenario_name,
                start_time,
                status
            )
            VALUES (%s, %s, NOW(), 'RUNNING')
        """, (
            test_name,
            scenario_name
        ))

        return result["lastrowid"]

    # =========================================================
    # SAVE LOAD RUNTIME READINGS
    # =========================================================

    def save_load_runtime_reading(
        self,
        run_id,
        cpu_percent,
        memory_percent,
        memory_used,
        memory_available,
        disk_percent,
        disk_used,
        disk_free
    ):

        self._write("""
            INSERT INTO load_runtime_readings (
                run_id,
                cpu_percent,
                memory_percent,
                memory_used,
                memory_available,
                disk_percent,
                disk_used,
                disk_free
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            run_id,
            cpu_percent,
            memory_percent,
            memory_used,
            memory_available,
            disk_percent,
            disk_used,
            disk_free
        ))

    # =========================================================
    # FINISH LOAD RUNTIME
    # =========================================================

    def finish_load_runtime(self, run_id, status):

        result = self._write("""
            UPDATE load_runtime_runs

            SET

                end_time = NOW(),

                duration_seconds = TIMESTAMPDIFF(
                    SECOND, start_time, NOW()
                ),

                average_cpu = (
                    SELECT AVG(cpu_percent)
                    FROM load_runtime_readings
                    WHERE run_id = %s
                ),

                peak_cpu = (
                    SELECT MAX(cpu_percent)
                    FROM load_runtime_readings
                    WHERE run_id = %s
                ),

                average_memory = (
                    SELECT AVG(memory_percent)
                    FROM load_runtime_readings
                    WHERE run_id = %s
                ),

                peak_memory = (
                    SELECT MAX(memory_percent)
                    FROM load_runtime_readings
                    WHERE run_id = %s
                ),

                average_disk = (
                    SELECT AVG(disk_percent)
                    FROM load_runtime_readings
                    WHERE run_id = %s
                ),

                peak_disk = (
                    SELECT MAX(disk_percent)
                    FROM load_runtime_readings
                    WHERE run_id = %s
                ),

                status = %s

            WHERE run_id = %s

        """, (
            run_id,
            run_id,
            run_id,
            run_id,
            run_id,
            run_id,
            status,
            run_id
        ))

        return result["rowcount"]

    # =========================================================
    # FETCH LOAD RUNTIME HISTORY
    # =========================================================

    def get_load_runtime_history(self, limit=100):

        limit = max(1, min(int(limit), 1000))

        return self._read("""
            SELECT *
            FROM load_runtime_runs
            ORDER BY start_time DESC, run_id DESC
            LIMIT %s
        """, (limit,))

    # =========================================================
    # FETCH LOAD RUNTIME READINGS
    # =========================================================

    def get_load_runtime_readings(self, run_id):

        return self._read("""
            SELECT *
            FROM load_runtime_readings
            WHERE run_id = %s
            ORDER BY recorded_at ASC, reading_id ASC
        """, (run_id,))
