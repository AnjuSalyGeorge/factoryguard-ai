
from src.agents.diagnostic import DiagnosticAgent
from src.rag.retriever import MaintenanceRetriever
from src.rag.advisor import (
    MaintenanceAdvisor,
    AdvisorError,
)
from src.vision.client import (
    OllamaVisionClient,
    VisionError,
)


class FactoryGuardDiagnosticPipeline:
    """
    Read-only diagnostic orchestration.

    Does not acknowledge, clear, approve,
    or restart the conveyor.
    """

    def __init__(
        self,
        vision_client=None,
        retriever=None,
        advisor=None,
        diagnostic_agent=None,
    ):
        self.vision_client = (
            vision_client or OllamaVisionClient()
        )
        self.retriever = (
            retriever or MaintenanceRetriever()
        )
        self.advisor = (
            advisor or MaintenanceAdvisor()
        )
        self.diagnostic_agent = (
            diagnostic_agent or DiagnosticAgent()
        )

    def run(
        self,
        machine,
        image_path: str,
    ):
        # Snapshot machine status for diagnostics.
        status = machine.get_status()

        vision_report = None
        advice = None
        documents = []
        errors = []

        # 1. Visual inspection
        try:
            vision_report = self.vision_client.inspect(
                image_path
            )
        except VisionError as exc:
            errors.append(f"Vision: {exc}")

        # 2. Build evidence-based retrieval query
        visual_description = (
            vision_report.get("suspected_issue", "")
            if vision_report else
            "Visual inspection unavailable"
        )

        query = (
            f"Machine state: {status['state']}. "
            f"Sensor faults: "
            f"{', '.join(status['active_faults'])}. "
            f"Visual observation: {visual_description}."
        )

        # 3. Retrieve maintenance procedures
        try:
            documents = self.retriever.search(
                query=query,
                fault_codes=status["active_faults"],
                top_k=3,
            )
        except Exception as exc:
            errors.append(
                f"Retrieval: {type(exc).__name__}: {exc}"
            )

        # 4. Generate optional grounded advice
        if documents:
            try:
                advice = self.advisor.recommend(
                    query=query,
                    retrieved_documents=documents,
                )
            except AdvisorError as exc:
                errors.append(f"Advisor: {exc}")

        # 5. Deterministic evidence assessment
        report = self.diagnostic_agent.diagnose(
            machine_status=status,
            vision_report=vision_report,
            documents=documents,
            advice=advice,
        )

        # 6. Record degraded operation
        report.limitations.extend(errors)

        report.metadata["pipeline_errors"] = errors
        report.metadata["retrieval_query"] = query

        # No machine-control method is called.
        return report
