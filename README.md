# ClinicalOrient — Système d'Orientation Clinique Préliminaire



Application multi-agents basée sur LangGraph simulant un workflow d'orientation clinique préliminaire.

## Architecture

```
project/
├── backend/           # LangGraph + FastAPI
│   ├── app/
│   │   ├── graph.py          # Graphe LangGraph principal
│   │   ├── state.py          # MedicalState (état partagé)
│   │   ├── nodes/
│   │   │   ├── supervisor.py
│   │   │   ├── diagnostic_agent.py
│   │   │   ├── physician_review.py
│   │   │   └── report_agent.py
│   │   ├── tools/
│   │   │   ├── patient_tools.py  (ask_patient, get_next_question)
│   │   │   ├── care_tools.py     (recommend_interim_care, assess_red_flags)
│   │   │   └── mcp_client.py     (client MCP)
│   │   └── api.py            # FastAPI endpoints
│   ├── langgraph.json        # Config LangGraph Studio
│   └── requirements.txt
├── mcp_server/        # Serveur MCP (outils médicaux)
│   └── server.py
├── frontend/          # React application
│   └── src/
│       ├── pages/     # 4 écrans (intake, questionnaire, physician, report)
│       └── api/       # Appels API
├── docker-compose.yml
└── README.md
```

## Prérequis

- Python 3.11+
- Node.js 20+
- Clé API OpenAI

## Installation rapide

### 1. Backend

```bash
cd backend
cp .env.example .env
#  Edite .env : ajouter OPENAI_API_KEY=sk-...

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.api:app --reload --port 8000
```

### 2. Serveur MCP

```bash
cd mcp_server
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

### 3. Frontend React

```bash
cd frontend
npm install
npm start   # http://localhost:3000
```

### Avec Docker Compose

```bash
cp backend/.env.example .env
# Éditer .env
docker-compose up --build
```

## Endpoints API

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/sessions/start` | Créer une session |
| POST | `/consultation/start` | Démarrer une consultation |
| POST | `/consultation/resume` | Reprendre (réponse patient ou médecin) |
| GET | `/consultation/{thread_id}` | État courant |
| GET | `/consultation/{thread_id}/report` | Rapport final |

## LangGraph Studio

```bash
cd backend
langgraph dev
# Ouvrir http://localhost:2024
```

## Jeux de tests

**Cas 1 – Syndrome respiratoire simple**
- Motif : "Toux et fièvre depuis 3 jours"
- Réponses : durée 3j, 5/10, fièvre 38.2°C, aucun ATCD, pas de signes d'alerte

**Cas 2 – Red flags**
- Motif : "Douleur thoracique intense"
- Réponses : depuis ce matin, 8/10, essoufflement sévère, anticoagulant, douleur thoracique

**Cas 3 – Cas bénin**
- Motif : "Léger mal de gorge"
- Réponses : 2 jours, 2/10, pas de fièvre, aucun ATCD, pas de signes d'alerte

## Workflow LangGraph

```
START → Supervisor → DiagnosticAgent (×5 questions) → Supervisor
     → PhysicianReview [Human-in-the-Loop] → Supervisor
     → ReportAgent → Supervisor → END
```
