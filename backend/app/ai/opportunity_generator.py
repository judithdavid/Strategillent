"""Evidence-grounded opportunity generation and legacy-model mapping."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.ai.context_builder import build_intelligence_context
from app.ai.evidence_validator import validate_evidence_references
from app.ai.llm import generate_json, get_model_name
from app.ai.prompts import build_opportunity_prompt
from app.ai.structured_output import validate_model_output
from app.core.config import settings
from app.schemas.intelligence_output import Opportunity as OpportunityOutput

logger = logging.getLogger(__name__)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Read a field from a dictionary or an object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _id(record: Any) -> str | None:
    """Return the external evidence ID, falling back to the DB ID."""
    value = _get(record, "external_id") or _get(record, "id")
    return str(value) if value is not None else None


def _score(value: Any, default: float = 0.0) -> float:
    """Convert a score to a bounded numeric value."""
    try:
        return max(0.0, min(10.0, float(value)))
    except (TypeError, ValueError):
        return default


def _to_legacy_opportunity_fields(
    generated: dict[str, Any],
    issue: Any,
    evidence_records: list[Any],
) -> dict[str, Any]:
    """
    Map rich structured output to the current Opportunity service contract.

    The current schema does not provide all legacy numeric prioritisation
    fields. Provisional proxies are clearly marked here; priority ranking
    itself remains deterministic in prioritisation_service.py.
    """
    title = str(generated.get("title") or "").strip()
    if not title:
        raise ValueError("Generated opportunity is missing a title.")

    benefits = generated.get("expected_benefits") or []
    intervention = str(generated.get("proposed_intervention") or "").strip()
    problem = str(generated.get("problem_addressed") or "").strip()

    description_parts = [
        str(generated.get("description") or "").strip(),
        intervention,
    ]
    description = "\n".join(
        part for part in description_parts if part
    )

    rationale_parts = []
    if problem:
        rationale_parts.append(f"Problem addressed: {problem}")
    else:
        rationale_parts.append(
            f"Addresses strategic issue: {_get(issue, 'title', 'Unknown issue')}"
        )

    if benefits:
        rationale_parts.append(
            "Expected benefits: " + "; ".join(str(item) for item in benefits)
        )

    alternatives = generated.get("alternatives") or []
    if alternatives:
        rationale_parts.append(
            "Alternatives to compare: "
            + "; ".join(str(item) for item in alternatives)
        )

    risks = generated.get("risks") or []
    if risks:
        rationale_parts.append(
            "Risks to review: " + "; ".join(str(item) for item in risks)
        )

    rationale_parts.append(
        "Human review required: "
        f"{bool(generated.get('requires_human_review', True))}."
    )

    confidence = _score(
        float(generated.get("confidence") or 0.0) * 10.0,
        default=0.0,
    )

    # The rich schema doesn't supply numeric feasibility, urgency or alignment.
    # Keep these neutral until an explicit scoring rubric is implemented.
    return {
        "title": title,
        "description": description or title,
        "rationale": "\n".join(rationale_parts),
        "business_impact": confidence,
        "feasibility": 5.0,
        "urgency": 5.0,
        "strategic_alignment": 5.0,
        "evidence_confidence": confidence,
        "evidence_ids": [
            evidence_id
            for record in evidence_records
            if (evidence_id := _id(record)) is not None
        ],
        "model_used": generated.get("model_used", "structured-llm"),
        "status": generated.get("status", "completed"),
        "rich_opportunity": generated,
    }


def generate_opportunity(
    dimension: Any,
    issue: Any,
    organisation: Any,
    evidence_records: list[Any] | None = None,
) -> dict[str, Any]:
    """
    Generate an opportunity using only the supplied evidence records.

    The service should pass its industry- and dimension-filtered evidence
    explicitly through evidence_records.
    """
    evidence_records = list(evidence_records or [])

    if not evidence_records:
        return {
            "title": f"Investigate {_get(dimension, 'name', dimension)}",
            "description": (
                "Gather internal evidence before committing to a "
                "transformation initiative."
            ),
            "rationale": (
                "The current research set does not provide enough evidence "
                "to recommend a substantive intervention."
            ),
            "business_impact": 0.0,
            "feasibility": 1.0,
            "urgency": 1.0,
            "strategic_alignment": 1.0,
            "evidence_confidence": 0.0,
            "evidence_ids": [],
            "model_used": "deterministic",
            "status": "insufficient_evidence",
        }

    if settings.intelligence_use_llm:
        try:
            context = build_intelligence_context(
                organisation=organisation,
                evidence_records=evidence_records,
                question=(
                    "Generate an opportunity for strategic issue: "
                    f"{_get(issue, 'title', 'unspecified issue')}"
                ),
                max_chars=settings.intelligence_max_context_chars,
                max_evidence_records=settings.intelligence_max_evidence_records,
            )

            dimension_payload = {
                "name": _get(dimension, "name", str(dimension)),
                "description": _get(dimension, "description", ""),
            }

            issue_payload = {
                "title": _get(issue, "title", ""),
                "description": _get(issue, "description", ""),
                "rationale": _get(issue, "rationale", ""),
            }

            evidence_payload = [
                {
                    "evidence_id": _id(record),
                    "title": _get(record, "title", ""),
                    "claim": _get(record, "claim", ""),
                    "evidence_text": _get(record, "evidence_text", ""),
                    "strategic_implication": _get(
                        record, "strategic_implication", ""
                    ),
                    "url": _get(record, "url", ""),
                }
                for record in evidence_records
                if _id(record)
            ]

            prompt = build_opportunity_prompt(
                organisation_context=context.rendered_context,
                issue_context=json.dumps(
                    issue_payload,
                    ensure_ascii=False,
                    default=str,
                ),
                dimension_context=json.dumps(
                    dimension_payload,
                    ensure_ascii=False,
                    default=str,
                ),
                evidence_context=json.dumps(
                    evidence_payload,
                    ensure_ascii=False,
                    default=str,
                ),
            )

            raw = generate_json(
                prompt,
                schema=OpportunityOutput.model_json_schema(),
            )

            validated = validate_model_output(
                json.dumps(raw, ensure_ascii=False, default=str),
                OpportunityOutput,
            )

            allowed_ids = {
                evidence_id
                for record in evidence_records
                if (evidence_id := _id(record)) is not None
            }

            validation = validate_evidence_references(
                validated.model_dump(),
                allowed_ids,
            )

            if not validation.valid:
                raise ValueError(
                    "Opportunity contains invalid evidence references: "
                    f"{getattr(validation, 'invalid_evidence_ids', [])}"
                )

            result = validated.model_dump()
            result["model_used"] = get_model_name()
            result["status"] = "completed"

            return _to_legacy_opportunity_fields(
                result,
                issue,
                evidence_records,
            )

        except Exception:
            logger.exception(
                "Structured opportunity generation failed for issue %s",
                _get(issue, "title", "unknown"),
            )

            if not settings.intelligence_allow_deterministic_fallback:
                raise

    # Deterministic fallback: do not claim measured ROI or guaranteed outcomes.
    issue_title = _get(issue, "title", "the identified issue")
    dimension_name = _get(dimension, "name", str(dimension))
    goals = _get(organisation, "goals", []) or []

    evidence_ids = [
        evidence_id
        for record in evidence_records
        if (evidence_id := _id(record)) is not None
    ]

    return {
        "title": f"Assess {dimension_name} improvements",
        "description": (
            f"Run a focused assessment of {dimension_name}, identify "
            "potential root causes, and compare interventions before "
            "selecting an initiative."
        ),
        "rationale": (
            f"This opportunity addresses '{issue_title}' and should be "
            f"evaluated against the organisation's goals: {goals}. "
            f"It is based on {len(evidence_ids)} supplied evidence record(s); "
            "validate internal impact and feasibility before implementation."
        ),
        "business_impact": 5.0,
        "feasibility": 5.0,
        "urgency": 5.0,
        "strategic_alignment": 5.0,
        "evidence_confidence": 5.0,
        "evidence_ids": evidence_ids,
        "model_used": "deterministic",
        "status": "completed",
    }
