
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path("data/factoryguard.db")


class FactoryGuardDatabase:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = str(db_path)

        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        self.initialize()

    def connect(self):
        connection = sqlite3.connect(
            self.db_path,
            timeout=10,
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA busy_timeout = 10000"
        )

        return connection

    def initialize(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    machine_id TEXT,
                    machine_state TEXT,
                    details_json TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS diagnostics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    machine_id TEXT NOT NULL,
                    machine_state TEXT NOT NULL,
                    primary_diagnosis TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    report_json TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS recovery_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    machine_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL,
                    machine_state TEXT NOT NULL,
                    details_json TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp
                ON events(timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recovery_timestamp
                ON recovery_actions(timestamp)
            """)

    def fetch_all(self, query, parameters=()):
        with self.connect() as conn:
            rows = conn.execute(
                query,
                parameters,
            ).fetchall()

        return [dict(row) for row in rows]

    # Day 9 - Step 11: SQLite health check
    def health_check(self):
        try:
            with self.connect() as conn:
                conn.execute(
                    "SELECT 1"
                ).fetchone()

            return True

        except sqlite3.Error:
            return False
