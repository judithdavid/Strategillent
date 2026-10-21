
"""Pydantic schemas for semantic retrieval endpoints."""
from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=6, ge=1, le=100)
    industry: str | None = None
    domain: str | None = None
    include_unverified: bool = True


class SemanticSearchResult(BaseModel):
    text: str
    score: float
    record_type: str | None = None
    evidence_id: int | None = None
    external_id: str | None = None
    source_id: int | str | None = None
    source_name: str = ""
    source_url: str = ""
    industry: str = ""
    industry_id: str | None = None
    industry_ids: list[str] = []
    industries: list[str] = []
    domain: str = ""
    title: str = ""
    chunk_index: int | None = None
    tags: list[str] = []
    verified: bool = False


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchResult]


class DocumentIngestionResponse(BaseModel):
    source_id: str
    filename: str
    industry: str
    industry_id: str
    chunks_created_or_updated: int
    characters_extracted: int
