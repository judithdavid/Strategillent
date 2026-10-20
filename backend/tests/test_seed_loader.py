
import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import Evidence, ResearchSource, TransformationDimension
from app.seed import loader


@pytest.fixture
def seed_test_env(tmp_path, monkeypatch):
    """Use temporary seed files and an isolated in-memory database."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    db = TestSession()

    original_paths = {
        "ORGANISATION_FILE": loader.ORGANISATION_FILE,
        "EVIDENCE_FILE": loader.EVIDENCE_FILE,
        "TRANSFORMATION_FILE": loader.TRANSFORMATION_FILE,
    }

    try:
        # Copy the repository's real seed data into the temporary directory.
        for constant, original_path in original_paths.items():
            temporary_path = tmp_path / original_path.name
            temporary_path.write_text(
                original_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            monkeypatch.setattr(loader, constant, temporary_path)

        # Keep optional packs absent for these tests.
        monkeypatch.setattr(
            loader,
            "EDTECH_EVIDENCE_FILE",
            tmp_path / "missing_edtech.json",
        )
        monkeypatch.setattr(
            loader,
            "HEALTHCARE_EVIDENCE_FILE",
            tmp_path / "missing_healthcare.json",
        )

        yield db, tmp_path

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_seed_is_idempotent(seed_test_env):
    """Running the seed loader twice should not duplicate seeded records."""

    db, _ = seed_test_env

    loader.seed_database(db)

    first_evidence_count = db.query(Evidence).count()
    first_dimension_count = db.query(TransformationDimension).count()
    first_source_count = db.query(ResearchSource).count()

    loader.seed_database(db)

    assert db.query(Evidence).count() == first_evidence_count
    assert db.query(TransformationDimension).count() == first_dimension_count
    assert db.query(ResearchSource).count() == first_source_count


def test_compact_dimension_seed_preserves_existing_metadata(seed_test_env):
    """Omitted dimension metadata must not erase previously stored values."""

    db, tmp_path = seed_test_env

    loader.seed_database(db)

    dimension = db.query(TransformationDimension).first()
    assert dimension is not None

    dimension_id = dimension.external_id
    original_description = dimension.description
    original_domains = list(dimension.evidence_domains or [])
    original_initiatives = list(dimension.candidate_initiatives or [])

    assert original_description
    assert original_domains
    assert original_initiatives

    seed_path = loader.TRANSFORMATION_FILE
    seed_dimensions = json.loads(seed_path.read_text(encoding="utf-8"))

    compact_record = next(
        item for item in seed_dimensions if item["id"] == dimension_id
    )

    # Retain only fields that the compact seed explicitly supplies.
    compact_record = {
        "id": compact_record["id"],
        "name": compact_record["name"],
        "industries": compact_record.get("industries", ["FinTech"]),
    }

    seed_path.write_text(
        json.dumps([compact_record], indent=2),
        encoding="utf-8",
    )

    loader.seed_database(db)

    db.expire_all()
    updated = (
        db.query(TransformationDimension)
        .filter_by(external_id=dimension_id)
        .one()
    )

    assert updated.description == original_description
    assert updated.evidence_domains == original_domains
    assert updated.candidate_initiatives == original_initiatives


def test_optional_industry_seed_files_can_be_missing(seed_test_env):
    """Missing optional EdTech and Healthcare packs must not break seeding."""

    db, _ = seed_test_env

    loader.seed_database(db)

    assert db.query(Evidence).count() > 0
    assert db.query(TransformationDimension).count() > 0


def test_non_seeded_evidence_survives_seed_rerun(seed_test_env):
    """A seed rerun must not delete evidence absent from seed JSON files."""

    db, _ = seed_test_env

    loader.seed_database(db)

    source = ResearchSource(
        source_name="example.com",
        source_type="web_search",
        url="https://example.com/unique-web-evidence",
    )
    db.add(source)
    db.flush()

    web_evidence = Evidence(
        external_id="WEB-TEST-PRESERVATION-001",
        domain="FRAUD",
        title="Persisted web evidence",
        research_source_id=source.id,
        url="https://example.com/unique-web-evidence",
        claim="A test claim from a web research result.",
        evidence_text="Evidence content used to verify persistence.",
        strategic_implication="Evaluate relevance before recommending action.",
        confidence=1,
        relevance=1,
        tags=["web_search", "unverified"],
        industries=["FinTech"],
    )
    db.add(web_evidence)
    db.commit()

    loader.seed_database(db)

    db.expire_all()
    persisted = (
        db.query(Evidence)
        .filter_by(external_id="WEB-TEST-PRESERVATION-001")
        .one_or_none()
    )

    assert persisted is not None
    assert persisted.title == "Persisted web evidence"
    assert persisted.industries == ["FinTech"]
    assert "unverified" in persisted.tags
