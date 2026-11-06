
from src.agents.diagnostic import DiagnosticAgent
from src.recovery.runner import RecoveryRunner
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def make_runner():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    report = DiagnosticAgent().diagnose(
        machine_status=machine.get_status(),
        vision_report={"scene_status": "obstruction"},
    )

    return machine, RecoveryRunner(machine, report)


def test_waits_for_acknowledgement():
    machine, runner = make_runner()

    result = runner.tick()

    assert result["status"] == "RUNNING"
    assert machine.state.value == "STOPPED_FAULT"


def test_active_fault_blocks_clearance():
    machine, runner = make_runner()

    runner.acknowledge()
    result = runner.tick()

    assert result["status"] == "RUNNING"
    assert machine.fault_latched is True


def test_no_restart_without_approval():
    machine, runner = make_runner()

    runner.acknowledge()
    runner.tick()

    machine.update_sensors(get_reading("normal"))
    result = runner.tick()

    assert result["status"] == "RUNNING"
    assert machine.state.value == "READY_FOR_REVIEW"
    assert runner.context.operator_restart_approved is False

    assert machine.restart() is False


def test_successful_recovery():
    machine, runner = make_runner()

    runner.acknowledge()
    runner.tick()

    machine.update_sensors(get_reading("normal"))
    runner.tick()

    assert runner.approve_restart() is True

    result = runner.tick()

    assert result["status"] == "SUCCESS"
    assert machine.state.value == "RUNNING"


def test_emergency_stop_blocks_recovery():
    machine, runner = make_runner()

    machine.activate_emergency_stop()

    runner.acknowledge()

    assert runner.approve_restart() is False
    assert runner.context.operator_restart_approved is False

    result = runner.tick()

    assert result["status"] == "FAILURE"
    assert machine.restart() is False


def test_open_guard_blocks_recovery():
    machine, runner = make_runner()

    machine.set_guard_door(False)

    runner.acknowledge()

    assert runner.approve_restart() is False
    assert runner.context.operator_restart_approved is False

    result = runner.tick()

    assert result["status"] == "FAILURE"
    assert machine.restart() is False


def test_stale_readings_block_recovery():
    machine, runner = make_runner()

    runner.acknowledge()
    runner.tick()

    machine.update_sensors(get_reading("normal"))
    runner.tick()

    machine.advance_time(10)

    assert runner.approve_restart() is False
    assert runner.context.operator_restart_approved is False

    result = runner.tick()

    assert result["status"] != "SUCCESS"
    assert machine.restart() is False


def test_missing_diagnostic_blocks_recovery():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    runner = RecoveryRunner(
        machine=machine,
        diagnostic_report=None,
    )

    runner.acknowledge()

    assert runner.approve_restart() is False

    result = runner.tick()

    assert result["status"] == "RUNNING"
    assert machine.restart() is False


def test_wrong_machine_report_rejected():
    machine, runner = make_runner()

    runner.context.diagnostic_report.machine_id = "M-999"

    result = runner.tick()

    assert result["status"] == "FAILURE"
    assert machine.restart() is False


def test_approval_is_consumed():
    machine, runner = make_runner()

    runner.acknowledge()
    runner.tick()

    machine.update_sensors(get_reading("normal"))
    runner.tick()

    assert runner.approve_restart() is True

    result = runner.tick()

    assert result["status"] == "SUCCESS"
    assert runner.context.operator_restart_approved is False
    assert runner.context.recovery_completed is True


def test_early_approval_rejected():
    machine, runner = make_runner()

    # Approval must be rejected while the fault is active.
    assert runner.approve_restart() is False
    assert runner.context.operator_restart_approved is False

    runner.acknowledge()
    runner.tick()

    # The simulated fault is now resolved.
    machine.update_sensors(get_reading("normal"))
    runner.tick()

    # Previous early approval must not be reused.
    result = runner.tick()

    assert result["status"] == "RUNNING"
    assert machine.state.value == "READY_FOR_REVIEW"
    assert runner.context.operator_restart_approved is False

    # The machine must remain stopped without fresh approval.
    assert machine.restart() is False
    assert runner.context.recovery_completed is False


def test_invalid_diagnostic_state_rejected():
    machine, runner = make_runner()

    # Simulate a report captured while the machine
    # was running rather than stopped for a fault.
    runner.context.diagnostic_report.machine_state = "RUNNING"

    result = runner.tick()

    # The behaviour tree must reject this report.
    assert result["status"] == "FAILURE"
    assert result["machine_state"] == "STOPPED_FAULT"

    # The rejection should explain the reason.
    assert result["message"] == (
        "Diagnostic report was not captured during a fault stop"
    )

    # No recovery or restart should occur.
    assert machine.restart() is False
    assert runner.context.recovery_completed is False
    assert runner.context.operator_restart_approved is False
