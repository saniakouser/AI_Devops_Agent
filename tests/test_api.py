import os
os.environ["DATABASE_URL"] = "sqlite:///./test_incidents.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_and_get_incident():
    response = client.post("/incidents", json={
        "title": "Payment API returns 500",
        "service_name": "payment-api",
        "severity": "high",
        "description": "HTTP 500 after deployment",
        "logs": "Internal Server Error: 500"
    })
    assert response.status_code == 201
    incident_id = response.json()["id"]
    detail = client.get(f"/incidents/{incident_id}")
    assert detail.status_code == 200
    assert detail.json()["service_name"] == "payment-api"

def test_invalid_severity():
    response = client.post("/incidents", json={
        "title": "Invalid severity test",
        "service_name": "test-api",
        "severity": "super-critical",
        "description": "invalid severity"
    })
    assert response.status_code == 422

def test_missing_incident():
    response = client.get("/incidents/999999")
    assert response.status_code == 404

def test_investigation_and_simulated_remediation():
    create = client.post("/incidents", json={
        "title": "Container OOMKilled",
        "service_name": "orders-api",
        "severity": "high",
        "description": "Pod restarted due to memory",
        "logs": "OOMKilled"
    })
    incident_id = create.json()["id"]
    investigation = client.post(f"/incidents/{incident_id}/investigate")
    assert investigation.status_code == 200
    assert "memory" in investigation.json()["root_cause"].lower()
    remediation = client.post(
        f"/incidents/{incident_id}/remediate",
        params={"action": "restart_service"}
    )
    assert remediation.status_code == 200
    assert remediation.json()["simulation"] is True
