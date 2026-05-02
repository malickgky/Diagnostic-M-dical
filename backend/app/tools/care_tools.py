from langchain_core.tools import tool
from typing import List


@tool
def recommend_interim_care(symptoms: List[str], severity: str = "moderate") -> str:
    """
    Génère une recommandation intermédiaire de soins basée sur les symptômes.
    Cette recommandation est prudente et ne remplace pas l'avis médical.
    
    Args:
        symptoms: Liste des symptômes rapportés par le patient
        severity: Sévérité estimée ('mild', 'moderate', 'severe')
    
    Returns:
        Recommandation intermédiaire de soins
    """
    base_recommendations = [
        "Repos suffisant et évitement des activités physiques intenses.",
        "Hydratation adéquate (au minimum 1,5 à 2 litres d'eau par jour).",
        "Surveillance de l'évolution des symptômes.",
    ]
    
    red_flag_keywords = [
        "douleur thoracique", "chest pain", "essoufflement sévère", 
        "perte de conscience", "saignement", "difficulté respiratoire"
    ]
    
    symptoms_lower = [s.lower() for s in symptoms]
    has_red_flags = any(
        any(flag in symptom for symptom in symptoms_lower)
        for flag in red_flag_keywords
    )
    
    if has_red_flags or severity == "severe":
        urgent_recommendations = [
            "⚠️ SIGNES D'ALERTE DÉTECTÉS : Consultation médicale urgente recommandée.",
            "En cas d'aggravation rapide, appeler le 15 (SAMU) ou le 112 immédiatement.",
        ]
        recommendations = urgent_recommendations + base_recommendations
    elif severity == "mild":
        mild_recommendations = [
            "Les symptômes semblent bénins. Surveillance à domicile possible.",
            "Consultation médicale recommandée si les symptômes persistent au-delà de 48-72 heures.",
        ]
        recommendations = mild_recommendations + base_recommendations
    else:
        moderate_recommendations = [
            "Consultation médicale recommandée dans les 24-48 heures.",
        ]
        recommendations = moderate_recommendations + base_recommendations
    
    return (
        "RECOMMANDATION INTERMÉDIAIRE DE SOINS (à titre indicatif uniquement) :\n"
        + "\n".join(f"- {r}" for r in recommendations)
        + "\n\n⚠️ Cette recommandation ne remplace pas une consultation médicale professionnelle."
    )


@tool
def assess_red_flags(symptoms: List[str]) -> dict:
    """
    Évalue la présence de signes d'alerte (red flags) dans les symptômes rapportés.
    
    Args:
        symptoms: Liste des symptômes
    
    Returns:
        Dictionnaire avec présence de red flags et détails
    """
    red_flags = {
        "cardiovascular": ["douleur thoracique", "palpitation", "syncope", "œdème"],
        "respiratory": ["dyspnée", "essoufflement", "hémoptysie", "cyanose"],
        "neurological": ["céphalée sévère", "confusion", "perte de conscience", "paralysie"],
        "hemorrhagic": ["saignement", "hématurie", "méléna", "hématémèse"],
    }
    
    detected = {}
    symptoms_text = " ".join(symptoms).lower()
    
    for category, flags in red_flags.items():
        detected_flags = [f for f in flags if f in symptoms_text]
        if detected_flags:
            detected[category] = detected_flags
    
    return {
        "has_red_flags": len(detected) > 0,
        "red_flags_by_category": detected,
        "severity_level": "severe" if detected else "moderate",
        "requires_urgent_care": len(detected) > 0
    }
