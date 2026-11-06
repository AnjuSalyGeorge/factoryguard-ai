
import csv
from pathlib import Path

from src.agents.evidence import assess_evidence


CASES = [
    ("jam_matching", ["OVERCURRENT", "LOW_RPM"],
     "obstruction", "CONVEYOR_JAM"),

    ("jam_conflict", ["OVERCURRENT", "LOW_RPM"],
     "normal", "CONVEYOR_JAM"),

    ("overheating", ["OVERHEATING"],
     "uncertain", "MOTOR_OVERHEATING"),

    ("vibration", ["HIGH_VIBRATION"],
     "uncertain", "HIGH_VIBRATION"),

    ("misalignment", [],
     "misaligned", "PRODUCT_MISALIGNMENT"),

    ("vision_obstruction", [],
     "obstruction", "CONVEYOR_JAM"),

    ("invalid_sensor", ["INVALID_SENSOR_DATA"],
     "normal", "SENSOR_DATA_INVALID"),

    ("normal", [],
     "normal", "NORMAL"),

    ("unknown", ["UNRECOGNIZED_FAULT"],
     "uncertain", "UNKNOWN"),

    ("insufficient", [],
     "uncertain", "UNKNOWN"),
]


def main():
    rows = []

    for name, faults, vision, expected in CASES:
        result = assess_evidence(
            sensor_faults=faults,
            vision_status=vision,
        )

        correct = result.diagnosis == expected

        rows.append({
            "scenario": name,
            "sensor_faults": "|".join(faults),
            "vision_status": vision,
            "expected": expected,
            "predicted": result.diagnosis,
            "severity": result.severity,
            "confidence": result.confidence_label,
            "correct": correct,
        })

        print(
            f"{name:20} "
            f"Expected={expected:24} "
            f"Predicted={result.diagnosis:24} "
            f"Pass={correct}"
        )

    output_dir = Path("evaluation")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir / "diagnostic_results.csv"
    )

    with output_file.open(
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

    correct_count = sum(
        row["correct"] for row in rows
    )

    print("\nRESULTS")
    print(
        f"Correct: {correct_count}/{len(rows)}"
    )
    print(
        f"Rule agreement: "
        f"{correct_count / len(rows):.1%}"
    )
    print("Saved:", output_file)


if __name__ == "__main__":
    main()
