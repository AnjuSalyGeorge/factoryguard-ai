
# FactoryGuard AI — Day 7 LangGraph Architecture

## Objective

Coordinate sensor evidence, local vision inspection,
maintenance retrieval, and diagnostic reporting using
a structured LangGraph workflow.

## Framework

LangGraph, Python, local Ollama models.

## Workflow Nodes

1. validate
2. vision
3. retrieve
4. advisor (conditional)
5. diagnosis
6. handoff

## Conditional Routing

- Invalid input -> END
- Valid input -> vision
- Retrieved documents -> advisor
- No documents -> diagnosis
- Diagnosis -> advisory handoff -> END

## Failure Handling

- Vision failure: use sensor evidence.
- Retrieval failure: produce limited diagnosis.
- Advisor failure: preserve retrieved documents.
- Invalid machine input: stop workflow.

## Safety Architecture

LangGraph does not call machine-control methods.

The diagnostic report always has
restart_authorized=False.

The recovery handoff is advisory only.

The Day 6 behaviour tree coordinates simulated
recovery with explicit operator actions.

The Day 2 deterministic controller remains
authoritative over machine state.

## Known Limitations

- Synthetic industrial scenarios.
- Small maintenance knowledge base.
- Local VLM inference may be slow.
- No persistent graph checkpointing yet.
- No immutable fault-episode identifier.
- No authenticated operator identity.
- No real hardware integration.
- Not certified for industrial safety.

## Next Development Stage

Day 8: Streamlit operator dashboard.
Day 9: SQLite logging and persistence.
Day 10: Full integration and hardening.
Day 11: Evaluation and adversarial tests.
Day 12: Final demo and submission.
