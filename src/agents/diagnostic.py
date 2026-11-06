
from src.agents.schemas import DiagnosticReport
from src.agents.evidence import assess_evidence


class DiagnosticAgent:
    """
    Combines sensor, vision, and RAG evidence.

    Produces advisory reports only.
    Never changes machine state.
    """

    def diagnose(
        self,
        machine_status: dict,
        vision_report: dict | None = None,
        documents: list[dict] | None = None,
        advice: dict | None = None,
    ) -> DiagnosticReport:

        vision_report = vision_report or {}
        documents = documents or []
        advice = advice or {}

        vision_status = vision_report.get(
            "scene_status", "unavailable"
        )

        sensor_faults = list(
            machine_status.get("active_faults", [])
        )

        assessment = assess_evidence(
            sensor_faults=sensor_faults,
            vision_status=vision_status,
            emergency_stop=machine_status.get(
                "emergency_stop", False
            ),
            guard_door_closed=machine_status.get(
                "guard_door_closed", True
            ),
        )

        evidence = list(assessment.evidence)
        limitations = list(assessment.limitations)

        if vision_status == "unavailable":
            limitations.append(
                "Local visual inspection unavailable"
            )

        if not machine_status.get(
            "readings_fresh", False
        ):
            limitations.append(
                "Sensor readings are missing or stale"
            )

        if machine_status.get("fault_latched", False):
            evidence.append(
                "The safety controller has a latched fault"
            )

        procedure_ids = [
            doc["id"]
            for doc in documents
            if isinstance(doc.get("id"), str)
        ]

        recommended_checks = []

        # Use retrieved manual text as a deterministic
        # fallback if the generative advisor is unavailable.
        if documents:
            recommended_checks.append(
                "Review retrieved maintenance procedures: "
                + ", ".join(procedure_ids)
            )

        if advice:
            cited_ids = advice.get("procedure_ids", [])

            if (
                isinstance(cited_ids, list)
                and set(cited_ids).issubset(
                    set(procedure_ids)
                )
            ):
                checks = advice.get(
                    "recommended_checks", []
                )

                if (
                    isinstance(checks, list)
                    and all(
                        isinstance(c, str)
                        for c in checks
                    )
                ):
                    recommended_checks.extend(checks)
            else:
                limitations.append(
                    "Generated advice contained unsupported citations"
                )

        recommended_checks.append(
            "Keep all recovery actions under "
            "deterministic safety and operator control"
        )

        return DiagnosticReport(
            machine_id=machine_status["machine_id"],
            machine_state=machine_status["state"],
            primary_diagnosis=assessment.diagnosis,
            severity=assessment.severity,
            sensor_faults=sensor_faults,
            vision_status=vision_status,
            evidence=evidence,
            procedure_ids=procedure_ids,
            recommended_checks=recommended_checks,
            limitations=limitations,
            confidence_label=assessment.confidence_label,
            ai_available=bool(vision_report),
            restart_authorized=False,
            metadata={
                "fault_latched": machine_status.get(
                    "fault_latched", False
                ),
                "vision_model": vision_report.get(
                    "model"
                ),
                "retrieved_document_count": len(
                    documents
                ),
                "generated_advice_available": bool(
                    advice
                ),
            },
        )
