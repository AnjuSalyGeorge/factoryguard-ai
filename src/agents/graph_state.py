
from typing import Any, TypedDict


class FactoryGuardState(TypedDict, total=False):
    machine_status: dict[str, Any]
    image_path: str

    vision_report: dict[str, Any] | None
    retrieved_documents: list[dict[str, Any]]
    maintenance_advice: dict[str, Any] | None

    diagnostic_report: dict[str, Any] | None
    recovery_handoff: dict[str, Any] | None

    errors: list[str]
    execution_trace: list[str]

    workflow_status: str
