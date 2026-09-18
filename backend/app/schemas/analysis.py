from pydantic import BaseModel, ConfigDict


class EvidenceSummary(BaseModel):
    id: int
    external_id: str
    domain: str
    title: str

    model_config = ConfigDict(from_attributes=True)


class StrategicIssueResponse(BaseModel):
    id: int
    title: str
    description: str
    rationale: str | None = None
    severity: int
    urgency: int
    model_used: str | None = None
    analysis_version: str | None = None
    evidence: list[EvidenceSummary] = []

    model_config = ConfigDict(from_attributes=True)


class OpportunityResponse(BaseModel):
    id: int
    title: str
    description: str
    rationale: str | None = None

    business_impact: float
    feasibility: float
    urgency: float
    strategic_alignment: float
    evidence_confidence: float

    priority_score: float | None = None
    priority_rank: int | None = None

    model_used: str | None = None
    analysis_version: str | None = None

    evidence: list[EvidenceSummary] = []

    model_config = ConfigDict(from_attributes=True)


class InitiativeResponse(BaseModel):
    id: int
    name: str
    description: str
    expected_outcome: str | None = None
    success_metric: str | None = None
    implementation_phase: str | None = None
    status: str
    model_used: str | None = None
    analysis_version: str | None = None

    model_config = ConfigDict(from_attributes=True)


class IntelligenceResponse(BaseModel):
    organisation_id: int
    organisation_name: str
    analysis_run_id: int | None = None
    strategic_issues: list[StrategicIssueResponse]
    opportunities: list[OpportunityResponse]
    initiatives: list[InitiativeResponse]