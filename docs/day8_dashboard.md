
# FactoryGuard AI — Day 8 Streamlit Dashboard

## Objective

Provide an interactive, local dashboard for
simulated industrial fault monitoring, AI diagnosis,
maintenance evidence, and controlled recovery.

## Technology

- Python
- Streamlit
- Plotly
- Pandas
- LangGraph
- Ollama
- py_trees

## Dashboard Features

1. Machine state and active fault indicators
2. Synthetic scenario injection
3. Sensor metrics and sample-history charts
4. Local visual fault inspection
5. LangGraph diagnostic execution
6. Maintenance RAG evidence
7. Structured diagnostic reports
8. Operator acknowledgement
9. Simulated authorized fault resolution
10. Explicit simulated restart approval
11. Behaviour-tree recovery history
12. Event history and CSV/JSON exports

## Safety Architecture

The dashboard is an interface, not a safety controller.

AI outputs are advisory only.

Machine state transitions are validated by the
deterministic safety controller.

The behaviour tree coordinates recovery prerequisites.

Operator approval is required for simulated restart.

## Known Limitations

- Software-only simulation
- Button-driven sensor updates
- No live industrial hardware
- No real operator authentication
- In-memory session and event history
- No safety certification
- Local AI inference latency varies
- Fault-episode identity is not yet implemented
- No persistent audit database yet

## Run Instructions

From the project root:

python -m streamlit run app/dashboard.py

## Next Steps

Day 9: SQLite audit logging and persistence.

Day 10: Integration hardening and safety validation.

Day 11: Evaluation and adversarial testing.

Day 12: Final demonstration and submission.
