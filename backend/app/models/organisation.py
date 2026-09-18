from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Organisation(Base):
    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    fictional: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    business_model: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    markets: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    customers: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    employees: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    products: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    challenges: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    objectives = relationship(
        "Objective",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    strategic_issues = relationship(
        "StrategicIssue",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    opportunities = relationship(
        "Opportunity",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    initiatives = relationship(
        "Initiative",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organisation(id={self.id}, name='{self.name}')>"