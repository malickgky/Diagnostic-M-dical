from langchain_core.tools import tool
from typing import Optional


CLINICAL_QUESTIONS = [
    "Depuis combien de temps ressentez-vous ces symptômes ?",
    "Pouvez-vous décrire la localisation et l'intensité de la douleur ou de la gêne (sur une échelle de 1 à 10) ?",
    "Avez-vous de la fièvre, des frissons ou d'autres symptômes associés (toux, essoufflement, nausées) ?",
    "Avez-vous des antécédents médicaux, des allergies ou prenez-vous des médicaments régulièrement ?",
    "Avez-vous remarqué des signes d'alerte comme une douleur thoracique, des difficultés respiratoires sévères, des troubles de la conscience ou des saignements importants ?"
]


@tool
def ask_patient(question_index: int) -> str:
    """
    Retourne la question clinique correspondant à l'index donné (0-4).
    Ces questions sont posées successivement au patient pour recueillir des informations cliniques.
    """
    if 0 <= question_index < len(CLINICAL_QUESTIONS):
        return CLINICAL_QUESTIONS[question_index]
    return "Toutes les questions ont été posées."


@tool
def get_next_question(current_count: int) -> dict:
    """
    Retourne la prochaine question à poser et indique si d'autres questions restent.
    Utilisé pour gérer la boucle d'interrogatoire patient.
    """
    if current_count < len(CLINICAL_QUESTIONS):
        return {
            "question": CLINICAL_QUESTIONS[current_count],
            "question_number": current_count + 1,
            "total_questions": len(CLINICAL_QUESTIONS),
            "has_more": current_count + 1 < len(CLINICAL_QUESTIONS)
        }
    return {
        "question": None,
        "question_number": current_count,
        "total_questions": len(CLINICAL_QUESTIONS),
        "has_more": False
    }
