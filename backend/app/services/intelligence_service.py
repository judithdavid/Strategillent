"""Industry-aware, evidence-driven strategic intelligence pipeline.

The seed data determines which dimensions and candidate initiatives apply to an
industry. Evidence is strictly filtered by its industries metadata. No LLM output
or external fact is treated as evidence, and opportunity ranking stays deterministic.
"""
from statistics import mean
from sqlalchemy.orm import Session

from app.models import (
    Organisation, StrategicIssue, Opportunity, TransformationDimension,
    Initiative, AnalysisRun, Evidence,
)
from app.ai.issue_analyser import analyse_dimension
from app.ai.opportunity_generator import generate_opportunity
from app.services.industry_selection import (
    filter_evidence_for_industry,
    normalise_industry,
    select_applicable_dimensions,
)
from app.services.prioritisation_service import calculate_and_rank_opportunities

ANALYSIS_VERSION = "2.0-evidence-driven"


def get_dimension_by_external_id(db: Session, external_id: str):
    return (
        db.query(TransformationDimension)
        .filter(TransformationDimension.external_id == external_id)
        .first()
    )


def get_industry_evidence(db: Session, organisation: Organisation):
    """Return only evidence explicitly tagged for the organisation's industry."""
    all_records = db.query(Evidence).order_by(Evidence.id).all()
    return filter_evidence_for_industry(all_records, organisation.industry)


def get_applicable_dimensions(db: Session, organisation: Organisation):
    dimensions = db.query(TransformationDimension).order_by(
        TransformationDimension.external_id
    ).all()
    return select_applicable_dimensions(dimensions, organisation.industry)


def _evidence_for_dimension(evidence_records, dimension):
    """Return evidence matching a dimension's declared research domains."""

    allowed_domains = {
        str(value).strip().casefold()
        for value in (dimension.evidence_domains or [])
        if value and str(value).strip()
    }

    if not allowed_domains:
        return []

    return [
        record
        for record in evidence_records
        if (record.domain or "").strip().casefold() in allowed_domains
    ]

def create_analysis_run(db: Session, organisation: Organisation):
    run = AnalysisRun(
        organisation_id=organisation.id,
        model_used="deterministic-evidence-engine",
        analysis_version=ANALYSIS_VERSION,
        status="running",
    )
    db.add(run)
    db.flush()
    return run


def create_strategic_issues(db: Session, organisation: Organisation):
    created_issues = []
    industry_evidence = get_industry_evidence(db, organisation)
    dimensions = get_applicable_dimensions(db, organisation)

    for dimension in dimensions:
        evidence = _evidence_for_dimension(industry_evidence, dimension)
        if not evidence:
            # No relevant, industry-tagged evidence means no recommendation.
            continue

        issue_data = analyse_dimension(dimension, evidence, organisation)
        existing = (
            db.query(StrategicIssue)
            .filter(
                StrategicIssue.organisation_id == organisation.id,
                StrategicIssue.title == issue_data["title"],
            )
            .first()
        )
        if existing:
            existing.description = issue_data["description"]
            existing.rationale = issue_data["rationale"]
            existing.severity = issue_data["severity"]
            existing.urgency = issue_data["urgency"]
            existing.evidence = evidence
            existing.model_used = "deterministic-evidence-engine"
            existing.analysis_version = ANALYSIS_VERSION
            created_issues.append(existing)
            continue

        issue = StrategicIssue(
            organisation_id=organisation.id,
            title=issue_data["title"],
            description=issue_data["description"],
            rationale=issue_data["rationale"],
            severity=issue_data["severity"],
            urgency=issue_data["urgency"],
            model_used="deterministic-evidence-engine",
            analysis_version=ANALYSIS_VERSION,
        )
        issue.evidence = evidence
        db.add(issue)
        db.flush()
        created_issues.append(issue)

    # db.commit()
    return created_issues


def create_opportunities(db: Session, organisation: Organisation, issues: list[StrategicIssue]):
    created_opportunities = []
    dimensions = {
        dimension.name: dimension
        for dimension in get_applicable_dimensions(db, organisation)
    }

    for issue in issues:
        dimension = dimensions.get(issue.title)
        if dimension is None or not issue.evidence:
            continue

        opportunity_data = generate_opportunity(dimension, issue, organisation)
        existing = (
            db.query(Opportunity)
            .filter(
                Opportunity.organisation_id == organisation.id,
                Opportunity.strategic_issue_id == issue.id,
                Opportunity.title == opportunity_data["title"],
            )
            .first()
        )
        if existing:
            existing.transformation_dimension_id = dimension.id
            existing.description = opportunity_data["description"]
            existing.rationale = opportunity_data["rationale"]
            existing.business_impact = opportunity_data["business_impact"]
            existing.feasibility = opportunity_data["feasibility"]
            existing.urgency = opportunity_data["urgency"]
            existing.strategic_alignment = opportunity_data["strategic_alignment"]
            existing.evidence_confidence = opportunity_data["evidence_confidence"]
            existing.evidence = list(issue.evidence)
            existing.model_used = "deterministic-evidence-engine"
            existing.analysis_version = ANALYSIS_VERSION
            created_opportunities.append(existing)
            continue

        opportunity = Opportunity(
            organisation_id=organisation.id,
            strategic_issue_id=issue.id,
            transformation_dimension_id=dimension.id,
            title=opportunity_data["title"],
            description=opportunity_data["description"],
            rationale=opportunity_data["rationale"],
            business_impact=opportunity_data["business_impact"],
            feasibility=opportunity_data["feasibility"],
            urgency=opportunity_data["urgency"],
            strategic_alignment=opportunity_data["strategic_alignment"],
            evidence_confidence=opportunity_data["evidence_confidence"],
            model_used="deterministic-evidence-engine",
            analysis_version=ANALYSIS_VERSION,
        )
        opportunity.evidence = list(issue.evidence)
        db.add(opportunity)
        db.flush()
        created_opportunities.append(opportunity)

    # db.commit()
    return created_opportunities


def build_initiative_context(organisation: Organisation, opportunity: Opportunity) -> str:
    sections = [f"Opportunity: {opportunity.title}"]
    fields = {
        "Goals": getattr(organisation, "goals", None) or [],
        "Challenges": getattr(organisation, "challenges", None) or [],
        "Processes": getattr(organisation, "processes", None) or [],
        "Technology": getattr(organisation, "technology", None) or [],
        "Constraints": getattr(organisation, "constraints", None) or [],
    }
    for label, values in fields.items():
        if values:
            sections.append(f"{label}: " + "; ".join(str(value) for value in values))
    evidence_ids = [item.external_id for item in (opportunity.evidence or [])]
    sections.append("Supporting evidence: " + (", ".join(evidence_ids) if evidence_ids else "none"))
    return "\n".join(sections)


def create_initiatives(
    db: Session,
    organisation: Organisation,
    opportunities: list[Opportunity],
    analysis_run: AnalysisRun,
):
    created_initiatives = []
    for opportunity in opportunities:
        if not opportunity.evidence:
            continue
        name = f"Pilot: {opportunity.title}"
        existing = (
            db.query(Initiative)
            .filter(
                Initiative.organisation_id == organisation.id,
                Initiative.opportunity_id == opportunity.id,
                Initiative.name == name,
            )
            .first()
        )
        context = build_initiative_context(organisation, opportunity)
        evidence_ids = ", ".join(item.external_id for item in opportunity.evidence)
        description = (
            f"Validate the opportunity '{opportunity.title}' using a bounded pilot. "
            f"The pilot should test feasibility, operational fit, and relevant safeguards.\n{context}"
        )
        expected_outcome = (
            f"Evidence-based decision on whether to scale '{opportunity.title}', "
            f"using baseline and post-pilot measures. Supporting evidence: {evidence_ids}."
        )
        if existing:
            existing.description = description
            existing.expected_outcome = expected_outcome
            existing.model_used = "deterministic-evidence-engine"
            existing.analysis_version = ANALYSIS_VERSION
            created_initiatives.append(existing)
            continue

        initiative = Initiative(
            organisation_id=organisation.id,
            opportunity_id=opportunity.id,
            name=name,
            description=description,
            expected_outcome=expected_outcome,
            success_metric="Define a baseline, then measure the agreed outcome and risk indicators",
            implementation_phase="Phase 1 - Validate",
            status="proposed",
            model_used="deterministic-evidence-engine",
            analysis_version=ANALYSIS_VERSION,
        )
        db.add(initiative)
        db.flush()
        created_initiatives.append(initiative)

    # db.commit()
    return created_initiatives


def run_intelligence_analysis(db: Session, organisation: Organisation):
    try:
        analysis_run = create_analysis_run(db, organisation)

        issues = create_strategic_issues(db, organisation)
        for issue in issues:
            issue.analysis_run_id = analysis_run.id

        opportunities = create_opportunities(db, organisation, issues)
        for opportunity in opportunities:
            opportunity.analysis_run_id = analysis_run.id

        ranked_opportunities = calculate_and_rank_opportunities(
            db, opportunities
        )

        initiatives = create_initiatives(
            db,
            organisation,
            ranked_opportunities,
            analysis_run,
        )

        # Mark success only after every pipeline stage has completed.
        analysis_run.status = "completed"
        db.commit()

        return {
            "organisation": organisation,
            "analysis_run": analysis_run,
            "issues": issues,
            "opportunities": ranked_opportunities,
            "initiatives": initiatives,
        }

    except Exception:
        # Undo all uncommitted changes, including updates to existing records.
        db.rollback()

        # Record the failed run in a separate transaction.
        try:
            failed_run = AnalysisRun(
                organisation_id=organisation.id,
                model_used="deterministic-evidence-engine",
                analysis_version=ANALYSIS_VERSION,
                status="failed",
            )
            db.add(failed_run)
            db.commit()
        except Exception:
            # Do not let failure-recording errors hide the original exception.
            db.rollback()

        raise
