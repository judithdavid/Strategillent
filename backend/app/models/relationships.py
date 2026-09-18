from sqlalchemy import Column, ForeignKey, Table

from app.core.database import Base


# ---------------------------------------------------------
# Strategic Issue <-> Evidence
# ---------------------------------------------------------

issue_evidence = Table(
    "issue_evidence",
    Base.metadata,
    Column(
        "issue_id",
        ForeignKey("strategic_issues.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "evidence_id",
        ForeignKey("evidence.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# ---------------------------------------------------------
# Opportunity <-> Evidence
# ---------------------------------------------------------

opportunity_evidence = Table(
    "opportunity_evidence",
    Base.metadata,
    Column(
        "opportunity_id",
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "evidence_id",
        ForeignKey("evidence.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)