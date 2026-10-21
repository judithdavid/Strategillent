"""Index existing SQL evidence into Qdrant without changing SQL schema."""
import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.models import Evidence
from app.retrieval.chunking import chunk_text
from app.retrieval.vector_store import upsert_chunks


def index_evidence_records(db: Session, batch_size: int = 64) -> dict[str, int]:
    if not 1 <= batch_size <= 512:
        raise ValueError("batch_size must be between 1 and 512.")

    records = db.query(Evidence).order_by(Evidence.id).all()
    chunks: list[dict[str, Any]] = []
    records_indexed = 0

    for evidence in records:
        source = evidence.research_source
        text = "\n".join(filter(None, [
            evidence.title,
            f"Domain: {evidence.domain}",
            f"Claim: {evidence.claim}",
            f"Evidence: {evidence.evidence_text}",
            f"Strategic implication: {evidence.strategic_implication}",
            f"Tags: {', '.join(evidence.tags or [])}",
        ]))
        pieces = chunk_text(text)
        if not pieces:
            continue

        records_indexed += 1
        source_name = getattr(source, "source_name", "") if source else ""
        source_url = evidence.url or (getattr(source, "url", "") if source else "")
        industries = list(evidence.industries or [])
        verified = "unverified" not in [str(tag).casefold() for tag in (evidence.tags or [])]
        for index, piece in enumerate(pieces):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"evidence:{evidence.external_id}:{index}"))
            chunks.append({
                "point_id": point_id,
                "text": piece,
                "record_type": "evidence",
                "evidence_id": evidence.id,
                "external_id": evidence.external_id,
                "source_id": evidence.research_source_id,
                "source_name": source_name,
                "source_url": source_url,
                "industry": industries[0] if industries else "",
                "industries": industries,
                "domain": evidence.domain or "",
                "title": evidence.title or "",
                "chunk_index": index,
                "chunk_count": len(pieces),
                "tags": list(evidence.tags or []),
                "confidence": evidence.confidence,
                "relevance": evidence.relevance,
                "verified": verified,
            })

    indexed_chunks = 0
    for start in range(0, len(chunks), batch_size):
        indexed_chunks += upsert_chunks(chunks[start:start + batch_size])

    return {
        "records_found": len(records),
        "records_indexed": records_indexed,
        "chunks_indexed": indexed_chunks,
    }
