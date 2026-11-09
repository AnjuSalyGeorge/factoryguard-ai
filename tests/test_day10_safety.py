
from src.safety.episode import FaultEpisodeTracker
from src.agents.report_binding import (
    bind_report,
    validate_report_binding,
)
from src.recovery.authorization import evaluate_restart
from src.recovery.approval import ApprovalManager


def stopped_status(faults=None):
    return {
        "machine_id": "CONV-001",
        "state": "STOPPED_FAULT",
        "active_faults": faults or ["OVERCURRENT", "LOW_RPM"],
        "fault_latched": True,
        "readings_fresh": True,
        "emergency_stop_active": False,
        "guard_door_closed": True,
    }


def ready_status():
    return {
        "machine_id": "CONV-001",
        "state": "READY_FOR_REVIEW",
        "active_faults": [],
        "fault_latched": False,
        "readings_fresh": True,
        "emergency_stop_active": False,
        "guard_door_closed": True,
    }


def make_bound_report():
    tracker = FaultEpisodeTracker()
    episode = tracker.observe(stopped_status())

    report = {
        "machine_id": "CONV-001",
        "machine_state": "STOPPED_FAULT",
        "primary_diagnosis": "CONVEYOR_JAM",
        "restart_authorized": False,
    }

    bound = bind_report(report, episode)
    return tracker, episode, bound


def authorize(status=None, **overrides):
    _, episode, bound = make_bound_report()

    args = {
        "machine_status": (
            status if status is not None else ready_status()
        ),
        "episode": episode,
        "bound_report": bound,
        "operator_acknowledged": True,
        "operator_approved": True,
        "audit_healthy": True,
    }

    args.update(overrides)

    return evaluate_restart(**args)


def test_new_fault_creates_new_episode():
    tracker = FaultEpisodeTracker()

    first = tracker.observe(stopped_status())
    second = tracker.observe(
        stopped_status(["OVERHEATING"])
    )

    assert first.episode_id != second.episode_id


def test_same_fault_preserves_episode():
    tracker = FaultEpisodeTracker()

    first = tracker.observe(stopped_status())
    second = tracker.observe(stopped_status())

    assert first.episode_id == second.episode_id


def test_ready_state_preserves_episode():
    tracker = FaultEpisodeTracker()

    first = tracker.observe(stopped_status())
    second = tracker.observe(ready_status())

    assert first.episode_id == second.episode_id


def test_running_state_clears_episode():
    tracker = FaultEpisodeTracker()
    tracker.observe(stopped_status())

    normal = ready_status()
    normal["state"] = "RUNNING"

    assert tracker.observe(normal) is None


def test_stale_report_rejected():
    tracker, old_episode, bound = make_bound_report()

    new_episode = tracker.observe(
        stopped_status(["OVERHEATING"])
    )

    assert not validate_report_binding(
        bound, new_episode
    )


def test_machine_mismatch_rejected():
    tracker, episode, _ = make_bound_report()

    report = {
        "machine_id": "OTHER-MACHINE",
        "machine_state": "STOPPED_FAULT",
        "restart_authorized": False,
    }

    try:
        bind_report(report, episode)
        assert False, "Expected rejection"
    except ValueError:
        pass


def test_ai_restart_authority_rejected():
    _, episode, _ = make_bound_report()

    report = {
        "machine_id": "CONV-001",
        "machine_state": "STOPPED_FAULT",
        "restart_authorized": True,
    }

    try:
        bind_report(report, episode)
        assert False, "Expected rejection"
    except ValueError:
        pass


def test_safe_conditions_allow_gate():
    assert authorize().allowed is True


def test_active_fault_blocks_restart():
    status = ready_status()
    status["active_faults"] = ["OVERCURRENT"]

    assert authorize(status).allowed is False


def test_stale_sensor_blocks_restart():
    status = ready_status()
    status["readings_fresh"] = False

    assert authorize(status).allowed is False


def test_missing_sensor_freshness_blocks_restart():
    status = ready_status()
    del status["readings_fresh"]

    assert authorize(status).allowed is False


def test_emergency_stop_blocks_restart():
    status = ready_status()
    status["emergency_stop_active"] = True

    assert authorize(status).allowed is False


def test_open_guard_blocks_restart():
    status = ready_status()
    status["guard_door_closed"] = False

    assert authorize(status).allowed is False


def test_missing_operator_approval_blocks_restart():
    decision = authorize(
        operator_approved=False
    )

    assert decision.allowed is False


def test_missing_acknowledgement_blocks_restart():
    decision = authorize(
        operator_acknowledged=False
    )

    assert decision.allowed is False


def test_audit_failure_blocks_restart():
    decision = authorize(
        audit_healthy=False
    )

    assert decision.allowed is False


def test_wrong_episode_blocks_restart():
    tracker = FaultEpisodeTracker()
    wrong_episode = tracker.observe(
        stopped_status(["HIGH_VIBRATION"])
    )

    decision = authorize(
        episode=wrong_episode
    )

    assert decision.allowed is False


def test_approval_is_single_use():
    manager = ApprovalManager()

    manager.approve("episode-001")

    assert manager.consume("episode-001")
    assert not manager.consume("episode-001")


def test_approval_wrong_episode_rejected():
    manager = ApprovalManager()

    manager.approve("episode-001")

    assert not manager.consume("episode-002")


def test_approval_invalidation():
    manager = ApprovalManager()

    manager.approve("episode-001")
    manager.invalidate()

    assert not manager.is_valid("episode-001")
