from sqlalchemy import (
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.relationships import opportunity_evidence


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
    )

    strategic_issue_id: Mapped[int] = mapped_column(
        ForeignKey("strategic_issues.id", ondelete="CASCADE"),
        nullable=False,
    )

    analysis_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
        nullable=True,
    )

    transformation_dimension_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "transformation_dimensions.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rationale: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    business_impact: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    feasibility: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    urgency: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    strategic_alignment: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    evidence_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    priority_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    priority_rank: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    model_used: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    analysis_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    organisation = relationship(
        "Organisation",
        back_populates="opportunities",
    )

    strategic_issue = relationship(
        "StrategicIssue",
        back_populates="opportunities",
    )

    analysis_run = relationship(
        "AnalysisRun",
    )

    transformation_dimension = relationship(
        "TransformationDimension",
        back_populates="opportunities",
    )

    evidence = relationship(
        "Evidence",
        secondary=opportunity_evidence,
        back_populates="opportunities",
    )

    initiatives = relationship(
        "Initiative",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Opportunity("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"priority_score={self.priority_score}"
            f")>"
        )