from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.relationships import issue_evidence


class StrategicIssue(Base):
    __tablename__ = "strategic_issues"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
    )

    analysis_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
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

    severity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    urgency: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
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
        back_populates="strategic_issues",
    )

    analysis_run = relationship(
        "AnalysisRun",
    )

    evidence = relationship(
        "Evidence",
        secondary=issue_evidence,
        back_populates="strategic_issues",
    )

    opportunities = relationship(
        "Opportunity",
        back_populates="strategic_issue",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<StrategicIssue("
            f"id={self.id}, "
            f"title='{self.title}'"
            f")>"
        )