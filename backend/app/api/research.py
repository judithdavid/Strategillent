from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.research import (
    ResearchSourceResponse,
    EvidenceResponse,
)
from app.services.research_service import (
    get_research_sources,
    get_research_source,
    get_evidence,
    get_evidence_by_id,
    get_domains,
)

router = APIRouter(
    prefix="/api/research",
    tags=["Research"],
)


@router.get(
    "/sources",
    response_model=list[ResearchSourceResponse],
)
def list_research_sources(
    db: Session = Depends(get_db),
):
    return get_research_sources(db)


@router.get(
    "/sources/{source_id}",
    response_model=ResearchSourceResponse,
)
def read_research_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    source = get_research_source(db, source_id)

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Research source not found",
        )

    return source


@router.get(
    "/evidence",
    response_model=list[EvidenceResponse],
)
def list_evidence(
    domain: str | None = None,
    db: Session = Depends(get_db),
):
    return get_evidence(
        db=db,
        domain=domain,
    )


@router.get(
    "/evidence/{evidence_id}",
    response_model=EvidenceResponse,
)
def read_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
):
    evidence = get_evidence_by_id(
        db,
        evidence_id,
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )

    return evidence


@router.get(
    "/domains",
    response_model=list[str],
)
def list_research_domains(
    db: Session = Depends(get_db),
):
    return get_domains(db)