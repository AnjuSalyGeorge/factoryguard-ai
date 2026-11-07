
from src.agents.graph_nodes import FactoryGuardGraphNodes
from src.agents.workflow import build_workflow
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


class FakeVision:
    def inspect(self, image_path):
        return {
            "scene_status": "obstruction",
            "observations": [
                "Object visible on conveyor"
            ],
            "suspected_issue": "Possible obstruction",
            "uncertainty": "Still image only",
        }


class FailingVision:
    def inspect(self, image_path):
        raise RuntimeError("Vision unavailable")


class FakeRetriever:
    def search(self, query, fault_codes=None, top_k=3):
        return [{
            "id": "PROC-001",
            "title": "Conveyor Jam",
            "text": "Inspect obstruction using approved procedures.",
            "fault_codes": ["OVERCURRENT", "LOW_RPM"],
            "ranking_score": 0.9,
        }]


class EmptyRetriever:
    def search(self, query, fault_codes=None, top_k=3):
        return []


class FakeAdvisor:
    def recommend(self, query, retrieved_documents):
        return {
            "suspected_issue": "Possible conveyor jam",
            "recommended_checks": [
                "Request authorized inspection"
            ],
            "procedure_ids": ["PROC-001"],
            "limitations": "Physical cause unverified",
        }


class FailingAdvisor:
    def recommend(self, query, retrieved_documents):
        raise RuntimeError("Advisor unavailable")


def make_machine():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))
    return machine


def run_workflow(
    machine=None,
    vision=None,
    retriever=None,
    advisor=None,
    image_path="fake.png",
):
    machine = machine or make_machine()

    nodes = FactoryGuardGraphNodes(
        vision_client=vision or FakeVision(),
        retriever=retriever or FakeRetriever(),
        advisor=advisor or FakeAdvisor(),
    )

    workflow = build_workflow(nodes)

    result = workflow.invoke({
        "machine_status": machine.get_status(),
        "image_path": image_path,
        "errors": [],
        "execution_trace": [],
        "workflow_status": "PENDING",
    })

    return machine, result


def test_successful_workflow():
    machine, result = run_workflow()

    assert result["workflow_status"] == "ADVISORY_READY"
    assert (
        result["diagnostic_report"]["primary_diagnosis"]
        == "CONVEYOR_JAM"
    )
    assert machine.state.value == "STOPPED_FAULT"


def test_recovery_handoff_never_authorizes_restart():
    machine, result = run_workflow()

    assert (
        result["recovery_handoff"]["restart_authorized"]
        is False
    )
    assert machine.restart() is False


def test_vision_failure_graceful_degradation():
    machine, result = run_workflow(
        vision=FailingVision()
    )

    assert result["workflow_status"] == "ADVISORY_READY"
    assert result["vision_report"] is None
    assert result["errors"]
    assert (
        result["diagnostic_report"]["primary_diagnosis"]
        == "CONVEYOR_JAM"
    )


def test_no_documents_skips_advisor():
    machine, result = run_workflow(
        retriever=EmptyRetriever()
    )

    assert result["workflow_status"] == "ADVISORY_READY"
    assert "advise_skipped" not in result["execution_trace"]
    assert "diagnose" in result["execution_trace"]
    assert result["retrieved_documents"] == []


def test_advisor_failure_does_not_break_diagnosis():
    machine, result = run_workflow(
        advisor=FailingAdvisor()
    )

    assert result["workflow_status"] == "ADVISORY_READY"
    assert result["maintenance_advice"] is None
    assert result["errors"]


def test_invalid_machine_snapshot():
    nodes = FactoryGuardGraphNodes(
        vision_client=FakeVision(),
        retriever=FakeRetriever(),
        advisor=FakeAdvisor(),
    )

    workflow = build_workflow(nodes)

    result = workflow.invoke({
        "machine_status": {"invalid": True},
        "image_path": "fake.png",
        "errors": [],
        "execution_trace": [],
    })

    assert result["workflow_status"] == "INVALID_INPUT"
    assert result.get("diagnostic_report") is None
    assert result.get("recovery_handoff") is None


def test_missing_image_does_not_bypass_safety():
    machine, result = run_workflow(
        image_path=""
    )

    assert result["vision_report"] is None
    assert result["workflow_status"] == "ADVISORY_READY"
    assert machine.fault_latched is True
    assert machine.restart() is False


def test_execution_trace_order():
    machine, result = run_workflow()

    assert result["execution_trace"] == [
        "validate",
        "inspect_vision",
        "retrieve",
        "advise",
        "diagnose",
        "prepare_handoff",
    ]


def test_diagnostic_is_advisory_only():
    machine, result = run_workflow()

    report = result["diagnostic_report"]

    assert report["restart_authorized"] is False
    assert machine.fault_latched is True
    assert machine.state.value == "STOPPED_FAULT"


def test_machine_id_preserved():
    machine, result = run_workflow()

    assert (
        result["recovery_handoff"]["machine_id"]
        == machine.machine_id
    )
