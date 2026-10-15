from types import SimpleNamespace

from app.services.industry_selection import (
    filter_evidence_for_industry,
    select_applicable_dimensions,
)
from app.ai.issue_analyser import analyse_dimension
from app.ai.opportunity_generator import generate_opportunity


def item(**kwargs):
    defaults = {
        "external_id": "E1", "domain": "AI", "industries": ["FinTech"],
        "confidence": 4, "relevance": 4, "claim": "sample claim",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_fintech_evidence_does_not_leak_into_edtech_or_healthcare():
    records = [
        item(external_id="FIN1", industries=["FinTech"]),
        item(external_id="EDU1", industries=["EdTech", "Education"]),
        item(external_id="HLT1", industries=["Healthcare", "HealthTech"]),
    ]

    assert [x.external_id for x in filter_evidence_for_industry(records, "FinTech")] == ["FIN1"]
    assert [x.external_id for x in filter_evidence_for_industry(records, "EdTech")] == ["EDU1"]
    assert [x.external_id for x in filter_evidence_for_industry(records, "Healthcare")] == ["HLT1"]


def test_industry_aliases_are_supported():
    record = item(industries=["EdTech", "Education"])
    assert filter_evidence_for_industry([record], "Education") == [record]


def test_only_applicable_dimensions_are_selected():
    dimensions = [
        SimpleNamespace(name="Fraud", industries=["FinTech"]),
        SimpleNamespace(name="Teaching", industries=["EdTech", "Education"]),
        SimpleNamespace(name="Patient Safety", industries=["Healthcare"]),
    ]
    assert [d.name for d in select_applicable_dimensions(dimensions, "EdTech")] == ["Teaching"]
    assert [d.name for d in select_applicable_dimensions(dimensions, "Healthcare")] == ["Patient Safety"]


def test_issue_and_opportunity_are_derived_from_dimension_and_evidence():
    organisation = SimpleNamespace(
        industry="EdTech", goals=["Improve learning outcomes"],
        challenges=["Slow manual grading"], processes=["Manual assessment"],
        technology=["LMS"], constraints=["Student privacy"],
    )
    evidence = item(external_id="EDU001", industries=["EdTech", "Education"])
    dimension = SimpleNamespace(
        name="AI-Assisted Teaching and Assessment",
        description="Evaluate educator-controlled AI support for assessment.",
        evidence_domains=["AI"],
        candidate_initiatives=["Educator-reviewed feedback assistant"],
    )
    issue_data = analyse_dimension(dimension, [evidence], organisation)
    issue = SimpleNamespace(title=issue_data["title"], evidence=[evidence])
    opportunity = generate_opportunity(dimension, issue, organisation)

    assert issue_data["title"] == dimension.name
    assert "EDU001" in issue_data["rationale"]
    assert opportunity["title"] == "Educator-reviewed feedback assistant"
    assert "EDU001" in opportunity["rationale"]
    assert "FinNova" not in opportunity["description"]
