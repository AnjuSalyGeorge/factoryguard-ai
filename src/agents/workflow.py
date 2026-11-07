
from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from src.agents.graph_state import FactoryGuardState
from src.agents.graph_nodes import FactoryGuardGraphNodes


def route_after_validation(state):
    if state.get("workflow_status") == "INVALID_INPUT":
        return "end"

    return "vision"


def route_after_retrieval(state):
    if state.get("retrieved_documents"):
        return "advisor"

    return "diagnosis"


def build_workflow(nodes=None):
    nodes = nodes or FactoryGuardGraphNodes()

    builder = StateGraph(FactoryGuardState)

    builder.add_node("validate", nodes.validate)
    builder.add_node(
        "vision", nodes.inspect_vision
    )
    builder.add_node(
        "retrieve", nodes.retrieve
    )
    builder.add_node(
        "advisor", nodes.advise
    )
    builder.add_node(
        "diagnosis", nodes.diagnose
    )
    builder.add_node(
        "handoff", nodes.prepare_handoff
    )

    builder.add_edge(START, "validate")

    builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "vision": "vision",
            "end": END,
        },
    )

    builder.add_edge("vision", "retrieve")

    builder.add_conditional_edges(
        "retrieve",
        route_after_retrieval,
        {
            "advisor": "advisor",
            "diagnosis": "diagnosis",
        },
    )

    builder.add_edge("advisor", "diagnosis")
    builder.add_edge("diagnosis", "handoff")
    builder.add_edge("handoff", END)

    return builder.compile()
