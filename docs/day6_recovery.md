
# FactoryGuard AI — Day 6 Recovery Architecture

## Objective

Coordinate simulated conveyor fault recovery using
a deterministic behaviour tree.

## Framework

py_trees 2.x

## Recovery Sequence

1. Confirm fault-stopped or ready-for-review state.
2. Require a matching diagnostic report.
3. Validate emergency-stop and guard interlocks.
4. Wait for explicit operator acknowledgement.
5. Request fault acknowledgement from the controller.
6. Confirm no active faults and fresh sensor readings.
7. Request fault clearance from the controller.
8. Wait for explicit operator restart approval.
9. Revalidate safety and request simulated restart.

## Authority Separation

### Diagnostic Agent

- Provides advisory evidence.
- Cannot approve or execute recovery.

### Behaviour Tree

- Coordinates workflow steps.
- Cannot bypass controller safety checks.

### Safety Controller

- Maintains authoritative machine state.
- Validates fault clearance and restart.
- Rejects unsafe operations.

### Operator

- Acknowledges faults.
- Provides explicit simulated restart approval.

## Failure Handling

- Active emergency stop: reject recovery.
- Open guard: reject recovery.
- Unresolved fault: wait.
- Stale readings: wait or reject restart.
- Missing diagnosis: wait.
- Invalid diagnosis: reject.
- Missing operator approval: wait.

## Evaluation Results

Evaluation script: `evaluate_recovery.py`

Results file: `evaluation/recovery_results.csv`

| Scenario | Expected Result | Observed State | Passed |
|---|---|---|---|
| Normal recovery | Restart succeeds | RUNNING | Yes |
| Unresolved fault | Restart blocked | STOPPED_FAULT | Yes |
| Emergency stop | Restart blocked | STOPPED_EMERGENCY | Yes |
| Open guard | Restart blocked | STOPPED_FAULT | Yes |
| Stale readings | Restart blocked | READY_FOR_REVIEW | Yes |

### Evaluation Summary

- Scenario evaluations: 5/5 passed.
- Unsafe scenarios: 4/4 did not restart.
- Full project test suite: 59/59 passed.
- Day 5 to Day 6 integration demo: passed.

These results verify expected simulated control-flow
outcomes. They do not establish safety for real
industrial equipment.

## Known Limitations

- Software-only simulation.
- No physical lockout verification.
- No operator authentication.
- No certified safety controller.
- No immutable fault-episode identity yet.
- No protection against all possible race conditions.
- Recovery approvals are simulated inputs.
- Behaviour-tree event history is held in memory.
- Evaluation does not cover every possible failure
  condition or adversarial sequence.

## Future Work

- Day 7: LangGraph orchestration.
- Day 8: Operator dashboard.
- Day 9: SQLite event persistence.
- Day 10: End-to-end integration and hardening.
