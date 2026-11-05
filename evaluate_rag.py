
import csv
from pathlib import Path

from src.rag.retriever import MaintenanceRetriever


CASES = [
    {
        "query": "Foreign object blocking conveyor, high current and low speed",
        "fault_codes": ["OVERCURRENT", "LOW_RPM"],
        "expected": "PROC-001",
    },
    {
        "query": "Motor temperature too high and overheating",
        "fault_codes": ["OVERHEATING"],
        "expected": "PROC-002",
    },
    {
        "query": "Excessive vibration near motor bearings",
        "fault_codes": ["HIGH_VIBRATION"],
        "expected": "PROC-003",
    },
    {
        "query": "Product is rotated and touching the guide rail",
        "fault_codes": [],
        "expected": "PROC-004",
    },
    {
        "query": "Emergency stop activated and guard door open",
        "fault_codes": ["EMERGENCY_STOP", "GUARD_OPEN"],
        "expected": "PROC-005",
    },
    {
        "query": "Sensor readings are missing or stale",
        "fault_codes": ["STALE_SENSOR_DATA"],
        "expected": "PROC-006",
    },
]


def main():
    retriever = MaintenanceRetriever()
    rows = []

    for case in CASES:
        results = retriever.search(
            case["query"],
            fault_codes=case["fault_codes"],
            top_k=3,
        )

        predicted = results[0]["id"] if results else None

        rows.append({
            "query": case["query"],
            "expected": case["expected"],
            "predicted": predicted,
            "correct": predicted == case["expected"],
        })

        print(
            f"Expected: {case['expected']} | "
            f"Predicted: {predicted}"
        )

    correct = sum(row["correct"] for row in rows)
    accuracy = correct / len(rows)

    output_dir = Path("evaluation")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "rag_results.csv"

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Retrieval top-1 accuracy: {accuracy:.1%}")
    print("Saved:", output_path)


if __name__ == "__main__":
    main()
