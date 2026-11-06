
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecoveryContext:
    machine: Any

    # Diagnostic report from Day 5.
    diagnostic_report: Any = None

    # Explicit simulated operator actions.
    operator_acknowledged: bool = False
    operator_restart_approved: bool = False

    # Records whether recovery has finished.
    recovery_completed: bool = False

    # Latest node-level explanation.
    last_message: str = ""

    # Behaviour-tree audit history.
    history: list[dict] = field(default_factory=list)

    def record(self, node: str, status: str, message: str):
        self.last_message = message

        self.history.append({
            "simulation_time_s":
                self.machine.simulation_time_s,
            "node": node,
            "status": status,
            "message": message,
            "machine_state": self.machine.state.value,
        })

    def set_diagnostic_report(self, report):
        self.diagnostic_report = report
        self.record(
            "RecoveryContext",
            "INFO",
            "Diagnostic report attached",
        )

    def acknowledge_by_operator(self):
        self.operator_acknowledged = True

        self.record(
            "Operator",
            "INFO",
            "Operator requested fault acknowledgement",
        )

    def approve_by_operator(self):
        self.operator_restart_approved = True

        self.record(
            "Operator",
            "INFO",
            "Operator requested simulated restart approval",
        )
