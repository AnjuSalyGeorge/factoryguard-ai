
import json

from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading
from src.vision.client import (
    OllamaVisionClient,
    VisionError,
)


def main():
    print("=" * 55)
    print("FACTORYGUARD AI — DAY 3 INTEGRATION DEMO")
    print("=" * 55)

    machine = ConveyorMachine()

    # Deterministic sensor evaluation happens first.
    machine.update_sensors(get_reading("jam"))

    print("\n1. MACHINE STATUS")
    print("State:", machine.state.value)
    print("Active faults:", machine.active_faults)
    print("Fault latched:", machine.fault_latched)

    # Local AI provides diagnostic observations only.
    print("\n2. LOCAL AI VISUAL INSPECTION")

    client = OllamaVisionClient()

    try:
        report = client.inspect(
            "data/scenarios/obstruction.png"
        )
        print(json.dumps(report, indent=2))

    except VisionError as exc:
        report = None
        print("AI inspection unavailable:", exc)

    # The AI report is never passed to a restart method.
    print("\n3. DETERMINISTIC SAFETY VALIDATION")

    restart_result = machine.restart()

    print("Restart accepted:", restart_result)
    print("Final machine state:", machine.state.value)

    assert restart_result is False
    assert machine.fault_latched is True

    print("\n4. RESULT")
    print("AI inspection completed:", report is not None)
    print("Unsafe restart blocked: YES")


if __name__ == "__main__":
    main()
