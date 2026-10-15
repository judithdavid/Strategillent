"""Evidence-grounded strategic issue construction.

This module deliberately does not invent external facts. Issues are derived from
an applicable transformation dimension and the evidence records selected for it.
"""
from statistics import mean


def analyse_dimension(dimension, evidence_records: list, organisation) -> dict:
    if not evidence_records:
        raise ValueError("Cannot analyse a transformation dimension without evidence.")

    evidence_ids = [record.external_id for record in evidence_records]
    evidence_domains = sorted({record.domain for record in evidence_records})
    challenges = getattr(organisation, "challenges", None) or []
    goals = getattr(organisation, "goals", None) or []
    profile_context = "; ".join(str(value) for value in [*challenges, *goals])

    summary = dimension.description or dimension.name
    rationale = (
        f"Selected for industry '{organisation.industry}' because transformation "
        f"dimension '{dimension.name}' applies to this industry and has "
        f"{len(evidence_records)} industry-matched evidence record(s). "
        f"Evidence IDs: {', '.join(evidence_ids)}. "
        f"Research domains: {', '.join(evidence_domains)}."
    )
    if profile_context:
        rationale += f" Organisation goals/challenges considered: {profile_context}."

    avg_relevance = mean(float(getattr(item, "relevance", 1) or 1) for item in evidence_records)
    avg_confidence = mean(float(getattr(item, "confidence", 1) or 1) for item in evidence_records)
    severity = max(1, min(5, round((avg_relevance + avg_confidence) / 2)))

    return {
        "title": dimension.name,
        "description": summary,
        "rationale": rationale,
        "severity": severity,
        "urgency": severity,
        "evidence_ids": evidence_ids,
    }
