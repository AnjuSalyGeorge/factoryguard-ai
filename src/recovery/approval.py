
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class RestartApproval:
    approval_id: str
    episode_id: str
    consumed: bool = False


class ApprovalManager:
    def __init__(self):
        self.current = None

    def approve(self, episode_id):
        if not episode_id:
            raise ValueError("Episode ID required")

        self.current = RestartApproval(
            approval_id=str(uuid4()),
            episode_id=episode_id,
        )

        return self.current

    def is_valid(self, episode_id):
        return (
            self.current is not None
            and self.current.episode_id == episode_id
            and not self.current.consumed
        )

    def consume(self, episode_id):
        if not self.is_valid(episode_id):
            return False

        self.current.consumed = True
        return True

    def invalidate(self):
        self.current = None
