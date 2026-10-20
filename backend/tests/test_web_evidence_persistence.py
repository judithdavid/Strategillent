
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import Evidence, ResearchSource
from app.services import web_evidence_service as service


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def mock_search(monkeypatch):
    def fake_search(query, max_results=5):
        return [
            {
                "title": "Payment fraud report",
                "url": "https://example.com/fraud-report",
                "content": "The report describes payment fraud trends.",
                "published_date": "2026-08-15",
                "score": 0.9,
                "source_type": "web_search",
                "query": query,
            }
        ]

    monkeypatch.setattr(service, "search_web", fake_search)


def test_persists_web_evidence_and_source(db, mock_search):
    result = service.search_and_store_web_evidence(
        db, "payment fraud", "FinTech", "FRAUD"
    )

    evidence = db.query(Evidence).one()
    source = db.query(ResearchSource).one()

    assert result["created"] == 1
    assert result["updated"] == 0
    assert evidence.research_source_id == source.id
    assert evidence.industries == ["FinTech"]
    assert evidence.domain == "FRAUD"
    assert "unverified" in evidence.tags


def test_repeated_search_updates_existing_evidence(db, mock_search):
    first = service.search_and_store_web_evidence(
        db, "payment fraud", "FinTech", "FRAUD"
    )
    second = service.search_and_store_web_evidence(
        db, "payment fraud", "FinTech", "FRAUD"
    )

    assert first["created"] == 1
    assert second["created"] == 0
    assert second["updated"] == 1
    assert db.query(Evidence).count() == 1
    assert db.query(ResearchSource).count() == 1


def test_rejects_empty_industry(db, mock_search):
    with pytest.raises(ValueError):
        service.search_and_store_web_evidence(
            db, "payment fraud", " ", "FRAUD"
        )

    assert db.query(Evidence).count() == 0


def test_rejects_empty_domain(db, mock_search):
    with pytest.raises(ValueError):
        service.search_and_store_web_evidence(
            db, "payment fraud", "FinTech", " "
        )

    assert db.query(Evidence).count() == 0


def test_existing_url_does_not_automatically_add_another_industry(
    db, mock_search
):
    service.search_and_store_web_evidence(
        db, "payment fraud", "FinTech", "FRAUD"
    )

    service.search_and_store_web_evidence(
        db, "payment fraud", "Healthcare", "FRAUD"
    )

    evidence = db.query(Evidence).one()

    # This assertion documents the desired behaviour.
    # It will fail with the current implementation.
    assert evidence.industries == ["FinTech"]


def test_existing_url_does_not_overwrite_original_domain(
    db, mock_search
):
    service.search_and_store_web_evidence(
        db, "payment fraud", "FinTech", "FRAUD"
    )

    service.search_and_store_web_evidence(
        db, "payment fraud", "FinTech", "GOVERNANCE"
    )

    evidence = db.query(Evidence).one()

    # The same URL does not prove that the result supports
    # a different domain. Preserve the original classification.
    assert evidence.domain == "FRAUD"
