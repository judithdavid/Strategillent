

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# -------------------------------------------------------------------
# Legacy response schemas: used by the existing intelligence API
# -------------------------------------------------------------------

class EvidenceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str | None = None
    title: str | None = None
    domain: str | None = None
    url: str | None = None
    evidence_text: str | None = None
    confidence: float | None = None


class StrategicIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organisation_id: int
    title: str
    description: str | None = None
    rationale: str | None = None
    severity: int
    urgency: int
    model_used: str | None = None
    analysis_version: str | None = None
    analysis_run_id: int | None = None
    evidence: list[EvidenceSummary] = Field(default_factory=list)


class OpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organisation_id: int
    strategic_issue_id: int | None = None
    transformation_dimension_id: int | None = None
    title: str
    description: str | None = None
    rationale: str | None = None
    business_impact: float | None = None
    feasibility: float | None = None
    urgency: float | None = None
    strategic_alignment: float | None = None
    evidence_confidence: float | None = None
    priority_score: float | None = None
    priority_rank: int | None = None
    model_used: str | None = None
    analysis_version: str | None = None
    analysis_run_id: int | None = None
    evidence: list[EvidenceSummary] = Field(default_factory=list)


class InitiativeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organisation_id: int
    opportunity_id: int | None = None
    name: str
    description: str | None = None
    expected_outcome: str | None = None
    success_metric: str | None = None
    implementation_phase: str | None = None
    status: str | None = None
    model_used: str | None = None
    analysis_version: str | None = None


class IntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organisation_id: int
    organisation_name: str
    analysis_run_id: int | None = None
    strategic_issues: list[StrategicIssueResponse] = Field(
        default_factory=list
    )
    opportunities: list[OpportunityResponse] = Field(
        default_factory=list
    )
    initiatives: list[InitiativeResponse] = Field(
        default_factory=list
    )


# -------------------------------------------------------------------
# Newer AI-run schemas: keep available for newer endpoints/workflows
# -------------------------------------------------------------------

class AnalysisRunRequest(BaseModel):
    question: str | None = None
    dimensions: list[str] = Field(default_factory=list)


class EvidenceReference(BaseModel):
    external_id: str | None = None
    title: str | None = None
    domain: str | None = None
    url: str | None = None
    confidence: float | None = None


class IssueResult(BaseModel):
    title: str
    description: str | None = None
    rationale: str | None = None
    severity: int
    urgency: int
    evidence: list[EvidenceReference] = Field(default_factory=list)


class OpportunityResult(BaseModel):
    title: str
    description: str | None = None
    rationale: str | None = None
    business_impact: float | None = None
    feasibility: float | None = None
    urgency: float | None = None
    strategic_alignment: float | None = None
    evidence_confidence: float | None = None
    priority_score: float | None = None
    priority_rank: int | None = None
    evidence: list[EvidenceReference] = Field(default_factory=list)


class AnswerResult(BaseModel):
    answer: str
    evidence: list[EvidenceReference] = Field(default_factory=list)
    confidence: float | None = None


class IntelligenceRunResponse(BaseModel):
    """Response schema for newer AI workflows, not the legacy endpoints."""

    organisation_id: int
    organisation_name: str
    analysis_run_id: int | None = None
    answer: AnswerResult | None = None
    strategic_issues: list[IssueResult] = Field(default_factory=list)
    opportunities: list[OpportunityResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
