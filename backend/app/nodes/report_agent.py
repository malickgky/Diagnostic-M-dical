import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.state import MedicalState

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY", "")
)

REPORT_SYSTEM_PROMPT = """Tu es un assistant de rédaction de rapports cliniques académiques.
Tu produis des rapports structurés, professionnels, clairs et objectifs.
Tu rappelles systématiquement que le système ne remplace pas une consultation médicale.
"""


def report_agent_node(state: MedicalState) -> MedicalState:
    """
    Report Agent : génère le rapport final structuré à partir de toutes
    les données collectées (synthèse diagnostique + avis médecin).
    """
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M")
    patient_name = state.get("patient_name", "Patient anonyme")
    initial_complaint = state.get("initial_complaint", "Non renseigné")
    diagnostic_summary = state.get("diagnostic_summary", "Non disponible")
    interim_care = state.get("interim_care", "Non générée")
    physician_treatment = state.get("physician_treatment", "Non renseigné")
    patient_answers = state.get("patient_answers", [])

    try:
        report_prompt = f"""
Génère un rapport clinique final structuré avec les informations suivantes :

PATIENT : {patient_name}
DATE : {timestamp}
MOTIF DE CONSULTATION : {initial_complaint}

SYNTHÈSE CLINIQUE PRÉLIMINAIRE :
{diagnostic_summary}

RECOMMANDATION INTERMÉDIAIRE :
{interim_care}

CONDUITE À TENIR DU MÉDECIN TRAITANT :
{physician_treatment}

Le rapport doit être structuré avec les sections suivantes :
1. En-tête (patient, date, motif)
2. Anamnèse (résumé des réponses patient)
3. Synthèse clinique préliminaire
4. Recommandation intermédiaire de soins
5. Prescription / Conduite à tenir du médecin
6. Conclusion
7. Avertissement légal obligatoire

L'avertissement légal DOIT inclure : "Ce système ne remplace pas une consultation médicale."
"""
        response = llm.invoke([
            SystemMessage(content=REPORT_SYSTEM_PROMPT),
            HumanMessage(content=report_prompt)
        ])
        final_report = response.content
    except Exception:
        final_report = f"""
================================================================================
                    RAPPORT CLINIQUE FINAL - ORIENTATION PRÉLIMINAIRE
================================================================================
Patient      : {patient_name}
Date         : {timestamp}
Référence    : CONS-{datetime.now().strftime('%Y%m%d%H%M%S')}
--------------------------------------------------------------------------------

1. MOTIF DE CONSULTATION
{initial_complaint}

2. ANAMNÈSE - DONNÉES RECUEILLIES
{chr(10).join(f'  - Réponse {i+1}: {a}' for i, a in enumerate(patient_answers))}

3. SYNTHÈSE CLINIQUE PRÉLIMINAIRE
{diagnostic_summary}

4. RECOMMANDATION INTERMÉDIAIRE DE SOINS
{interim_care}

5. CONDUITE À TENIR DU MÉDECIN TRAITANT
{physician_treatment}

6. CONCLUSION
Ce rapport synthétise les informations collectées lors de la consultation préliminaire.
Il a été généré automatiquement et validé par le médecin traitant.

================================================================================
⚠️  AVERTISSEMENT LÉGAL ET ÉTHIQUE
Ce système ne remplace pas une consultation médicale.
Ce document est produit dans le cadre d'un exercice académique uniquement.
Il ne constitue pas un diagnostic médical définitif.
En cas d'urgence, composez le 15 (SAMU) ou le 112.
================================================================================
"""

    return {
        **state,
        "final_report": final_report,
        "status": "completed",
        "messages": state.get("messages", []) + [
            AIMessage(content=f" Rapport final généré.\n\n{final_report}")
        ]
    }
