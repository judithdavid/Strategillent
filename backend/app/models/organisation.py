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

    business_model: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    markets: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    customers: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    employees: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    products: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    challenges: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    goals: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    processes: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    technology: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    constraints: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Relationships

    objectives: Mapped[list["Objective"]] = relationship(
        "Objective",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    strategic_issues: Mapped[list["StrategicIssue"]] = relationship(
        "StrategicIssue",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    opportunities: Mapped[list["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    initiatives: Mapped[list["Initiative"]] = relationship(
        "Initiative",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Organisation(id={self.id}, name='{self.name}')>"
        )
