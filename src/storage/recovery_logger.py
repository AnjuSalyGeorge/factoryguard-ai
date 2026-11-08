
import json

from src.storage.database import FactoryGuardDatabase
from src.storage.event_logger import utc_now


class RecoveryLogger:
    def __init__(self, database=None):
        self.database = (
            database
            if database is not None
            else FactoryGuardDatabase()
        )

    def log(
        self,
        machine_id,
        action,
        result,
        machine_state,
        details=None,
    ):
        with self.database.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO recovery_actions (
                    timestamp,
                    machine_id,
                    action,
                    result,
                    machine_state,
                    details_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now(),
                    machine_id,
                    action,
                    result,
                    machine_state,
                    json.dumps(
                        details,
                        default=str,
                    )
                    if details is not None
                    else None,
                ),
            )

            return cursor.lastrowid

    def recent(self, limit=100):
        limit = max(1, min(int(limit), 1000))

        return self.database.fetch_all(
            """
            SELECT *
            FROM recovery_actions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
