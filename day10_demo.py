
from src.safety.episode import FaultEpisodeTracker
from src.agents.report_binding import bind_report
from src.recovery.authorization import evaluate_restart
from src.recovery.approval import ApprovalManager


def make_status(state, faults, latched):
    return {
        "machine_id": "CONV-001",
        "state": state,
        "active_faults": faults,
        "fault_latched": latched,
        "readings_fresh": True,
        "emergency_stop_active": False,
        "guard_door_closed": True,
    }


def main():
    print("=" * 65)
    print("FACTORYGUARD AI — DAY 10 SAFETY HARDENING")
    print("=" * 65)

    tracker = FaultEpisodeTracker()
    approvals = ApprovalManager()

    print("\n1. CONVEYOR JAM DETECTED")

    jam_status = make_status(
        "STOPPED_FAULT",
        ["OVERCURRENT", "LOW_RPM"],
        True,
    )

    episode_a = tracker.observe(jam_status)

    print("Episode:", episode_a.episode_id)

    print("\n2. DIAGNOSTIC REPORT CREATED")

    report = {
        "machine_id": "CONV-001",
        "machine_state": "STOPPED_FAULT",
        "primary_diagnosis": "CONVEYOR_JAM",
        "restart_authorized": False,
    }

    bound = bind_report(report, episode_a)

    print("Report bound to:", bound.episode_id)

    print("\n3. FAULT CLEARED")

    ready = make_status(
        "READY_FOR_REVIEW",
        [],
        False,
    )

    tracker.observe(ready)

    print("\n4. OPERATOR APPROVES RESTART")

    approvals.approve(episode_a.episode_id)

    decision = evaluate_restart(
        machine_status=ready,
        episode=tracker.current,
        bound_report=bound,
        operator_acknowledged=True,
        operator_approved=approvals.is_valid(
            episode_a.episode_id
        ),
        audit_healthy=True,
    )

    assert decision.allowed is True
    print("Authorization gate:", decision.allowed)

    print("\n5. APPROVAL CONSUMED")

    assert approvals.consume(episode_a.episode_id)
    assert not approvals.consume(episode_a.episode_id)

    print("Replay attempt rejected")

    print("\n6. NEW FAULT DETECTED")

    overheating = make_status(
        "STOPPED_FAULT",
        ["OVERHEATING"],
        True,
    )

    episode_b = tracker.observe(overheating)

    assert episode_b.episode_id != episode_a.episode_id

    print("New episode:", episode_b.episode_id)

    print("\n7. OLD DIAGNOSIS REJECTED")

    decision = evaluate_restart(
        machine_status=ready,
        episode=episode_b,
        bound_report=bound,
        operator_acknowledged=True,
        operator_approved=True,
        audit_healthy=True,
    )

    assert decision.allowed is False

    print("Authorization gate:", decision.allowed)
    print("Reasons:", decision.reasons)

    print("\nDAY 10 SAFETY DEMO PASSED")


if __name__ == "__main__":
    main()
