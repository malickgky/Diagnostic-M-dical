from langchain_core.messages import HumanMessage, AIMessage
from app.state import MedicalState


def supervisor_node(state: MedicalState) -> MedicalState:
    """
    Supervisor : orchestre le workflow en décidant de la prochaine étape.
    """
    question_count = state.get("question_count", 0)
    diagnostic_summary = state.get("diagnostic_summary")
    physician_treatment = state.get("physician_treatment")
    final_report = state.get("final_report")
    status = state.get("status", "running")

    # Determine next step
    if final_report:
        next_step = "FINISH"
    elif physician_treatment and diagnostic_summary:
        next_step = "report_agent"
    elif diagnostic_summary and not physician_treatment:
        next_step = "physician_review"
    elif question_count < 5 or not diagnostic_summary:
        next_step = "diagnostic_agent"
    else:
        next_step = "physician_review"

    return {
        **state,
        "next": next_step,
    }
