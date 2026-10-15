"""Industry-aware selection helpers shared by the strategy pipeline."""

INDUSTRY_ALIASES = {
    "edtech": {"edtech", "education", "educational technology"},
    "healthcare": {"healthcare", "health tech", "healthtech", "health services"},
    "fintech": {"fintech", "financial services", "financial technology", "banking"},
}


def normalise_industry(value: str | None) -> str:
    value = (value or "").strip().casefold()
    for canonical, aliases in INDUSTRY_ALIASES.items():
        if value in aliases:
            return canonical
    return value


def industry_matches(values, requested_industry: str) -> bool:
    requested = normalise_industry(requested_industry)
    available = {normalise_industry(value) for value in (values or [])}
    return "*" in available or requested in available


def filter_evidence_for_industry(evidence_records, industry: str):
    """Strictly exclude evidence that is not tagged for this industry."""
    return [
        record for record in evidence_records
        if industry_matches(getattr(record, "industries", []), industry)
    ]


def select_applicable_dimensions(dimensions, industry: str):
    return [
        dimension for dimension in dimensions
        if industry_matches(getattr(dimension, "industries", []), industry)
    ]
