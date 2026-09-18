from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Organisation
from app.schemas.analysis import IntelligenceResponse
from app.services.intelligence_service import (
    run_intelligence_analysis,
)


router = APIRouter(
    prefix="/api/intelligence",
    tags=["Intelligence"],
)


@router.post(
    "/{organisation_id}/run",
    response_model=IntelligenceResponse,
)
def run_analysis(
    organisation_id: int,
    db: Session = Depends(get_db),
):
    organisation = (
        db.query(Organisation)
        .filter(
            Organisation.id == organisation_id
        )
        .first()
    )

    if organisation is None:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found",
        )

    result = run_intelligence_analysis(
        db,
        organisation,
    )

    return {
    "organisation_id": organisation.id,
    "organisation_name": organisation.name,
    "analysis_run_id": result["analysis_run"].id,
    "strategic_issues": result["issues"],
    "opportunities": result["opportunities"],
    "initiatives": result["initiatives"],
    }

@router.get(
    "/{organisation_id}",
    response_model=IntelligenceResponse,
)
def get_intelligence(
    organisation_id: int,
    db: Session = Depends(get_db),
):
    organisation = (
        db.query(Organisation)
        .filter(
            Organisation.id == organisation_id
        )
        .first()
    )

    if organisation is None:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found",
        )

    issues = organisation.strategic_issues

    opportunities = sorted(
        organisation.opportunities,
        key=lambda item: (
            item.priority_rank
            if item.priority_rank is not None
            else 999
        ),
    )

    initiatives = []

    for opportunity in opportunities:
        initiatives.extend(
            opportunity.initiatives
        )

    latest_run = None

    if issues:
        latest_run = issues[-1].analysis_run_id

    return {
        "organisation_id": organisation.id,
        "organisation_name": organisation.name,
        "analysis_run_id": latest_run,
        "strategic_issues": issues,
        "opportunities": opportunities,
        "initiatives": initiatives,
    }