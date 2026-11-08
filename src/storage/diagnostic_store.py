
import json

from src.storage.database import FactoryGuardDatabase
from src.storage.event_logger import utc_now


class DiagnosticStore:
    def __init__(self, database=None):
        self.database = (
            database
            if database is not None
            else FactoryGuardDatabase()
        )

    def save(self, report):
        if hasattr(report, "to_dict"):
            report = report.to_dict()

        if not isinstance(report, dict):
            raise TypeError(
                "Diagnostic report must be a dictionary"
            )

        required = (
            "machine_id",
            "machine_state",
            "primary_diagnosis",
            "severity",
        )

        for field in required:
            if field not in report:
                raise ValueError(
                    f"Missing diagnostic field: {field}"
                )

        with self.database.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO diagnostics (
                    timestamp,
                    machine_id,
                    machine_state,
                    primary_diagnosis,
                    severity,
                    report_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now(),
                    report["machine_id"],
                    report["machine_state"],
                    report["primary_diagnosis"],
                    report["severity"],
                    json.dumps(
                        report,
                        default=str,
                    ),
                ),
            )

            return cursor.lastrowid

    def recent(self, limit=50):
        limit = max(1, min(int(limit), 1000))

        rows = self.database.fetch_all(
            """
            SELECT *
            FROM diagnostics
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        for row in rows:
            row["report"] = json.loads(
                row["report_json"]
            )

        return rows
