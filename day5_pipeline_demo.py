
import json

from src.agents.pipeline import FactoryGuardDiagnosticPipeline
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def main():
    print("=" * 60)
    print("FACTORYGUARD AI — DAY 5 DIAGNOSTIC PIPELINE")
    print("=" * 60)

    # 1. Create a simulated conveyor jam.
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    # Capture the safety state before diagnosis.
    status_before = machine.get_status()

    print("\nMACHINE STATE BEFORE DIAGNOSIS")
    print(json.dumps(status_before, indent=2))

    # 2. Initialize the integrated diagnostic pipeline.
    pipeline = FactoryGuardDiagnosticPipeline()

    # 3. Run vision, RAG, advisor, and diagnosis.
    report = pipeline.run(
        machine=machine,
        image_path="data/scenarios/obstruction.png",
    )

    print("\nDIAGNOSTIC REPORT")
    print(json.dumps(report.to_dict(), indent=2))

    # 4. Verify that the pipeline did not change machine state.
    status_after = machine.get_status()

    print("\nSAFETY VERIFICATION")
    print("State before:", status_before["state"])
    print("State after:", status_after["state"])
    print("Restart authorized:", report.restart_authorized)
    print("Machine status unchanged:", status_before == status_after)

    assert status_before == status_after, (
        "Diagnostic pipeline modified machine status"
    )

    assert report.restart_authorized is False, (
        "Diagnostic report must not authorize restart"
    )

    assert report.primary_diagnosis == "CONVEYOR_JAM", (
        "Expected conveyor jam diagnosis"
    )

    assert report.severity == "CRITICAL", (
        "Expected critical severity"
    )

    print("\nDay 5 diagnostic pipeline demo completed.")


if __name__ == "__main__":
    main()
