from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable


DEFAULT_MAX_CHARS = 18_000


def _get(obj: Any, name: str, default: Any = None) -> Any:
    """Read a field from either a dictionary or an ORM/Pydantic object."""
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return "; ".join(_as_text(item) for item in value if item is not None)
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(value)


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 15)].rstrip() + "\n[TRUNCATED]"


def _profile_section(organisation: Any) -> dict[str, Any]:
    fields = (
        "id",
        "name",
        "industry",
        "business_model",
        "description",
        "goals",
        "challenges",
        "processes",
        "technology",
        "constraints",
        "resources",
    )
    return {
        field: _get(organisation, field)
        for field in fields
        if _get(organisation, field) not in (None, "", [], {})
    }


def _evidence_record(record: Any) -> dict[str, Any]:
    """Keep evidence provenance and relevant retrieval metadata."""
    external_id = _get(record, "external_id")
    record_id = _get(record, "evidence_id", _get(record, "id"))

    evidence_id = external_id if external_id not in (None, "") else record_id
    source = _get(record, "source")
    source_name = _get(record, "source_name")

    if not source_name and source is not None:
        source_name = _get(source, "source_name", _get(source, "name"))

    return {
        "evidence_id": str(evidence_id) if evidence_id is not None else None,
        "title": _get(record, "title"),
        "domain": _get(record, "domain"),
        "industry": _get(record, "industry"),
        "claim": _get(record, "claim"),
        "evidence_text": _get(record, "evidence_text"),
        "strategic_implication": _get(record, "strategic_implication"),
        "source_name": source_name,
        "source_url": _get(record, "url", _get(source, "url")),
        "publication_date": _as_text(_get(record, "publication_date")) or None,
        "verified": _get(record, "verified"),
        "relevance": _get(record, "relevance"),
        "confidence": _get(record, "confidence"),
    }


@dataclass(frozen=True)
class IntelligenceContext:
    organisation_id: str | None
    organisation_context: dict[str, Any]
    evidence: list[dict[str, Any]]
    previous_analysis: Any
    question: str | None
    rendered_context: str
    allowed_evidence_ids: frozenset[str]
    truncated: bool


def build_intelligence_context(
    organisation: Any,
    evidence_records: Iterable[Any] | None = None,
    previous_analysis: Any = None,
    question: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    max_evidence_records: int = 12,
) -> IntelligenceContext:
    """
    Build bounded context for an LLM request.

    The returned allowed_evidence_ids set is the authoritative set against
    which generated citations should be validated.

    Note: character limits are a simple safety bound, not an exact token limit.
    """
    if max_chars < 1000:
        raise ValueError("max_chars must be at least 1000")
    if max_evidence_records < 0:
        raise ValueError("max_evidence_records cannot be negative")

    profile = _profile_section(organisation)
    organisation_id = _get(organisation, "id")
    evidence: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for record in list(evidence_records or [])[:max_evidence_records]:
        item = _evidence_record(record)
        evidence_id = item.get("evidence_id")

        # Records without IDs cannot safely be cited by generated output.
        if not evidence_id:
            continue

        if evidence_id in seen_ids:
            continue

        seen_ids.add(evidence_id)
        evidence.append(item)

    payload = {
        "organisation_context": profile,
        "external_evidence": evidence,
        "previous_analysis": previous_analysis,
        "user_question": question,
        "instructions": {
            "separate_company_context_from_external_evidence": True,
            "treat_previous_ai_analysis_as_unverified": True,
            "cite_only_ids_in_external_evidence": sorted(seen_ids),
            "state_when_evidence_is_insufficient": True,
        },
    }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    truncated = len(rendered) > max_chars

    if truncated:
        # Preserve the organisation profile and question first, then allocate
        # remaining space to evidence and previous analysis.
        compact_payload = {
            "organisation_context": profile,
            "user_question": question,
            "external_evidence": [],
            "previous_analysis": None,
            "instructions": payload["instructions"],
        }

        for item in evidence:
            candidate = dict(compact_payload)
            candidate["external_evidence"] = [
                *compact_payload["external_evidence"],
                item,
            ]
            candidate_text = json.dumps(
                candidate, ensure_ascii=False, indent=2, default=str
            )
            if len(candidate_text) > max_chars:
                break
            compact_payload = candidate

        rendered = json.dumps(
            compact_payload, ensure_ascii=False, indent=2, default=str
        )

        if len(rendered) > max_chars:
            rendered = _clip(rendered, max_chars)

        included = {
            str(item["evidence_id"])
            for item in compact_payload["external_evidence"]
            if item.get("evidence_id")
        }
        evidence = [
            item for item in evidence if item["evidence_id"] in included
        ]
        seen_ids = included

    return IntelligenceContext(
        organisation_id=str(organisation_id) if organisation_id is not None else None,
        organisation_context=profile,
        evidence=evidence,
        previous_analysis=previous_analysis,
        question=question,
        rendered_context=rendered,
        allowed_evidence_ids=frozenset(seen_ids),
        truncated=truncated,
    )