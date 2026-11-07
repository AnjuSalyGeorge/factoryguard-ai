
import json
import time

from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading
from src.agents.workflow import build_workflow


def main():
    print("=" * 65)
    print("FACTORYGUARD AI — DAY 7 LANGGRAPH DEMO")
    print("=" * 65)

    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    initial_state = {
        "machine_status": machine.get_status(),
        "image_path": "data/scenarios/obstruction.png",
        "vision_report": None,
        "retrieved_documents": [],
        "maintenance_advice": None,
        "diagnostic_report": None,
        "recovery_handoff": None,
        "errors": [],
        "execution_trace": [],
        "workflow_status": "PENDING",
    }

    workflow = build_workflow()

    start = time.perf_counter()
    result = workflow.invoke(initial_state)
    elapsed = time.perf_counter() - start

    print("\nWORKFLOW STATUS")
    print(result["workflow_status"])

    print("\nEXECUTION TRACE")
    for step in result.get("execution_trace", []):
        print(" -", step)

    print("\nDIAGNOSTIC REPORT")
    print(json.dumps(
        result.get("diagnostic_report"),
        indent=2,
    ))

    print("\nRECOVERY HANDOFF")
    print(json.dumps(
        result.get("recovery_handoff"),
        indent=2,
    ))

    print("\nERRORS")
    print(json.dumps(
        result.get("errors", []),
        indent=2,
    ))

    print(f"\nTotal latency: {elapsed:.2f}s")

    assert result["workflow_status"] == "ADVISORY_READY"
    assert result["diagnostic_report"] is not None
    assert (
        result["recovery_handoff"]["restart_authorized"]
        is False
    )

    # Diagnostic workflow must not alter machine state.
    assert machine.fault_latched is True
    assert machine.state.value == "STOPPED_FAULT"

    print("\nDAY 7 LANGGRAPH DEMO PASSED")


if __name__ == "__main__":
    main()
