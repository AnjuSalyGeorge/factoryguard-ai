
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent


def load_csv(filename):
    path = BASE / filename

    if not path.exists():
        return None

    with path.open(
        newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def count_true(rows, field):
    return sum(
        str(row.get(field, "")).lower() == "true"
        for row in rows
    )


def ratio(numerator, denominator):
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def main():
    faults = load_csv("day11_fault_results.csv")
    diagnostics = load_csv(
        "day11_diagnostic_results.csv"
    )
    rag = load_csv("day11_rag_results.csv")
    safety = load_csv("day11_safety_results.csv")
    latency = load_csv("day11_latency.csv")

    summary = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "evaluation_type": "Synthetic prototype evaluation",
        "fault_detection": None,
        "diagnostics": None,
        "rag": None,
        "safety": None,
        "latency": None,
    }

    if faults is not None:
        passed = count_true(faults, "passed")

        summary["fault_detection"] = {
            "passed": passed,
            "total": len(faults),
            "accuracy": ratio(passed, len(faults)),
        }

    if diagnostics is not None:
        correct = count_true(
            diagnostics, "correct"
        )

        completed = count_true(
            diagnostics, "completed"
        )

        summary["diagnostics"] = {
            "correct": correct,
            "completed": completed,
            "total": len(diagnostics),
            "accuracy": ratio(
                correct, len(diagnostics)
            ),
        }

    if rag is not None:
        hits = count_true(rag, "hit_at_3")

        summary["rag"] = {
            "hits": hits,
            "total": len(rag),
            "hit_at_3": ratio(hits, len(rag)),
        }

    if safety is not None:
        blocked = count_true(safety, "blocked")

        summary["safety"] = {
            "blocked": blocked,
            "total": len(safety),
            "block_rate": ratio(
                blocked, len(safety)
            ),
        }

    if latency is not None:
        completed_runs = [
            float(row["latency_seconds"])
            for row in latency
            if str(
                row.get("completed", "")
            ).lower() == "true"
        ]

        summary["latency"] = {
            "completed_runs": len(completed_runs),
            "total_runs": len(latency),
            "mean_seconds": (
                round(
                    sum(completed_runs)
                    / len(completed_runs),
                    3,
                )
                if completed_runs else None
            ),
        }

    output = BASE / "day11_summary.json"

    output.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print("\nSaved:", output)


if __name__ == "__main__":
    main()
