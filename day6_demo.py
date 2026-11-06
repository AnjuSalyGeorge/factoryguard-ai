
import json

from src.agents.diagnostic import DiagnosticAgent
from src.recovery.runner import RecoveryRunner
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def show_result(label, result):
    print(f"\n{label}")
    print(json.dumps(result, indent=2))


def main():
    print("=" * 65)
    print("FACTORYGUARD AI — DAY 6 BEHAVIOUR TREE")
    print("=" * 65)

    machine = ConveyorMachine()

    # 1. A conveyor jam occurs.
    machine.update_sensors(get_reading("jam"))

    # 2. Produce a diagnostic report.
    report = DiagnosticAgent().diagnose(
        machine_status=machine.get_status(),
        vision_report={
            "scene_status": "obstruction",
            "model": "simulated-diagnostic-input",
        },
        documents=[
            {
                "id": "PROC-001",
                "title": "Conveyor Jam and Obstruction",
            }
        ],
    )

    runner = RecoveryRunner(
        machine=machine,
        diagnostic_report=report,
    )

    # 3. Initial tick: operator has not acknowledged.
    show_result(
        "TICK 1 — WAITING FOR ACKNOWLEDGEMENT",
        runner.tick(),
    )

    # 4. Operator acknowledges the fault.
    runner.acknowledge()

    show_result(
        "TICK 2 — FAULT STILL ACTIVE",
        runner.tick(),
    )

    # 5. Simulate authorized fault resolution.
    # This changes the synthetic sensor readings only.
    machine.advance_time(1)
    machine.update_sensors(get_reading("normal"))

    show_result(
        "TICK 3 — FAULT RESOLVED",
        runner.tick(),
    )

    # 6. No restart approval yet.
    show_result(
        "TICK 4 — STILL WAITING FOR APPROVAL",
        runner.tick(),
    )

    # 7. Operator explicitly approves restart.
    runner.approve_restart()

    show_result(
        "TICK 5 — SIMULATED RESTART",
        runner.tick(),
    )

    print("\nFINAL MACHINE STATUS")
    print(json.dumps(machine.get_status(), indent=2))

    print("\nBEHAVIOUR TREE")
    runner.print_tree()

    print("\nRECOVERY EVENT HISTORY")

    for event in runner.get_history():
        print(
            f"[{event['simulation_time_s']:.1f}s] "
            f"{event['node']}: "
            f"{event['status']} — "
            f"{event['message']}"
        )

    assert machine.state.value == "RUNNING"
    assert runner.context.recovery_completed is True

    print("\nDAY 6 RECOVERY DEMO PASSED")


if __name__ == "__main__":
    main()
