
# FactoryGuard AI — Offline Verification Report

## Test Date
November 5, 2026

## Objective
Verify that FactoryGuard AI can perform local maintenance
procedure retrieval, AI vision inspection, maintenance advice
generation, and deterministic safety checks without internet
connectivity.

## Test Environment
- Operating system: Windows
- Python: 3.12
- AI runtime: Ollama (local)
- Vision and advisory model: gemma3:4b
- Embedding model: nomic-embed-text
- Maintenance documents: Local JSON
- Vector index: Local JSON
- Internet connection: Wi-Fi disconnected during testing

## Test 1 — Offline RAG Retrieval

Command:

    .venv\Scripts\python.exe rag_search_demo.py

Results:

| Rank | Procedure | Score |
|---|---|---|
| 1 | PROC-001 Conveyor Jam and Obstruction | 0.9063 |
| 2 | PROC-004 Misaligned Product | 0.7652 |
| 3 | PROC-003 High Vibration | 0.6212 |

Result: PASS

The retriever ranked the expected conveyor jam procedure
first without requiring an external search service.

## Test 2 — Complete Offline Integration

Command:

    .venv\Scripts\python.exe day4_demo.py

### Sensor Detection
- Machine ID: M-102
- Faults: OVERCURRENT, LOW_RPM
- Machine state: STOPPED_FAULT
- Fault latched: True

### Vision Inspection
- Model: gemma3:4b
- Execution time: 73.11 seconds
- Scene classification: normal
- Observed an orange irregular object on the conveyor

The vision model completed its inspection but did not
correctly classify the simulated obstruction as a fault.

### RAG Retrieval
Top-ranked procedure:
PROC-001 Conveyor Jam and Obstruction

### Maintenance Recommendation
Suspected issue:
Conveyor obstruction with OVERCURRENT and LOW_RPM faults.

Recommended checks:
- Visual inspection of the conveyor belt
- Fresh sensor readings

Cited procedure:
PROC-001

The advisor stated that machine restart could not be
authorized until the obstruction was resolved by authorized
personnel following isolation and lockout procedures.

### Safety Verification
- Restart allowed: False
- Machine state: STOPPED_FAULT

Result: PASS

The deterministic safety controller prevented restart
despite the vision model reporting a normal scene.

## Conclusion

Both offline demonstrations completed successfully.

The results support that FactoryGuard AI can run its
simulated sensor monitoring, local AI inference, RAG
retrieval, maintenance advisory generation, and
deterministic safety checks without internet connectivity.

## Limitations
- Testing used synthetic maintenance documents and scenarios.
- Vision classification did not correctly identify the obstruction.
- Maintenance advice is advisory and is not independently
  verified for complete factual grounding.
- The system has not been validated on physical machinery.
- The AI cannot authorize machine restart.

## Final Status
OFFLINE VERIFICATION: PASSED

Wi-Fi was reconnected after testing.
