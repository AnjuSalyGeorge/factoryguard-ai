
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading
from src.agents.workflow import build_workflow
from src.agents.schemas import DiagnosticReport
from src.recovery.runner import RecoveryRunner


def main():
    machine = ConveyorMachine()
    machine.update_sensors(get_reading("jam"))

    workflow = build_workflow()

    result = workflow.invoke({
        "machine_status": machine.get_status(),
        "image_path": "data/scenarios/obstruction.png",
        "errors": [],
        "execution_trace": [],
        "workflow_status": "PENDING",
    })

    if result["workflow_status"] != "ADVISORY_READY":
        raise RuntimeError(
            "Diagnostic workflow did not complete"
        )

    report_data = result["diagnostic_report"]

    # Reconstruct a typed advisory report.
    report = DiagnosticReport(**report_data)

    # Confirm the report is for this machine
    # and its current fault-stopped episode.
    assert report.machine_id == machine.machine_id
    assert report.machine_state == "STOPPED_FAULT"
    assert report.restart_authorized is False
    assert machine.fault_latched is True

    runner = RecoveryRunner(
        machine=machine,
        diagnostic_report=report,
    )

    print("\n1. RECOVERY INITIALIZED")
    print(runner.tick())

    print("\n2. OPERATOR ACKNOWLEDGES")
    runner.acknowledge()
    print(runner.tick())

    print("\n3. SIMULATED FAULT RESOLUTION")
    machine.advance_time(1)
    machine.update_sensors(get_reading("normal"))
    print(runner.tick())

    print("\n4. OPERATOR APPROVES RESTART")
    accepted = runner.approve_restart()
    assert accepted is True

    print(runner.tick())

    assert machine.state.value == "RUNNING"
    assert runner.context.recovery_completed is True

    print("\nDAY 7 INTEGRATION PASSED")


if __name__ == "__main__":
    main()
