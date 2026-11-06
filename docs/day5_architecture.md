
# FactoryGuard AI — Day 5 Diagnostic Architecture

## Purpose

Combine deterministic sensor evidence, local visual
inspection, and maintenance RAG into an advisory
industrial fault diagnosis.

## Components

### Sensor Safety Controller
- Detects simulated faults
- Latches fault states
- Rejects unauthorized restarts
- Maintains authoritative machine state

### Local Vision Client
- Uses Ollama and Gemma 3
- Inspects synthetic workcell images
- Returns structured visual observations
- Has no machine-control permissions

### Maintenance RAG
- Retrieves synthetic maintenance procedures
- Uses local semantic embeddings
- Returns traceable procedure identifiers
- Supports grounded troubleshooting advice

### Diagnostic Evidence Engine
- Applies deterministic diagnosis rules
- Prioritizes safety interlocks
- Identifies contradictory evidence
- Produces qualitative evidence labels

### Diagnostic Agent
- Combines available evidence
- Generates structured diagnostic reports
- Preserves limitations and uncertainty
- Cannot authorize restart

## Safety Boundary

The diagnostic pipeline must never invoke:

- acknowledge_fault()
- clear_fault()
- approve_restart()
- restart()

Recovery authorization belongs to the
deterministic controller and operator workflow.

## Known Limitations

- Synthetic sensor data and images
- Prototype thresholds, not certified limits
- Small maintenance knowledge base
- Uncalibrated diagnostic confidence labels
- Rule-based primary diagnosis selection
- No real industrial hardware integration
- No safety certification
- AI latency may be high on CPU

## Future Work

Day 6: Deterministic behaviour-tree recovery
Day 7: LangGraph orchestration
Day 8: Operator dashboard
Day 9: SQLite audit logging
Day 10+: Integration, evaluation, demonstration
