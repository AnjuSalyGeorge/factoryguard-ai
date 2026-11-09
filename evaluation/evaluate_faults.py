
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def main():
    cases_path = (
        ROOT / "evaluation" / "day11_cases.json"
    )

    cases = json.loads(
        cases_path.read_text(encoding="utf-8")
    )["cases"]

    results = []

    for case in cases:
        machine = ConveyorMachine()

        machine.update_sensors(
            get_reading(case["scenario"])
        )

        status = machine.get_status()

        actual_state = status["state"]

        actual_faults = set(
            status.get("active_faults", [])
        )

        expected_faults = set(
            case["expected_faults"]
        )

        state_correct = (
            actual_state == case["expected_state"]
        )

        faults_correct = (
            actual_faults == expected_faults
        )

        passed = state_correct and faults_correct

        results.append({
            "case_id": case["id"],
            "scenario": case["scenario"],
            "expected_state": case["expected_state"],
            "actual_state": actual_state,
            "expected_faults": ",".join(
                sorted(expected_faults)
            ),
            "actual_faults": ",".join(
                sorted(actual_faults)
            ),
            "state_correct": state_correct,
            "faults_correct": faults_correct,
            "passed": passed,
        })

        print(
            f"{case['id']}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    output = (
        ROOT / "evaluation" / "day11_fault_results.csv"
    )

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    total = len(results)
    correct = sum(row["passed"] for row in results)

    accuracy = correct / total if total else 0

    print(f"\nAccuracy: {accuracy:.2%}")
    print(f"Correct: {correct}/{total}")
    print(f"Saved: {output}")

    if correct != total:
        raise SystemExit(
            "Some controller evaluations failed"
        )


if __name__ == "__main__":
    main()
