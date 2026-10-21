"""Endpoints for indexing and querying the semantic retrieval layer."""
import logging
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.retrieval.evidence_index import index_evidence_records
from app.retrieval.document_ingestion import ingest_document
from app.retrieval.semantic_search import semantic_search
from app.schemas.semantic_retrieval import (
    SemanticSearchRequest,
    SemanticSearchResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/semantic_retrieval", tags=["Semantic Retrieval"])


@router.post("/index-evidence")
def index_existing_evidence(db: Session = Depends(get_db)):
    try:
        return index_evidence_records(db)
    except Exception as exc:
        logger.exception("Failed to index existing evidence")
        raise HTTPException(
            status_code=500,
            detail="Evidence indexing failed. Check backend logs.",
        ) from exc


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    industry: str = Form(...),
    domain: str = Form("DOCUMENT"),
):
    try:
        content = await file.read()
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File exceeds 20 MB limit.")
        return ingest_document(
            filename=file.filename or "uploaded.txt",
            content=content,
            industry=industry,
            domain=domain,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Document ingestion failed")
        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed. Check backend logs.",
        ) from exc


@router.post("/search", response_model=SemanticSearchResponse)
def search_semantic(payload: SemanticSearchRequest):
    try:
        results = semantic_search(
            query=payload.query,
            limit=payload.limit,
            industry=payload.industry,
            domain=payload.domain,
            include_unverified=payload.include_unverified,
        )
        return {"query": payload.query, "results": results}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Semantic retrieval failed")
        raise HTTPException(
            status_code=503,
            detail="Semantic retrieval unavailable. Check backend logs.",
        ) from exc
