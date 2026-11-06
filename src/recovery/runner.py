
import py_trees

from src.recovery.context import RecoveryContext
from src.recovery.tree import create_recovery_tree


class RecoveryRunner:
    def __init__(self, machine, diagnostic_report=None):
        self.context = RecoveryContext(
            machine=machine,
            diagnostic_report=diagnostic_report,
        )

        self.tree = create_recovery_tree(self.context)
        self.tick_count = 0

    def tick(self):
        if self.context.recovery_completed:
            return {
                "tick": self.tick_count,
                "status": "SUCCESS",
                "message": "Recovery already completed",
                "machine_state":
                    self.context.machine.state.value,
            }

        self.tick_count += 1

        self.tree.tick()

        status = self.tree.root.status

        return {
            "tick": self.tick_count,
            "status": status.name,
            "message": self.context.last_message,
            "machine_state":
                self.context.machine.state.value,
        }

    def acknowledge(self):
        self.context.acknowledge_by_operator()

    def approve_restart(self):
        machine = self.context.machine

        if machine.state.value != "READY_FOR_REVIEW":
            self.context.record(
                "Operator",
                "FAILURE",
                "Restart approval rejected: machine not ready",
            )
            return False

        if (
            machine.fault_latched
            or machine.active_faults
            or machine.emergency_stop_active
            or not machine.guard_door_closed
            or not machine.get_status()["readings_fresh"]
        ):
            self.context.record(
                "Operator",
                "FAILURE",
                "Restart approval rejected: unsafe conditions",
            )
            return False

        self.context.approve_by_operator()
        return True

    def get_history(self):
        return list(self.context.history)

    def print_tree(self):
        print(
            py_trees.display.unicode_tree(
                self.tree.root,
                show_status=True,
            )
        )
