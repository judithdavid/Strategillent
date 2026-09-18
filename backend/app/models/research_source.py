from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResearchSource(Base):
    __tablename__ = "research_sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    publication_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True,
    )

    evidence = relationship(
        "Evidence",
        back_populates="research_source",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ResearchSource("
            f"id={self.id}, "
            f"source_name='{self.source_name}')>"
        )