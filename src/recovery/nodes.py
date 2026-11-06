
import py_trees

from src.recovery.context import RecoveryContext
from src.simulator.conveyor import ConveyorState


Status = py_trees.common.Status


class RecoveryNode(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, context: RecoveryContext):
        super().__init__(name=name)
        self.context = context

    def result(self, status, message):
        self.context.record(
            self.name,
            status.name,
            message,
        )
        return status


class CheckStopped(RecoveryNode):
    def __init__(self, context):
        super().__init__("CheckStopped", context)

    def update(self):
        machine = self.context.machine

        if machine.state in (
            ConveyorState.STOPPED_FAULT,
            ConveyorState.STOPPED_EMERGENCY,
            ConveyorState.READY_FOR_REVIEW,
        ):
            return self.result(
                Status.SUCCESS,
                "Machine is stopped",
            )

        return self.result(
            Status.FAILURE,
            "Machine is not in a fault-stopped state",
        )


class CheckDiagnostic(RecoveryNode):
    def __init__(self, context):
        super().__init__("CheckDiagnostic", context)

    def update(self):
        report = self.context.diagnostic_report

        if report is None:
            return self.result(
                Status.RUNNING,
                "Waiting for diagnostic report",
            )

        if getattr(report, "restart_authorized", False):
            return self.result(
                Status.FAILURE,
                "Diagnostic report improperly grants restart",
            )

        if (
            getattr(report, "machine_id", None)
            != self.context.machine.machine_id
        ):
            return self.result(
                Status.FAILURE,
                "Diagnostic report machine ID mismatch",
            )

        # Step 10.2:
        # The diagnostic report must have been captured
        # while the machine was stopped due to a fault
        # or emergency condition.
        if getattr(report, "machine_state", None) not in (
            "STOPPED_FAULT",
            "STOPPED_EMERGENCY",
        ):
            return self.result(
                Status.FAILURE,
                "Diagnostic report was not captured during a fault stop",
            )

        return self.result(
            Status.SUCCESS,
            "Diagnostic report available",
        )


class CheckInterlocks(RecoveryNode):
    def __init__(self, context):
        super().__init__("CheckInterlocks", context)

    def update(self):
        machine = self.context.machine

        if machine.emergency_stop_active:
            return self.result(
                Status.FAILURE,
                "Emergency stop is active",
            )

        if not machine.guard_door_closed:
            return self.result(
                Status.FAILURE,
                "Guard door is open",
            )

        return self.result(
            Status.SUCCESS,
            "Safety interlocks satisfied",
        )


class WaitForAcknowledgement(RecoveryNode):
    def __init__(self, context):
        super().__init__("WaitForAcknowledgement", context)

    def update(self):
        if not self.context.operator_acknowledged:
            return self.result(
                Status.RUNNING,
                "Waiting for operator acknowledgement",
            )

        return self.result(
            Status.SUCCESS,
            "Operator acknowledgement received",
        )


class AcknowledgeFault(RecoveryNode):
    def __init__(self, context):
        super().__init__("AcknowledgeFault", context)

    def update(self):
        machine = self.context.machine

        if machine.state == ConveyorState.READY_FOR_REVIEW:
            return self.result(
                Status.SUCCESS,
                "Fault already cleared; acknowledgement stage complete",
            )

        if machine.fault_acknowledged:
            return self.result(
                Status.SUCCESS,
                "Fault already acknowledged",
            )

        if machine.acknowledge_fault():
            return self.result(
                Status.SUCCESS,
                "Fault acknowledged by controller",
            )

        return self.result(
            Status.FAILURE,
            "Fault acknowledgement rejected",
        )


class CheckFaultResolved(RecoveryNode):
    def __init__(self, context):
        super().__init__("CheckFaultResolved", context)

    def update(self):
        machine = self.context.machine

        if machine.state == ConveyorState.READY_FOR_REVIEW:
            if not machine.get_status()["readings_fresh"]:
                return self.result(
                    Status.RUNNING,
                    "Waiting for fresh sensor readings",
                )

            if machine.active_faults:
                return self.result(
                    Status.FAILURE,
                    "New sensor fault detected",
                )

            return self.result(
                Status.SUCCESS,
                "Fault already resolved and cleared",
            )

        if machine.active_faults:
            return self.result(
                Status.RUNNING,
                "Waiting for active faults to resolve",
            )

        if not machine.get_status()["readings_fresh"]:
            return self.result(
                Status.RUNNING,
                "Waiting for fresh sensor readings",
            )

        return self.result(
            Status.SUCCESS,
            "No active sensor faults; readings fresh",
        )


class ClearFault(RecoveryNode):
    def __init__(self, context):
        super().__init__("ClearFault", context)

    def update(self):
        machine = self.context.machine

        if machine.state == ConveyorState.READY_FOR_REVIEW:
            return self.result(
                Status.SUCCESS,
                "Machine already ready for review",
            )

        if machine.clear_fault():
            return self.result(
                Status.SUCCESS,
                "Fault cleared by safety controller",
            )

        return self.result(
            Status.FAILURE,
            "Safety controller rejected fault clearance",
        )


class WaitForRestartApproval(RecoveryNode):
    def __init__(self, context):
        super().__init__(
            "WaitForRestartApproval", context
        )

    def update(self):
        if not self.context.operator_restart_approved:
            return self.result(
                Status.RUNNING,
                "Waiting for explicit operator restart approval",
            )

        return self.result(
            Status.SUCCESS,
            "Operator restart approval received",
        )


class AuthorizeAndRestart(RecoveryNode):
    def __init__(self, context):
        super().__init__("AuthorizeAndRestart", context)

    def update(self):
        machine = self.context.machine

        # Recheck live conditions immediately before
        # requesting restart.
        if machine.state != ConveyorState.READY_FOR_REVIEW:
            return self.result(
                Status.FAILURE,
                "Machine not ready for review",
            )

        if machine.fault_latched or machine.active_faults:
            return self.result(
                Status.FAILURE,
                "Fault remains unresolved",
            )

        if (
            machine.emergency_stop_active
            or not machine.guard_door_closed
            or not machine.get_status()["readings_fresh"]
        ):
            return self.result(
                Status.FAILURE,
                "Live safety conditions are not satisfied",
            )

        if not self.context.operator_restart_approved:
            return self.result(
                Status.FAILURE,
                "Operator approval missing",
            )

        if not machine.approve_restart():
            return self.result(
                Status.FAILURE,
                "Controller rejected restart approval",
            )

        if not machine.restart():
            return self.result(
                Status.FAILURE,
                "Controller rejected simulated restart",
            )

        # Consume operator approval after use.
        self.context.operator_restart_approved = False
        self.context.operator_acknowledged = False
        self.context.recovery_completed = True

        return self.result(
            Status.SUCCESS,
            "Simulated restart completed successfully",
        )
