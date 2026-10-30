
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from src.simulator.machine import MachineReading
from src.safety.controller import evaluate


class ConveyorState(str, Enum):
    RUNNING = "RUNNING"
    STOPPED_FAULT = "STOPPED_FAULT"
    STOPPED_EMERGENCY = "STOPPED_EMERGENCY"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


@dataclass(frozen=True)
class MachineEvent:
    timestamp: str
    simulation_time_s: float
    event_type: str
    message: str


class ConveyorMachine:
    """
    Stateful industrial conveyor simulation.

    All actions are simulated. This class does not
    control real machinery.
    """

    MAX_READING_AGE_S = 5.0

    def __init__(self, machine_id: str = "M-102"):
        self.machine_id = machine_id
        self.state = ConveyorState.RUNNING

        self.fault_latched = False
        self.active_faults = []
        self.fault_acknowledged = False

        self.emergency_stop_active = False
        self.guard_door_closed = True

        self.operator_approved = False

        self.current_reading: Optional[MachineReading] = None
        self.last_reading_time_s: Optional[float] = None

        self.simulation_time_s = 0.0
        self.events: list[MachineEvent] = []

        self._log(
            "INITIALIZED",
            "Conveyor initialized in RUNNING state"
        )

    def _log(self, event_type: str, message: str):
        event = MachineEvent(
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
            simulation_time_s=self.simulation_time_s,
            event_type=event_type,
            message=message
        )
        self.events.append(event)

    def advance_time(self, seconds: float):
        if seconds < 0:
            raise ValueError(
                "Simulation time cannot move backwards"
            )

        self.simulation_time_s += seconds

    def _readings_fresh(self) -> bool:
        if self.last_reading_time_s is None:
            return False

        age = (
            self.simulation_time_s
            - self.last_reading_time_s
        )

        return 0 <= age <= self.MAX_READING_AGE_S

    def _interlocks_safe(self) -> bool:
        return (
            not self.emergency_stop_active
            and self.guard_door_closed
        )

    def update_sensors(self, reading: MachineReading):
        if reading.machine_id != self.machine_id:
            raise ValueError(
                "Reading belongs to another machine"
            )

        self.current_reading = reading
        self.last_reading_time_s = self.simulation_time_s

        decision = evaluate(reading)
        self.active_faults = list(decision.faults)

        if self.active_faults:
            if not self.fault_latched:
                self._log(
                    "FAULT_DETECTED",
                    ", ".join(self.active_faults)
                )

            self.fault_latched = True
            self.fault_acknowledged = False
            self.operator_approved = False

            if not self.emergency_stop_active:
                self.state = ConveyorState.STOPPED_FAULT

        elif self.fault_latched:
            # Normal sensors do not clear a latched fault.
            if not self.emergency_stop_active:
                self.state = ConveyorState.STOPPED_FAULT

        elif not self._interlocks_safe():
            self.state = (
                ConveyorState.STOPPED_EMERGENCY
                if self.emergency_stop_active
                else ConveyorState.STOPPED_FAULT
            )

        self._log(
            "SENSOR_UPDATE",
            f"Faults: {self.active_faults}"
        )

    def activate_emergency_stop(self):
        self.emergency_stop_active = True
        self.fault_latched = True
        self.fault_acknowledged = False
        self.operator_approved = False

        self.state = ConveyorState.STOPPED_EMERGENCY

        self._log(
            "EMERGENCY_STOP",
            "Emergency stop activated"
        )

    def release_emergency_stop(self):
        self.emergency_stop_active = False
        self.operator_approved = False

        # Releasing the E-stop never restarts the machine.
        self.state = ConveyorState.STOPPED_FAULT

        self._log(
            "EMERGENCY_RELEASED",
            "Emergency stop released; restart blocked"
        )

    def set_guard_door(self, closed: bool):
        self.guard_door_closed = closed

        if not closed:
            self.fault_latched = True
            self.fault_acknowledged = False
            self.operator_approved = False

            if self.emergency_stop_active:
                self.state = ConveyorState.STOPPED_EMERGENCY
            else:
                self.state = ConveyorState.STOPPED_FAULT

            self._log(
                "GUARD_OPENED",
                "Guard door opened; conveyor stopped"
            )
        else:
            self._log(
                "GUARD_CLOSED",
                "Guard door closed"
            )

    def acknowledge_fault(self) -> bool:
        if not self.fault_latched:
            self._log(
                "ACK_REJECTED",
                "No latched fault to acknowledge"
            )
            return False

        self.fault_acknowledged = True
        self.operator_approved = False

        self._log(
            "FAULT_ACKNOWLEDGED",
            "Operator acknowledged fault"
        )

        return True

    def clear_fault(self) -> bool:
        if not self.fault_latched:
            return False

        if not self.fault_acknowledged:
            self._log(
                "CLEAR_REJECTED",
                "Fault has not been acknowledged"
            )
            return False

        if self.active_faults:
            self._log(
                "CLEAR_REJECTED",
                "Sensor faults are still active"
            )
            return False

        if not self._readings_fresh():
            self._log(
                "CLEAR_REJECTED",
                "Sensor readings are stale or missing"
            )
            return False

        if not self._interlocks_safe():
            self._log(
                "CLEAR_REJECTED",
                "Safety interlock is not satisfied"
            )
            return False

        self.fault_latched = False
        self.fault_acknowledged = False
        self.operator_approved = False

        self.state = ConveyorState.READY_FOR_REVIEW

        self._log(
            "FAULT_CLEARED",
            "Fault cleared; awaiting restart approval"
        )

        return True

    def approve_restart(self) -> bool:
        if self.state != ConveyorState.READY_FOR_REVIEW:
            self._log(
                "APPROVAL_REJECTED",
                "Machine is not ready for review"
            )
            return False

        if not self._readings_fresh():
            self._log(
                "APPROVAL_REJECTED",
                "Sensor readings are stale"
            )
            return False

        if not self._interlocks_safe():
            self._log(
                "APPROVAL_REJECTED",
                "Safety interlock is active"
            )
            return False

        if self.fault_latched or self.active_faults:
            self._log(
                "APPROVAL_REJECTED",
                "Unresolved machine fault"
            )
            return False

        self.operator_approved = True

        self._log(
            "RESTART_APPROVED",
            "Operator approved simulated restart"
        )

        return True

    def restart(self) -> bool:
        if (
            self.state != ConveyorState.READY_FOR_REVIEW
            or not self.operator_approved
            or self.fault_latched
            or self.active_faults
            or not self._readings_fresh()
            or not self._interlocks_safe()
        ):
            self._log(
                "RESTART_BLOCKED",
                "Restart rejected by safety controller"
            )
            return False

        self.state = ConveyorState.RUNNING
        self.operator_approved = False

        self._log(
            "RESTART_SUCCESS",
            "Simulated conveyor restarted"
        )

        return True

    def get_status(self) -> dict:
        return {
            "machine_id": self.machine_id,
            "state": self.state.value,
            "fault_latched": self.fault_latched,
            "active_faults": list(self.active_faults),
            "fault_acknowledged": self.fault_acknowledged,
            "emergency_stop": self.emergency_stop_active,
            "guard_door_closed": self.guard_door_closed,
            "operator_approved": self.operator_approved,
            "readings_fresh": self._readings_fresh(),
            "simulation_time_s": self.simulation_time_s,
            "event_count": len(self.events)
        }
