
import tempfile
import time
from pathlib import Path

from src.storage.database import FactoryGuardDatabase
from src.storage.event_logger import EventLogger
from src.storage.diagnostic_store import DiagnosticStore
from src.storage.recovery_logger import RecoveryLogger


def main():
    print("=" * 65)
    print("FACTORYGUARD AI — DAY 9 SQLITE DEMO")
    print("=" * 65)

    with tempfile.TemporaryDirectory(
        ignore_cleanup_errors=True
    ) as directory:
        db_path = Path(directory) / "factoryguard_demo.db"

        database = FactoryGuardDatabase(db_path)

        events = EventLogger(database)
        diagnostics = DiagnosticStore(database)
        recovery = RecoveryLogger(database)

        print("\n1. LOGGING FAULT EVENT")

        events.log(
            event_type="FAULT",
            message="Conveyor jam detected",
            status="WARNING",
            machine_id="CONV-001",
            machine_state="STOPPED_FAULT",
            details={
                "faults": ["OVERCURRENT", "LOW_RPM"]
            },
        )

        print("\n2. SAVING DIAGNOSTIC REPORT")

        diagnostics.save({
            "machine_id": "CONV-001",
            "machine_state": "STOPPED_FAULT",
            "primary_diagnosis": "CONVEYOR_JAM",
            "severity": "CRITICAL",
            "evidence": [
                "Overcurrent",
                "Low RPM",
            ],
            "restart_authorized": False,
        })

        print("\n3. LOGGING RECOVERY ACTIONS")

        recovery.log(
            "CONV-001",
            "ACKNOWLEDGE_FAULT",
            "SUCCESS",
            "STOPPED_FAULT",
        )

        recovery.log(
            "CONV-001",
            "RESTART_REQUEST",
            "REQUESTED",
            "READY_FOR_REVIEW",
        )

        recovery.log(
            "CONV-001",
            "RESTART_OUTCOME",
            "SUCCESS",
            "RUNNING",
        )

        print("\n4. REOPENING DATABASE")

        reopened = FactoryGuardDatabase(db_path)

        stored_events = EventLogger(reopened).recent()
        stored_diagnostics = DiagnosticStore(
            reopened
        ).recent()
        stored_recovery = RecoveryLogger(
            reopened
        ).recent()

        print("Events:", len(stored_events))
        print("Diagnostics:", len(stored_diagnostics))
        print("Recovery actions:", len(stored_recovery))

        assert len(stored_events) == 1
        assert len(stored_diagnostics) == 1
        assert len(stored_recovery) == 3

        print("\nDAY 9 SQLITE DEMO PASSED")

        # Allow Windows to release SQLite file handles
        # before temporary-directory cleanup.
        time.sleep(0.5)


if __name__ == "__main__":
    main()
