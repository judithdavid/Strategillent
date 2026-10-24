
from fastapi.testclient import TestClient

from app.main import app
from app.services import intelligence_service


def test_full_intelligence_workflow_passes_evidence(monkeypatch):
    received_evidence = []

    def fake_analyse_dimension(dimension, evidence_records, organisation):
        assert evidence_records, "Issue analysis must receive evidence"

        return {
            "title": f"Test issue: {dimension.name}",
            "description": "Evidence-backed test issue",
            "rationale": "Derived from filtered research evidence",
            "severity": 3,
            "urgency": 3,
            "evidence_ids": [
                item.external_id
                for item in evidence_records
                if getattr(item, "external_id", None)
            ],
            "model_used": "test-model",
            "status": "completed",
        }

    def fake_generate_opportunity(
        dimension,
        issue,
        organisation,
        evidence_records=None,
    ):
        assert evidence_records, (
            "The service must pass filtered evidence to opportunity generation"
        )
        received_evidence.extend(evidence_records)

        return {
            "title": f"Test opportunity: {dimension.name}",
            "description": "Evidence-backed test opportunity",
            "rationale": "Generated using the filtered evidence",
            "business_impact": 7.0,
            "feasibility": 6.0,
            "urgency": 5.0,
            "strategic_alignment": 7.0,
            "evidence_confidence": 6.0,
            "evidence_ids": [
                item.external_id
                for item in evidence_records
                if getattr(item, "external_id", None)
            ],
            "model_used": "test-model",
            "status": "completed",
        }

    monkeypatch.setattr(
        intelligence_service,
        "analyse_dimension",
        fake_analyse_dimension,
    )
    monkeypatch.setattr(
        intelligence_service,
        "generate_opportunity",
        fake_generate_opportunity,
    )

    with TestClient(app) as client:
        response = client.post("/api/intelligence/1/run")

    assert response.status_code == 200, response.text

    payload = response.json()

    assert payload["organisation_id"] == 1
    assert payload["analysis_run_id"] is not None
    assert isinstance(payload["strategic_issues"], list)
    assert isinstance(payload["opportunities"], list)
    assert isinstance(payload["initiatives"], list)

    # A seeded organisation with applicable dimensions and evidence should
    # produce issues, opportunities, and pilot initiatives.
    assert payload["strategic_issues"]
    assert payload["opportunities"]
    assert payload["initiatives"]

    # Proves the service passed evidence into the opportunity generator.
    assert received_evidence
