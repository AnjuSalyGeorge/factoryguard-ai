
from datetime import datetime, timezone


SENSOR_FIELDS = {
    "temperature_c": "Temperature (°C)",
    "current_a": "Current (A)",
    "vibration_mm_s": "Vibration (mm/s)",
    "rpm": "RPM",
}


def normalize_status(status: dict) -> dict:
    """
    Convert machine status into a consistent
    dashboard-friendly dictionary.
    """
    if not isinstance(status, dict):
        raise TypeError("Machine status must be a dictionary")

    result = dict(status)

    result.setdefault("machine_id", "UNKNOWN")
    result.setdefault("state", "UNKNOWN")
    result.setdefault("active_faults", [])
    result.setdefault("fault_latched", False)
    result.setdefault("readings_fresh", False)

    for key in SENSOR_FIELDS:
        result.setdefault(key, None)

    return result


def make_sensor_record(status: dict) -> dict:
    status = normalize_status(status)

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "machine_state": status["state"],
    }

    for key in SENSOR_FIELDS:
        record[key] = status.get(key)

    return record


def make_event(
    event_type: str,
    message: str,
    status: str = "INFO",
) -> dict:
    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "event_type": event_type,
        "status": status,
        "message": message,
    }


def state_label(state: str) -> str:
    labels = {
        "RUNNING": "Running",
        "STOPPED_FAULT": "Stopped — Fault",
        "STOPPED_EMERGENCY": "Emergency Stop",
        "READY_FOR_REVIEW": "Ready for Review",
    }

    return labels.get(state, state)


def diagnosis_summary(report: dict | None) -> dict:
    if not report:
        return {
            "diagnosis": "Not analyzed",
            "severity": "UNKNOWN",
            "confidence": "UNAVAILABLE",
            "procedures": [],
        }

    return {
        "diagnosis": report.get(
            "primary_diagnosis", "UNKNOWN"
        ),
        "severity": report.get(
            "severity", "UNKNOWN"
        ),
        "confidence": report.get(
            "confidence_label", "UNAVAILABLE"
        ),
        "procedures": report.get(
            "procedure_ids", []
        ),
    }
