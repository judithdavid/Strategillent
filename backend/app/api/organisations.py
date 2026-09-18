from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.organisation import (
    OrganisationCreate,
    OrganisationResponse,
)
from app.services.organisation_service import (
    get_organisation,
    get_organisations,
    create_organisation,
)


router = APIRouter(
    prefix="/api/organisations",
    tags=["Organisations"],
)


@router.get(
    "",
    response_model=list[OrganisationResponse],
)
def list_organisations(
    db: Session = Depends(get_db),
):
    return get_organisations(db)


@router.get(
    "/{organisation_id}",
    response_model=OrganisationResponse,
)
def read_organisation(
    organisation_id: int,
    db: Session = Depends(get_db),
):
    organisation = get_organisation(
        db,
        organisation_id,
    )

    if organisation is None:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found",
        )

    return organisation


@router.post(
    "",
    response_model=OrganisationResponse,
    status_code=201,
)
def create_new_organisation(
    data: OrganisationCreate,
    db: Session = Depends(get_db),
):
    return create_organisation(
        db,
        data,
    )