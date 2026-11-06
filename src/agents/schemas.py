
from dataclasses import dataclass, asdict, field
from typing import Any


VALID_SEVERITIES = {
    "INFO",
    "WARNING",
    "CRITICAL",
}

VALID_DIAGNOSES = {
    "NORMAL",
    "CONVEYOR_JAM",
    "MOTOR_OVERHEATING",
    "HIGH_VIBRATION",
    "PRODUCT_MISALIGNMENT",
    "SAFETY_INTERLOCK",
    "SENSOR_DATA_INVALID",
    "UNKNOWN",
}


@dataclass
class DiagnosticReport:
    machine_id: str
    machine_state: str

    primary_diagnosis: str
    severity: str

    sensor_faults: list[str]
    vision_status: str

    evidence: list[str]
    procedure_ids: list[str]

    recommended_checks: list[str]
    limitations: list[str]

    confidence_label: str = "UNVERIFIED"
    ai_available: bool = False

    # Advisory reports never grant machine authority.
    restart_authorized: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):
        if self.severity not in VALID_SEVERITIES:
            raise ValueError("Invalid severity")

        if self.primary_diagnosis not in VALID_DIAGNOSES:
            raise ValueError("Invalid diagnosis")

        if self.restart_authorized:
            raise ValueError(
                "Diagnostic reports cannot authorize restart"
            )

    def to_dict(self):
        return asdict(self)
