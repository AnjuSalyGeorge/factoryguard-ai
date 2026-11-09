
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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
        "active_faults": (
            faults
            if faults is not None
            else ["OVERCURRENT", "LOW_RPM"]
        ),
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


def setup():
    tracker = FaultEpisodeTracker()
    episode = tracker.observe(stopped_status())

    bound = bind_report({
        "machine_id": "CONV-001",
        "machine_state": "STOPPED_FAULT",
        "primary_diagnosis": "CONVEYOR_JAM",
        "restart_authorized": False,
    }, episode)

    return tracker, episode, bound


def main():
    tracker, episode, bound = setup()

    scenarios = []

    def add(name, changes=None, overrides=None):
        status = ready_status()
        status.update(changes or {})

        arguments = {
            "machine_status": status,
            "episode": episode,
            "bound_report": bound,
            "operator_acknowledged": True,
            "operator_approved": True,
            "audit_healthy": True,
        }
        arguments.update(overrides or {})

        decision = evaluate_restart(**arguments)

        scenarios.append({
            "scenario": name,
            "blocked": not decision.allowed,
            "reasons": "; ".join(decision.reasons),
        })

    add("Active fault", {
        "active_faults": ["OVERCURRENT"]
    })
    add("Stale sensors", {
        "readings_fresh": False
    })
    add("Missing freshness", {
        "readings_fresh": None
    })
    add("Emergency stop", {
        "emergency_stop_active": True
    })
    add("Open guard", {
        "guard_door_closed": False
    })
    add("Missing acknowledgement", overrides={
        "operator_acknowledged": False
    })
    add("Missing approval", overrides={
        "operator_approved": False
    })
    add("Audit failure", overrides={
        "audit_healthy": False
    })

    new_episode = tracker.observe(
        stopped_status(["OVERHEATING"])
    )

    add("Wrong fault episode", overrides={
        "episode": new_episode
    })

    try:
        bind_report({
            "machine_id": "CONV-001",
            "machine_state": "STOPPED_FAULT",
            "restart_authorized": True,
        }, episode)
        ai_blocked = False
    except ValueError:
        ai_blocked = True

    scenarios.append({
        "scenario": "AI restart claim",
        "blocked": ai_blocked,
        "reasons": "Report binding validation",
    })

    approvals = ApprovalManager()
    approvals.approve(episode.episode_id)
    first_use = approvals.consume(episode.episode_id)
    replay_blocked = (
        first_use
        and not approvals.consume(episode.episode_id)
    )

    scenarios.append({
        "scenario": "Approval replay",
        "blocked": replay_blocked,
        "reasons": "One-time token consumption",
    })

    scenarios.append({
        "scenario": "New fault invalidates old report",
        "blocked": not validate_report_binding(
            bound, new_episode
        ),
        "reasons": "Episode binding validation",
    })

    output = (
        ROOT / "evaluation" / "day11_safety_results.csv"
    )

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=scenarios[0].keys()
        )
        writer.writeheader()
        writer.writerows(scenarios)

    blocked = sum(
        row["blocked"] for row in scenarios
    )

    for row in scenarios:
        print(
            f"{'PASS' if row['blocked'] else 'FAIL'} "
            f"{row['scenario']}"
        )

    print(
        f"\nBlocked/rejected: {blocked}/{len(scenarios)}"
    )
    print("Saved:", output)

    if blocked != len(scenarios):
        raise SystemExit("Safety evaluation failed")


if __name__ == "__main__":
    main()
