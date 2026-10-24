
from __future__ import annotations

import json
import logging
from typing import Any

from app.ai.context_builder import build_intelligence_context
from app.ai.evidence_validator import validate_evidence_references
from app.ai.llm import generate_text, get_model_name
from app.ai.prompts import build_question_prompt
from app.core.config import settings

logger = logging.getLogger(__name__)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _id(record: Any) -> str | None:
    value = _get(record, "external_id") or _get(record, "id")
    return str(value) if value is not None else None


def build_organisation_context(organisation: Any) -> str:
    """Return a bounded representation of the organisation profile."""
    context = build_intelligence_context(
        organisation=organisation,
        evidence_records=[],
        max_chars=settings.intelligence_max_context_chars,
        max_evidence_records=1,
    )
    return context.rendered_context


def build_evidence_context(evidence_records: list[Any]) -> str:
    """Render evidence with stable IDs and provenance."""
    items = []

    for record in evidence_records[
        :settings.intelligence_max_evidence_records
    ]:
        evidence_id = _id(record)
        if not evidence_id:
            continue

        items.append({
            "evidence_id": evidence_id,
            "title": _get(record, "title", ""),
            "claim": _get(record, "claim", ""),
            "evidence_text": _get(record, "evidence_text", ""),
            "strategic_implication": _get(
                record, "strategic_implication", ""
            ),
            "url": _get(record, "url", ""),
            "publication_date": str(
                _get(record, "publication_date", "") or ""
            ),
            "confidence": _get(record, "confidence"),
            "relevance": _get(record, "relevance"),
        })

    return json.dumps(items, ensure_ascii=False, default=str)


def _extract_citations(
    answer: str,
    evidence_records: list[Any],
) -> list[dict[str, Any]]:
    """Return only references explicitly cited and present in the evidence set."""
    allowed = {
        _id(record): record
        for record in evidence_records
        if _id(record)
    }

    import re

    cited_ids = re.findall(
        r"\[EVIDENCE_ID:\s*([^\]]+)\]",
        answer,
        flags=re.IGNORECASE,
    )

    citations = []
    seen = set()

    for raw_id in cited_ids:
        evidence_id = raw_id.strip()
        if evidence_id in seen or evidence_id not in allowed:
            continue

        record = allowed[evidence_id]
        citations.append({
            "evidence_id": evidence_id,
            "title": _get(record, "title", ""),
            "url": _get(record, "url", ""),
            "claim": _get(record, "claim", ""),
        })
        seen.add(evidence_id)

    return citations


def generate_answer(
    organisation: Any,
    evidence_records: list[Any],
    question: str,
) -> dict[str, Any]:
    """
    Answer a question using supplied organisation context and research.

    Citation ID validation checks reference integrity, not semantic
    entailment. Factual claims still need a grounding evaluation.
    """
    if not question or not question.strip():
        raise ValueError("A non-empty question is required.")

    context = build_intelligence_context(
        organisation=organisation,
        evidence_records=evidence_records,
        question=question,
        max_chars=settings.intelligence_max_context_chars,
        max_evidence_records=settings.intelligence_max_evidence_records,
    )

    organisation_context = build_organisation_context(organisation)
    evidence_context = build_evidence_context(evidence_records)

    prompt = build_question_prompt(
        organisation_context=organisation_context,
        evidence_context=evidence_context,
        question=question.strip(),
    )

    warnings: list[str] = []

    if not evidence_records:
        warnings.append(
            "No external evidence was supplied; external factual claims "
            "cannot be substantiated."
        )

    try:
        if not settings.intelligence_use_llm:
            raise RuntimeError("LLM generation is disabled.")

        answer = generate_text(prompt)

    except Exception:
        logger.exception("LLM answer generation failed")

        if not settings.intelligence_allow_deterministic_fallback:
            raise

        answer = (
            "I cannot generate a reliable evidence-grounded answer right "
            "now because the language model is unavailable. Please retry "
            "after checking the LLM service. No substantive conclusion "
            "has been inferred from unavailable model output."
        )
        warnings.append("LLM unavailable; returned a safe fallback.")
        model_used = "fallback"
    else:
        model_used = get_model_name()

    answer = answer[:settings.intelligence_max_answer_chars].strip()

    allowed_ids = {
        _id(record) for record in evidence_records if _id(record)
    }
    validation = validate_evidence_references(
        {"answer": answer},
        allowed_ids,
    )

    # Unknown citation IDs are not silently accepted.
    invalid_ids = getattr(validation, "invalid_ids", [])
    if not validation.valid:
        warnings.append(
            "The generated answer contained unrecognised evidence "
            "references. Review the answer before relying on it."
        )
        logger.warning(
            "Invalid evidence references in answer: %s",
            invalid_ids,
        )

    citations = _extract_citations(answer, evidence_records)

    lower_answer = answer.lower()
    explicit_uncertainty = any(
        phrase in lower_answer
        for phrase in (
            "insufficient evidence",
            "cannot determine",
            "not enough information",
            "uncertain",
            "cannot verify",
        )
    )

    if not evidence_records or explicit_uncertainty or not validation.valid:
        uncertainty = "high"
    elif citations:
        uncertainty = "medium"
    else:
        uncertainty = "high"
        warnings.append(
            "The answer has no recognised evidence citations. "
            "Treat its external factual claims as unverified."
        )

    return {
        "answer": answer,
        "citations": citations,
        "evidence_ids": [item["evidence_id"] for item in citations],
        "uncertainty": uncertainty,
        "limitations": warnings,
        "model_used": model_used,
        "prompt_version": "2026-10-01",
    }
