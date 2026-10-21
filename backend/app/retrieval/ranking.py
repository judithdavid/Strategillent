from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class RankingWeights:
    semantic: float = 0.60
    lexical: float = 0.20
    relevance: float = 0.10
    confidence: float = 0.10

    def __post_init__(self) -> None:
        values = (
            self.semantic,
            self.lexical,
            self.relevance,
            self.confidence,
        )
        if any(value < 0 for value in values):
            raise ValueError("Ranking weights cannot be negative.")
        if not math.isclose(sum(values), 1.0, abs_tol=1e-6):
            raise ValueError("Ranking weights must sum to 1.0.")


@dataclass(frozen=True)
class RankedEvidence:
    evidence: Any
    score: float
    components: dict[str, float]


DEFAULT_WEIGHTS = RankingWeights()


def _get(record: Any, name: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(name, default)
    return getattr(record, name, default)


def _normalise(value: Any, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return minimum

    if not math.isfinite(number):
        return minimum

    return max(minimum, min(maximum, number))


def _tokens(text: str | None) -> set[str]:
    if not text:
        return set()
    return {
        token
        for token in re.findall(r"\b[\w'-]+\b", text.casefold())
        if len(token) > 1
    }


def lexical_score(query: str, record: Any) -> float:
    """Compute a bounded token-overlap score between a query and a record."""
    query_tokens = _tokens(query)
    if not query_tokens:
        return 0.0

    fields = (
        _get(record, "title", ""),
        _get(record, "claim", ""),
        _get(record, "evidence_text", ""),
        _get(record, "strategic_implication", ""),
    )
    record_tokens = _tokens(" ".join(str(value or "") for value in fields))

    if not record_tokens:
        return 0.0

    # Query coverage is useful for short, intent-focused search queries.
    return len(query_tokens & record_tokens) / len(query_tokens)


def _quality_score(value: Any, default: float = 0.5) -> float:
    """
    Convert existing 1-5 quality values to [0, 1].

    Missing values use a neutral default rather than being treated as perfect.
    Values already between 0 and 1 are accepted as normalised scores.
    """
    if value is None:
        return default

    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    if not math.isfinite(number):
        return default

    if 0.0 <= number <= 1.0:
        return number

    if 1.0 <= number <= 5.0:
        return (number - 1.0) / 4.0

    return default


def rank_evidence(
    query: str,
    records: Iterable[Any],
    *,
    semantic_scores: dict[str, float] | None = None,
    weights: RankingWeights = DEFAULT_WEIGHTS,
    limit: int | None = None,
) -> list[RankedEvidence]:
    """
    Rank already-retrieved evidence.

    `semantic_scores` maps a record ID (external_id or id) to a normalised
    similarity score. This function does not perform vector search or metadata
    filtering; those remain the responsibility of the retrieval service.
    """
    if limit is not None and limit < 0:
        raise ValueError("limit cannot be negative.")

    semantic_scores = semantic_scores or {}
    ranked: list[RankedEvidence] = []

    for record in records:
        record_id = _get(record, "external_id", _get(record, "id"))
        semantic = _normalise(semantic_scores.get(str(record_id), 0.0))
        lexical = lexical_score(query, record)
        relevance = _quality_score(_get(record, "relevance"))
        confidence = _quality_score(_get(record, "confidence"))

        components = {
            "semantic": semantic,
            "lexical": lexical,
            "relevance": relevance,
            "confidence": confidence,
        }
        score = (
            semantic * weights.semantic
            + lexical * weights.lexical
            + relevance * weights.relevance
            + confidence * weights.confidence
        )

        ranked.append(
            RankedEvidence(
                evidence=record,
                score=round(max(0.0, min(1.0, score)), 6),
                components=components,
            )
        )

    # Stable tie-breaking makes tests and benchmark comparisons reproducible.
    ranked.sort(
        key=lambda item: (
            -item.score,
            str(_get(item.evidence, "external_id", _get(item.evidence, "id", ""))),
        )
    )

    return ranked if limit is None else ranked[:limit]
