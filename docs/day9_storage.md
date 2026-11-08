
# FactoryGuard AI — Day 9 Storage Architecture

## Objective

Persist simulated industrial fault events,
AI diagnostic reports, and recovery decisions
using a local SQLite database.

## Technology

- Python sqlite3
- SQLite database
- Streamlit dashboard
- LangGraph diagnostics
- py_trees recovery controller

## Database Tables

### events
Stores simulator, fault, operator, and system events.

### diagnostics
Stores structured AI reports and supporting evidence.

### recovery_actions
Stores operator requests, recovery decisions,
and simulated restart outcomes.

## Reliability Features

- Automatic schema initialization
- Parameterized SQL queries
- UTC timestamps
- Persistent local database
- Database health checks
- Explicit audit failure indicators
- Restart blocked when required
  pre-restart audit writes fail

## Safety Boundaries

The database does not authorize machine control.

LangGraph produces advisory reports only.

The behaviour tree coordinates recovery.

The deterministic safety controller validates
machine state transitions.

## Known Limitations

- Local single-machine SQLite storage
- No authenticated operator identity
- No immutable or tamper-evident audit log
- No persistent live machine state
- No transactional guarantee spanning
  database writes and simulated machine actions
- No real industrial hardware integration

## Next Steps

Day 10: End-to-end integration and hardening.
Day 11: Safety evaluation and adversarial testing.
Day 12: Final demonstration and submission.
