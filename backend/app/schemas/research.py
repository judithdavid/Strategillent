from datetime import date

from pydantic import BaseModel, ConfigDict


class ResearchSourceResponse(BaseModel):
    id: int
    source_name: str
    source_type: str
    url: str
    publication_date: date | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class EvidenceResponse(BaseModel):
    id: int
    external_id: str
    domain: str
    title: str
    publication_date: date | None = None
    url: str
    claim: str
    evidence_text: str
    strategic_implication: str
    confidence: int
    relevance: int
    tags: list[str] = []

    research_source: ResearchSourceResponse

    model_config = ConfigDict(
        from_attributes=True
    )