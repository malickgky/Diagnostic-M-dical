from typing import Annotated, Optional
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    next: Literal[
        "diagnostic_agent",
        "physician_review",
        "report_agent",
        "FINISH"
    ]
    patient_name: Optional[str]
    initial_complaint: Optional[str]
    question_count: int
    patient_answers: list
    interim_care: Optional[str]
    diagnostic_summary: Optional[str]
    physician_treatment: Optional[str]
    final_report: Optional[str]
    thread_id: Optional[str]
    status: Optional[str]  # "running", "awaiting_patient", "awaiting_physician", "completed"
