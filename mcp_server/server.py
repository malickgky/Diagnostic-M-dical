"""
Serveur MCP (Model Context Protocol) pour les outils médicaux de référence.
Expose des outils que les agents LangGraph peuvent appeler via le protocole MCP.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os

app = FastAPI(
    title="ClinicalOrient MCP Server",
    description="Serveur MCP exposant des outils médicaux de référence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Données de référence médicale (simulées) ───────────────────────────────

MEDICAL_REFERENCES = {
    "syndrome_grippal": {
        "description": "Infection virale aiguë des voies respiratoires",
        "symptoms": ["fièvre", "myalgies", "céphalées", "toux", "asthénie"],
        "duration": "5-7 jours",
        "treatment": "Repos, antalgiques, hydratation",
        "red_flags": ["dyspnée sévère", "douleur thoracique", "confusion"]
    },
    "gastroenterite": {
        "description": "Inflammation gastro-intestinale aiguë",
        "symptoms": ["nausées", "vomissements", "diarrhée", "douleurs abdominales"],
        "duration": "2-5 jours",
        "treatment": "Hydratation orale, régime alimentaire doux",
        "red_flags": ["déshydratation sévère", "sang dans les selles", "fièvre > 38.5°C"]
    },
    "infection_respiratoire": {
        "description": "Infection des voies respiratoires supérieures ou inférieures",
        "symptoms": ["toux", "dyspnée", "fièvre", "expectorations"],
        "duration": "7-14 jours",
        "treatment": "Selon étiologie (virale ou bactérienne)",
        "red_flags": ["SpO2 < 95%", "FR > 30/min", "confusion", "cyanose"]
    }
}

ICD10_CODES = {
    "fièvre": "R50.9",
    "toux": "R05",
    "douleur thoracique": "R07.9",
    "dyspnée": "R06.0",
    "céphalée": "R51",
    "diarrhée": "R19.7",
    "nausées": "R11.0",
    "asthénie": "R53.1",
}


# ─── Schémas Pydantic ────────────────────────────────────────────────────────

class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]


class MedicalReferenceRequest(BaseModel):
    condition: str


class DrugInteractionRequest(BaseModel):
    medications: List[str]


class ICDCodesRequest(BaseModel):
    symptoms: List[str]


# ─── Endpoints MCP ──────────────────────────────────────────────────────────

@app.get("/tools")
async def list_tools():
    """Liste tous les outils disponibles sur ce serveur MCP."""
    return {
        "tools": [
            {
                "name": "get_medical_reference",
                "description": "Récupère des informations de référence sur une condition médicale",
                "parameters": {"condition": "string"}
            },
            {
                "name": "check_drug_interactions",
                "description": "Vérifie les interactions entre médicaments",
                "parameters": {"medications": "list[string]"}
            },
            {
                "name": "get_icd_codes",
                "description": "Retourne les codes CIM-10 associés aux symptômes",
                "parameters": {"symptoms": "list[string]"}
            }
        ]
    }


@app.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """Point d'entrée unifié pour appeler n'importe quel outil MCP."""
    tool = request.tool
    args = request.arguments

    if tool == "get_medical_reference":
        return await get_medical_reference(MedicalReferenceRequest(**args))
    elif tool == "check_drug_interactions":
        return await check_drug_interactions(DrugInteractionRequest(**args))
    elif tool == "get_icd_codes":
        return await get_icd_codes(ICDCodesRequest(**args))
    else:
        return {"error": f"Outil inconnu : {tool}"}


@app.post("/tools/medical_reference")
async def get_medical_reference(request: MedicalReferenceRequest):
    """Récupère des informations de référence sur une condition médicale."""
    condition_lower = request.condition.lower().replace(" ", "_")
    
    # Recherche exacte puis partielle
    ref = MEDICAL_REFERENCES.get(condition_lower)
    if not ref:
        for key, value in MEDICAL_REFERENCES.items():
            if condition_lower in key or key in condition_lower:
                ref = value
                break
    
    if ref:
        return {"condition": request.condition, "reference": ref, "found": True}
    
    return {
        "condition": request.condition,
        "found": False,
        "message": "Condition non trouvée dans la base de référence locale"
    }


@app.post("/tools/drug_interactions")
async def check_drug_interactions(request: DrugInteractionRequest):
    """Vérifie les interactions médicamenteuses (simulé)."""
    # Simulation d'interactions connues
    known_interactions = {
        ("aspirine", "anticoagulant"): "Risque hémorragique augmenté",
        ("ibuprofen", "anticoagulant"): "Risque hémorragique augmenté",
    }
    
    detected_interactions = []
    meds_lower = [m.lower() for m in request.medications]
    
    for (drug1, drug2), warning in known_interactions.items():
        if any(drug1 in m for m in meds_lower) and any(drug2 in m for m in meds_lower):
            detected_interactions.append({
                "drugs": [drug1, drug2],
                "warning": warning,
                "severity": "moderate"
            })
    
    return {
        "medications": request.medications,
        "interactions": detected_interactions,
        "has_interactions": len(detected_interactions) > 0
    }


@app.post("/tools/icd_codes")
async def get_icd_codes(request: ICDCodesRequest):
    """Retourne les codes CIM-10 associés aux symptômes."""
    codes = {}
    for symptom in request.symptoms:
        symptom_lower = symptom.lower()
        for key, code in ICD10_CODES.items():
            if key in symptom_lower or symptom_lower in key:
                codes[symptom] = code
                break
        if symptom not in codes:
            codes[symptom] = "R69"  # Code inconnu/non spécifié
    
    return {"symptoms": request.symptoms, "icd10_codes": codes}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ClinicalOrient MCP Server"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
