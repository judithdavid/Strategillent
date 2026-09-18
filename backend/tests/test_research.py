from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_research_sources():
    response = client.get("/api/research/sources")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_evidence():
    response = client.get("/api/research/evidence")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_evidence_has_required_fields():
    response = client.get("/api/research/evidence")

    assert response.status_code == 200

    evidence = response.json()[0]

    assert "external_id" in evidence
    assert "title" in evidence
    assert "claim" in evidence
    assert "evidence_text" in evidence
    assert "strategic_implication" in evidence


def test_get_research_domains():
    response = client.get("/api/research/domains")

    assert response.status_code == 200

    domains = response.json()

    assert isinstance(domains, list)
    assert len(domains) > 0