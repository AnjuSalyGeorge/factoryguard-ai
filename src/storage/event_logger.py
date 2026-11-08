
import json
from datetime import datetime, timezone

from src.storage.database import FactoryGuardDatabase


def utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")


class EventLogger:
    def __init__(self, database=None):
        self.database = (
            database
            if database is not None
            else FactoryGuardDatabase()
        )

    def log(
        self,
        event_type,
        message,
        status="INFO",
        machine_id=None,
        machine_state=None,
        details=None,
    ):
        timestamp = utc_now()

        with self.database.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO events (
                    timestamp,
                    event_type,
                    status,
                    message,
                    machine_id,
                    machine_state,
                    details_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    event_type,
                    status,
                    message,
                    machine_id,
                    machine_state,
                    json.dumps(details, default=str)
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
            FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
