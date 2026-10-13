from datetime import date

from sqlalchemy import (
    Integer,
    String,
    Text,
    Date,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.relationships import (
    issue_evidence,
    opportunity_evidence,
)


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Original ID from JSON, e.g. E001, E002, CX
    external_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    domain: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    research_source_id: Mapped[int] = mapped_column(
        ForeignKey("research_sources.id", ondelete="CASCADE"),
        nullable=False,
    )

    publication_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    claim: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    evidence_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    strategic_implication: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    relevance: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    tags: Mapped[list] = mapped_column(
    JSON,
    default=list,
    nullable=False,
    )

    industries: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    
    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    research_source = relationship(
        "ResearchSource",
        back_populates="evidence",
    )

    strategic_issues = relationship(
        "StrategicIssue",
        secondary=issue_evidence,
        back_populates="evidence",
    )

    opportunities = relationship(
        "Opportunity",
        secondary=opportunity_evidence,
        back_populates="evidence",
    )

    def __repr__(self) -> str:
        return (
            f"<Evidence("
            f"id={self.id}, "
            f"external_id='{self.external_id}', "
            f"title='{self.title}')>"
        )