from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Initiative(Base):
    __tablename__ = "initiatives"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
    )

    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_outcome: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    success_metric: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    implementation_phase: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="proposed",
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
        back_populates="initiatives",
    )

    opportunity = relationship(
        "Opportunity",
        back_populates="initiatives",
    )

    def __repr__(self) -> str:
        return (
            f"<Initiative("
            f"id={self.id}, "
            f"name='{self.name}')>"
        )