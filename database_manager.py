import os
import psycopg2


class DatabaseManager:

    def __init__(self):

        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "sysnexa")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")

        self.connection = None

    def connect(self):

        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

        return self.connection

    def close(self):

        if self.connection:
            self.connection.close()
            self.connection = None

    def create_tables(self):

        if self.connection is None:
            self.connect()

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processes (
                process_id SERIAL PRIMARY KEY,
                task_id VARCHAR(100),
                process_name VARCHAR(200),
                workload_type VARCHAR(50),
                priority INT,
                state VARCHAR(30),
                pid INT,
                arrival_time TIMESTAMP,
                start_time TIMESTAMP,
                completion_time TIMESTAMP,
                exit_code INT,
                retry_count INT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_usage (
                usage_id SERIAL PRIMARY KEY,
                task_id VARCHAR(100),
                pid INT,
                cpu_usage FLOAT,
                memory_usage FLOAT,
                disk_usage FLOAT,
                timestamp TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_log (
                failure_id SERIAL PRIMARY KEY,
                task_id VARCHAR(100),
                exit_code INT,
                retry_count INT,
                failure_time TIMESTAMP
            );
        """)

        self.connection.commit()
        cursor.close()

    def insert_process(self, task):

        if self.connection is None:
            self.connect()

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO processes (
                task_id,
                process_name,
                workload_type,
                priority,
                state,
                pid,
                arrival_time,
                start_time,
                completion_time,
                exit_code,
                retry_count
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            task.task_id,
            task.workload_name,
            task.workload_type,
            task.priority,
            task.state,
            task.pid,
            task.arrival_time,
            task.start_time,
            task.completion_time,
            task.exit_code,
            task.retry_count
        ))

        self.connection.commit()
        cursor.close()

    def get_workload_history(self, workload_name):

        if self.connection is None:
            self.connect()

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT
                EXTRACT(
                    EPOCH FROM
                    (completion_time - start_time)
                ) AS execution_time
            FROM processes
            WHERE process_name = %s
            AND state = 'COMPLETED'
        """, (workload_name,))

        rows = cursor.fetchall()

        cursor.close()

        return [
            {"execution_time": row[0]}
            for row in rows
        ]

    def save_failure(self, task):

        if self.connection is None:
            self.connect()

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO failure_log (
                task_id,
                exit_code,
                retry_count,
                failure_time
            )
            VALUES (%s, %s, %s, %s)
        """, (
            task.task_id,
            task.exit_code,
            task.retry_count,
            task.completion_time
        ))

        self.connection.commit()
        cursor.close()