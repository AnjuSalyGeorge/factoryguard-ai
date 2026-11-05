
import json

from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading
from src.vision.client import (
    OllamaVisionClient,
    VisionError,
)
from src.rag.retriever import MaintenanceRetriever
from src.rag.advisor import (
    MaintenanceAdvisor,
    AdvisorError,
)


def main():
    print("=" * 60)
    print("FACTORYGUARD AI — DAY 4 RAG DEMO")
    print("=" * 60)

    machine = ConveyorMachine()

    # Step 1: Deterministic fault detection.
    machine.update_sensors(get_reading("jam"))

    print("\nMACHINE STATE")
    print(machine.get_status())

    # Step 2: Local vision inspection.
    vision_client = OllamaVisionClient()

    try:
        vision_report = vision_client.inspect(
            "data/scenarios/obstruction.png"
        )

        print("\nVISION REPORT")
        print(json.dumps(vision_report, indent=2))

        vision_description = (
            vision_report["suspected_issue"]
        )

    except VisionError as exc:
        print("\nVision unavailable:", exc)
        vision_description = (
            "Visual inspection unavailable"
        )

    # Step 3: Combine vision and sensor evidence.
    query = (
        f"Visual observation: {vision_description}. "
        f"Sensor faults: {', '.join(machine.active_faults)}"
    )

    # Step 4: Retrieve local maintenance procedures.
    retriever = MaintenanceRetriever()

    documents = retriever.search(
        query=query,
        fault_codes=machine.active_faults,
        top_k=3,
    )

    print("\nRETRIEVED PROCEDURES")

    for doc in documents:
        print(
            doc["id"],
            doc["title"],
            doc["ranking_score"],
        )

    # Step 5: Generate grounded advice.
    advisor = MaintenanceAdvisor()

    try:
        advice = advisor.recommend(
            query=query,
            retrieved_documents=documents,
        )

        print("\nMAINTENANCE RECOMMENDATION")
        print(json.dumps(advice, indent=2))

    except AdvisorError as exc:
        print("\nAdvisor unavailable:", exc)

    # Step 6: Verify deterministic safety.
    print("\nSAFETY CHECK")

    print("Restart allowed:", machine.restart())
    print("Machine state:", machine.state.value)

    assert machine.fault_latched is True
    assert machine.restart() is False

    print("\nDay 4 demo completed.")


if __name__ == "__main__":
    main()
