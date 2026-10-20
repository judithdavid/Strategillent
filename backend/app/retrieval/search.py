from sqlalchemy.orm import Session

from app.models import Evidence
from app.services.industry_selection import (
    filter_evidence_for_industry,
)


def search_evidence(
    db: Session,
    query: str,
    limit: int = 6,
    industry: str | None = None,
    domain: str | None = None,
):
    """
    Search persisted evidence using keyword scoring.

    Optionally restrict results to an industry and domain.
    Includes seeded evidence and online research already persisted
    in the Evidence table.
    """

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    words = [
        word.casefold()
        for word in query.split()
        if len(word) >= 3
    ]

    evidence_records = (
        db.query(Evidence)
        .order_by(Evidence.relevance.desc(), Evidence.id)
        .all()
    )

    # When an industry is provided, exclude evidence from other industries.
    if industry is not None:
        if not industry.strip():
            raise ValueError("Industry cannot be empty.")

        evidence_records = filter_evidence_for_industry(
            evidence_records,
            industry,
        )

    if domain:
        requested_domain = domain.strip().casefold()
        evidence_records = [
            evidence
            for evidence in evidence_records
            if (evidence.domain or "").strip().casefold()
            == requested_domain
        ]

    scored = []

    for evidence in evidence_records:
        searchable_text = " ".join([
            evidence.title or "",
            evidence.domain or "",
            evidence.claim or "",
            evidence.evidence_text or "",
            evidence.strategic_implication or "",
            " ".join(evidence.tags or []),
        ]).casefold()

        score = sum(
            1 for word in words
            if word in searchable_text
        )

        if score > 0:
            scored.append((score, evidence))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1].relevance,
            item[1].confidence,
        ),
        reverse=True,
    )

    return [
        evidence
        for _, evidence in scored[:limit]
    ]

