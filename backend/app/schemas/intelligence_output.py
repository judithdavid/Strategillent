from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IntelligenceSchema(BaseModel):
    """Shared strict schema configuration for AI-generated data."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EvidenceCitation(IntelligenceSchema):
    evidence_id: str = Field(
        min_length=1,
        description="Exact evidence ID supplied in the context.",
    )
    claim_supported: str = Field(
        min_length=1,
        description="The specific claim this evidence is intended to support.",
    )
    support_type: Literal["direct", "partial", "contextual"] = "direct"


class Finding(IntelligenceSchema):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1, max_length=3000)
    finding_type: Literal[
        "strength", "weakness", "gap", "risk", "observation"
    ]
    citations: list[EvidenceCitation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_validation: bool = False


class RootCauseHypothesis(IntelligenceSchema):
    hypothesis: str = Field(min_length=3, max_length=2000)
    reasoning: str = Field(min_length=1, max_length=3000)
    supporting_finding_titles: list[str] = Field(default_factory=list)
    citations: list[EvidenceCitation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    validation_questions: list[str] = Field(default_factory=list)
    status: Literal["hypothesis", "partially_supported", "validated"] = "hypothesis"


class Opportunity(IntelligenceSchema):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1, max_length=3000)
    problem_addressed: str = Field(min_length=1, max_length=2000)
    proposed_intervention: str = Field(min_length=1, max_length=3000)
    expected_benefits: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    required_resources: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    citations: list[EvidenceCitation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    requires_human_review: bool = True


class RiskAssessment(IntelligenceSchema):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    likelihood: Literal["low", "medium", "high", "unknown"] = "unknown"
    impact: Literal["low", "medium", "high", "critical", "unknown"] = "unknown"
    mitigation: str = Field(min_length=1, max_length=2000)
    citations: list[EvidenceCitation] = Field(default_factory=list)


class Recommendation(IntelligenceSchema):
    title: str = Field(min_length=3, max_length=200)
    rationale: str = Field(min_length=1, max_length=3000)
    action: str = Field(min_length=1, max_length=3000)
    expected_outcome: str = Field(min_length=1, max_length=2000)
    priority: Literal["low", "medium", "high", "critical"]
    feasibility: float = Field(ge=0.0, le=1.0)
    expected_impact: float = Field(ge=0.0, le=1.0)
    evidence_confidence: float = Field(ge=0.0, le=1.0)
    dependencies: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    citations: list[EvidenceCitation] = Field(default_factory=list)
    requires_approval: bool = True


class IssueAnalysis(IntelligenceSchema):
    summary: str = Field(min_length=1, max_length=4000)
    findings: list[Finding] = Field(default_factory=list)
    root_cause_hypotheses: list[RootCauseHypothesis] = Field(
        default_factory=list
    )
    opportunities: list[Opportunity] = Field(default_factory=list)
    risks: list[RiskAssessment] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    insufficient_evidence: bool = False


class StrategyOption(IntelligenceSchema):
    title: str = Field(min_length=3, max_length=200)
    objective: str = Field(min_length=1, max_length=2000)
    rationale: str = Field(min_length=1, max_length=3000)
    initiatives: list[str] = Field(default_factory=list)
    expected_outcomes: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    estimated_cost: str = Field(
        default="unknown",
        description="Use unknown when no defensible estimate is available.",
    )
    time_horizon: str = Field(default="unknown")
    feasibility: float = Field(ge=0.0, le=1.0)
    expected_impact: float = Field(ge=0.0, le=1.0)
    risk_level: Literal["low", "medium", "high", "critical", "unknown"] = "unknown"
    trade_offs: list[str] = Field(default_factory=list)
    citations: list[EvidenceCitation] = Field(default_factory=list)


class StrategyAnalysis(IntelligenceSchema):
    organisation_summary: str = Field(min_length=1, max_length=4000)
    decision_criteria: list[str] = Field(default_factory=list)
    options: list[StrategyOption] = Field(min_length=1, max_length=5)
    recommended_option_title: str = Field(min_length=1, max_length=200)
    recommendation_rationale: str = Field(min_length=1, max_length=4000)
    first_steps: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    requires_human_review: bool = True

    @model_validator(mode="after")
    def recommended_option_must_exist(self) -> "StrategyAnalysis":
        titles = {option.title.casefold() for option in self.options}
        if self.recommended_option_title.casefold() not in titles:
            raise ValueError(
                "recommended_option_title must match one of the supplied options"
            )
        return self
