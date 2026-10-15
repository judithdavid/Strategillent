import json
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models import (
    Evidence,
    Objective,
    Organisation,
    ResearchSource,
    TransformationDimension,
)


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"

ORGANISATION_FILE = SEED_DIR / "organisation.json"
EVIDENCE_FILE = SEED_DIR / "evidence.json"
TRANSFORMATION_FILE = SEED_DIR / "transformation_dimensions.json"
EDTECH_EVIDENCE_FILE = SEED_DIR / "edtech_evidence.json"
HEALTHCARE_EVIDENCE_FILE = SEED_DIR / "healthcare_evidence.json"


# ---------------------------------------------------------------------
# JSON and date helpers
# ---------------------------------------------------------------------

def load_json(file_path: Path) -> Any:
    """Load a required JSON seed file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Required seed file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_optional_json(file_path: Path) -> list[dict]:
    """Load an optional industry evidence pack; return [] if it is absent."""
    if not file_path.exists():
        print(f"Optional seed file not found; skipping: {file_path}")
        return []

    with file_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"Expected a JSON list in seed file: {file_path}")

    return records


def parse_date(value: Any) -> date | None:
    """Parse YYYY-MM-DD or YYYY date strings."""
    if not value:
        return None

    value = str(value)
    try:
        return date.fromisoformat(value)
    except ValueError:
        if len(value) == 4 and value.isdigit():
            return date(int(value), 1, 1)
        return None


# ---------------------------------------------------------------------
# Organisation
# ---------------------------------------------------------------------

def seed_organisation(
    db: Session,
    organisation_data: dict,
) -> Organisation:

    company_name = organisation_data["company"]
    industry = organisation_data.get("industry")

    if not isinstance(industry, str) or not industry.strip():
        raise ValueError(
            f"Missing or invalid industry for organisation: {company_name}"
        )

    organisation = (
        db.query(Organisation)
        .filter(Organisation.name == company_name)
        .first()
    )

    profile_fields = {
        "fictional": organisation_data.get("fictional", True),
        "industry": industry.strip(),
        "business_model": organisation_data.get("business_model", []),
        "markets": organisation_data.get("markets", []),
        "customers": organisation_data.get("customers"),
        "employees": organisation_data.get("employees"),
        "products": organisation_data.get("products", []),
        "challenges": organisation_data.get("challenges", []),
        "goals": organisation_data.get(
            "goals",
            organisation_data.get("strategic_objectives", []),
        ),
        "processes": organisation_data.get("processes", []),
        "technology": organisation_data.get("technology", []),
        "constraints": organisation_data.get("constraints", []),
    }

    if organisation is None:
        organisation = Organisation(
            name=company_name,
            **profile_fields,
        )
        db.add(organisation)
        db.flush()
    else:
        for field, value in profile_fields.items():
            supplied = field in organisation_data

            if field == "goals":
                supplied = (
                    supplied
                    or "strategic_objectives" in organisation_data
                )

            if supplied and hasattr(organisation, field):
                setattr(organisation, field, value)

    objective_names = organisation_data.get("strategic_objectives", [])

    existing_objectives = {
        objective.name for objective in organisation.objectives
    }

    for objective_name in objective_names:
        if objective_name not in existing_objectives:
            db.add(
                Objective(
                    organisation_id=organisation.id,
                    name=objective_name,
                )
            )

    db.flush()
    return organisation


# ---------------------------------------------------------------------
# Research sources
# ---------------------------------------------------------------------

def get_or_create_research_source(
    db: Session, evidence_data: dict
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
            publication_date=parse_date(evidence_data.get("publication_date")),
        )
        db.add(source)
        db.flush()

    return source


# ---------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------

def seed_evidence(
    db: Session, evidence_records: list[dict]
) -> tuple[int, int]:
    created = 0
    updated = 0

    for item in evidence_records:
        external_id = item["id"]
        industries = item.get("industries") or []

        existing = (
            db.query(Evidence)
            .filter(Evidence.external_id == external_id)
            .first()
        )

        if existing is not None:
            # Update industry applicability and any supplied evidence metadata.
            existing.industries = industries
            existing.domain = item["domain"]
            existing.title = item["title"]
            existing.publication_date = parse_date(item.get("publication_date"))
            existing.url = item["url"]
            existing.claim = item["claim"]
            existing.evidence_text = item["evidence"]
            existing.strategic_implication = item["strategic_implication"]
            existing.confidence = item.get("confidence", 1)
            existing.relevance = item.get("relevance", 1)
            existing.tags = item.get("tags", [])
            updated += 1
            continue

        research_source = get_or_create_research_source(db, item)
        evidence = Evidence(
            external_id=external_id,
            domain=item["domain"],
            title=item["title"],
            research_source_id=research_source.id,
            publication_date=parse_date(item.get("publication_date")),
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


# ---------------------------------------------------------------------
# Transformation dimensions
# ---------------------------------------------------------------------

def seed_transformation_dimensions(
    db: Session, dimensions: list[dict]
) -> tuple[int, int]:
    created = 0
    updated = 0

    for item in dimensions:
        external_id = item["id"]
        industries = item.get("industries") or ["FinTech"]

        existing = (
            db.query(TransformationDimension)
            .filter(TransformationDimension.external_id == external_id)
            .first()
        )

        if existing is not None:
            # Only overwrite fields present in the JSON. This preserves rich
            # metadata when a compact seed entry only declares id/name/industries.
            if "name" in item:
                existing.name = item["name"]
            if "description" in item:
                existing.description = item["description"]
            if "evidence_domains" in item:
                existing.evidence_domains = item["evidence_domains"]
            if "candidate_initiatives" in item:
                existing.candidate_initiatives = item["candidate_initiatives"]
            existing.industries = industries
            updated += 1
            continue

        dimension = TransformationDimension(
            external_id=external_id,
            name=item["name"],
            description=item.get("description"),
            evidence_domains=item.get("evidence_domains", []),
            candidate_initiatives=item.get("candidate_initiatives", []),
            industries=industries,
        )
        db.add(dimension)
        created += 1

    db.flush()
    return created, updated


# ---------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------

def seed_database(db: Session) -> None:
    """Seed organisation, industry evidence packs, and transformation dimensions."""
    print("=" * 60)
    print("Strategillent Database Seeder")
    print("=" * 60)
    print("\nLoading seed files...")

    organisation_data = load_json(ORGANISATION_FILE)
    fintech_records = load_json(EVIDENCE_FILE)
    edtech_records = load_optional_json(EDTECH_EVIDENCE_FILE)
    healthcare_records = load_optional_json(HEALTHCARE_EVIDENCE_FILE)
    transformation_dimensions = load_json(TRANSFORMATION_FILE)

    # Apply pack-level defaults without incorrectly tagging one industry's
    # evidence as belonging to another industry.
    for item in fintech_records:
        item.setdefault("industries", ["FinTech"])
    for item in edtech_records:
        item.setdefault("industries", ["EdTech", "Education"])
    for item in healthcare_records:
        item.setdefault("industries", ["Healthcare"])

    all_evidence_records = fintech_records + edtech_records + healthcare_records

    print(f"Organisation file: {ORGANISATION_FILE}")
    print(f"FinTech evidence records: {len(fintech_records)}")
    print(f"EdTech evidence records: {len(edtech_records)}")
    print(f"Healthcare evidence records: {len(healthcare_records)}")
    print(f"Total evidence records: {len(all_evidence_records)}")
    print(f"Transformation dimensions: {len(transformation_dimensions)}")

    try:
        organisation = seed_organisation(db, organisation_data)
        print(f"\nOrganisation: {organisation.name}")

        evidence_created, evidence_updated = seed_evidence(
            db, all_evidence_records
        )
        print(f"Evidence created: {evidence_created}")
        print(f"Evidence updated: {evidence_updated}")

        dimensions_created, dimensions_updated = seed_transformation_dimensions(
            db, transformation_dimensions
        )
        print(f"Transformation dimensions created: {dimensions_created}")
        print(f"Transformation dimensions updated: {dimensions_updated}")

        db.commit()
        print("\nDatabase seed completed successfully.")
        print("=" * 60)
    except Exception:
        db.rollback()
        raise
