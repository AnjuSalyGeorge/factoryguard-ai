
import json

from src.agents.pipeline import FactoryGuardDiagnosticPipeline
from src.recovery.runner import RecoveryRunner
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def main():
    print("=" * 65)
    print("FACTORYGUARD AI — DIAGNOSIS TO RECOVERY")
    print("=" * 65)

    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    print("\n1. RUNNING DAY 5 DIAGNOSTIC PIPELINE")

    pipeline = FactoryGuardDiagnosticPipeline()

    report = pipeline.run(
        machine=machine,
        image_path="data/scenarios/obstruction.png",
    )

    print(json.dumps(report.to_dict(), indent=2))

    print("\n2. INITIALIZING DAY 6 RECOVERY TREE")

    runner = RecoveryRunner(
        machine=machine,
        diagnostic_report=report,
    )

    print(runner.tick())

    print("\n3. OPERATOR ACKNOWLEDGES FAULT")
    runner.acknowledge()
    print(runner.tick())

    print("\n4. SIMULATED FAULT RESOLUTION")

    machine.advance_time(1)
    machine.update_sensors(get_reading("normal"))

    print(runner.tick())

    print("\n5. OPERATOR APPROVES RESTART")
    runner.approve_restart()

    print(runner.tick())

    print("\n6. FINAL MACHINE STATE")
    print(machine.get_status())

    assert report.restart_authorized is False
    assert runner.context.recovery_completed is True
    assert machine.state.value == "RUNNING"

    print("\nINTEGRATION DEMO PASSED")


if __name__ == "__main__":
    main()
