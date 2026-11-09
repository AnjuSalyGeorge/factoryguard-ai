import json
import traceback
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.dashboard_state import (
    new_dashboard_state,
    reset_dashboard_state,
    apply_scenario,
    add_event,
    get_dashboard_status,
)
from app.dashboard_utils import (
    SENSOR_FIELDS,
    diagnosis_summary,
    make_sensor_record,
    state_label,
)

from src.simulator.machine import get_reading
from src.agents.workflow import build_workflow
from src.agents.schemas import DiagnosticReport
from src.agents.report_binding import bind_report
from src.recovery.runner import RecoveryRunner

from src.recovery.audit_gate import check_restart_preconditions


from src.storage.database import FactoryGuardDatabase
from src.storage.event_logger import EventLogger
from src.storage.diagnostic_store import DiagnosticStore
from src.storage.recovery_logger import RecoveryLogger


# ==================================================
# 1. STREAMLIT PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="FactoryGuard AI",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# 2. INITIALIZE DASHBOARD SESSION STATE
# ==================================================

if "factoryguard" not in st.session_state:
    st.session_state.factoryguard = new_dashboard_state()

state = st.session_state.factoryguard
machine = state["machine"]


# ==================================================
# DAY 9 - STEP 9: RECOVERY AUDIT HELPER
# ==================================================

def log_recovery_action(
    state,
    action,
    result,
    details=None,
):
    machine = state["machine"]

    try:
        return RecoveryLogger().log(
            machine_id=machine.machine_id,
            action=action,
            result=result,
            machine_state=machine.state.value,
            details=details,
        )

    except Exception as exc:
        state["audit_logging_failed"] = True
        state["last_error"] = (
            f"Recovery audit failed: {exc}"
        )
        return None


# ==================================================
# 3. DASHBOARD HEADER
# ==================================================

st.title("🏭 FactoryGuard AI")

st.caption(
    "Offline-first industrial fault diagnosis "
    "and controlled recovery — software-only prototype"
)

st.warning(
    "SIMULATION ONLY: This dashboard is not connected "
    "to physical industrial equipment."
)


# ==================================================
# DAY 9 - STEP 11: AUDIT HEALTH WARNING
# ==================================================

if state.get("audit_logging_failed", False):
    st.error(
        "AUDIT SYSTEM DEGRADED: "
        "Persistent logging failed. "
        "Simulated restart is disabled."
    )


# ==================================================
# DAY 9 - STEP 11: DATABASE HEALTH INDICATOR
# ==================================================

try:
    database_healthy = (
        FactoryGuardDatabase().health_check()
    )
except Exception:
    database_healthy = False

if database_healthy:
    st.caption("SQLite connection: available")
else:
    st.error("SQLite connection: unavailable")
    state["audit_logging_failed"] = True


# ==================================================
# 4. SIDEBAR SIMULATION CONTROLS
# ==================================================

with st.sidebar:
    st.header("Simulation Controls")

    selected_scenario = st.selectbox(
        "Select machine scenario",
        options=[
            "normal",
            "jam",
            "overheating",
            "high_vibration",
        ],
        format_func=lambda value: {
            "normal": "Normal operation",
            "jam": "Conveyor jam",
            "overheating": "Motor overheating",
            "high_vibration": "High vibration",
        }[value],
    )

    if st.button(
        "Inject Scenario",
        use_container_width=True,
    ):
        try:
            apply_scenario(
                state,
                selected_scenario,
            )

            state["last_error"] = None
            state["analysis_pending"] = False

            st.rerun()

        except Exception as exc:
            state["last_error"] = str(exc)

            add_event(
                state,
                "ERROR",
                str(exc),
                "ERROR",
            )

            st.error(
                f"Scenario injection failed: {exc}"
            )

    st.divider()

    if st.button(
        "Reset Simulation",
        use_container_width=True,
    ):
        st.session_state.factoryguard = (
            reset_dashboard_state()
        )

        st.rerun()


# ==================================================
# 5. MACHINE OVERVIEW
# ==================================================

# The deterministic controller remains authoritative.
# Sensor values are added for dashboard presentation.

status = get_dashboard_status(machine)

st.subheader("Machine Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Machine State",
        state_label(status["state"]),
    )

with col2:
    st.metric(
        "Active Faults",
        len(status["active_faults"]),
    )

with col3:
    st.metric(
        "Fault Latched",
        "YES" if status["fault_latched"] else "NO",
    )

with col4:
    st.metric(
        "Sensor Data",
        "FRESH" if status["readings_fresh"]
        else "STALE / UNKNOWN",
    )


# ==================================================
# 6. MACHINE SAFETY MESSAGES
# ==================================================

if status["state"] == "RUNNING":
    st.success("Machine is running")

elif status["state"] == "READY_FOR_REVIEW":
    st.info(
        "Fault cleared. Awaiting controlled restart."
    )

else:
    st.error(
        "Machine stopped. Restart requires "
        "deterministic safety approval."
    )

if status["active_faults"]:
    st.write(
        "**Active faults:**",
        ", ".join(status["active_faults"]),
    )


# ==================================================
# 7. SENSOR MONITORING
# ==================================================

st.subheader("Sensor Monitoring")

sensor_columns = st.columns(4)

for column, (field, label) in zip(
    sensor_columns,
    SENSOR_FIELDS.items(),
):
    value = status.get(field)

    with column:
        st.metric(
            label,
            f"{value:.1f}"
            if isinstance(value, (int, float))
            else "N/A",
        )


# ==================================================
# 8. SENSOR HISTORY CHARTS
# ==================================================

st.subheader("Sensor History")

history_df = pd.DataFrame(
    state["sensor_history"]
)

available_fields = [
    field
    for field in SENSOR_FIELDS
    if field in history_df.columns
    and history_df[field].notna().any()
]

if available_fields:
    selected_metric = st.selectbox(
        "Sensor history",
        available_fields,
        format_func=lambda field:
            SENSOR_FIELDS[field],
    )

    chart_df = history_df.copy()

    chart_df["sample"] = range(
        1,
        len(chart_df) + 1,
    )

    fig = px.line(
        chart_df,
        x="sample",
        y=selected_metric,
        markers=True,
        title=SENSOR_FIELDS[selected_metric],
    )

    fig.update_layout(
        xaxis_title="Simulation sample",
        yaxis_title=SENSOR_FIELDS[selected_metric],
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

else:
    st.info(
        "No normalized sensor measurements available."
    )


# ==================================================
# 9. SCENARIO CAMERA IMAGE MAPPING
# ==================================================

SCENARIO_IMAGES = {
    "normal": "data/scenarios/normal.png",
    "jam": "data/scenarios/obstruction.png",
    "overheating": "data/scenarios/normal.png",
    "high_vibration": "data/scenarios/normal.png",
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent

relative_image_path = SCENARIO_IMAGES.get(
    state["scenario"],
    "data/scenarios/normal.png",
)

image_path = str(
    PROJECT_ROOT / relative_image_path
)


# ==================================================
# 10. AI DIAGNOSTIC ANALYSIS
# ==================================================

st.divider()

st.subheader("AI Diagnostic Analysis")

st.caption(
    "Local vision inspection, maintenance knowledge "
    "retrieval, and LangGraph diagnostic reasoning."
)


# ==================================================
# 11. SIMULATED CAMERA IMAGE
# ==================================================

with st.expander(
    "View simulated camera image",
    expanded=True,
):
    if Path(image_path).is_file():
        st.image(
            image_path,
            caption=(
                f"Simulated camera input: "
                f"{state['scenario']}"
            ),
            width="stretch",
        )

    else:
        st.error(
            f"Scenario image not found: {image_path}"
        )


# ==================================================
# 12. RUN AI DIAGNOSIS
# DAY 9 - STEP 8: SQLITE DIAGNOSTIC PERSISTENCE
# ==================================================

if st.button(
    "Run AI Diagnosis",
    type="primary",
    use_container_width=True,
):

    # Invalidate previous diagnostic evidence
    # and recovery workflow before new analysis.

    state["diagnostic_report"] = None
    state["graph_result"] = None
    state["recovery_runner"] = None
    state["bound_diagnostic"] = None
    state["approval_manager"].invalidate()
    state["last_error"] = None
    state["analysis_pending"] = True

    try:
        if not Path(image_path).is_file():
            raise FileNotFoundError(
                f"Camera image not found: {image_path}"
            )

        # Advisory snapshot only.
        # The AI cannot modify machine safety state.

        machine_snapshot = machine.get_status()

        with st.spinner(
            "Running local vision, RAG, "
            "and diagnostic reasoning..."
        ):
            workflow = build_workflow()

            result = workflow.invoke({
                "machine_status": machine_snapshot,
                "image_path": image_path,
                "errors": [],
                "execution_trace": [],
                "workflow_status": "PENDING",
            })

        state["graph_result"] = result

        if (
            result.get("workflow_status")
            == "ADVISORY_READY"
        ):
            report_data = result.get(
                "diagnostic_report"
            )

            if not report_data:
                raise ValueError(
                    "Workflow completed without "
                    "a diagnostic report"
                )

            if isinstance(
                report_data,
                DiagnosticReport,
            ):
                report = report_data

            else:
                report = DiagnosticReport(
                    **report_data
                )

            state["diagnostic_report"] = report

            # ==========================================
            # DAY 9 - STEP 8
            # PERSIST DIAGNOSTIC REPORT TO SQLITE
            # ==========================================

            try:
                diagnostic_id = DiagnosticStore().save(
                    report
                )

                add_event(
                    state,
                    "DIAGNOSTIC_SAVED",
                    f"Diagnostic report stored with ID {diagnostic_id}",
                )

            except Exception as exc:
                state["audit_logging_failed"] = True
                state["last_error"] = (
                    f"Diagnostic persistence failed: {exc}"
                )

                st.error(
                    "Diagnostic report generated but "
                    "could not be saved to SQLite."
                )

            # DAY 10 - STEP 7.3: BIND DIAGNOSIS TO FAULT EPISODE
            episode = state["episode_tracker"].observe(
                machine.get_status()
            )
            if episode is not None:
                state["bound_diagnostic"] = bind_report(
                    report,
                    episode,
                )
            else:
                state["bound_diagnostic"] = None

            # A recovery runner is created only
            # for a fault-stopped machine.
            #
            # Runner initialization does not
            # authorize or perform a restart.

            if machine.state.value in (
                "STOPPED_FAULT",
                "STOPPED_EMERGENCY",
            ):
                state["recovery_runner"] = (
                    RecoveryRunner(
                        machine=machine,
                        diagnostic_report=report,
                    )
                )

            add_event(
                state,
                "AI_DIAGNOSIS",
                (
                    "Diagnosis: "
                    f"{report.primary_diagnosis}"
                ),
            )

            st.success(
                "Diagnostic workflow completed"
            )

            st.info(
                "AI diagnosis is advisory only. "
                "Machine recovery requires "
                "operator actions and deterministic "
                "safety checks."
            )

        else:
            workflow_status = result.get(
                "workflow_status",
                "UNKNOWN",
            )

            add_event(
                state,
                "AI_DIAGNOSIS",
                (
                    "Diagnostic workflow did not "
                    f"complete: {workflow_status}"
                ),
                "WARNING",
            )

            st.error(
                "Diagnostic workflow did not complete. "
                f"Status: {workflow_status}"
            )

    except Exception as exc:
        full_traceback = traceback.format_exc()

        state["last_error"] = full_traceback

        state["diagnostic_report"] = None
        state["bound_diagnostic"] = None
        state["recovery_runner"] = None

        add_event(
            state,
            "AI_ERROR",
            str(exc),
            "ERROR",
        )

        st.error(
            f"Diagnostic workflow failed: {exc}"
        )

        st.subheader(
            "Diagnostic Error Details"
        )

        st.code(
            full_traceback,
            language="text",
        )

    finally:
        state["analysis_pending"] = False


# ==================================================
# 13. DIAGNOSTIC REPORT AND EVIDENCE
# DAY 8 - STEP 9
# ==================================================

report = state.get("diagnostic_report")
graph_result = state.get("graph_result")

if report is not None:

    st.divider()

    st.subheader("Diagnostic Report")

    # DAY 10 - STEP 7.4: SHOW CURRENT FAULT EPISODE
    episode = state["episode_tracker"].current
    if episode is not None:
        st.caption(
            f"Active fault episode: {episode.episode_id}"
        )

    report_data = report.to_dict()

    summary = diagnosis_summary(
        report_data
    )

    # Diagnosis summary

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Diagnosis",
            str(summary["diagnosis"]),
        )

    with c2:
        st.metric(
            "Severity",
            str(summary["severity"]),
        )

    with c3:
        st.metric(
            "Evidence Quality",
            str(summary["confidence"]),
        )

    # Display full evidence-quality label
    # because metric values may be truncated.

    st.caption(
        "Full evidence-quality assessment: "
        f"{summary['confidence']}"
    )

    # Supporting evidence

    st.markdown("**Supporting evidence**")

    if report.evidence:
        for item in report.evidence:
            st.write("•", item)
    else:
        st.info(
            "No supporting evidence was reported."
        )

    # Recommended maintenance checks

    st.markdown("**Recommended checks**")

    if report.recommended_checks:
        for item in report.recommended_checks:
            st.write("•", item)
    else:
        st.info(
            "No maintenance checks were recommended."
        )

    # Limitations and uncertainty

    if report.limitations:
        st.markdown(
            "**Limitations and uncertainty**"
        )

        for item in report.limitations:
            st.write("•", item)

    st.info(
        "AI diagnostic reports are advisory. "
        "They cannot authorize restart."
    )

    # JSON report download

    st.download_button(
        label="Download Diagnostic Report",
        data=json.dumps(
            report_data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        file_name="factoryguard_diagnosis.json",
        mime="application/json",
        use_container_width=True,
    )


# ==================================================
# 14. LANGGRAPH EVIDENCE AND EXECUTION DETAILS
# ==================================================

if graph_result is not None:

    st.divider()

    st.subheader(
        "Diagnostic Evidence and Workflow Details"
    )

    # Vision observations

    with st.expander(
        "Vision AI observations"
    ):
        vision_report = (
            graph_result.get("vision_report")
            or {}
        )

        if vision_report:
            st.json(vision_report)
        else:
            st.info(
                "No vision observations available."
            )

    # Retrieved maintenance procedures

    with st.expander(
        "Retrieved maintenance procedures"
    ):
        documents = graph_result.get(
            "retrieved_documents",
            [],
        ) or []

        if documents:

            st.caption(
                "Original maintenance references "
                "retrieved by the diagnostic workflow."
            )

            for document in documents:

                if isinstance(document, dict):

                    document_id = document.get(
                        "id",
                        "UNKNOWN",
                    )

                    document_title = document.get(
                        "title",
                        "Untitled procedure",
                    )

                    document_text = document.get(
                        "text",
                        "",
                    )

                    st.markdown(
                        f"**{document_id} — "
                        f"{document_title}**"
                    )

                    if document_text:
                        st.text(
                            str(document_text)
                        )
                    else:
                        st.info(
                            "No procedure text available."
                        )

                else:
                    st.write(document)

                st.divider()

        else:
            st.info(
                "No maintenance procedures retrieved."
            )

    # LangGraph execution trace

    with st.expander(
        "LangGraph execution trace"
    ):
        execution_trace = graph_result.get(
            "execution_trace",
            [],
        ) or []

        if execution_trace:
            st.write(execution_trace)
        else:
            st.info(
                "No execution trace available."
            )

        workflow_errors = graph_result.get(
            "errors",
            [],
        ) or []

        if workflow_errors:

            st.warning(
                "Some AI components operated "
                "in degraded mode."
            )

            st.json(workflow_errors)

    workflow_status = graph_result.get(
        "workflow_status",
        "UNKNOWN",
    )

    st.caption(
        f"LangGraph workflow status: {workflow_status}"
    )

    st.caption(
        "Diagnostic conclusions are advisory only. "
        "Deterministic machine safety checks and "
        "explicit operator approval remain required "
        "for controlled recovery."
    )


# ==================================================
# 15. CONTROLLED RECOVERY
# DAY 8 - STEP 10
# DAY 9 - STEP 9: RECOVERY AUDIT LOGGING
# ==================================================

st.divider()

st.subheader("Controlled Recovery")

st.caption(
    "Behaviour-tree recovery with explicit operator "
    "actions and deterministic safety checks."
)

st.warning(
    "SIMULATED RECOVERY ONLY. Fault resolution "
    "represents an authorized maintenance action; "
    "it does not verify physical maintenance, "
    "isolation, or operator identity."
)

runner = state.get("recovery_runner")

if runner is None:

    st.info(
        "Run AI Diagnosis on a stopped-fault "
        "scenario to initialize recovery."
    )

else:

    # ----------------------------------------------
    # 16. RECOVERY STATUS
    # ----------------------------------------------

    st.write(
        "**Current machine state:**",
        machine.state.value,
    )

    st.write(
        "**Operator acknowledged:**",
        runner.context.operator_acknowledged,
    )

    st.write(
        "**Restart approved:**",
        runner.context.operator_restart_approved,
    )

    st.write(
        "**Recovery completed:**",
        runner.context.recovery_completed,
    )

    st.info(
        "Recovery follows three separate steps. "
        "No dashboard action directly sets "
        "the machine state to RUNNING."
    )

    # ----------------------------------------------
    # 17. STEP 1 - ACKNOWLEDGE FAULT
    # DAY 9 - STEP 9.1
    # ----------------------------------------------

    st.markdown(
        "#### Step 1 — Operator Acknowledgement"
    )

    st.caption(
        "The operator explicitly acknowledges "
        "the simulated fault."
    )

    if st.button(
        "1. Acknowledge Fault",
        use_container_width=True,
        disabled=(
            runner.context.operator_acknowledged
            or runner.context.recovery_completed
        ),
    ):

        try:
            runner.acknowledge()

            result = runner.tick()

            log_recovery_action(
                state,
                action="ACKNOWLEDGE_FAULT",
                result=result["status"],
                details=result,
            )

            add_event(
                state,
                "RECOVERY",
                (
                    "Acknowledgement: "
                    f"{result['status']} "
                    f"— {result['message']}"
                ),
            )

            st.rerun()

        except Exception as exc:

            add_event(
                state,
                "RECOVERY_ERROR",
                str(exc),
                "ERROR",
            )

            st.error(
                f"Fault acknowledgement failed: {exc}"
            )

    # ----------------------------------------------
    # 18. STEP 2 - SIMULATED FAULT RESOLUTION
    # DAY 9 - STEP 9.2
    # ----------------------------------------------

    st.markdown(
        "#### Step 2 — Authorized Fault Resolution"
    )

    st.caption(
        "Simulates authorized maintenance having "
        "resolved the fault, then supplies fresh "
        "normal sensor readings."
    )

    if st.button(
        "2. Simulate Authorized Fault Resolution",
        use_container_width=True,
        disabled=(
            not runner.context.operator_acknowledged
            or runner.context.recovery_completed
            or machine.state.value
            not in (
                "STOPPED_FAULT",
                "STOPPED_EMERGENCY",
            )
        ),
    ):

        try:

            # Advance simulated machine time.
            # This helps ensure a new sensor sample
            # is evaluated by the controller.

            machine.advance_time(1)

            # Supply simulated post-maintenance
            # sensor readings.
            #
            # This does not directly modify the
            # machine state or clear safety faults.

            machine.update_sensors(
                get_reading("normal")
            )

            state["scenario"] = "normal"

            # Use actual sensor values rather
            # than safety status alone.

            updated_status = get_dashboard_status(
                machine
            )

            state["sensor_history"].append(
                make_sensor_record(updated_status)
            )

            # Let the recovery behaviour tree
            # evaluate the updated machine.

            result = runner.tick()

            log_recovery_action(
                state,
                action="FAULT_RESOLUTION",
                result=result["status"],
                details=result,
            )

            add_event(
                state,
                "RECOVERY",
                (
                    "Authorized resolution simulated: "
                    f"{result['status']} "
                    f"— {result['message']}"
                ),
            )

            st.rerun()

        except Exception as exc:

            add_event(
                state,
                "RECOVERY_ERROR",
                str(exc),
                "ERROR",
            )

            st.error(
                f"Fault resolution failed: {exc}"
            )

    # ----------------------------------------------
    # 19. STEP 3 - RESTART READINESS CHECK
    # ----------------------------------------------

    # These UI checks improve usability.
    #
    # They are not the safety authority.
    # RecoveryRunner and the deterministic
    # controller must independently enforce
    # the restart conditions.

    current_status = machine.get_status()

    ready = (
        machine.state.value == "READY_FOR_REVIEW"
        and not machine.fault_latched
        and not machine.active_faults
        and not machine.emergency_stop_active
        and machine.guard_door_closed
        and current_status.get(
            "readings_fresh",
            False,
        )
        and runner.context.operator_acknowledged
    )

    st.markdown(
        "#### Step 3 — Explicit Restart Approval"
    )

    if ready and not state.get(
        "audit_logging_failed", False
    ):
        st.success(
            "Controller readiness conditions are "
            "satisfied. Operator restart approval "
            "may now be requested."
        )

    elif state.get("audit_logging_failed", False):
        st.error(
            "Restart unavailable: persistent "
            "audit logging is degraded."
        )

    else:
        st.warning(
            "Restart approval is unavailable until "
            "the deterministic controller reports "
            "safe conditions."
        )

    # ----------------------------------------------
    # 20. APPROVE SIMULATED RESTART
    # DAY 9 - STEP 9.3 AND STEP 11
    # ----------------------------------------------

    
    # ----------------------------------------------
    # 20. APPROVE SIMULATED RESTART
    # DAY 10 - STEP 8.2
    # EPISODE-BOUND, AUDIT-AWARE RESTART
    # ----------------------------------------------

    if st.button(
        "3. Approve Simulated Restart",
        use_container_width=True,
        disabled=(
            not ready
            or runner.context.recovery_completed
            or state.get("audit_logging_failed", False)
        ),
    ):

        try:
            if state.get("audit_logging_failed", False):
                st.error(
                    "Restart blocked: audit logging is degraded."
                )

            else:
                # Step 1: Persist restart request.

                request_id = log_recovery_action(
                    state,
                    action="RESTART_REQUEST",
                    result="REQUESTED",
                )

                if request_id is None:
                    st.error(
                        "Restart blocked: request was not "
                        "durably recorded."
                    )

                else:
                    # Step 2: Obtain operator approval
                    # through the existing recovery runner.

                    approved = runner.approve_restart()

                    if not approved:
                        log_recovery_action(
                            state,
                            action="RESTART_APPROVAL",
                            result="REJECTED",
                        )

                        add_event(
                            state,
                            "RESTART",
                            "Restart approval rejected",
                            "WARNING",
                        )

                        st.error(
                            "Safety conditions rejected approval."
                        )

                    else:
                        # Step 3: Persist explicit approval
                        # before creating any approval token.

                        approval_id = log_recovery_action(
                            state,
                            action="RESTART_APPROVAL",
                            result="APPROVED",
                        )

                        if approval_id is None:
                            runner.context.operator_restart_approved = False
                            state["approval_manager"].invalidate()

                            st.error(
                                "Restart blocked: approval audit failed."
                            )

                        else:
                            # Step 4: Recheck current safety,
                            # episode binding, operator state,
                            # and audit health.

                            episode = state["episode_tracker"].current

                            decision = check_restart_preconditions(
                                machine_status=machine.get_status(),
                                episode=episode,
                                bound_diagnostic=state.get(
                                    "bound_diagnostic"
                                ),
                                runner=runner,
                                audit_healthy=not state.get(
                                    "audit_logging_failed",
                                    False,
                                ),
                            )

                            if not decision.allowed:
                                state["approval_manager"].invalidate()
                                runner.context.operator_restart_approved = False

                                log_recovery_action(
                                    state,
                                    action="RESTART_BLOCKED",
                                    result="REJECTED",
                                    details={
                                        "reasons": list(decision.reasons)
                                    },
                                )

                                st.error(
                                    "Restart rejected: "
                                    + "; ".join(decision.reasons)
                                )

                            else:
                                # Step 5: Create the episode-bound
                                # one-time approval token only after
                                # durable approval logging.

                                if episode is None:
                                    raise RuntimeError(
                                        "No active fault episode"
                                    )

                                state["approval_manager"].approve(
                                    episode.episode_id
                                )

                                # Step 6: Consume the token
                                # before executing recovery.

                                if not state["approval_manager"].consume(
                                    episode.episode_id
                                ):
                                    runner.context.operator_restart_approved = False

                                    raise RuntimeError(
                                        "Approval token invalid"
                                    )

                                # Step 7: Execute the existing
                                # Day 6 recovery runner.
                                # The deterministic safety controller
                                # remains authoritative.

                                result = runner.tick()

                                # Step 8: Persist the recovery outcome.

                                outcome_id = log_recovery_action(
                                    state,
                                    action="RESTART_OUTCOME",
                                    result=result["status"],
                                    details={
                                        "recovery_result": result,
                                        "episode_id": episode.episode_id,
                                        "machine_state": machine.state.value,
                                    },
                                )

                                if outcome_id is None:
                                    st.error(
                                        "Recovery outcome could not be "
                                        "persisted. Audit system degraded."
                                    )

                                add_event(
                                    state,
                                    "RESTART",
                                    (
                                        f"{result['status']} "
                                        f"— {result['message']}"
                                    ),
                                )

                                if result["status"] == "SUCCESS":
                                    state["episode_tracker"].observe(
                                        machine.get_status()
                                    )

                                    st.success(
                                        "Simulated restart completed"
                                    )
                                else:
                                    st.warning(
                                        result["message"]
                                    )

            st.rerun()

        except Exception as exc:
            state["approval_manager"].invalidate()
            runner.context.operator_restart_approved = False

            log_recovery_action(
                state,
                action="RESTART_ERROR",
                result="ERROR",
                details={"error": str(exc)},
            )

            add_event(
                state,
                "RESTART_ERROR",
                str(exc),
                "ERROR",
            )

            st.error(
                f"Simulated restart failed: {exc}"
            )


    # ----------------------------------------------
    # 21. FINAL RECOVERY STATUS
    # ----------------------------------------------

    if runner.context.recovery_completed:

        st.success(
            "Controlled recovery completed "
            "through the behaviour tree."
        )

    elif machine.state.value == "READY_FOR_REVIEW":

        st.info(
            "Machine is ready for review. "
            "Explicit restart approval is required."
        )

    elif machine.state.value in (
        "STOPPED_FAULT",
        "STOPPED_EMERGENCY",
    ):

        st.warning(
            "Machine remains stopped. "
            "Recovery requirements are not "
            "yet fully satisfied."
        )


# ==================================================
# 22. EVENT HISTORY AND AUDIT LOGS
# DAY 8 - STEP 11
# ==================================================

st.divider()

st.subheader("Event History")

st.caption(
    "In-memory simulation events and recovery "
    "decisions. Newest events appear first."
)

if state["events"]:

    event_df = pd.DataFrame(
        state["events"]
    )

    # Display newest events first.
    # Preserve original order in the CSV export.

    st.dataframe(
        event_df.iloc[::-1],
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Event History CSV",
        data=event_df.to_csv(index=False),
        file_name="factoryguard_events.csv",
        mime="text/csv",
        use_container_width=True,
    )

else:

    st.info(
        "No simulation events recorded yet."
    )


# ==================================================
# 23. BEHAVIOUR-TREE EXECUTION HISTORY
# ==================================================

if runner is not None:

    with st.expander(
        "Behaviour-tree execution history"
    ):

        recovery_history = runner.get_history()

        if recovery_history:

            st.dataframe(
                pd.DataFrame(recovery_history),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No recovery actions recorded yet."
            )


# ==================================================
# 24. RAW MACHINE STATUS
# ==================================================

with st.expander("Raw machine status"):

    st.json(
        machine.get_status()
    )


# ==================================================
# DAY 9 - STEP 10: PERSISTENT AUDIT HISTORY
# ==================================================

st.divider()
st.subheader("Persistent Audit History")

try:
    tab1, tab2, tab3 = st.tabs([
        "Events",
        "Diagnostics",
        "Recovery Actions",
    ])

    with tab1:
        events = EventLogger().recent(100)

        if events:
            event_df = pd.DataFrame(events)

            st.dataframe(
                event_df,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "Download SQLite Events",
                event_df.to_csv(index=False),
                file_name="factoryguard_db_events.csv",
                mime="text/csv",
            )

        else:
            st.info("No persisted events yet.")

    with tab2:
        diagnostics = DiagnosticStore().recent(50)

        if diagnostics:
            for record in diagnostics:
                with st.expander(
                    f"#{record['id']} — "
                    f"{record['primary_diagnosis']} "
                    f"({record['severity']})"
                ):
                    st.json(record["report"])

        else:
            st.info("No saved diagnoses yet.")

    with tab3:
        recovery_actions = RecoveryLogger().recent(100)

        if recovery_actions:
            st.dataframe(
                pd.DataFrame(recovery_actions),
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info("No recovery actions yet.")

except Exception as exc:
    state["audit_logging_failed"] = True
    state["last_error"] = str(exc)

    st.error(
        f"Persistent audit history unavailable: {exc}"
    )


# ==================================================
# END OF DAY 9 - STEPS 8, 9, 10 AND 11 DASHBOARD
# ==================================================