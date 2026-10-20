
from types import SimpleNamespace

from app.services.industry_selection import (
    filter_evidence_for_industry,
)
from app.services.intelligence_service import (
    _evidence_for_dimension,
)


def test_persisted_web_evidence_can_match_a_dimension():
    evidence = [
        SimpleNamespace(
            external_id="WEB001",
            industries=["FinTech"],
            domain="Risk Management",
        ),
        SimpleNamespace(
            external_id="WEB002",
            industries=["EdTech"],
            domain="Risk Management",
        ),
    ]

    fintech_evidence = filter_evidence_for_industry(
        evidence,
        "FinTech",
    )

    dimension = SimpleNamespace(
        evidence_domains=["Risk Management"],
    )

    result = _evidence_for_dimension(
        fintech_evidence,
        dimension,
    )

    assert [item.external_id for item in result] == ["WEB001"]


def test_dimension_without_matching_domain_gets_no_evidence():
    evidence = [
        SimpleNamespace(
            external_id="WEB001",
            industries=["FinTech"],
            domain="Customer Experience",
        ),
    ]

    fintech_evidence = filter_evidence_for_industry(
        evidence,
        "FinTech",
    )

    dimension = SimpleNamespace(
        evidence_domains=["Risk Management"],
    )

    assert _evidence_for_dimension(
        fintech_evidence,
        dimension,
    ) == []
