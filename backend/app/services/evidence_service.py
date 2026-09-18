from sqlalchemy.orm import Session

from app.models import Evidence


def get_evidence_for_domain(
    db: Session,
    domain: str,
):
    return (
        db.query(Evidence)
        .filter(Evidence.domain == domain)
        .order_by(Evidence.id)
        .all()
    )


def get_evidence_by_external_ids(
    db: Session,
    external_ids: list[str],
):
    if not external_ids:
        return []

    return (
        db.query(Evidence)
        .filter(Evidence.external_id.in_(external_ids))
        .all()
    )