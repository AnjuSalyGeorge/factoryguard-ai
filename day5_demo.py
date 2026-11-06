
import json
import time

from src.agents.pipeline import (
    FactoryGuardDiagnosticPipeline,
)
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def main():
    print("=" * 65)
    print("FACTORYGUARD AI — DAY 5 DIAGNOSTIC AGENT")
    print("=" * 65)

    machine = ConveyorMachine()

    # The deterministic safety controller
    # detects and latches the fault.
    machine.update_sensors(get_reading("jam"))

    print("\n[1] MACHINE STATUS")
    print(json.dumps(machine.get_status(), indent=2))

    print("\n[2] RUNNING DIAGNOSTIC PIPELINE")

    pipeline = FactoryGuardDiagnosticPipeline()

    start = time.perf_counter()

    report = pipeline.run(
        machine=machine,
        image_path="data/scenarios/obstruction.png",
    )

    elapsed = time.perf_counter() - start

    print("\n[3] DIAGNOSTIC REPORT")
    print(json.dumps(report.to_dict(), indent=2))

    print("\n[4] SAFETY VALIDATION")

    restart_result = machine.restart()

    print("Restart accepted:", restart_result)
    print("Fault latched:", machine.fault_latched)
    print("Machine state:", machine.state.value)

    assert report.restart_authorized is False
    assert restart_result is False
    assert machine.fault_latched is True

    print("\n[5] PERFORMANCE")
    print(f"Total pipeline latency: {elapsed:.2f}s")

    print("\n[6] RESULT")
    print("Diagnostic report generated: YES")
    print("Unauthorized restart blocked: YES")


if __name__ == "__main__":
    main()
