
from dataclasses import dataclass
from enum import Enum
import math

from src.simulator.machine import MachineReading


class MachineState(str, Enum):
    RUNNING = "RUNNING"
    STOPPED_FAULT = "STOPPED_FAULT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


@dataclass
class SafetyDecision:
    state: MachineState
    faults: list[str]
    restart_allowed: bool


# Demonstration thresholds only.
MAX_TEMP_C = 85.0
MAX_CURRENT_A = 15.0
MAX_VIBRATION = 7.0


def evaluate(reading: MachineReading) -> SafetyDecision:
    faults = []

    values = [
        reading.temperature_c,
        reading.current_a,
        reading.vibration_mm_s,
        reading.rpm,
    ]

    if (
        not all(math.isfinite(v) for v in values)
        or any(v < 0 for v in values)
    ):
        faults.append("INVALID_SENSOR_DATA")

    if faults:
        return SafetyDecision(
            MachineState.STOPPED_FAULT,
            faults,
            False,
        )

    if reading.temperature_c > MAX_TEMP_C:
        faults.append("OVERHEATING")

    if reading.current_a > MAX_CURRENT_A:
        faults.append("OVERCURRENT")

    if reading.vibration_mm_s > MAX_VIBRATION:
        faults.append("HIGH_VIBRATION")

    if reading.rpm < 500:
        faults.append("LOW_RPM")

    if faults:
        return SafetyDecision(
            MachineState.STOPPED_FAULT,
            faults,
            False,
        )

    return SafetyDecision(
        MachineState.RUNNING,
        [],
        False,
    )
