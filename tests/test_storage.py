
import sqlite3

import pytest

from src.storage.database import FactoryGuardDatabase
from src.storage.event_logger import EventLogger
from src.storage.diagnostic_store import DiagnosticStore
from src.storage.recovery_logger import RecoveryLogger


@pytest.fixture
def database(tmp_path):
    return FactoryGuardDatabase(
        tmp_path / "test_factoryguard.db"
    )


def test_database_initializes(database):
    tables = database.fetch_all(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """
    )

    names = {row["name"] for row in tables}

    assert "events" in names
    assert "diagnostics" in names
    assert "recovery_actions" in names


def test_database_health(database):
    assert database.health_check() is True


def test_event_logging(database):
    logger = EventLogger(database)

    event_id = logger.log(
        "FAULT",
        "Overcurrent detected",
        machine_id="CONV-001",
        machine_state="STOPPED_FAULT",
    )

    assert event_id > 0

    events = logger.recent()

    assert len(events) == 1
    assert events[0]["event_type"] == "FAULT"


def test_event_persistence_after_reopen(database):
    logger = EventLogger(database)
    logger.log("SYSTEM", "Persistent test")

    reopened = EventLogger(
        FactoryGuardDatabase(database.db_path)
    )

    assert len(reopened.recent()) == 1


def test_diagnostic_persistence(database):
    store = DiagnosticStore(database)

    report = {
        "machine_id": "CONV-001",
        "machine_state": "STOPPED_FAULT",
        "primary_diagnosis": "CONVEYOR_JAM",
        "severity": "CRITICAL",
        "restart_authorized": False,
        "evidence": ["Overcurrent", "Low RPM"],
        "limitations": [],
    }

    report_id = store.save(report)

    assert report_id > 0

    saved = store.recent()[0]["report"]

    assert saved["primary_diagnosis"] == "CONVEYOR_JAM"
    assert saved["restart_authorized"] is False


def test_invalid_diagnostic_rejected(database):
    store = DiagnosticStore(database)

    with pytest.raises(ValueError):
        store.save({
            "machine_id": "CONV-001",
        })


def test_recovery_logging(database):
    logger = RecoveryLogger(database)

    record_id = logger.log(
        machine_id="CONV-001",
        action="RESTART_REQUEST",
        result="REQUESTED",
        machine_state="READY_FOR_REVIEW",
    )

    assert record_id > 0

    rows = logger.recent()

    assert rows[0]["action"] == "RESTART_REQUEST"


def test_recovery_history_order(database):
    logger = RecoveryLogger(database)

    logger.log(
        "CONV-001",
        "ACKNOWLEDGE",
        "SUCCESS",
        "STOPPED_FAULT",
    )

    logger.log(
        "CONV-001",
        "RESTART_REQUEST",
        "REQUESTED",
        "READY_FOR_REVIEW",
    )

    rows = logger.recent()

    assert rows[0]["action"] == "RESTART_REQUEST"
    assert rows[1]["action"] == "ACKNOWLEDGE"


def test_sql_parameterization(database):
    logger = EventLogger(database)

    message = "'; DROP TABLE events; --"

    logger.log("TEST", message)

    assert logger.recent()[0]["message"] == message

    tables = database.fetch_all(
        """
        SELECT name FROM sqlite_master
        WHERE name='events'
        """
    )

    assert len(tables) == 1


def test_history_limit(database):
    logger = EventLogger(database)

    for i in range(10):
        logger.log("TEST", f"Event {i}")

    assert len(logger.recent(limit=3)) == 3


def test_separate_tables(database):
    EventLogger(database).log(
        "FAULT", "Jam detected"
    )

    RecoveryLogger(database).log(
        "CONV-001",
        "RESTART_REQUEST",
        "REJECTED",
        "STOPPED_FAULT",
    )

    assert len(EventLogger(database).recent()) == 1
    assert len(RecoveryLogger(database).recent()) == 1


def test_database_failure(tmp_path):
    bad_path = tmp_path / "directory_as_database"
    bad_path.mkdir()

    with pytest.raises(sqlite3.Error):
        FactoryGuardDatabase(bad_path)
