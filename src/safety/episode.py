
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class FaultEpisode:
    episode_id: str
    machine_id: str
    initial_faults: tuple[str, ...]
    started_at: str


class FaultEpisodeTracker:
    def __init__(self):
        self.current = None
        self._last_fault_signature = ()

    def observe(self, machine_status):
        machine_id = machine_status["machine_id"]
        machine_state = machine_status["state"]

        faults = tuple(sorted(
            machine_status.get("active_faults", [])
        ))

        stopped = machine_state in (
            "STOPPED_FAULT",
            "STOPPED_EMERGENCY",
        )

        if stopped and faults:
            new_episode = (
                self.current is None
                or self.current.machine_id != machine_id
                or faults != self._last_fault_signature
            )

            if new_episode:
                self.current = FaultEpisode(
                    episode_id=str(uuid4()),
                    machine_id=machine_id,
                    initial_faults=faults,
                    started_at=utc_now(),
                )

            self._last_fault_signature = faults

        elif machine_state == "RUNNING" and not faults:
            self.current = None
            self._last_fault_signature = ()

        # READY_FOR_REVIEW retains the episode.
        return self.current

    def reset(self):
        self.current = None
        self._last_fault_signature = ()
