"""Industry-aware semantic retrieval over the local Qdrant index."""
from typing import Any

from qdrant_client import models

from app.services.industry_selection import normalise_industry
from app.retrieval.vector_store import (
    COLLECTION_NAME,
    embed_query,
    ensure_collection,
    get_vector_client,
)


def _industry_aliases(industry: str) -> list[str]:
    normalized = normalise_industry(industry)
    aliases = {
        "fintech": ["FinTech", "Financial Services", "Financial Technology", "Banking"],
        "edtech": ["EdTech", "Education", "Educational Technology"],
        "healthcare": ["Healthcare", "HealthTech", "Health Services"],
    }
    if not normalized:
        raise ValueError("A valid industry is required for semantic retrieval.")
    return list(dict.fromkeys([*aliases.get(normalized, [industry.strip()]), "*"]))


def semantic_search(
    query: str,
    limit: int = 6,
    industry: str | None = None,
    domain: str | None = None,
    include_unverified: bool = True,
) -> list[dict[str, Any]]:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")
    if industry is not None and not industry.strip():
        raise ValueError("Industry cannot be empty.")

    client = ensure_collection()
    query_filter = None
    must = []
    must_not = []

    if industry is not None:
        must.append(models.FieldCondition(
            key="industries",
            match=models.MatchAny(any=_industry_aliases(industry)),
        ))
    if domain:
        must.append(models.FieldCondition(
            key="domain",
            match=models.MatchValue(value=domain.strip()),
        ))
    if not include_unverified:
        must_not.append(models.FieldCondition(
            key="tags",
            match=models.MatchAny(any=["unverified"]),
        ))
    if must or must_not:
        query_filter = models.Filter(must=must or None, must_not=must_not or None)

    vector = embed_query(query)
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    )
    results = []
    for point in response.points:
        payload = point.payload or {}
        results.append({
            "text": payload.get("text", ""),
            "score": float(point.score or 0.0),
            "record_type": payload.get("record_type"),
            "evidence_id": payload.get("evidence_id"),
            "external_id": payload.get("external_id"),
            "source_id": payload.get("source_id"),
            "source_name": payload.get("source_name", ""),
            "source_url": payload.get("source_url", ""),
            "industry": payload.get("industry", ""),
            "industries": payload.get("industries", []),
            "domain": payload.get("domain", ""),
            "title": payload.get("title", payload.get("source_name", "")),
            "chunk_index": payload.get("chunk_index"),
            "tags": payload.get("tags", []),
            "verified": payload.get("verified", False),
        })
    return results
