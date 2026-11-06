
import csv
from pathlib import Path

from src.agents.diagnostic import DiagnosticAgent
from src.recovery.runner import RecoveryRunner
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def setup():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    report = DiagnosticAgent().diagnose(
        machine_status=machine.get_status(),
        vision_report={"scene_status": "obstruction"},
    )

    runner = RecoveryRunner(machine, report)

    return machine, runner


def evaluate_case(name, setup_action, expected_success):
    machine, runner = setup()

    setup_action(machine, runner)

    result = runner.tick()

    success = result["status"] == "SUCCESS"

    return {
        "scenario": name,
        "expected_success": expected_success,
        "actual_success": success,
        "passed": success == expected_success,
        "machine_state": machine.state.value,
        "tree_status": result["status"],
    }


def normal_recovery(machine, runner):
    runner.acknowledge()
    runner.tick()

    machine.update_sensors(get_reading("normal"))
    runner.tick()

    runner.approve_restart()


def unresolved_fault(machine, runner):
    runner.acknowledge()
    runner.approve_restart()


def emergency_stop(machine, runner):
    machine.activate_emergency_stop()
    runner.acknowledge()
    runner.approve_restart()


def open_guard(machine, runner):
    machine.set_guard_door(False)
    runner.acknowledge()
    runner.approve_restart()


def stale_readings(machine, runner):
    runner.acknowledge()
    runner.tick()

    machine.update_sensors(get_reading("normal"))
    runner.tick()

    machine.advance_time(10)
    runner.approve_restart()


CASES = [
    ("normal_recovery", normal_recovery, True),
    ("unresolved_fault", unresolved_fault, False),
    ("emergency_stop", emergency_stop, False),
    ("open_guard", open_guard, False),
    ("stale_readings", stale_readings, False),
]


def main():
    results = []

    for name, action, expected in CASES:
        result = evaluate_case(
            name, action, expected
        )

        results.append(result)

        print(
            f"{name:20} "
            f"Passed={result['passed']} "
            f"State={result['machine_state']}"
        )

    output_dir = Path("evaluation")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "recovery_results.csv"

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
        )
        writer.writeheader()
        writer.writerows(results)

    passed = sum(row["passed"] for row in results)

    print(f"\nPassed: {passed}/{len(results)}")
    print("Saved:", output_file)


if __name__ == "__main__":
    main()
