
import pytest

from src.simulator.conveyor import (
    ConveyorMachine,
    ConveyorState,
)
from src.simulator.machine import get_reading


def test_initial_state():
    machine = ConveyorMachine()

    assert machine.state == ConveyorState.RUNNING
    assert machine.fault_latched is False


def test_jam_stops_machine():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))

    assert machine.state == ConveyorState.STOPPED_FAULT
    assert machine.fault_latched is True
    assert machine.restart() is False


def test_fault_remains_latched():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))
    machine.update_sensors(get_reading("normal"))

    assert machine.fault_latched is True
    assert machine.state == ConveyorState.STOPPED_FAULT


def test_emergency_stop_blocks_restart():
    machine = ConveyorMachine()

    machine.activate_emergency_stop()

    assert machine.state == ConveyorState.STOPPED_EMERGENCY
    assert machine.restart() is False


def test_estop_release_does_not_restart():
    machine = ConveyorMachine()

    machine.activate_emergency_stop()
    machine.release_emergency_stop()

    assert machine.state == ConveyorState.STOPPED_FAULT
    assert machine.restart() is False


def test_guard_door_blocks_restart():
    machine = ConveyorMachine()

    machine.set_guard_door(False)

    assert machine.guard_door_closed is False
    assert machine.restart() is False


def test_active_fault_cannot_be_cleared():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))
    machine.acknowledge_fault()

    assert machine.clear_fault() is False


def test_acknowledgement_required():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))
    machine.update_sensors(get_reading("normal"))

    assert machine.clear_fault() is False


def test_recovery_requires_approval():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))
    machine.acknowledge_fault()
    machine.update_sensors(get_reading("normal"))

    assert machine.clear_fault() is True
    assert machine.restart() is False


def test_successful_recovery():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))
    machine.acknowledge_fault()
    machine.update_sensors(get_reading("normal"))

    assert machine.clear_fault() is True
    assert machine.approve_restart() is True
    assert machine.restart() is True

    assert machine.state == ConveyorState.RUNNING


def test_stale_readings_block_restart():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))
    machine.acknowledge_fault()
    machine.update_sensors(get_reading("normal"))

    assert machine.clear_fault() is True

    machine.advance_time(10)

    assert machine.approve_restart() is False
    assert machine.restart() is False


def test_negative_time_rejected():
    machine = ConveyorMachine()

    with pytest.raises(ValueError):
        machine.advance_time(-1)


def test_event_logging():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))
    machine.restart()

    event_types = [
        event.event_type for event in machine.events
    ]

    assert "FAULT_DETECTED" in event_types
    assert "RESTART_BLOCKED" in event_types


def test_wrong_machine_reading_rejected():
    from src.simulator.machine import MachineReading

    machine = ConveyorMachine("M-102")

    reading = MachineReading(
        machine_id="M-999",
        temperature_c=55,
        current_a=8,
        vibration_mm_s=2,
        rpm=1450
    )

    with pytest.raises(ValueError):
        machine.update_sensors(reading)
