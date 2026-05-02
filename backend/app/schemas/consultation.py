from pydantic import BaseModel
from typing import Optional, List


class StartConsultationRequest(BaseModel):
    patient_name: str
    initial_complaint: str


class ResumeConsultationRequest(BaseModel):
    thread_id: str
    patient_answer: Optional[str] = None
    physician_treatment: Optional[str] = None
    action: str  # "answer_patient" | "physician_review"


class ConsultationResponse(BaseModel):
    thread_id: str
    status: str
    current_question: Optional[str] = None
    question_number: Optional[int] = None
    diagnostic_summary: Optional[str] = None
    interim_care: Optional[str] = None
    physician_treatment: Optional[str] = None
    final_report: Optional[str] = None
    messages: Optional[List[str]] = None


class SessionResponse(BaseModel):
    session_id: str
    message: str
