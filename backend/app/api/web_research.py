
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.web_research import (
    WebResearchRequest,
    WebResearchResponse,
)
from app.services.web_evidence_service import (
    search_and_store_web_evidence,
)
from app.services.web_research_service import WebResearchError


router = APIRouter(
    prefix="/api/research",
    tags=["Web Research"],
)


@router.post(
    "/web-search",
    response_model=WebResearchResponse,
)
def run_web_research(
    payload: WebResearchRequest,
    db: Session = Depends(get_db),
):
    try:
        return search_and_store_web_evidence(
            db=db,
            query=payload.query,
            industry=payload.industry,
            domain=payload.domain,
            max_results=payload.max_results,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except WebResearchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
