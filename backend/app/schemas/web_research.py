
from pydantic import BaseModel, Field


class WebResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    industry: str = Field(min_length=1, max_length=100)
    domain: str = Field(min_length=1, max_length=100)
    max_results: int = Field(default=5, ge=1, le=10)


class WebResearchResponse(BaseModel):
    query: str
    industry: str
    domain: str
    results_found: int
    created: int
    updated: int
    skipped: int
