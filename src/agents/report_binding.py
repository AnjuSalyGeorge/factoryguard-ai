
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class BoundDiagnostic:
    episode_id: str
    machine_id: str
    created_at: str
    report: dict[str, Any]


def bind_report(report, episode):
    if episode is None:
        raise ValueError(
            "Cannot bind diagnosis without an active fault episode"
        )

    if hasattr(report, "to_dict"):
        report = report.to_dict()

    if not isinstance(report, dict):
        raise TypeError("Report must be a dictionary")

    if report.get("machine_id") != episode.machine_id:
        raise ValueError("Diagnostic machine ID mismatch")

    if report.get("restart_authorized") is not False:
        raise ValueError(
            "Diagnostic report must explicitly deny restart authority"
        )

    if report.get("machine_state") not in (
        "STOPPED_FAULT",
        "STOPPED_EMERGENCY",
    ):
        raise ValueError(
            "Diagnostic must originate from a stopped fault state"
        )

    return BoundDiagnostic(
        episode_id=episode.episode_id,
        machine_id=episode.machine_id,
        created_at=datetime.now(
            timezone.utc
        ).isoformat(),
        report=dict(report),
    )


def validate_report_binding(bound_report, episode):
    if bound_report is None or episode is None:
        return False

    if bound_report.episode_id != episode.episode_id:
        return False

    if bound_report.machine_id != episode.machine_id:
        return False

    if bound_report.report.get("restart_authorized") is not False:
        return False

    return True
