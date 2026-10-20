
from types import SimpleNamespace

import pytest

from app.models import Evidence, TransformationDimension
from app.services.intelligence_service import (
    get_applicable_dimensions,
    get_industry_evidence,
)


class FakeQuery:
    def __init__(self, records):
        self.records = records

    def order_by(self, *_args):
        return self

    def all(self):
        return self.records


class FakeDB:
    def __init__(self, evidence, dimensions):
        self.evidence = evidence
        self.dimensions = dimensions

    def query(self, model):
        if model is Evidence:
            return FakeQuery(self.evidence)

        if model is TransformationDimension:
            return FakeQuery(self.dimensions)

        raise AssertionError(f"Unexpected model queried: {model}")


@pytest.fixture
def industry_data():
    evidence = [
        SimpleNamespace(
            external_id="FIN-001",
            domain="FRAUD",
            industries=["FinTech"],
        ),
        SimpleNamespace(
            external_id="EDU-001",
            domain="LEARNING",
            industries=["EdTech", "Education"],
        ),
        SimpleNamespace(
            external_id="HLT-001",
            domain="PATIENT_SAFETY",
            industries=["Healthcare", "HealthTech"],
        ),
        SimpleNamespace(
            external_id="ALL-001",
            domain="GOVERNANCE",
            industries=["*"],
        ),
        SimpleNamespace(
            external_id="UNTAGGED-001",
            domain="FRAUD",
            industries=[],
        ),
    ]

    dimensions = [
        SimpleNamespace(
            external_id="DIM-FIN",
            name="Fraud Risk",
            industries=["FinTech"],
            evidence_domains=["FRAUD"],
        ),
        SimpleNamespace(
            external_id="DIM-EDU",
            name="Learning Outcomes",
            industries=["EdTech"],
            evidence_domains=["LEARNING"],
        ),
        SimpleNamespace(
            external_id="DIM-HLT",
            name="Patient Safety",
            industries=["Healthcare"],
            evidence_domains=["PATIENT_SAFETY"],
        ),
        SimpleNamespace(
            external_id="DIM-ALL",
            name="Universal Governance",
            industries=["*"],
            evidence_domains=["GOVERNANCE"],
        ),
        SimpleNamespace(
            external_id="DIM-UNTAGGED",
            name="Unclassified Dimension",
            industries=[],
            evidence_domains=["FRAUD"],
        ),
    ]

    return evidence, dimensions


@pytest.mark.parametrize(
    ("industry", "expected_ids"),
    [
        ("FinTech", {"FIN-001", "ALL-001"}),
        ("financial services", {"FIN-001", "ALL-001"}),
        ("EdTech", {"EDU-001", "ALL-001"}),
        ("education", {"EDU-001", "ALL-001"}),
        ("Healthcare", {"HLT-001", "ALL-001"}),
        ("health tech", {"HLT-001", "ALL-001"}),
        ("Unknown Industry", {"ALL-001"}),
    ],
)
def test_intelligence_evidence_is_industry_isolated(
    industry_data, industry, expected_ids
):
    evidence, dimensions = industry_data
    db = FakeDB(evidence, dimensions)
    organisation = SimpleNamespace(industry=industry)

    selected = get_industry_evidence(db, organisation)

    assert {item.external_id for item in selected} == expected_ids


@pytest.mark.parametrize(
    ("industry", "expected_ids"),
    [
        ("FinTech", {"DIM-FIN", "DIM-ALL"}),
        ("financial services", {"DIM-FIN", "DIM-ALL"}),
        ("EdTech", {"DIM-EDU", "DIM-ALL"}),
        ("Healthcare", {"DIM-HLT", "DIM-ALL"}),
        ("Unknown Industry", {"DIM-ALL"}),
    ],
)
def test_intelligence_dimensions_are_industry_isolated(
    industry_data, industry, expected_ids
):
    evidence, dimensions = industry_data
    db = FakeDB(evidence, dimensions)
    organisation = SimpleNamespace(industry=industry)

    selected = get_applicable_dimensions(db, organisation)

    assert {item.external_id for item in selected} == expected_ids


@pytest.mark.parametrize("industry", [None, "", "   "])
def test_missing_industry_returns_no_evidence_or_dimensions(
    industry_data, industry
):
    evidence, dimensions = industry_data
    db = FakeDB(evidence, dimensions)
    organisation = SimpleNamespace(industry=industry)

    assert get_industry_evidence(db, organisation) == []
    assert get_applicable_dimensions(db, organisation) == []


def test_industry_evidence_does_not_include_untagged_records(industry_data):
    evidence, dimensions = industry_data
    db = FakeDB(evidence, dimensions)
    organisation = SimpleNamespace(industry="FinTech")

    selected = get_industry_evidence(db, organisation)

    assert all(item.external_id != "UNTAGGED-001" for item in selected)


def test_dimension_domain_matching_is_case_insensitive(industry_data):
    evidence, dimensions = industry_data
    db = FakeDB(evidence, dimensions)
    organisation = SimpleNamespace(industry="FinTech")

    selected_evidence = get_industry_evidence(db, organisation)
    selected_dimensions = get_applicable_dimensions(db, organisation)

    fraud_dimension = next(
        item for item in selected_dimensions
        if item.external_id == "DIM-FIN"
    )

    matching = [
        item for item in selected_evidence
        if item.domain.strip().casefold()
        in {
            domain.strip().casefold()
            for domain in fraud_dimension.evidence_domains
        }
    ]

    assert {item.external_id for item in matching} == {"FIN-001"}
