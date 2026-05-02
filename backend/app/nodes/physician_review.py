from app.state import MedicalState
from langchain_core.messages import AIMessage


def physician_review_node(state: MedicalState) -> MedicalState:
    """
    Physician Review : étape Human-in-the-Loop.
    Le workflow s'interrompt ici pour attendre la validation du médecin traitant.
    Le médecin reçoit la synthèse et la recommandation intermédiaire, puis
    propose un traitement ou une conduite à tenir.
    
    LangGraph gère l'interruption via l'annotation interrupt_before ou interrupt_after.
    Cette fonction est appelée APRÈS que le médecin a soumis son avis.
    """
    physician_treatment = state.get("physician_treatment")
    
    if not physician_treatment:
        # En attente de l'intervention du médecin
        return {
            **state,
            "status": "awaiting_physician",
            "messages": state.get("messages", []) + [
                AIMessage(
                    content=(
                        "⏸️ INTERRUPTION HUMAN-IN-THE-LOOP\n\n"
                        "En attente de la validation du médecin traitant.\n"
                        f"Synthèse clinique disponible pour revue médicale.\n"
                        f"Recommandation intermédiaire : {state.get('interim_care', 'Non générée')}"
                    )
                )
            ]
        }
    
    # Le médecin a fourni son avis
    return {
        **state,
        "status": "running",
        "messages": state.get("messages", []) + [
            AIMessage(
                content=f" Revue médicale intégrée.\nConducte à tenir du médecin : {physician_treatment}"
            )
        ]
    }
