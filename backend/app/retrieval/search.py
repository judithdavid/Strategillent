from sqlalchemy.orm import Session

from app.models import Evidence


def search_evidence(
    db: Session,
    query: str,
    limit: int = 6,
):
    """
    Simple local retrieval.

    Matches query terms against evidence title,
    domain, claim, evidence text and strategic implication.
    """

    words = [
        word.lower()
        for word in query.split()
        if len(word) >= 3
    ]

    evidence_records = (
        db.query(Evidence)
        .order_by(Evidence.relevance.desc(), Evidence.id)
        .all()
    )

    scored = []

    for evidence in evidence_records:

        searchable_text = " ".join([
            evidence.title or "",
            evidence.domain or "",
            evidence.claim or "",
            evidence.evidence_text or "",
            evidence.strategic_implication or "",
            " ".join(evidence.tags or []),
        ]).lower()

        score = 0

        for word in words:
            if word in searchable_text:
                score += 1

        if score > 0:
            scored.append(
                (score, evidence)
            )

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