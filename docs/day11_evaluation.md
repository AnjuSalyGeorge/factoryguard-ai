
# FactoryGuard AI — Day 11 Evaluation Report

**Project:** FactoryGuard AI  
**Evaluation:** Synthetic Prototype Testing  
**Date:** November 9, 2026  
**Environment:** Windows, Python 3.12, Ollama (Gemma 3 4B), LangGraph, SQLite, Streamlit

## 1. Evaluation Objective

The objective of Day 11 was to evaluate the fault detection, AI diagnosis, maintenance-document retrieval, safety enforcement, workflow reliability, latency, and controlled recovery behavior of FactoryGuard AI.

FactoryGuard AI is an offline-first, software-only industrial fault diagnosis and simulated recovery prototype.

All evaluations were performed using simulated machine conditions and predefined test scenarios. No physical industrial equipment was connected.

## 2. Quantitative Evaluation Results

| Evaluation | Result | Scope |
|---|---|---|
| Fault detection | 4/4 passed (100%) | Four predefined synthetic scenarios |
| AI diagnosis | 4/4 correct (100%) | Four predefined diagnostic cases |
| RAG retrieval | Hit@3 = 3/3 (100%) | Three maintenance queries |
| Safety enforcement | 12/12 blocked (100%) | Twelve constructed unsafe restart conditions |
| Workflow reliability | 5/5 scenarios completed as expected | Normal and failure-handling scenarios |
| Workflow unit tests | 10/10 passed | Automated workflow tests |
| AI benchmark completion | 3/3 completed | Three benchmark runs |
| Mean AI benchmark latency | 48.577 seconds | Three local benchmark runs |
| Median AI benchmark latency | 22.020 seconds | Three local benchmark runs |

These results describe performance on the specified test cases only. They do not establish equivalent accuracy or reliability in real industrial environments.

## 3. Fault Detection Evaluation

Four simulated machine conditions were evaluated:

1. Normal operation
2. Conveyor jam
3. Motor overheating
4. High vibration

The deterministic safety controller correctly classified the expected operating or fault condition in all four cases.

**Result:** 4/4 passed.

The evaluation used predefined sensor readings. It did not test broad sensor noise, sensor drift, hardware calibration errors, or previously unseen industrial faults.

## 4. AI Diagnostic Evaluation

The LangGraph diagnostic workflow was evaluated on the same four synthetic scenarios.

The expected diagnostic labels were:

- NORMAL
- CONVEYOR_JAM
- MOTOR_OVERHEATING
- HIGH_VIBRATION

All four diagnostic runs completed and returned the expected primary diagnosis.

**Result:** 4/4 correct.

Observed diagnostic execution times were approximately:

- 87.908 seconds
- 91.744 seconds
- 36.964 seconds
- 31.349 seconds

These timings demonstrate that local AI inference introduces meaningful latency. They are not suitable evidence of hard real-time diagnostic performance.

## 5. Maintenance RAG Evaluation

The maintenance retrieval system was tested using three predefined queries associated with:

- Conveyor jam — PROC-001
- Motor overheating — PROC-002
- High vibration — PROC-003

All three expected procedures were retrieved within the top three results and appeared at rank one.

**Hit@3:** 3/3 (100%).

The maintenance knowledge base contains a small set of procedures. These results do not establish retrieval quality on large document collections, ambiguous questions, or unfamiliar maintenance terminology.

## 6. Safety Enforcement Evaluation

Twelve constructed unsafe restart conditions were evaluated.

The cases included active faults, stale or missing sensor freshness, emergency stop, open guard door, missing operator acknowledgement, missing restart approval, audit failure, incorrect fault episode, AI-generated restart claims, replayed approval, and invalidation after a new fault.

**Result:** 12/12 unsafe conditions blocked.

Additional automated tests confirmed that emergency-stop and open-guard conditions prevent restart across the simulated machine, recovery logic, and authorization checks.

**Additional result:** 6/6 targeted safety tests passed.

The deterministic safety controller remains authoritative. AI-generated recommendations do not independently authorize a restart.

These are software-level safety checks, not certified industrial safety functions.

## 7. Workflow Reliability Evaluation

Five workflow scenarios were evaluated:

| Scenario | Expected behavior |
|---|---|
| Normal | Advisory report produced |
| Vision failure | Workflow continues with available evidence |
| No documents | Workflow handles missing retrieval evidence |
| Advisor failure | Workflow handles advisor failure |
| Invalid input | Input rejected appropriately |

All five scenarios produced their expected workflow outcomes.

**Result:** 5/5 passed.

The dedicated workflow test suite also passed all ten tests.

## 8. Local AI Latency

Three benchmark runs completed.

| Run | Duration |
|---|---:|
| 1 | 102.012 seconds |
| 2 | 21.695 seconds |
| 3 | 22.023 seconds |

**Mean:** 48.577 seconds  
**Median:** 22.020 seconds

Latency varied substantially across runs. The small sample is insufficient to characterize tail latency or sustained performance.

FactoryGuard AI should be described as an advisory diagnostic system rather than a real-time industrial control system.

## 9. Dashboard Recovery Evaluation

### Scenario A — Successful Controlled Recovery

**Status: Passed in the simulated dashboard.**

The following sequence was observed:

1. Machine began in normal operation.
2. Conveyor jam was injected.
3. Deterministic safety controller entered STOPPED_FAULT.
4. LangGraph produced an AI diagnostic report.
5. Maintenance procedures were retrieved.
6. Diagnostic report was persisted to SQLite.
7. Operator acknowledged the fault.
8. Fault resolution was simulated.
9. Machine entered READY_FOR_REVIEW.
10. Explicit restart approval was recorded.
11. Simulated recovery completed successfully.
12. Machine returned to RUNNING.

Recovery actions were recorded in SQLite, including acknowledgement, fault resolution, restart request, restart approval, and restart outcome.

**Important observation:** The vision model described the obstruction image as normal while sensor evidence indicated a conveyor jam. The workflow identified this as CONFLICTING_EVIDENCE.

This demonstrates evidence-conflict detection in the observed case, but also highlights a limitation in vision-model reliability.

### Scenario B — New Fault During Recovery

**Status: Passed at the dashboard invalidation level.**

A conveyor jam was diagnosed and acknowledged. Before resolution, a new motor-overheating fault was injected.

The dashboard displayed the new active fault and invalidated the previous active recovery context.

A fresh diagnosis was required before recovery could continue.

This test did not exhaustively evaluate concurrent events or all possible approval-replay conditions.

### Scenario C — Audit Logging Failure

**Status: Component and safety tests passed; dashboard integration not fully verified.**

A disposable SQLite database was used to simulate an unavailable recovery audit table.

The recovery logger raised an SQLite error as expected.

An existing automated safety test also passed, confirming that restart authorization is rejected when audit health is false.

Code inspection confirmed that the dashboard contains checks intended to block restart when recovery request or approval logging fails.

However, a complete Streamlit interaction with an injected audit-write failure was not executed.

Therefore, end-to-end dashboard behavior under audit failure remains unverified.

### Scenario D — Emergency Stop and Guard Interlock

**Status: Automated safety tests passed; manual dashboard integration not verified.**

Six targeted automated tests passed across:

- Simulated machine restart
- Recovery execution
- Restart authorization

Both active emergency stop and open guard door were rejected in the tested conditions.

A complete manual dashboard restart attempt under these conditions was not performed during this evaluation.

## 10. Known Limitations

### Synthetic Data

The prototype uses simulated machine readings and predefined fault scenarios. Results may differ with noisy, incomplete, or real-world sensor data.

### Small Evaluation Dataset

The quantitative evaluation contains only four fault cases, four diagnostic cases, three RAG queries, and twelve constructed safety cases.

Reported 100% results apply only to these limited evaluations.

### Vision Reliability

The local vision model incorrectly described the obstruction image as normal during the observed jam scenario.

Sensor and vision evidence can disagree. Such disagreement must remain visible to the operator.

### Local AI Latency

AI diagnosis can take tens of seconds or longer, depending on local inference conditions.

The AI workflow must not be used as a time-critical safety shutdown mechanism.

### Simulated Recovery

Machine shutdown, fault resolution, acknowledgement, and restart are software simulations.

The prototype does not control industrial motors, programmable logic controllers, emergency-stop circuits, or physical safety interlocks.

### Audit and Recovery Integration

Audit logging and restart authorization include software safeguards.

Full dashboard-level audit-failure injection was not completed. Audit persistence and simulated machine actions are not established as one atomic transaction.

### Limited Generalization Evidence

The evaluation does not demonstrate robustness across industrial sites, equipment types, unseen faults, extensive sensor noise, or large maintenance knowledge bases.

### No Industrial Safety Certification

FactoryGuard AI is a demonstration prototype and has not undergone industrial safety certification, hardware validation, or production commissioning.

## 11. Evaluation Artifacts

Evaluation outputs are stored under the `evaluation/` directory:

- day11_fault_results.csv
- day11_diagnostic_results.csv
- day11_rag_results.csv
- day11_safety_results.csv
- day11_latency.csv
- workflow_results.csv
- day11_summary.json

These files provide reproducible records of the executed prototype evaluations.

## 12. Conclusion

FactoryGuard AI successfully demonstrated its intended core prototype capabilities across the evaluated synthetic scenarios:

- Deterministic machine fault detection
- Local AI-assisted diagnosis
- Maintenance-document retrieval
- Evidence-conflict reporting
- Operator-controlled simulated recovery
- Audit-aware restart authorization
- Emergency-stop and guard-interlock protections
- Workflow failure handling

The evaluation results support the feasibility of the software-only demonstration, but they do not establish real-world industrial accuracy, production readiness, or certified safety performance.

Further validation would require larger independent datasets, noisy sensor simulations, more varied maintenance queries, additional dashboard integration tests, and physical equipment testing under appropriate industrial safety supervision.
