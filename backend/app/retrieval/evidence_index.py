
"""Index SQL Evidence rows into Qdrant with canonical industry metadata.

Adapt the SQLAlchemy import/model access in `index_evidence` to match your
existing project if your current evidence_index.py uses different model paths.
The important addition is `industry_ids` on each Qdrant payload.
"""
from __future__ import annotations

import uuid
from typing import Any

from app.retrieval.chunking import chunk_text
from app.retrieval.vector_store import upsert_chunks
from app.services.industry_resolution import resolve_industry


def _industry_labels(record: Any) -> list[str]:
    raw = getattr(record, "industries", None) or []
    if isinstance(raw, str):
        raw = [raw]
    if not raw:
        fallback = getattr(record, "industry", None)
        raw = [fallback] if fallback else []
    return [str(item).strip() for item in raw if str(item).strip()]


def build_evidence_chunks(record: Any, chunk_size: int = 2000, overlap: int = 300) -> list[dict]:
    """Build canonicalized Qdrant chunks for one Evidence ORM record."""
    title = getattr(record, "title", "") or ""
    domain = (getattr(record, "domain", "") or "GENERAL").strip().upper()
    claim = getattr(record, "claim", "") or ""
    evidence_text = getattr(record, "evidence_text", "") or ""
    implication = getattr(record, "strategic_implication", "") or ""
    tags = getattr(record, "tags", None) or []
    if isinstance(tags, str):
        tags = [tags]

    body = "\n".join([
        title,
        f"Domain: {domain}",
        f"Claim: {claim}",
        f"Evidence: {evidence_text}",
        f"Strategic implication: {implication}",
        f"Tags: {', '.join(str(tag) for tag in tags)}",
    ]).strip()
    pieces = chunk_text(body, chunk_size=chunk_size, overlap=overlap)
    if not pieces:
        return []

    raw_industries = _industry_labels(record)
    resolved = []
    for label in raw_industries:
        item = resolve_industry(label, allow_unknown=True)
        if item and item.id not in [x.id for x in resolved]:
            resolved.append(item)

    canonical_ids = [item.id for item in resolved]
    canonical_names = [item.canonical_name for item in resolved]
    external_id = str(getattr(record, "external_id", None) or getattr(record, "id", ""))
    evidence_id = getattr(record, "id", None)
    source = getattr(record, "research_source", None)
    source_id = getattr(record, "research_source_id", None)
    source_name = getattr(source, "source_name", "") if source else ""
    source_url = getattr(source, "url", "") if source else ""
    verified = "unverified" not in [str(tag).casefold() for tag in tags]

    chunks = []
    for index, piece in enumerate(pieces):
        point_id = str(uuid.uuid5(
            uuid.NAMESPACE_URL, f"evidence:{external_id}:{index}"
        ))
        chunks.append({
            "point_id": point_id,
            "text": piece,
            "record_type": "evidence",
            "evidence_id": evidence_id,
            "external_id": external_id,
            "source_id": source_id,
            "source_name": source_name,
            "source_url": source_url,
            "title": title,
            "industry": canonical_names[0] if canonical_names else "",
            "industry_id": canonical_ids[0] if canonical_ids else "",
            "industry_ids": canonical_ids,
            "industries": list(dict.fromkeys([
                *canonical_names,
                *raw_industries,
                *[alias for item in resolved for alias in item.aliases],
            ])),
            "domain": domain,
            "chunk_index": index,
            "chunk_count": len(pieces),
            "tags": [str(tag) for tag in tags],
            "verified": verified,
        })
    return chunks


def index_evidence_records(records: list[Any]) -> dict[str, int]:
    """Index already-loaded Evidence records; DB querying stays in the API layer."""
    chunks: list[dict] = []
    for record in records:
        chunks.extend(build_evidence_chunks(record))
    indexed = upsert_chunks(chunks) if chunks else 0
    return {
        "records_found": len(records),
        "records_indexed": len(records),
        "chunks_indexed": indexed,
    }
