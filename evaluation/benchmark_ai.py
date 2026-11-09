
import csv
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading
from src.agents.workflow import build_workflow


RUNS = 3


def main():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    workflow = build_workflow()
    rows = []

    for number in range(1, RUNS + 1):
        print(f"\nAI benchmark run {number}/{RUNS}")

        started = time.perf_counter()

        try:
            result = workflow.invoke({
                "machine_status": machine.get_status(),
                "image_path": "data/scenarios/obstruction.png",
                "errors": [],
                "execution_trace": [],
                "workflow_status": "PENDING",
            })

            elapsed = time.perf_counter() - started

            rows.append({
                "run": number,
                "latency_seconds": round(elapsed, 3),
                "completed": (
                    result.get("workflow_status")
                    == "ADVISORY_READY"
                ),
                "degraded": bool(
                    result.get("errors", [])
                ),
                "error": "; ".join(
                    result.get("errors", [])
                ),
            })

        except Exception as exc:
            elapsed = time.perf_counter() - started

            rows.append({
                "run": number,
                "latency_seconds": round(elapsed, 3),
                "completed": False,
                "degraded": True,
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            })

        print(rows[-1])

    output = (
        ROOT / "evaluation" / "day11_latency.csv"
    )

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)

    successful = [
        row["latency_seconds"]
        for row in rows
        if row["completed"]
    ]

    if successful:
        print("\nLATENCY SUMMARY")
        print(
            "Mean:",
            round(statistics.mean(successful), 2),
            "seconds"
        )
        print(
            "Median:",
            round(statistics.median(successful), 2),
            "seconds"
        )
        print("Min:", min(successful))
        print("Max:", max(successful))
    else:
        print("\nNo successful runs to summarize.")

    print("Saved:", output)


if __name__ == "__main__":
    main()
