from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node


def route_from_supervisor(state: MedicalState) -> str:
    """Router function appelée après le supervisor pour diriger vers le bon nœud."""
    next_step = state.get("next", "diagnostic_agent")
    if next_step == "FINISH":
        return END
    return next_step


def build_graph():
    """Construit et compile le graphe LangGraph du workflow médical."""
    
    workflow = StateGraph(MedicalState)
    
    # Ajout des nœuds
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("diagnostic_agent", diagnostic_agent_node)
    workflow.add_node("physician_review", physician_review_node)
    workflow.add_node("report_agent", report_agent_node)
    
    # Point d'entrée
    workflow.add_edge(START, "supervisor")
    
    # Routage conditionnel depuis le supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            END: END,
        }
    )
    
    # Retour au supervisor après chaque nœud métier
    workflow.add_edge("diagnostic_agent", "supervisor")
    workflow.add_edge("physician_review", "supervisor")
    workflow.add_edge("report_agent", "supervisor")
    
    # Persistance en mémoire (MemorySaver pour dev; SqliteSaver pour prod)
    memory = MemorySaver()
    
    # Interruption avant physician_review (Human-in-the-Loop)
    graph = workflow.compile(
        checkpointer=memory,
        interrupt_before=["physician_review"],
    )
    
    return graph


# Instance du graphe (singleton)
medical_graph = build_graph()
