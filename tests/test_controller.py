
from src.simulator.machine import (
    get_reading,
    MachineReading,
)
from src.safety.controller import (
    evaluate,
    MachineState,
)


def test_normal_machine():
    result = evaluate(get_reading("normal"))
    assert result.state == MachineState.RUNNING
    assert result.faults == []
    assert result.restart_allowed is False


def test_conveyor_jam():
    result = evaluate(get_reading("jam"))
    assert result.state == MachineState.STOPPED_FAULT
    assert "OVERCURRENT" in result.faults
    assert "LOW_RPM" in result.faults


def test_overheating():
    result = evaluate(get_reading("overheating"))
    assert "OVERHEATING" in result.faults


def test_high_vibration():
    result = evaluate(get_reading("high_vibration"))
    assert "HIGH_VIBRATION" in result.faults


def test_invalid_sensor_data():
    reading = MachineReading(
        "M-102", float("nan"), 8.0, 2.0, 1450
    )
    result = evaluate(reading)
    assert "INVALID_SENSOR_DATA" in result.faults
    assert result.restart_allowed is False
