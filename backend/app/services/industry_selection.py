
"""Canonical industry matching and industry-specific data selection.

This module provides shared helpers for:
- Normalising industry names and aliases.
- Checking whether evidence applies to an industry.
- Filtering evidence by industry.
- Selecting applicable transformation dimensions.
- Matching evidence to a dimension's research domains.

Unknown or missing industry tags fail closed. Only an explicit "*" tag
makes a record applicable to every industry.
"""

from collections.abc import Iterable
from typing import Any


INDUSTRY_ALIASES: dict[str, set[str]] = {
    "fintech": {
        "fintech",
        "financial services",
        "financial technology",
        "banking",
    },
    "edtech": {
        "edtech",
        "education",
        "educational technology",
    },
    "healthcare": {
        "healthcare",
        "health tech",
        "healthtech",
        "health services",
    },
}


def normalise_industry(value: str | None) -> str:
    """Return the canonical industry name when an alias is recognised."""
    value = (value or "").strip().casefold()

    if not value:
        return ""

    for canonical, aliases in INDUSTRY_ALIASES.items():
        if value == canonical or value in aliases:
            return canonical

    # Preserve unknown industry names in a consistent format.
    return value


def industry_matches(
    values: Iterable[str] | None,
    requested_industry: str | None,
) -> bool:
    """Check whether industry tags apply to the requested industry.

    Examples:
        ["FinTech"] matches "financial services".
        ["EdTech", "Education"] matches "education".
        ["*"] matches any non-empty requested industry.
        [] does not match any industry.
    """
    requested = normalise_industry(requested_industry)

    if not requested:
        return False

    available = {
        normalise_industry(value)
        for value in (values or [])
        if isinstance(value, str) and value.strip()
    }

    return "*" in available or requested in available


def filter_evidence_for_industry(
    evidence_records: Iterable[Any],
    industry: str | None,
) -> list[Any]:
    """Return only evidence applicable to the requested industry."""
    if not normalise_industry(industry):
        return []

    return [
        record
        for record in evidence_records
        if industry_matches(
            getattr(record, "industries", None),
            industry,
        )
    ]


def select_applicable_dimensions(
    dimensions: Iterable[Any],
    industry: str | None,
) -> list[Any]:
    """Return only transformation dimensions applicable to an industry."""
    if not normalise_industry(industry):
        return []

    return [
        dimension
        for dimension in dimensions
        if industry_matches(
            getattr(dimension, "industries", None),
            industry,
        )
    ]


def evidence_matches_dimension(
    evidence: Any,
    dimension: Any,
) -> bool:
    """Check whether evidence belongs to one of a dimension's domains."""
    evidence_domain = getattr(evidence, "domain", None)

    if not isinstance(evidence_domain, str) or not evidence_domain.strip():
        return False

    allowed_domains = {
        domain.strip().casefold()
        for domain in (
            getattr(dimension, "evidence_domains", None) or []
        )
        if isinstance(domain, str) and domain.strip()
    }

    return evidence_domain.strip().casefold() in allowed_domains


def filter_evidence_for_dimension(
    evidence_records: Iterable[Any],
    dimension: Any,
) -> list[Any]:
    """Return evidence whose research domain matches a dimension."""
    return [
        record
        for record in evidence_records
        if evidence_matches_dimension(record, dimension)
    ]


def select_evidence_for_dimension(
    evidence_records: Iterable[Any],
    dimension: Any,
    industry: str | None,
) -> list[Any]:
    """Filter evidence by industry first, then by dimension domain."""
    industry_evidence = filter_evidence_for_industry(
        evidence_records,
        industry,
    )

    return filter_evidence_for_dimension(
        industry_evidence,
        dimension,
    )
