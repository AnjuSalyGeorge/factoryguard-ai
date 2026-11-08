
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading

from app.dashboard_utils import (
    make_event,
    make_sensor_record,
    normalize_status,
)


def get_dashboard_status(machine: ConveyorMachine) -> dict:
    """
    Combine the machine's safety status with its
    latest sensor measurements for the dashboard.

    This function only reads machine information.
    It does not change the safety controller.
    """
    status = machine.get_status()
    reading = machine.current_reading

    if reading is not None:
        status.update({
            "temperature_c": reading.temperature_c,
            "current_a": reading.current_a,
            "vibration_mm_s": reading.vibration_mm_s,
            "rpm": reading.rpm,
        })

    return normalize_status(status)


def new_dashboard_state():
    machine = ConveyorMachine()

    # Capture an initial normal reading.
    machine.update_sensors(get_reading("normal"))

    status = get_dashboard_status(machine)

    return {
        "machine": machine,
        "scenario": "normal",
        "sensor_history": [
            make_sensor_record(status)
        ],
        "events": [
            make_event(
                "SYSTEM",
                "Dashboard simulation initialized",
            )
        ],
        "diagnostic_report": None,
        "graph_result": None,
        "recovery_runner": None,
        "last_error": None,
        "analysis_pending": False,
    }


def reset_dashboard_state():
    return new_dashboard_state()


def add_event(state, event_type, message, level="INFO"):
    state["events"].append(
        make_event(event_type, message, level)
    )


def apply_scenario(state, scenario: str):
    """
    Inject a simulated sensor scenario.

    The existing machine controller determines
    the resulting safety state.
    """
    allowed = {
        "normal",
        "jam",
        "overheating",
        "high_vibration",
    }

    if scenario not in allowed:
        raise ValueError(
            f"Unsupported scenario: {scenario}"
        )

    machine = state["machine"]

    machine.advance_time(1)
    machine.update_sensors(get_reading(scenario))

    state["scenario"] = scenario

    # Previous diagnostic evidence must not be
    # silently reused after new sensor input.
    state["diagnostic_report"] = None
    state["graph_result"] = None
    state["recovery_runner"] = None

    status = get_dashboard_status(machine)

    state["sensor_history"].append(
        make_sensor_record(status)
    )

    add_event(
        state,
        "SIMULATOR",
        f"Scenario injected: {scenario}; "
        f"machine state: {status['state']}",
    )

    return status
