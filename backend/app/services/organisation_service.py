from sqlalchemy.orm import Session

from app.models import Organisation
from app.schemas.organisation import OrganisationCreate


def get_organisation(
    db: Session,
    organisation_id: int,
):
    return (
        db.query(Organisation)
        .filter(
            Organisation.id == organisation_id
        )
        .first()
    )


def get_organisations(
    db: Session,
):
    return (
        db.query(Organisation)
        .order_by(Organisation.id)
        .all()
    )


def create_organisation(
    db: Session,
    data: OrganisationCreate,
):
    organisation = Organisation(
        name=data.name,
        fictional=data.fictional,
        industry=data.industry,
        business_model=data.business_model,
        markets=data.markets,
        customers=data.customers,
        employees=data.employees,
        products=data.products,
        challenges=data.challenges,
        goals=data.goals,
        processes=data.processes,
        technology=data.technology,
        constraints=data.constraints,
    )

    db.add(organisation)
    db.commit()
    db.refresh(organisation)

    return organisation