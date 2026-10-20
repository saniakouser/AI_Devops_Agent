# AI DevOps Incident Resolution Agent

A starter implementation of a DevOps incident investigation service using FastAPI, SQLAlchemy, and LangGraph.

## Features
- Create, list, and retrieve incidents
- Rule-based root-cause analysis from caller-supplied logs/description
- LangGraph investigation workflow
- Lightweight local historical-incident retrieval (keyword overlap, not embedding-based RAG yet)
- Policy checks and **simulation-only** remediation
- Unit/API tests

## Important limitations
- Metrics/service status are demo stubs.
- Root-cause analysis is heuristic-based; no LLM is wired in yet.
- Historical retrieval uses keyword overlap; embeddings/vector database are not configured.
- Remediation does not touch real infrastructure.
- Verification endpoint intentionally reports unverified until a real health-check integration is added.
- Jira, Kubernetes, Prometheus, and Redis integrations are not connected.

## Run locally
```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs.

## Example incident
POST `/incidents`:
```json
{
  "title": "Payment API returns 500",
  "service_name": "payment-api",
  "severity": "high",
  "description": "HTTP 500 errors after deployment",
  "logs": "Internal Server Error: 500"
}
```
Then POST `/incidents/1/investigate` using the ID returned by your API.

## Test
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

## Security
Do not commit `.env`, API keys, tokens, customer logs, or production credentials. Use least-privilege identities and add authentication/authorization before deployment.
