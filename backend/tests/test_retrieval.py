
from types import SimpleNamespace

from app.services.industry_selection import (
    filter_evidence_for_industry,
)


def test_fintech_retrieval_excludes_other_industries():
    records = [
        SimpleNamespace(
            external_id="FIN001",
            industries=["FinTech"],
        ),
        SimpleNamespace(
            external_id="EDU001",
            industries=["EdTech", "Education"],
        ),
        SimpleNamespace(
            external_id="HLT001",
            industries=["Healthcare"],
        ),
    ]

    result = filter_evidence_for_industry(records, "FinTech")

    assert [item.external_id for item in result] == ["FIN001"]


def test_retrieval_excludes_untagged_evidence():
    records = [
        SimpleNamespace(
            external_id="FIN001",
            industries=["FinTech"],
        ),
        SimpleNamespace(
            external_id="UNKNOWN",
            industries=[],
        ),
    ]

    result = filter_evidence_for_industry(records, "FinTech")

    assert [item.external_id for item in result] == ["FIN001"]
