from sqlalchemy.orm import Session

from app.models import Evidence, ResearchSource


def get_research_sources(db: Session):
    return (
        db.query(ResearchSource)
        .order_by(ResearchSource.source_name)
        .all()
    )


def get_research_source(db: Session, source_id: int):
    return (
        db.query(ResearchSource)
        .filter(ResearchSource.id == source_id)
        .first()
    )


def get_evidence(
    db: Session,
    domain: str | None = None,
):
    query = db.query(Evidence)

    if domain:
        query = query.filter(Evidence.domain == domain)

    return (
        query
        .order_by(Evidence.domain, Evidence.id)
        .all()
    )


def get_evidence_by_id(db: Session, evidence_id: int):
    return (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )


def get_domains(db: Session):
    rows = (
        db.query(Evidence.domain)
        .distinct()
        .order_by(Evidence.domain)
        .all()
    )

    return [row[0] for row in rows]