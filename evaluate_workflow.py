
import csv
import time
from pathlib import Path

from src.agents.graph_nodes import FactoryGuardGraphNodes
from src.agents.workflow import build_workflow
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


class TestVision:
    def inspect(self, image_path):
        return {
            "scene_status": "obstruction",
            "suspected_issue": "Possible conveyor obstruction",
            "observations": ["Object on belt"],
            "uncertainty": "Still image",
        }


class BrokenVision:
    def inspect(self, image_path):
        raise RuntimeError("Simulated vision failure")


class TestRetriever:
    def search(self, query, fault_codes=None, top_k=3):
        return [{
            "id": "PROC-001",
            "title": "Conveyor Jam",
            "text": "Request authorized obstruction inspection.",
            "fault_codes": ["OVERCURRENT", "LOW_RPM"],
        }]


class EmptyRetriever:
    def search(self, query, fault_codes=None, top_k=3):
        return []


class TestAdvisor:
    def recommend(self, query, retrieved_documents):
        return {
            "suspected_issue": "Possible jam",
            "recommended_checks": [
                "Request authorized inspection"
            ],
            "procedure_ids": ["PROC-001"],
            "limitations": "Cause unverified",
        }


class BrokenAdvisor:
    def recommend(self, query, retrieved_documents):
        raise RuntimeError("Simulated advisor failure")


CASES = [
    (
        "normal",
        TestVision(),
        TestRetriever(),
        TestAdvisor(),
        "ADVISORY_READY",
    ),
    (
        "vision_failure",
        BrokenVision(),
        TestRetriever(),
        TestAdvisor(),
        "ADVISORY_READY",
    ),
    (
        "no_documents",
        TestVision(),
        EmptyRetriever(),
        TestAdvisor(),
        "ADVISORY_READY",
    ),
    (
        "advisor_failure",
        TestVision(),
        TestRetriever(),
        BrokenAdvisor(),
        "ADVISORY_READY",
    ),
    (
        "invalid_input",
        TestVision(),
        TestRetriever(),
        TestAdvisor(),
        "INVALID_INPUT",
    ),
]


def main():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    rows = []

    for name, vision, retriever, advisor, expected in CASES:
        nodes = FactoryGuardGraphNodes(
            vision_client=vision,
            retriever=retriever,
            advisor=advisor,
        )

        workflow = build_workflow(nodes)

        status = (
            {"invalid": True}
            if name == "invalid_input"
            else machine.get_status()
        )

        start = time.perf_counter()

        result = workflow.invoke({
            "machine_status": status,
            "image_path": "fake.png",
            "errors": [],
            "execution_trace": [],
            "workflow_status": "PENDING",
        })

        latency = time.perf_counter() - start

        actual = result["workflow_status"]

        rows.append({
            "scenario": name,
            "expected": expected,
            "actual": actual,
            "passed": actual == expected,
            "latency_seconds": round(latency, 4),
            "node_count": len(
                result.get("execution_trace", [])
            ),
            "error_count": len(
                result.get("errors", [])
            ),
        })

        print(
            f"{name:20} "
            f"Expected={expected:16} "
            f"Actual={actual:16} "
            f"Pass={actual == expected}"
        )

    output_dir = Path("evaluation")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "workflow_results.csv"

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

    passed = sum(row["passed"] for row in rows)

    print(f"\nPassed: {passed}/{len(rows)}")
    print("Saved:", output_file)

    assert passed == len(rows)


if __name__ == "__main__":
    main()
