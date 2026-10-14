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


def test_get_evidence_filters_by_industry():
    fintech_response = client.get(
        "/api/research/evidence",
        params={"industry": "FinTech"},
    )

    assert fintech_response.status_code == 200

    fintech_data = fintech_response.json()

    assert isinstance(fintech_data, list)
    assert len(fintech_data) > 0
    assert all(
        "FinTech" in item.get("industries", [])
        for item in fintech_data
    )


def test_edtech_filter_excludes_fintech_only_evidence():
    response = client.get(
        "/api/research/evidence",
        params={"industry": "EdTech"},
    )

    assert response.status_code == 200

    data = response.json()

    assert all(
        "EdTech" in item.get("industries", [])
        for item in data
    )


def test_get_evidence_filters_by_domain_and_industry():
    response = client.get(
        "/api/research/evidence",
        params={
            "domain": "AI",
            "industry": "FinTech",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert all(item["domain"] == "AI" for item in data)
    assert all(
        "FinTech" in item.get("industries", [])
        for item in data
    )

