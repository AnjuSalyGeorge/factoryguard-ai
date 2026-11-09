
from dataclasses import dataclass

from src.agents.report_binding import (
    validate_report_binding,
)


@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reasons: tuple[str, ...]


def evaluate_restart(
    machine_status,
    episode,
    bound_report,
    operator_acknowledged,
    operator_approved,
    audit_healthy,
):
    reasons = []

    if not isinstance(machine_status, dict):
        return AuthorizationDecision(
            allowed=False,
            reasons=("Invalid machine status",),
        )

    if machine_status.get("state") != "READY_FOR_REVIEW":
        reasons.append("Machine is not ready for review")

    if machine_status.get("fault_latched") is not False:
        reasons.append("Fault latch is not cleared")

    if machine_status.get("active_faults") != []:
        reasons.append("Active faults remain or are unknown")

    if machine_status.get("readings_fresh") is not True:
        reasons.append("Sensor readings are not confirmed fresh")

    # Accept the existing simulator's emergency-stop field
    # or the normalized safety-status field.
    # Reject missing, invalid, or conflicting values.

    emergency_stop = machine_status.get("emergency_stop")
    emergency_stop_active = machine_status.get(
        "emergency_stop_active"
    )

    if (
        emergency_stop is not None
        and emergency_stop_active is not None
        and emergency_stop is not emergency_stop_active
    ):
        reasons.append("Conflicting emergency stop status")

    elif emergency_stop_active is not None:
        if emergency_stop_active is not False:
            reasons.append(
                "Emergency stop is active or unknown"
            )

    elif emergency_stop is not False:
        reasons.append(
            "Emergency stop is active or unknown"
        )

    if machine_status.get("guard_door_closed") is not True:
        reasons.append("Guard interlock is open or unknown")

    if not validate_report_binding(bound_report, episode):
        reasons.append("Diagnostic episode mismatch")

    if not operator_acknowledged:
        reasons.append("Operator acknowledgement missing")

    if not operator_approved:
        reasons.append("Operator restart approval missing")

    if not audit_healthy:
        reasons.append("Audit system unavailable")

    return AuthorizationDecision(
        allowed=len(reasons) == 0,
        reasons=tuple(reasons),
    )
