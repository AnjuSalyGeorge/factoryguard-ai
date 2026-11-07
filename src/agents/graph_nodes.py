
from src.agents.diagnostic import DiagnosticAgent
from src.rag.retriever import MaintenanceRetriever
from src.rag.advisor import MaintenanceAdvisor
from src.vision.client import OllamaVisionClient


def add_trace(state, node_name):
    return [
        *state.get("execution_trace", []),
        node_name,
    ]


def add_error(state, message):
    return [
        *state.get("errors", []),
        message,
    ]


class FactoryGuardGraphNodes:
    def __init__(
        self,
        vision_client=None,
        retriever=None,
        advisor=None,
        diagnostic_agent=None,
    ):
        self.vision_client = vision_client
        self.retriever = retriever
        self.advisor = advisor
        self.diagnostic_agent = (
            diagnostic_agent or DiagnosticAgent()
        )

    def validate(self, state):
        status = state.get("machine_status")

        required = {
            "machine_id",
            "state",
            "active_faults",
        }

        valid = (
            isinstance(status, dict)
            and required.issubset(status)
            and isinstance(status.get("machine_id"), str)
            and isinstance(status.get("state"), str)
            and isinstance(status.get("active_faults"), list)
            and all(
                isinstance(code, str)
                for code in status.get("active_faults", [])
            )
        )

        if not valid:
            return {
                "workflow_status": "INVALID_INPUT",
                "errors": add_error(
                    state,
                    "Invalid machine status snapshot",
                ),
                "execution_trace": add_trace(
                    state, "validate"
                ),
            }

        return {
            "workflow_status": "VALIDATED",
            "execution_trace": add_trace(
                state, "validate"
            ),
        }

    def inspect_vision(self, state):
        image_path = state.get("image_path")

        if not image_path:
            return {
                "vision_report": None,
                "errors": add_error(
                    state, "Vision image not supplied"
                ),
                "execution_trace": add_trace(
                    state, "inspect_vision"
                ),
            }

        try:
            client = (
                self.vision_client
                if self.vision_client is not None
                else OllamaVisionClient()
            )

            report = client.inspect(image_path)

            return {
                "vision_report": report,
                "execution_trace": add_trace(
                    state, "inspect_vision"
                ),
            }

        except Exception as exc:
            return {
                "vision_report": None,
                "errors": add_error(
                    state,
                    f"Vision unavailable: {type(exc).__name__}: {exc}",
                ),
                "execution_trace": add_trace(
                    state, "inspect_vision"
                ),
            }

    def retrieve(self, state):
        status = state["machine_status"]
        vision = state.get("vision_report") or {}

        faults = status.get("active_faults", [])

        query = (
            f"Machine state: {status['state']}. "
            f"Sensor faults: {', '.join(faults)}. "
            f"Visual finding: "
            f"{vision.get('suspected_issue', 'unavailable')}."
        )

        try:
            retriever = (
                self.retriever
                if self.retriever is not None
                else MaintenanceRetriever()
            )

            documents = retriever.search(
                query=query,
                fault_codes=faults,
                top_k=3,
            )

            return {
                "retrieved_documents": documents,
                "execution_trace": add_trace(
                    state, "retrieve"
                ),
            }

        except Exception as exc:
            return {
                "retrieved_documents": [],
                "errors": add_error(
                    state,
                    f"Retrieval unavailable: {type(exc).__name__}: {exc}",
                ),
                "execution_trace": add_trace(
                    state, "retrieve"
                ),
            }

    def advise(self, state):
        documents = state.get(
            "retrieved_documents", []
        )

        if not documents:
            return {
                "maintenance_advice": None,
                "execution_trace": add_trace(
                    state, "advise_skipped"
                ),
            }

        status = state["machine_status"]
        vision = state.get("vision_report") or {}

        query = (
            f"Faults: {status['active_faults']}. "
            f"Visual finding: "
            f"{vision.get('suspected_issue', 'unavailable')}"
        )

        try:
            advisor = (
                self.advisor
                if self.advisor is not None
                else MaintenanceAdvisor()
            )

            advice = advisor.recommend(
                query=query,
                retrieved_documents=documents,
            )

            return {
                "maintenance_advice": advice,
                "execution_trace": add_trace(
                    state, "advise"
                ),
            }

        except Exception as exc:
            return {
                "maintenance_advice": None,
                "errors": add_error(
                    state,
                    f"Advisor unavailable: {type(exc).__name__}: {exc}",
                ),
                "execution_trace": add_trace(
                    state, "advise"
                ),
            }

    def diagnose(self, state):
        report = self.diagnostic_agent.diagnose(
            machine_status=state["machine_status"],
            vision_report=state.get("vision_report"),
            documents=state.get(
                "retrieved_documents", []
            ),
            advice=state.get("maintenance_advice"),
        )

        report_dict = report.to_dict()

        # Errors are important diagnostic limitations.
        report_dict["limitations"] = [
            *report_dict["limitations"],
            *state.get("errors", []),
        ]

        return {
            "diagnostic_report": report_dict,
            "workflow_status": "DIAGNOSED",
            "execution_trace": add_trace(
                state, "diagnose"
            ),
        }

    def prepare_handoff(self, state):
        report = state.get("diagnostic_report")

        if not report:
            return {
                "workflow_status": "FAILED",
                "execution_trace": add_trace(
                    state, "prepare_handoff"
                ),
            }

        handoff = {
            "machine_id": report["machine_id"],
            "machine_state": report["machine_state"],
            "primary_diagnosis":
                report["primary_diagnosis"],
            "severity": report["severity"],
            "procedure_ids": report["procedure_ids"],
            "requires_operator_review": True,
            "restart_authorized": False,
        }

        return {
            "recovery_handoff": handoff,
            "workflow_status": "ADVISORY_READY",
            "execution_trace": add_trace(
                state, "prepare_handoff"
            ),
        }
