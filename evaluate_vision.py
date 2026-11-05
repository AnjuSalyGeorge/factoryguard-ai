
import csv
import json
from pathlib import Path

from src.vision.client import (
    OllamaVisionClient,
    VisionError,
)


SCENARIOS = {
    "normal": "normal",
    "misaligned": "misaligned",
    "obstruction": "obstruction",
}


def main():
    client = OllamaVisionClient()

    output_dir = Path("evaluation")
    output_dir.mkdir(exist_ok=True)

    results = []

    for name, expected in SCENARIOS.items():
        image_path = f"data/scenarios/{name}.png"

        print(f"\nInspecting: {name}", flush=True)

        try:
            report = client.inspect(image_path)

            predicted = report["scene_status"]
            latency = report["latency_seconds"]
            correct = predicted == expected
            error = ""

        except VisionError as exc:
            report = None
            predicted = "error"
            latency = ""
            correct = False
            error = str(exc)

        results.append({
            "scenario": name,
            "expected": expected,
            "predicted": predicted,
            "correct": correct,
            "latency_seconds": latency,
            "error": error,
            "report": json.dumps(report),
        })

        print("Expected:", expected)
        print("Predicted:", predicted)
        print("Correct:", correct)
        print("Latency:", latency)

    output_file = output_dir / "vision_results.csv"

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

    correct_count = sum(
        row["correct"] for row in results
    )

    accuracy = correct_count / len(results)

    print("\n" + "=" * 40)
    print("FACTORYGUARD AI — VISION EVALUATION")
    print("=" * 40)
    print(f"Correct: {correct_count}/{len(results)}")
    print(f"Accuracy: {accuracy:.1%}")
    print("Results saved to:", output_file)


if __name__ == "__main__":
    main()
