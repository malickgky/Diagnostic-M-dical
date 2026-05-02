import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.state import MedicalState
from app.tools.patient_tools import CLINICAL_QUESTIONS
from app.tools.care_tools import recommend_interim_care, assess_red_flags

# Initialize LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY", "")
)

SYSTEM_PROMPT = """Tu es un assistant de collecte clinique préliminaire dans un contexte académique.
Ton rôle est de poser des questions standardisées au patient et d'analyser ses réponses pour 
produire une synthèse clinique préliminaire.

IMPORTANT : Tu ne poses PAS de diagnostic définitif. Tu produis une orientation clinique préliminaire.
Utilise les termes : "synthèse clinique préliminaire", "orientation clinique", "recommandation intermédiaire".
"""


def diagnostic_agent_node(state: MedicalState) -> MedicalState:
    """
    Agent Diagnostic : gère l'interrogatoire patient (5 questions) et produit
    une synthèse clinique préliminaire avec recommandation intermédiaire.
    """
    question_count = state.get("question_count", 0)
    patient_answers = state.get("patient_answers", [])
    initial_complaint = state.get("initial_complaint", "")

    # Si on a moins de 5 questions posées, retourner la prochaine question
    if question_count < 5:
        current_question = CLINICAL_QUESTIONS[question_count]
        return {
            **state,
            "question_count": question_count,  # pas encore incrémenté, en attente réponse
            "status": "awaiting_patient",
            "messages": state.get("messages", []) + [
                AIMessage(content=f"Question {question_count + 1}/5 : {current_question}")
            ]
        }

    # Toutes les questions ont été posées : produire la synthèse
    if question_count >= 5 and not state.get("diagnostic_summary"):
        answers_text = "\n".join([
            f"Q{i+1} ({CLINICAL_QUESTIONS[i]}): {ans}"
            for i, ans in enumerate(patient_answers[:5])
        ])

        # Évaluer les red flags
        symptoms_list = [initial_complaint] + patient_answers
        red_flags_result = {"has_red_flags": False, "severity_level": "moderate"}
        try:
            rf = assess_red_flags.invoke({"symptoms": symptoms_list})
            red_flags_result = rf
        except Exception:
            pass

        severity = red_flags_result.get("severity_level", "moderate")

        # Obtenir recommandation intermédiaire
        interim = ""
        try:
            interim = recommend_interim_care.invoke({
                "symptoms": symptoms_list,
                "severity": severity
            })
        except Exception:
            interim = "Repos, hydratation, surveillance des symptômes. Consulter un médecin si aggravation."

        # Générer la synthèse clinique via LLM
        try:
            synthesis_prompt = f"""
Motif de consultation : {initial_complaint}

Réponses du patient aux 5 questions cliniques :
{answers_text}

Red flags détectés : {red_flags_result.get('has_red_flags', False)}
Catégories à risque : {red_flags_result.get('red_flags_by_category', {})}

Produis une synthèse clinique préliminaire structurée comprenant :
1. Résumé du tableau clinique
2. Points cliniques saillants
3. Niveau d'urgence estimé (non urgent / semi-urgent / urgent)
4. Orientation préliminaire recommandée

Rappel : tu ne poses pas de diagnostic définitif.
"""
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=synthesis_prompt)
            ])
            diagnostic_summary = response.content
        except Exception as e:
            diagnostic_summary = f"""SYNTHÈSE CLINIQUE PRÉLIMINAIRE
            
Motif : {initial_complaint}
Données recueillies : {len(patient_answers)} réponses patient
Note : Synthèse générée en mode dégradé (LLM indisponible).
Présence de signes d'alerte : {red_flags_result.get('has_red_flags', False)}
"""

        return {
            **state,
            "diagnostic_summary": diagnostic_summary,
            "interim_care": interim,
            "status": "running",
            "messages": state.get("messages", []) + [
                AIMessage(content=f"Synthèse clinique produite.\n\n{diagnostic_summary}\n\n{interim}")
            ]
        }

    return state
