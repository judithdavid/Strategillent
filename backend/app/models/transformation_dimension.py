from sqlalchemy import Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TransformationDimension(Base):
    __tablename__ = "transformation_dimensions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    external_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evidence_domains: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    candidate_initiatives: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    industries: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    opportunities = relationship(
        "Opportunity",
        back_populates="transformation_dimension",
    )

    def __repr__(self) -> str:
        return (
            f"<TransformationDimension("
            f"id={self.id}, "
            f"external_id='{self.external_id}', "
            f"name='{self.name}')>"
        )