
import pytest

from app.dashboard_state import (
    new_dashboard_state,
    reset_dashboard_state,
    apply_scenario,
    add_event,
)

from app.dashboard_utils import (
    normalize_status,
    diagnosis_summary,
)


def test_dashboard_initializes():
    state = new_dashboard_state()

    assert state["machine"] is not None
    assert state["scenario"] == "normal"
    assert len(state["sensor_history"]) == 1


def test_initial_machine_state():
    state = new_dashboard_state()

    status = state["machine"].get_status()

    assert status["state"] == "RUNNING"


def test_jam_scenario():
    state = new_dashboard_state()

    status = apply_scenario(
        state, "jam"
    )

    assert status["state"] == "STOPPED_FAULT"
    assert status["fault_latched"] is True


def test_overheating_scenario():
    state = new_dashboard_state()

    status = apply_scenario(
        state, "overheating"
    )

    assert "OVERHEATING" in status["active_faults"]


def test_high_vibration_scenario():
    state = new_dashboard_state()

    status = apply_scenario(
        state, "high_vibration"
    )

    assert "HIGH_VIBRATION" in status["active_faults"]


def test_invalid_scenario_rejected():
    state = new_dashboard_state()

    with pytest.raises(ValueError):
        apply_scenario(
            state, "unsupported_scenario"
        )


def test_new_scenario_invalidates_diagnosis():
    state = new_dashboard_state()

    state["diagnostic_report"] = object()
    state["graph_result"] = {"old": True}
    state["recovery_runner"] = object()

    apply_scenario(state, "jam")

    assert state["diagnostic_report"] is None
    assert state["graph_result"] is None
    assert state["recovery_runner"] is None


def test_sensor_history_grows():
    state = new_dashboard_state()

    before = len(state["sensor_history"])

    apply_scenario(state, "jam")

    assert len(state["sensor_history"]) == before + 1


def test_event_history_grows():
    state = new_dashboard_state()

    before = len(state["events"])

    add_event(
        state,
        "TEST",
        "Test event",
    )

    assert len(state["events"]) == before + 1


def test_reset_creates_new_machine():
    old_state = new_dashboard_state()

    new_state = reset_dashboard_state()

    assert (
        old_state["machine"]
        is not new_state["machine"]
    )


def test_status_normalization():
    status = normalize_status({
        "machine_id": "M-1",
        "state": "STOPPED_FAULT",
    })

    assert status["machine_id"] == "M-1"
    assert status["active_faults"] == []


def test_diagnosis_summary_empty():
    summary = diagnosis_summary(None)

    assert summary["diagnosis"] == "Not analyzed"
    assert summary["severity"] == "UNKNOWN"
