import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from app.graph import medical_graph
from app.schemas.consultation import (
    StartConsultationRequest,
    ResumeConsultationRequest,
    ConsultationResponse,
    SessionResponse
)
from app.tools.patient_tools import CLINICAL_QUESTIONS

app = FastAPI(
    title="ClinicalOrient API",
    description="API d'orientation clinique préliminaire multi-agents (projet académique)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_state_response(state: dict, thread_id: str) -> ConsultationResponse:
    """Convertit l'état du graphe en réponse API."""
    question_count = state.get("question_count", 0)
    status = state.get("status", "running")
    
    current_question = None
    question_number = None
    if status == "awaiting_patient" and question_count < 5:
        current_question = CLINICAL_QUESTIONS[question_count]
        question_number = question_count + 1

    messages = []
    for msg in state.get("messages", [])[-5:]:
        if hasattr(msg, "content"):
            messages.append(msg.content)

    return ConsultationResponse(
        thread_id=thread_id,
        status=status,
        current_question=current_question,
        question_number=question_number,
        diagnostic_summary=state.get("diagnostic_summary"),
        interim_care=state.get("interim_care"),
        physician_treatment=state.get("physician_treatment"),
        final_report=state.get("final_report"),
        messages=messages
    )


@app.post("/sessions/start", response_model=SessionResponse)
async def start_session():
    """Crée une nouvelle session de consultation."""
    session_id = str(uuid.uuid4())
    return SessionResponse(
        session_id=session_id,
        message="Session créée. Utilisez POST /consultation/start pour démarrer."
    )


@app.post("/consultation/start", response_model=ConsultationResponse)
async def start_consultation(request: StartConsultationRequest):
    """
    Démarre une nouvelle consultation avec les données initiales du patient.
    Lance le workflow LangGraph et pose la première question.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "patient_name": request.patient_name,
        "initial_complaint": request.initial_complaint,
        "question_count": 0,
        "patient_answers": [],
        "status": "running",
        "messages": [HumanMessage(content=f"Motif de consultation: {request.initial_complaint}")]
    }

    try:
        # Lance le graphe jusqu'à la première interruption
        medical_graph.invoke(initial_state, config)
        
        # Récupère l'état actuel
        current_state = medical_graph.get_state(config)
        state_values = current_state.values
        
        # Premier run : on est dans awaiting_patient pour la Q1
        if state_values.get("status") != "awaiting_patient":
            state_values["status"] = "awaiting_patient"
        
        return get_state_response(state_values, thread_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consultation/resume", response_model=ConsultationResponse)
async def resume_consultation(request: ResumeConsultationRequest):
    """
    Reprend une consultation en cours.
    - action="answer_patient" : le patient répond à la question courante
    - action="physician_review" : le médecin soumet son avis
    """
    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        current_state = medical_graph.get_state(config)
        if not current_state:
            raise HTTPException(status_code=404, detail="Consultation non trouvée")
        
        state_values = dict(current_state.values)

        if request.action == "answer_patient" and request.patient_answer:
            question_count = state_values.get("question_count", 0)
            patient_answers = list(state_values.get("patient_answers", []))
            
            patient_answers.append(request.patient_answer)
            question_count += 1
            
            update = {
                "question_count": question_count,
                "patient_answers": patient_answers,
                "status": "running",
                "messages": [HumanMessage(content=request.patient_answer)]
            }
            
            medical_graph.update_state(config, update)
            medical_graph.invoke(None, config)
            
        elif request.action == "physician_review" and request.physician_treatment:
            update = {
                "physician_treatment": request.physician_treatment,
                "status": "running",
                "messages": [HumanMessage(content=f"Avis médecin: {request.physician_treatment}")]
            }
            medical_graph.update_state(config, update)
            medical_graph.invoke(None, config)

        current_state = medical_graph.get_state(config)
        return get_state_response(current_state.values, request.thread_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consultation/{thread_id}", response_model=ConsultationResponse)
async def get_consultation(thread_id: str):
    """Récupère l'état courant d'une consultation."""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        current_state = medical_graph.get_state(config)
        if not current_state or not current_state.values:
            raise HTTPException(status_code=404, detail="Consultation non trouvée")
        return get_state_response(current_state.values, thread_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consultation/{thread_id}/report")
async def get_report(thread_id: str):
    """Récupère le rapport final d'une consultation terminée."""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        current_state = medical_graph.get_state(config)
        if not current_state or not current_state.values:
            raise HTTPException(status_code=404, detail="Consultation non trouvée")
        
        report = current_state.values.get("final_report")
        if not report:
            raise HTTPException(status_code=404, detail="Rapport non encore généré")
        
        return {
            "thread_id": thread_id,
            "final_report": report,
            "patient_name": current_state.values.get("patient_name"),
            "status": "completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ClinicalOrient API"}
