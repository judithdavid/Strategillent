"""Create opportunities from dimension metadata and attached research evidence."""
from statistics import mean


def generate_opportunity(dimension, issue, organisation) -> dict:
    candidates = list(getattr(dimension, "candidate_initiatives", None) or [])
    if not candidates:
        # Do not invent a specific initiative when the seed data has none.
        candidates = [f"Assess {dimension.name.lower()} opportunities"]

    evidence = list(getattr(issue, "evidence", None) or [])
    if not evidence:
        raise ValueError("Cannot generate an opportunity without linked evidence.")

    confidence = mean(float(getattr(item, "confidence", 1) or 1) for item in evidence)
    relevance = mean(float(getattr(item, "relevance", 1) or 1) for item in evidence)
    goals = getattr(organisation, "goals", None) or []
    challenges = getattr(organisation, "challenges", None) or []
    processes = getattr(organisation, "processes", None) or []
    technology = getattr(organisation, "technology", None) or []
    constraints = getattr(organisation, "constraints", None) or []

    context = []
    for label, values in (
        ("Goals", goals), ("Challenges", challenges), ("Processes", processes),
        ("Technology", technology), ("Constraints", constraints),
    ):
        if values:
            context.append(f"{label}: " + "; ".join(str(value) for value in values))

    # Candidate names come from the selected dimension's seed metadata; evidence
    # and profile determine whether the opportunity is eligible and its rationale.
    title = candidates[0]
    description = (
        f"Explore '{title}' as an opportunity within the '{dimension.name}' "
        f"transformation dimension for the {organisation.industry} organisation. "
        f"Dimension context: {dimension.description or dimension.name}"
    )
    rationale = (
        f"Derived from strategic issue '{issue.title}' and supported by evidence "
        f"{', '.join(item.external_id for item in evidence)}. "
        f"Average evidence relevance: {relevance:.1f}/5; confidence: {confidence:.1f}/5."
    )
    if context:
        rationale += " Organisation context considered: " + " | ".join(context)

    # Keep scoring bounded and reproducible; ranking remains deterministic.
    profile_text = " ".join(str(v) for v in [*goals, *challenges, *processes]).casefold()
    candidate_words = set(title.casefold().replace("/", " ").replace("-", " ").split())
    overlap = sum(1 for word in candidate_words if len(word) > 3 and word in profile_text)
    alignment = min(10.0, 5.0 + overlap)
    impact = min(10.0, max(1.0, (relevance + confidence) * 1.0))
    feasibility = 6.0 if not constraints else 5.0
    urgency = min(10.0, max(1.0, relevance + (1 if challenges else 0)))

    return {
        "title": title,
        "description": description,
        "rationale": rationale,
        "business_impact": impact,
        "feasibility": feasibility,
        "urgency": urgency,
        "strategic_alignment": alignment,
        "evidence_confidence": round(confidence, 2),
    }
