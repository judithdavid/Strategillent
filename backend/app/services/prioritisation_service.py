# from sqlalchemy.orm import Session

# from app.models import Opportunity


# def calculate_priority_score(opportunity: Opportunity) -> float:
#     """
#     Calculate deterministic opportunity priority.

#     Score =
#         0.35 * Business Impact
#         + 0.20 * Feasibility
#         + 0.20 * Urgency
#         + 0.15 * Strategic Alignment
#         + 0.10 * Evidence Confidence
#     """

#     score = (
#         0.35 * opportunity.business_impact
#         + 0.20 * opportunity.feasibility
#         + 0.20 * opportunity.urgency
#         + 0.15 * opportunity.strategic_alignment
#         + 0.10 * opportunity.evidence_confidence
#     )

#     return round(score, 2)


# def calculate_and_rank_opportunities(
#     db: Session,
#     opportunities: list[Opportunity],
# ):
#     for opportunity in opportunities:
#         opportunity.priority_score = calculate_priority_score(
#             opportunity
#         )

#     ranked = sorted(
#         opportunities,
#         key=lambda item: item.priority_score or 0,
#         reverse=True,
#     )

#     for rank, opportunity in enumerate(ranked, start=1):
#         opportunity.priority_rank = rank

#     db.commit()

#     return ranked


from sqlalchemy.orm import Session

from app.models import Opportunity


def calculate_priority_score(opportunity: Opportunity) -> float:
    """
    Calculate deterministic opportunity priority.

    Score =
        0.35 * Business Impact
        + 0.20 * Feasibility
        + 0.20 * Urgency
        + 0.15 * Strategic Alignment
        + 0.10 * Evidence Confidence
    """
    score = (
        0.35 * opportunity.business_impact
        + 0.20 * opportunity.feasibility
        + 0.20 * opportunity.urgency
        + 0.15 * opportunity.strategic_alignment
        + 0.10 * opportunity.evidence_confidence
    )

    return round(score, 2)


def calculate_and_rank_opportunities(
    db: Session,
    opportunities: list[Opportunity],
):
    for opportunity in opportunities:
        opportunity.priority_score = calculate_priority_score(opportunity)

    ranked = sorted(
        opportunities,
        key=lambda item: item.priority_score or 0,
        reverse=True,
    )

    for rank, opportunity in enumerate(ranked, start=1):
        opportunity.priority_rank = rank

    # Do not commit here. The intelligence pipeline owns the transaction.
    return ranked
