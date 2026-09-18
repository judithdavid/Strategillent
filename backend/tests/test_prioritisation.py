from types import SimpleNamespace

from app.services.prioritisation_service import calculate_priority_score


def test_priority_score_calculation():
    opportunity = SimpleNamespace(
        business_impact=10,
        feasibility=8,
        urgency=9,
        strategic_alignment=10,
        evidence_confidence=8,
    )

    score = calculate_priority_score(opportunity)

    expected = (
        0.35 * 10
        + 0.20 * 8
        + 0.20 * 9
        + 0.15 * 10
        + 0.10 * 8
    )

    assert score == round(expected, 2)


def test_priority_score_is_bounded():
    opportunity = SimpleNamespace(
        business_impact=10,
        feasibility=10,
        urgency=10,
        strategic_alignment=10,
        evidence_confidence=10,
    )

    score = calculate_priority_score(opportunity)

    assert score == 10.0