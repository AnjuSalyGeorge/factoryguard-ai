
import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading
from src.agents.workflow import build_workflow


IMAGE_PATHS = {
    "normal": "data/scenarios/normal.png",
    "jam": "data/scenarios/obstruction.png",
    "overheating": "data/scenarios/normal.png",
    "high_vibration": "data/scenarios/normal.png",
}


def main():
    cases = json.loads(
        (
            ROOT / "evaluation" / "day11_cases.json"
        ).read_text(encoding="utf-8")
    )["cases"]

    workflow = build_workflow()
    results = []

    for case in cases:
        machine = ConveyorMachine()

        machine.update_sensors(
            get_reading(case["scenario"])
        )

        print(f"\nEvaluating {case['id']}...")

        started = time.perf_counter()

        try:
            output = workflow.invoke({
                "machine_status": machine.get_status(),
                "image_path": IMAGE_PATHS[
                    case["scenario"]
                ],
                "errors": [],
                "execution_trace": [],
                "workflow_status": "PENDING",
            })

            elapsed = (
                time.perf_counter() - started
            )

            report = (
                output.get("diagnostic_report")
                or {}
            )

            actual = report.get(
                "primary_diagnosis", "NO_REPORT"
            )

            expected = case[
                "expected_diagnosis"
            ]

            completed = (
                output.get("workflow_status")
                == "ADVISORY_READY"
            )

            correct = completed and actual == expected

            results.append({
                "case_id": case["id"],
                "expected": expected,
                "predicted": actual,
                "correct": correct,
                "completed": completed,
                "latency_seconds": round(elapsed, 3),
                "error": "; ".join(
                    output.get("errors", [])
                ),
            })

        except Exception as exc:
            elapsed = (
                time.perf_counter() - started
            )

            results.append({
                "case_id": case["id"],
                "expected": case[
                    "expected_diagnosis"
                ],
                "predicted": "ERROR",
                "correct": False,
                "completed": False,
                "latency_seconds": round(elapsed, 3),
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            })

        print(results[-1])

    path = (
        ROOT
        / "evaluation"
        / "day11_diagnostic_results.csv"
    )

    with path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    correct = sum(
        row["correct"] for row in results
    )

    completed = sum(
        row["completed"] for row in results
    )

    print("\nDIAGNOSTIC EVALUATION")
    print(f"Correct: {correct}/{len(results)}")
    print(f"Completed: {completed}/{len(results)}")
    print(f"Results: {path}")


if __name__ == "__main__":
    main()
