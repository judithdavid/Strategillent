import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import (
    Organisation,
    Objective,
    ResearchSource,
    Evidence,
    TransformationDimension,
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent

SEED_DIR = PROJECT_ROOT / "data" / "seed"


ORGANISATION_FILE = SEED_DIR / "organisation.json"
EVIDENCE_FILE = SEED_DIR / "evidence.json"
TRANSFORMATION_FILE = SEED_DIR / "transformation_dimensions.json"


# ---------------------------------------------------------
# JSON helper
# ---------------------------------------------------------

def load_json(file_path: Path):
    """
    Load a JSON file and return its contents.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Seed file not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ---------------------------------------------------------
# Date helper
# ---------------------------------------------------------

def parse_date(value):
    """
    Convert YYYY-MM-DD strings into Python date objects.

    Handles year-only values such as '2026' by returning
    January 1st of that year.
    """

    if not value:
        return None

    value = str(value)

    try:
        return date.fromisoformat(value)
    except ValueError:

        if len(value) == 4 and value.isdigit():
            return date(int(value), 1, 1)

        return None


# ---------------------------------------------------------
# Organisation
# ---------------------------------------------------------

def seed_organisation(
    db: Session,
    organisation_data: dict,
) -> Organisation:

    company_name = organisation_data["company"]

    organisation = (
        db.query(Organisation)
        .filter(
            Organisation.name == company_name
        )
        .first()
    )

    if organisation is None:

        organisation = Organisation(
            name=company_name,
            fictional=organisation_data.get(
                "fictional",
                True,
            ),
            industry=organisation_data.get(
                "industry",
                "",
            ),
            business_model=organisation_data.get(
                "business_model",
                [],
            ),
            markets=organisation_data.get(
                "markets",
                [],
            ),
            customers=organisation_data.get(
                "customers",
            ),
            employees=organisation_data.get(
                "employees",
            ),
            products=organisation_data.get(
                "products",
                [],
            ),
            challenges=organisation_data.get(
                "challenges",
                [],
            ),
        )

        db.add(organisation)
        db.flush()

    # -----------------------------------------------------
    # Objectives
    # -----------------------------------------------------

    existing_objectives = {
        objective.name
        for objective in organisation.objectives
    }

    for objective_name in organisation_data.get(
        "strategic_objectives",
        [],
    ):

        if objective_name not in existing_objectives:

            objective = Objective(
                organisation_id=organisation.id,
                name=objective_name,
            )

            db.add(objective)

    db.flush()

    return organisation


# ---------------------------------------------------------
# Research Sources
# ---------------------------------------------------------

def get_or_create_research_source(
    db: Session,
    evidence_data: dict,
) -> ResearchSource:

    source_name = evidence_data["source_name"]
    source_type = evidence_data["source_type"]
    url = evidence_data["url"]

    source = (
        db.query(ResearchSource)
        .filter(
            ResearchSource.source_name == source_name,
            ResearchSource.url == url,
        )
        .first()
    )

    if source is None:

        source = ResearchSource(
            source_name=source_name,
            source_type=source_type,
            url=url,
            publication_date=parse_date(
                evidence_data.get(
                    "publication_date"
                )
            ),
        )

        db.add(source)
        db.flush()

    return source


# ---------------------------------------------------------
# Evidence
# ---------------------------------------------------------


def seed_evidence(
    db: Session,
    evidence_records: list[dict],
):
    created = 0
    updated = 0

    for item in evidence_records:
        external_id = item["id"]

        # The current seed file contains FinTech research.
        # Future industry packs should specify their industries explicitly.
        industries = item.get("industries") or ["FinTech"]

        existing = (
            db.query(Evidence)
            .filter(Evidence.external_id == external_id)
            .first()
        )

        if existing:
            # Update industry metadata for records already in the database.
            existing.industries = industries
            updated += 1
            continue

        research_source = get_or_create_research_source(db, item)

        evidence = Evidence(
            external_id=external_id,
            domain=item["domain"],
            title=item["title"],
            research_source_id=research_source.id,
            publication_date=parse_date(
                item.get("publication_date")
            ),
            url=item["url"],
            claim=item["claim"],
            evidence_text=item["evidence"],
            strategic_implication=item["strategic_implication"],
            confidence=item.get("confidence", 1),
            relevance=item.get("relevance", 1),
            tags=item.get("tags", []),
            industries=industries,
        )

        db.add(evidence)
        created += 1

    db.flush()

    return created, updated


# ---------------------------------------------------------
# Transformation Dimensions
# ---------------------------------------------------------

def seed_transformation_dimensions(
    db: Session,
    dimensions: list[dict],
):
    created = 0
    skipped = 0

    for item in dimensions:

        external_id = item["id"]

        existing = (
            db.query(
                TransformationDimension
            )
            .filter(
                TransformationDimension.external_id
                == external_id
            )
            .first()
        )

        if existing:
            skipped += 1
            continue

        dimension = TransformationDimension(
            external_id=external_id,
            name=item["name"],
            description=item.get(
                "description"
            ),
            evidence_domains=item.get(
                "evidence_domains",
                [],
            ),
            candidate_initiatives=item.get(
                "candidate_initiatives",
                [],
            ),
        )

        db.add(dimension)
        created += 1

    db.flush()

    return created, skipped


# ---------------------------------------------------------
# Main seed function
# ---------------------------------------------------------

def seed_database(db: Session):

    print("=" * 60)
    print("Strategillent Database Seeder")
    print("=" * 60)

    print("\nLoading seed files...")

    organisation_data = load_json(
        ORGANISATION_FILE
    )

    evidence_records = load_json(
        EVIDENCE_FILE
    )

    transformation_dimensions = load_json(
        TRANSFORMATION_FILE
    )

    print(
        f"Organisation file: "
        f"{ORGANISATION_FILE}"
    )

    print(
        f"Evidence records: "
        f"{len(evidence_records)}"
    )

    print(
        f"Transformation dimensions: "
        f"{len(transformation_dimensions)}"
    )

    # -----------------------------------------------------
    # Organisation
    # -----------------------------------------------------

    organisation = seed_organisation(
        db,
        organisation_data,
    )

    print(
        f"\nOrganisation: "
        f"{organisation.name}"
    )

    # -----------------------------------------------------
    # Evidence
    # -----------------------------------------------------

    evidence_created,  evidence_updated = (
        seed_evidence(
            db,
            evidence_records,
        )
    )

    print(
        f"Evidence created: "
        f"{evidence_created}"
    )

    print(
        f"Evidence skipped: "
        f"{ evidence_updated}"
    )

    # -----------------------------------------------------
    # Transformation dimensions
    # -----------------------------------------------------

    dimensions_created, dimensions_skipped = (
        seed_transformation_dimensions(
            db,
            transformation_dimensions,
        )
    )

    print(
        f"Transformation dimensions created: "
        f"{dimensions_created}"
    )

    print(
        f"Transformation dimensions skipped: "
        f"{dimensions_skipped}"
    )

    # -----------------------------------------------------
    # Commit everything
    # -----------------------------------------------------

    db.commit()

    print("\nDatabase seed completed successfully.")
    print("=" * 60)