
from src.recovery.authorization import evaluate_restart


def check_restart_preconditions(
    machine_status,
    episode,
    bound_diagnostic,
    runner,
    audit_healthy,
):
    """
    Evaluate restart prerequisites using the current
    machine state, fault episode, diagnostic evidence,
    recovery context, and audit health.

    This function does not modify the machine or
    execute a restart.
    """
    return evaluate_restart(
        machine_status=machine_status,
        episode=episode,
        bound_report=bound_diagnostic,
        operator_acknowledged=(
            runner.context.operator_acknowledged
        ),
        operator_approved=(
            runner.context.operator_restart_approved
        ),
        audit_healthy=audit_healthy,
    )
