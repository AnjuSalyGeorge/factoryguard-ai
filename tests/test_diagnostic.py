
import pytest

from src.agents.evidence import assess_evidence
from src.agents.diagnostic import DiagnosticAgent
from src.agents.schemas import DiagnosticReport
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def test_jam_with_matching_vision():
    result = assess_evidence(
        ["OVERCURRENT", "LOW_RPM"],
        "obstruction",
    )

    assert result.diagnosis == "CONVEYOR_JAM"
    assert result.severity == "CRITICAL"
    assert (
        result.confidence_label
        == "MULTI_SOURCE_SUPPORTED"
    )


def test_sensor_vision_conflict():
    result = assess_evidence(
        ["OVERCURRENT", "LOW_RPM"],
        "normal",
    )

    assert result.diagnosis == "CONVEYOR_JAM"
    assert (
        result.confidence_label
        == "CONFLICTING_EVIDENCE"
    )


def test_overheating():
    result = assess_evidence(
        ["OVERHEATING"],
        "uncertain",
    )

    assert result.diagnosis == "MOTOR_OVERHEATING"
    assert result.severity == "CRITICAL"


def test_high_vibration():
    result = assess_evidence(
        ["HIGH_VIBRATION"],
        "uncertain",
    )

    assert result.diagnosis == "HIGH_VIBRATION"


def test_emergency_stop_priority():
    result = assess_evidence(
        ["OVERHEATING"],
        "obstruction",
        emergency_stop=True,
    )

    assert result.diagnosis == "SAFETY_INTERLOCK"
    assert result.severity == "CRITICAL"


def test_guard_door_priority():
    result = assess_evidence(
        [],
        "normal",
        guard_door_closed=False,
    )

    assert result.diagnosis == "SAFETY_INTERLOCK"


def test_invalid_sensor_data():
    result = assess_evidence(
        ["INVALID_SENSOR_DATA"],
        "normal",
    )

    assert result.diagnosis == "SENSOR_DATA_INVALID"


def test_vision_only_misalignment():
    result = assess_evidence(
        [],
        "misaligned",
    )

    assert result.diagnosis == "PRODUCT_MISALIGNMENT"
    assert result.confidence_label == "VISION_ONLY"


def test_unknown_fault():
    result = assess_evidence(
        ["UNRECOGNIZED_FAULT"],
        "uncertain",
    )

    assert result.diagnosis == "UNKNOWN"


def test_normal_scene():
    result = assess_evidence([], "normal")

    assert result.diagnosis == "NORMAL"
    assert result.severity == "INFO"


def test_report_cannot_authorize_restart():
    with pytest.raises(ValueError):
        DiagnosticReport(
            machine_id="M-102",
            machine_state="STOPPED_FAULT",
            primary_diagnosis="CONVEYOR_JAM",
            severity="CRITICAL",
            sensor_faults=["OVERCURRENT"],
            vision_status="obstruction",
            evidence=[],
            procedure_ids=[],
            recommended_checks=[],
            limitations=[],
            restart_authorized=True,
        )


def test_diagnostic_agent_preserves_safety():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    agent = DiagnosticAgent()

    report = agent.diagnose(
        machine_status=machine.get_status(),
        vision_report={
            "scene_status": "obstruction"
        },
        documents=[
            {
                "id": "PROC-001",
                "title": "Conveyor Jam",
            }
        ],
    )

    assert report.primary_diagnosis == "CONVEYOR_JAM"
    assert report.restart_authorized is False
    assert machine.fault_latched is True
    assert machine.restart() is False


def test_missing_ai_evidence():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    report = DiagnosticAgent().diagnose(
        machine_status=machine.get_status(),
        vision_report=None,
        documents=[],
    )

    assert report.primary_diagnosis == "CONVEYOR_JAM"
    assert report.ai_available is False
    assert report.restart_authorized is False
