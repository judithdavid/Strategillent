

"""API routes for indexing evidence, ingesting documents, and semantic search.

Integrate this router in your existing main.py. Keep the prefix consistent with
your current Swagger route. This default prefix matches the user's current API.
"""
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.evidence import Evidence
from app.retrieval.document_ingestion import ingest_document
from app.retrieval.evidence_index import index_evidence_records
from app.retrieval.semantic_search import semantic_search
from app.schemas.semantic_retrieval import (
    DocumentIngestionResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
)

router = APIRouter(prefix="/api/semantic_retrieval", tags=["Semantic Retrieval"])


@router.post("/index-evidence")
def index_evidence(db: Session = __import__("fastapi").Depends(get_db)):
    try:
        records = db.query(Evidence).all()
        return index_evidence_records(records)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/documents", response_model=DocumentIngestionResponse)
async def upload_document(
    file: UploadFile = File(...),
    industry: str = Form(...),
    domain: str = Form("DOCUMENT"),
    source_url: str | None = Form(None),
):
    try:
        content = await file.read()
        result = ingest_document(
            filename=file.filename or "uploaded_document.txt",
            content=content,
            industry=industry,
            domain=domain,
            source_url=source_url,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/search", response_model=SemanticSearchResponse)
def search_documents(request: SemanticSearchRequest):
    try:
        results = semantic_search(
            query=request.query,
            limit=request.limit,
            industry=request.industry,
            domain=request.domain,
            include_unverified=request.include_unverified,
        )
        return {"query": request.query, "results": results}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
