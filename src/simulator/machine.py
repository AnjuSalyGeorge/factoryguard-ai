
from dataclasses import dataclass


@dataclass(frozen=True)
class MachineReading:
    machine_id: str
    temperature_c: float
    current_a: float
    vibration_mm_s: float
    rpm: int


SCENARIOS = {
    "normal": MachineReading(
        "M-102", 55.0, 8.0, 2.1, 1450
    ),
    "jam": MachineReading(
        "M-102", 72.0, 19.0, 5.0, 200
    ),
    "overheating": MachineReading(
        "M-102", 96.0, 10.0, 3.0, 1400
    ),
    "high_vibration": MachineReading(
        "M-102", 65.0, 9.0, 9.2, 1350
    ),
}


def get_reading(scenario: str) -> MachineReading:
    if scenario not in SCENARIOS:
        raise ValueError(
            f"Unknown scenario: {scenario}"
        )
    return SCENARIOS[scenario]
