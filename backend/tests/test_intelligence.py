from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_intelligence_before_or_after_run():
    response = client.get("/api/intelligence/1")

    assert response.status_code in [200, 404]


def test_run_intelligence():
    response = client.post("/api/intelligence/1/run")

    assert response.status_code == 200

    data = response.json()

    assert "analysis_run_id" in data
    assert "organisation_id" in data
    assert "opportunities" in data
    assert "initiatives" in data

    assert isinstance(data["opportunities"], list)
    assert isinstance(data["initiatives"], list)

    assert len(data["opportunities"]) > 0
    assert len(data["initiatives"]) > 0


def test_intelligence_creates_expected_structure():
    response = client.get("/api/intelligence/1")

    assert response.status_code == 200

    data = response.json()

    assert "analysis_run_id" in data
    assert "organisation_id" in data
    assert "opportunities" in data
    assert "initiatives" in data