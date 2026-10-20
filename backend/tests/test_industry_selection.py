
from types import SimpleNamespace

from app.services.industry_selection import (
    evidence_matches_dimension,
    filter_evidence_for_dimension,
    filter_evidence_for_industry,
    industry_matches,
    normalise_industry,
    select_applicable_dimensions,
    select_evidence_for_dimension,
)


def make_evidence(
    external_id: str,
    domain: str = "AI",
    industries: list[str] | None = None,
):
    return SimpleNamespace(
        external_id=external_id,
        domain=domain,
        industries=industries or [],
    )


def make_dimension(
    external_id: str,
    industries: list[str] | None = None,
    evidence_domains: list[str] | None = None,
):
    return SimpleNamespace(
        external_id=external_id,
        industries=industries or [],
        evidence_domains=evidence_domains or [],
    )


# ---------------------------------------------------------
# Industry normalisation
# ---------------------------------------------------------


def test_industry_aliases_are_normalised():
    assert normalise_industry("FinTech") == "fintech"
    assert normalise_industry("Financial Services") == "fintech"
    assert normalise_industry("Banking") == "fintech"

    assert normalise_industry("EdTech") == "edtech"
    assert normalise_industry("Education") == "edtech"
    assert normalise_industry("Educational Technology") == "edtech"

    assert normalise_industry("Healthcare") == "healthcare"
    assert normalise_industry("HealthTech") == "healthcare"
    assert normalise_industry("Health Services") == "healthcare"


def test_industry_normalisation_handles_empty_and_unknown_values():
    assert normalise_industry(None) == ""
    assert normalise_industry("") == ""
    assert normalise_industry("  ") == ""
    assert normalise_industry("Retail") == "retail"


# ---------------------------------------------------------
# Industry matching
# ---------------------------------------------------------


def test_industry_matches_aliases():
    assert industry_matches(
        ["FinTech"],
        "Financial Services",
    )

    assert industry_matches(
        ["EdTech", "Education"],
        "Education",
    )

    assert industry_matches(
        ["Healthcare", "HealthTech"],
        "HealthTech",
    )


def test_industry_matching_is_case_insensitive():
    assert industry_matches(["FINTECH"], "fintech")
    assert industry_matches(["healthTECH"], "HEALTHCARE")


def test_untagged_evidence_does_not_match_an_industry():
    assert not industry_matches([], "FinTech")
    assert not industry_matches(None, "EdTech")


def test_empty_requested_industry_does_not_match():
    assert not industry_matches(["*"], "")
    assert not industry_matches(["FinTech"], None)


def test_explicit_universal_tag_matches_all_industries():
    assert industry_matches(["*"], "FinTech")
    assert industry_matches(["*"], "EdTech")
    assert industry_matches(["*"], "Healthcare")


# ---------------------------------------------------------
# Evidence filtering
# ---------------------------------------------------------


def test_evidence_is_isolated_by_industry():
    evidence = [
        make_evidence("FIN001", "FRAUD", ["FinTech"]),
        make_evidence("EDU001", "AI", ["EdTech", "Education"]),
        make_evidence(
            "HLT001",
            "GOVERNANCE",
            ["Healthcare", "HealthTech"],
        ),
    ]

    assert [
        item.external_id
        for item in filter_evidence_for_industry(evidence, "FinTech")
    ] == ["FIN001"]

    assert [
        item.external_id
        for item in filter_evidence_for_industry(evidence, "Education")
    ] == ["EDU001"]

    assert [
        item.external_id
        for item in filter_evidence_for_industry(evidence, "HealthTech")
    ] == ["HLT001"]


def test_untagged_evidence_is_excluded():
    evidence = [
        make_evidence("FIN001", "FRAUD", ["FinTech"]),
        make_evidence("UNKNOWN001", "AI", []),
    ]

    result = filter_evidence_for_industry(evidence, "FinTech")

    assert [item.external_id for item in result] == ["FIN001"]


def test_unknown_requested_industry_returns_no_evidence():
    evidence = [
        make_evidence("FIN001", "FRAUD", ["FinTech"]),
    ]

    assert filter_evidence_for_industry(evidence, "") == []
    assert filter_evidence_for_industry(evidence, None) == []


# ---------------------------------------------------------
# Transformation dimension selection
# ---------------------------------------------------------


def test_dimensions_are_filtered_by_industry():
    dimensions = [
        make_dimension("T01", ["FinTech"]),
        make_dimension("E01", ["EdTech", "Education"]),
        make_dimension("H01", ["Healthcare", "HealthTech"]),
    ]

    assert [
        item.external_id
        for item in select_applicable_dimensions(dimensions, "FinTech")
    ] == ["T01"]

    assert [
        item.external_id
        for item in select_applicable_dimensions(dimensions, "Education")
    ] == ["E01"]

    assert [
        item.external_id
        for item in select_applicable_dimensions(dimensions, "Healthcare")
    ] == ["H01"]


def test_dimensions_without_industry_tags_are_excluded():
    dimensions = [
        make_dimension("T01", ["FinTech"]),
        make_dimension("UNKNOWN01", []),
    ]

    result = select_applicable_dimensions(dimensions, "FinTech")

    assert [item.external_id for item in result] == ["T01"]


def test_unknown_requested_industry_returns_no_dimensions():
    dimensions = [
        make_dimension("T01", ["FinTech"]),
    ]

    assert select_applicable_dimensions(dimensions, "") == []
    assert select_applicable_dimensions(dimensions, None) == []


# ---------------------------------------------------------
# Evidence-to-dimension domain matching
# ---------------------------------------------------------


def test_evidence_matches_dimension_domain():
    evidence = make_evidence("EDU001", "AI", ["EdTech"])
    dimension = make_dimension(
        "E01",
        ["EdTech"],
        ["AI", "DATA"],
    )

    assert evidence_matches_dimension(evidence, dimension)


def test_domain_matching_is_case_insensitive():
    evidence = make_evidence("EDU001", "ai", ["EdTech"])
    dimension = make_dimension(
        "E01",
        ["EdTech"],
        ["AI"],
    )

    assert evidence_matches_dimension(evidence, dimension)


def test_evidence_with_unmatched_domain_is_excluded():
    evidence = [
        make_evidence("EDU001", "AI", ["EdTech"]),
        make_evidence("EDU002", "GOVERNANCE", ["EdTech"]),
    ]

    dimension = make_dimension(
        "E01",
        ["EdTech"],
        ["GOVERNANCE"],
    )

    result = filter_evidence_for_dimension(evidence, dimension)

    assert [item.external_id for item in result] == ["EDU002"]


def test_dimension_without_domains_matches_no_evidence():
    evidence = [
        make_evidence("EDU001", "AI", ["EdTech"]),
    ]

    dimension = make_dimension(
        "E01",
        ["EdTech"],
        [],
    )

    assert filter_evidence_for_dimension(evidence, dimension) == []


def test_missing_evidence_domain_is_excluded():
    evidence = SimpleNamespace(
        external_id="UNKNOWN001",
        industries=["EdTech"],
    )
    dimension = make_dimension(
        "E01",
        ["EdTech"],
        ["AI"],
    )

    assert not evidence_matches_dimension(evidence, dimension)


# ---------------------------------------------------------
# Combined industry and dimension selection
# ---------------------------------------------------------


def test_select_evidence_for_dimension_filters_industry_and_domain():
    evidence = [
        make_evidence("EDU001", "AI", ["EdTech"]),
        make_evidence("EDU002", "GOVERNANCE", ["EdTech"]),
        make_evidence("FIN001", "AI", ["FinTech"]),
        make_evidence("UNKNOWN001", "AI", []),
    ]

    dimension = make_dimension(
        "E01",
        ["EdTech"],
        ["AI"],
    )

    result = select_evidence_for_dimension(
        evidence,
        dimension,
        "Education",
    )

    assert [item.external_id for item in result] == ["EDU001"]


def test_no_matching_evidence_returns_empty_list():
    evidence = [
        make_evidence("FIN001", "FRAUD", ["FinTech"]),
    ]

    dimension = make_dimension(
        "E01",
        ["EdTech"],
        ["AI"],
    )

    result = select_evidence_for_dimension(
        evidence,
        dimension,
        "EdTech",
    )

    assert result == []


def test_universal_evidence_can_match_a_dimension_domain():
    evidence = [
        make_evidence("GEN001", "AI", ["*"]),
    ]

    dimension = make_dimension(
        "E01",
        ["EdTech"],
        ["AI"],
    )

    result = select_evidence_for_dimension(
        evidence,
        dimension,
        "EdTech",
    )

    assert [item.external_id for item in result] == ["GEN001"]
