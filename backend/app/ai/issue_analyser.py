"""Evidence-grounded strategic issue analysis and legacy-model mapping."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.ai.context_builder import build_intelligence_context
from app.ai.evidence_validator import validate_evidence_references
from app.ai.llm import generate_json, get_model_name
from app.ai.prompts import build_issue_analysis_prompt
from app.ai.structured_output import validate_model_output
from app.core.config import settings
from app.schemas.intelligence_output import IssueAnalysis

logger = logging.getLogger(__name__)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Read a field from a dictionary or an object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _evidence_id(record: Any) -> str | None:
    """Return a stable external evidence ID, falling back to the DB ID."""
    value = _get(record, "external_id") or _get(record, "id")
    return str(value) if value is not None else None


def _render_evidence(records: list[Any]) -> str:
    """Serialize the supplied evidence without inventing missing fields."""
    rendered = []

    for record in records:
        evidence_id = _evidence_id(record)
        if not evidence_id:
            continue

        rendered.append(
            {
                "evidence_id": evidence_id,
                "title": _get(record, "title", ""),
                "claim": _get(record, "claim", ""),
                "evidence_text": _get(record, "evidence_text", ""),
                "strategic_implication": _get(
                    record, "strategic_implication", ""
                ),
                "source_url": _get(record, "url", ""),
                "confidence": _get(record, "confidence"),
                "relevance": _get(record, "relevance"),
            }
        )

    return json.dumps(rendered, ensure_ascii=False, default=str)


def _to_legacy_issue_fields(
    analysis: dict[str, Any],
    dimension: Any,
    evidence_records: list[Any],
) -> dict[str, Any]:
    """Map the structured IssueAnalysis to the existing service contract."""
    dimension_name = str(
        _get(dimension, "name", "Transformation dimension")
    )

    findings = analysis.get("findings") or []
    hypotheses = analysis.get("root_cause_hypotheses") or []
    risks = analysis.get("risks") or []

    def item_text(item: Any, key: str) -> str:
        return str(_get(item, key, "") or "").strip()

    finding_lines = []
    for finding in findings:
        title = item_text(finding, "title") or "Finding"
        description = item_text(finding, "description")
        if description:
            finding_lines.append(f"{title}: {description}")

    summary = str(analysis.get("summary") or "").strip()
    description_parts = [summary, *finding_lines]
    description = "\n".join(part for part in description_parts if part)

    rationale_parts = []

    for hypothesis in hypotheses:
        statement = item_text(hypothesis, "hypothesis")
        if statement:
            status = item_text(hypothesis, "status") or "hypothesis"
            rationale_parts.append(
                f"Root-cause hypothesis ({status}): {statement}"
            )

    for risk in risks:
        title = item_text(risk, "title")
        risk_description = item_text(risk, "description")
        if title or risk_description:
            rationale_parts.append(
                f"Risk: {title}. {risk_description}".strip()
            )

    for missing in analysis.get("missing_information") or []:
        if str(missing).strip():
            rationale_parts.append(
                f"Missing information: {str(missing).strip()}"
            )

    if not rationale_parts:
        rationale_parts.append(
            "Root causes have not been established. Validate this "
            "assessment using internal organisational data."
        )

    # The existing StrategicIssue model expects an integer severity.
    # These are conservative mappings, not a claim of measured risk.
    severity = 2 if analysis.get("insufficient_evidence") else 3

    for risk in risks:
        impact = item_text(risk, "impact").casefold()
        if impact in {"high", "critical"}:
            severity = max(severity, 4)
        if impact == "critical":
            severity = 5

    severity = max(1, min(5, severity))

    return {
        "title": f"{dimension_name}: strategic assessment",
        "description": description or (
            f"Assess the strategic implications of {dimension_name}."
        ),
        "rationale": "\n".join(rationale_parts),
        "severity": severity,
        "urgency": severity,
        "evidence_ids": [
            evidence_id
            for record in evidence_records
            if (evidence_id := _evidence_id(record)) is not None
        ],
        "model_used": analysis.get("model_used", "structured-llm"),
        "status": (
            "insufficient_evidence"
            if analysis.get("insufficient_evidence")
            else analysis.get("status", "completed")
        ),
        # Keep the detailed AI output available for future API/schema work.
        "rich_analysis": analysis,
    }


def analyse_dimension(
    dimension: Any,
    evidence_records: list[Any],
    organisation: Any,
) -> dict[str, Any]:
    """
    Analyse one transformation dimension.

    The returned dictionary is compatible with the existing
    StrategicIssue persistence workflow.
    """
    dimension_name = _get(dimension, "name", str(dimension))

    if not evidence_records:
        return {
            "title": f"Insufficient evidence: {dimension_name}",
            "description": (
                "There is not enough research evidence to establish "
                "a strategic issue."
            ),
            "rationale": (
                "Investigate this dimension further before confirming "
                "a strategic issue."
            ),
            "severity": 1,
            "urgency": 1,
            "evidence_ids": [],
            "model_used": "deterministic",
            "status": "insufficient_evidence",
        }

    if settings.intelligence_use_llm:
        try:
            context = build_intelligence_context(
                organisation=organisation,
                evidence_records=evidence_records,
                question=f"Analyse transformation dimension: {dimension_name}",
                max_chars=settings.intelligence_max_context_chars,
                max_evidence_records=settings.intelligence_max_evidence_records,
            )

            dimension_payload = {
                "name": _get(dimension, "name", str(dimension)),
                "description": _get(dimension, "description", ""),
                "external_id": _get(dimension, "external_id"),
                "evidence_domains": _get(dimension, "evidence_domains", []),
            }

            prompt = build_issue_analysis_prompt(
                organisation_context=context.rendered_context,
                dimension_context=json.dumps(
                    dimension_payload,
                    ensure_ascii=False,
                    default=str,
                ),
                evidence_context=_render_evidence(evidence_records),
            )

            raw = generate_json(
                prompt,
                schema=IssueAnalysis.model_json_schema(),
            )

            validated = validate_model_output(
                json.dumps(raw, ensure_ascii=False, default=str),
                IssueAnalysis,
            )

            allowed_ids = {
                evidence_id
                for record in evidence_records
                if (evidence_id := _evidence_id(record)) is not None
            }

            validation = validate_evidence_references(
                validated.model_dump(),
                allowed_ids,
            )

            if not validation.valid:
                raise ValueError(
                    "Invalid evidence references: "
                    f"{getattr(validation, 'invalid_evidence_ids', [])}"
                )

            result = validated.model_dump()
            result["model_used"] = get_model_name()
            result["status"] = "completed"

            return _to_legacy_issue_fields(
                result,
                dimension,
                evidence_records,
            )

        except Exception:
            logger.exception(
                "Structured issue analysis failed for dimension %s",
                dimension_name,
            )

            if not settings.intelligence_allow_deterministic_fallback:
                raise

    # Deterministic fallback: no unsupported root-cause conclusions.
    numeric_values = []

    for record in evidence_records:
        for field in ("relevance", "confidence"):
            value = _get(record, field)
            try:
                if value is not None:
                    numeric_values.append(float(value))
            except (TypeError, ValueError):
                continue

    average = (
        sum(numeric_values) / len(numeric_values)
        if numeric_values
        else 3.0
    )

    severity = max(1, min(5, round(average)))

    goals = _get(organisation, "goals", []) or []
    challenges = _get(organisation, "challenges", []) or []

    evidence_ids = [
        evidence_id
        for record in evidence_records
        if (evidence_id := _evidence_id(record)) is not None
    ]

    return {
        "title": f"{dimension_name}: opportunity for improvement",
        "description": (
            f"Research evidence suggests that {dimension_name} merits "
            "assessment in the organisation's current context."
        ),
        "rationale": (
            f"Assessment dimension: {dimension_name}. "
            f"Organisation goals: {goals}. "
            f"Known challenges: {challenges}. "
            "Validate the finding with internal data before acting."
        ),
        "severity": severity,
        "urgency": severity,
        "evidence_ids": evidence_ids,
        "model_used": "deterministic",
        "status": "completed",
    }
