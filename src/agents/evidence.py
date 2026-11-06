
from dataclasses import dataclass


@dataclass
class EvidenceAssessment:
    diagnosis: str
    severity: str
    confidence_label: str
    evidence: list[str]
    limitations: list[str]


def assess_evidence(
    sensor_faults: list[str],
    vision_status: str,
    emergency_stop: bool = False,
    guard_door_closed: bool = True,
) -> EvidenceAssessment:

    faults = set(sensor_faults)
    evidence = []
    limitations = []

    if emergency_stop or not guard_door_closed:
        if emergency_stop:
            evidence.append(
                "Emergency-stop input is active"
            )

        if not guard_door_closed:
            evidence.append(
                "Protective guard is open"
            )

        return EvidenceAssessment(
            diagnosis="SAFETY_INTERLOCK",
            severity="CRITICAL",
            confidence_label="RULE_CONFIRMED",
            evidence=evidence,
            limitations=[
                "The cause of the interlock activation "
                "requires authorized investigation"
            ],
        )

    if "INVALID_SENSOR_DATA" in faults:
        return EvidenceAssessment(
            diagnosis="SENSOR_DATA_INVALID",
            severity="CRITICAL",
            confidence_label="RULE_CONFIRMED",
            evidence=[
                "Sensor validity check failed"
            ],
            limitations=[
                "Machine condition cannot be inferred "
                "reliably from invalid telemetry"
            ],
        )

    if "OVERHEATING" in faults:
        evidence.append(
            "Temperature exceeded the simulated threshold"
        )

        return EvidenceAssessment(
            diagnosis="MOTOR_OVERHEATING",
            severity="CRITICAL",
            confidence_label="RULE_CONFIRMED",
            evidence=evidence,
            limitations=[
                "Root cause of overheating is not established"
            ],
        )

    if "OVERCURRENT" in faults and "LOW_RPM" in faults:
        evidence.extend([
            "Motor current exceeded the simulated limit",
            "Conveyor RPM fell below the expected range",
        ])

        if vision_status == "obstruction":
            evidence.append(
                "Vision inspection reported an obstruction"
            )
            confidence = "MULTI_SOURCE_SUPPORTED"

        elif vision_status == "normal":
            limitations.append(
                "Vision report conflicts with sensor evidence"
            )
            confidence = "CONFLICTING_EVIDENCE"

        else:
            confidence = "SENSOR_SUPPORTED"

        return EvidenceAssessment(
            diagnosis="CONVEYOR_JAM",
            severity="CRITICAL",
            confidence_label=confidence,
            evidence=evidence,
            limitations=limitations or [
                "Physical cause requires operator verification"
            ],
        )

    if "HIGH_VIBRATION" in faults:
        return EvidenceAssessment(
            diagnosis="HIGH_VIBRATION",
            severity="CRITICAL",
            confidence_label="RULE_CONFIRMED",
            evidence=[
                "Vibration exceeded the simulated threshold"
            ],
            limitations=[
                "Mechanical cause has not been verified"
            ],
        )

    if vision_status == "misaligned":
        return EvidenceAssessment(
            diagnosis="PRODUCT_MISALIGNMENT",
            severity="WARNING",
            confidence_label="VISION_ONLY",
            evidence=[
                "Vision inspection reported a misaligned product"
            ],
            limitations=[
                "Visual observation has not been independently "
                "confirmed by sensor evidence"
            ],
        )

    if vision_status == "obstruction":
        return EvidenceAssessment(
            diagnosis="CONVEYOR_JAM",
            severity="WARNING",
            confidence_label="VISION_ONLY",
            evidence=[
                "Vision inspection reported an obstruction"
            ],
            limitations=[
                "A still image cannot establish a mechanical jam"
            ],
        )

    if faults:
        return EvidenceAssessment(
            diagnosis="UNKNOWN",
            severity="WARNING",
            confidence_label="UNRESOLVED",
            evidence=[
                f"Unclassified sensor fault: {code}"
                for code in sorted(faults)
            ],
            limitations=[
                "No matching diagnostic rule is available"
            ],
        )

    if vision_status == "normal":
        return EvidenceAssessment(
            diagnosis="NORMAL",
            severity="INFO",
            confidence_label="LIMITED_OBSERVATION",
            evidence=[
                "No active sensor fault codes",
                "Vision inspection reported a normal scene",
            ],
            limitations=[
                "A normal observation is not a restart clearance"
            ],
        )

    return EvidenceAssessment(
        diagnosis="UNKNOWN",
        severity="WARNING",
        confidence_label="INSUFFICIENT_EVIDENCE",
        evidence=[
            "Insufficient evidence for a specific diagnosis"
        ],
        limitations=[
            "Further inspection or telemetry is required"
        ],
    )
