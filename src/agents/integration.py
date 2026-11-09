
from src.agents.workflow import build_workflow
from src.agents.report_binding import bind_report


class FactoryGuardIntegration:
    def __init__(self, workflow=None):
        self.workflow = (
            workflow
            if workflow is not None
            else build_workflow()
        )

    def diagnose_episode(
        self,
        machine_status,
        image_path,
        episode,
    ):
        if episode is None:
            raise ValueError(
                "Active fault episode required"
            )

        if (
            machine_status.get("machine_id")
            != episode.machine_id
        ):
            raise ValueError(
                "Machine and episode do not match"
            )

        if machine_status.get("state") not in (
            "STOPPED_FAULT",
            "STOPPED_EMERGENCY",
        ):
            raise ValueError(
                "Machine must be fault-stopped"
            )

        result = self.workflow.invoke({
            "machine_status": machine_status,
            "image_path": image_path,
            "errors": [],
            "execution_trace": [],
            "workflow_status": "PENDING",
        })

        if result.get("workflow_status") != "ADVISORY_READY":
            raise RuntimeError(
                "Diagnostic workflow incomplete"
            )

        report = result.get("diagnostic_report")

        if not report:
            raise RuntimeError(
                "Diagnostic report missing"
            )

        bound = bind_report(report, episode)

        return {
            "graph_result": result,
            "bound_diagnostic": bound,
        }
