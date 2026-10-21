

"""Industry-aware semantic retrieval over the local Qdrant index."""
from typing import Any

from qdrant_client import models

from app.retrieval.vector_store import (
    COLLECTION_NAME,
    embed_query,
    ensure_collection,
    get_vector_client,
)
from app.services.industry_resolution import (
    industry_filter_names,
    resolve_industry,
)


def _industry_aliases(industry: str) -> list[str]:
    """Compatibility helper retained for existing callers/tests."""
    return industry_filter_names(industry)


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
    must = []
    should = []
    must_not = []

    if industry is not None:
        resolved = resolve_industry(industry, allow_unknown=True)
        assert resolved is not None
        # Canonical ID is the preferred filter; display-name matching supports
        # records indexed before this patch.
        should.extend([
            models.FieldCondition(
                key="industry_ids",
                match=models.MatchAny(any=[resolved.id]),
            ),
            models.FieldCondition(
                key="industries",
                match=models.MatchAny(any=industry_filter_names(industry)),
            ),
            models.FieldCondition(
                key="industry",
                match=models.MatchValue(value=resolved.canonical_name),
            ),
        ])

    if domain:
        must.append(models.FieldCondition(
            key="domain",
            match=models.MatchValue(value=domain.strip().upper()),
        ))

    if not include_unverified:
        # Exclude both explicitly unverified evidence and user-uploaded content
        # whose payload marks it as unverified.
        must_not.extend([
            models.FieldCondition(
                key="tags",
                match=models.MatchAny(any=["unverified"]),
            ),
            models.FieldCondition(
                key="verified",
                match=models.MatchValue(value=False),
            ),
        ])

    query_filter = None
    if must or should or must_not:
        query_filter = models.Filter(
            must=must or None,
            should=should or None,
            must_not=must_not or None,
        )

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
            "industry_id": payload.get("industry_id"),
            "industry_ids": payload.get("industry_ids", []),
            "industries": payload.get("industries", []),
            "domain": payload.get("domain", ""),
            "title": payload.get("title", payload.get("source_name", "")),
            "chunk_index": payload.get("chunk_index"),
            "tags": payload.get("tags", []),
            "verified": payload.get("verified", False),
        })
    return results
