from __future__ import annotations

import logging
from statistics import mean
from typing import Any

from sqlalchemy.orm import Session

from app.models import (
    AnalysisRun,
    Evidence,
    Initiative,
    Opportunity,
    Organisation,
    StrategicIssue,
    TransformationDimension,
)
from app.ai.issue_analyser import analyse_dimension
from app.ai.opportunity_generator import generate_opportunity
from app.services.industry_selection import (
    filter_evidence_for_industry,
    select_applicable_dimensions,
)
from app.services.prioritisation_service import calculate_and_rank_opportunities

logger = logging.getLogger(__name__)

ANALYSIS_VERSION = "2.0-evidence-driven"
MODEL_USED = "deterministic-evidence-engine"


def _get(value: Any, key: str, default: Any = None) -> Any:
    """Read a field from either a dictionary or an object."""
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _evidence_ids(records: list[Evidence]) -> set[int]:
    return {record.id for record in records if record.id is not None}


def _evidence_external_ids(records: list[Evidence]) -> set[str]:
    return {
        str(record.external_id)
        for record in records
        if record.external_id is not None
    }


def get_dimension_by_external_id(
    db: Session,
    external_id: str,
) -> TransformationDimension | None:
    return (
        db.query(TransformationDimension)
        .filter(TransformationDimension.external_id == external_id)
        .first()
    )


def get_industry_evidence(
    db: Session,
    organisation: Organisation,
) -> list[Evidence]:
    """Return only evidence applicable to this organisation's industry."""
    records = db.query(Evidence).order_by(Evidence.id).all()
    return filter_evidence_for_industry(records, organisation.industry)


def get_applicable_dimensions(
    db: Session,
    organisation: Organisation,
) -> list[TransformationDimension]:
    """Return dimensions applicable to the organisation's industry."""
    dimensions = (
        db.query(TransformationDimension)
        .order_by(TransformationDimension.external_id)
        .all()
    )
    return select_applicable_dimensions(dimensions, organisation.industry)


def _evidence_for_dimension(
    evidence_records: list[Evidence],
    dimension: TransformationDimension,
) -> list[Evidence]:
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


def create_analysis_run(
    db: Session,
    organisation: Organisation,
) -> AnalysisRun:
    analysis_run = AnalysisRun(
        organisation_id=organisation.id,
        model_used=MODEL_USED,
        analysis_version=ANALYSIS_VERSION,
        status="running",
    )
    db.add(analysis_run)
    db.flush()
    return analysis_run


def _find_existing_issue(
    db: Session,
    organisation_id: int,
    title: str,
) -> StrategicIssue | None:
    return (
        db.query(StrategicIssue)
        .filter(
            StrategicIssue.organisation_id == organisation_id,
            StrategicIssue.title == title,
        )
        .first()
    )


def _find_existing_opportunity(
    db: Session,
    organisation_id: int,
    title: str,
) -> Opportunity | None:
    return (
        db.query(Opportunity)
        .filter(
            Opportunity.organisation_id == organisation_id,
            Opportunity.title == title,
        )
        .first()
    )


def _attach_evidence(
    target: Any,
    evidence_records: list[Evidence],
) -> None:
    """Attach evidence only when the target exposes an evidence relationship."""
    if hasattr(target, "evidence"):
        target.evidence = list(evidence_records)


def create_strategic_issues(
    db: Session,
    organisation: Organisation,
) -> list[StrategicIssue]:
    evidence_records = get_industry_evidence(db, organisation)
    dimensions = get_applicable_dimensions(db, organisation)

    issues: list[StrategicIssue] = []

    for dimension in dimensions:
        dimension_evidence = _evidence_for_dimension(
            evidence_records,
            dimension,
        )

        # Never generate an issue without relevant, industry-filtered evidence.
        if not dimension_evidence:
            continue

        generated = analyse_dimension(
            dimension,
            dimension_evidence,
            organisation,
        )

        if not generated:
            continue

        title = _text(_get(generated, "title"))
        if not title:
            logger.warning(
                "Skipping generated issue without a title for dimension %s",
                dimension.external_id,
            )
            continue

        issue = _find_existing_issue(db, organisation.id, title)

        if issue is None:
            issue = StrategicIssue(
                organisation_id=organisation.id,
                title=title,
            )
            db.add(issue)

        issue.description = _text(_get(generated, "description"))
        issue.rationale = _text(_get(generated, "rationale"))
        issue.severity = _text(_get(generated, "severity"), "medium")
        issue.urgency = _number(_get(generated, "urgency"))
        issue.model_used = _text(
            _get(generated, "model_used"),
            MODEL_USED,
        )
        issue.analysis_version = ANALYSIS_VERSION
        _attach_evidence(issue, dimension_evidence)

        db.flush()
        issues.append(issue)

    return issues


def create_opportunities(
    db: Session,
    organisation: Organisation,
    issues: list[StrategicIssue],
) -> list[Opportunity]:
    evidence_records = get_industry_evidence(db, organisation)
    dimensions = get_applicable_dimensions(db, organisation)

    dimensions_by_name = {
        dimension.name.casefold(): dimension
        for dimension in dimensions
        if getattr(dimension, "name", None)
    }
    dimensions_by_external_id = {
        dimension.external_id: dimension
        for dimension in dimensions
        if getattr(dimension, "external_id", None)
    }

    opportunities: list[Opportunity] = []

    for issue in issues:
        issue_evidence = list(getattr(issue, "evidence", []) or [])
        if not issue_evidence:
            continue

        # Resolve the dimension using the issue's explicit dimension metadata
        # when available; otherwise let the generator determine applicability.
        dimension = None
        dimension_external_id = getattr(issue, "transformation_dimension_id", None)

        if dimension_external_id:
            dimension = dimensions_by_external_id.get(dimension_external_id)

        if dimension is None:
            dimension_name = _text(
                getattr(issue, "transformation_dimension", None)
                and getattr(issue.transformation_dimension, "name", None)
            )
            if dimension_name:
                dimension = dimensions_by_name.get(dimension_name.casefold())

        if dimension is None:
            # A dimension must be applicable to the organisation's industry.
            # Match the issue to a dimension only when its evidence domains
            # overlap with the issue's evidence.
            issue_domains = {
                (record.domain or "").strip().casefold()
                for record in issue_evidence
            }
            dimension = next(
                (
                    item
                    for item in dimensions
                    if issue_domains
                    & {
                        str(domain).strip().casefold()
                        for domain in (item.evidence_domains or [])
                    }
                ),
                None,
            )

        if dimension is None:
            logger.info(
                "Skipping opportunity for issue %s: no applicable dimension",
                issue.id,
            )
            continue

        # Re-check evidence against the industry-filtered set and dimension.
        allowed_ids = _evidence_ids(evidence_records)
        valid_issue_evidence = [
            record
            for record in issue_evidence
            if record.id in allowed_ids
        ]
        dimension_evidence = _evidence_for_dimension(
            evidence_records,
            dimension,
        )
        dimension_evidence_ids = _evidence_ids(dimension_evidence)
        valid_evidence = [
            record
            for record in valid_issue_evidence
            if record.id in dimension_evidence_ids
        ]

        if not valid_evidence:
            continue

        generated = generate_opportunity(
            dimension,
            issue,
            organisation,
            evidence_records=valid_evidence,
        )
        if not generated:
            continue

        title = _text(_get(generated, "title"))
        if not title:
            logger.warning(
                "Skipping generated opportunity without a title for issue %s",
                issue.id,
            )
            continue

        opportunity = _find_existing_opportunity(
            db,
            organisation.id,
            title,
        )

        if opportunity is None:
            opportunity = Opportunity(
                organisation_id=organisation.id,
                title=title,
            )
            db.add(opportunity)

        opportunity.strategic_issue_id = issue.id
        opportunity.transformation_dimension_id = dimension.id
        opportunity.description = _text(_get(generated, "description"))
        opportunity.rationale = _text(_get(generated, "rationale"))
        opportunity.business_impact = _number(
            _get(generated, "business_impact")
        )
        opportunity.feasibility = _number(
            _get(generated, "feasibility")
        )
        opportunity.urgency = _number(_get(generated, "urgency"))
        opportunity.strategic_alignment = _number(
            _get(generated, "strategic_alignment")
        )
        opportunity.evidence_confidence = _number(
            _get(generated, "evidence_confidence"),
            _number(
                mean(
                    [
                        _number(getattr(record, "confidence", None), 0.5)
                        for record in valid_evidence
                    ]
                )
                if valid_evidence
                else 0.0
            ),
        )
        opportunity.model_used = _text(
            _get(generated, "model_used"),
            MODEL_USED,
        )
        opportunity.analysis_version = ANALYSIS_VERSION
        _attach_evidence(opportunity, valid_evidence)

        db.flush()
        opportunities.append(opportunity)

    return opportunities


def build_initiative_context(
    organisation: Organisation,
    opportunity: Opportunity,
) -> str:
    evidence = list(getattr(opportunity, "evidence", []) or [])
    evidence_ids = [
        record.external_id
        for record in evidence
        if getattr(record, "external_id", None)
    ]

    parts = [
        f"Organisation: {organisation.name}",
        f"Industry: {organisation.industry or 'Unknown'}",
        f"Opportunity: {opportunity.title}",
        f"Description: {opportunity.description or ''}",
        f"Goals: {getattr(organisation, 'goals', None) or ''}",
        f"Challenges: {getattr(organisation, 'challenges', None) or ''}",
        f"Processes: {getattr(organisation, 'processes', None) or ''}",
        f"Technology: {getattr(organisation, 'technology', None) or ''}",
        f"Constraints: {getattr(organisation, 'constraints', None) or ''}",
        f"Evidence IDs: {', '.join(evidence_ids)}",
    ]
    return "\n".join(parts)


def create_initiatives(
    db: Session,
    organisation: Organisation,
    opportunities: list[Opportunity],
    analysis_run: AnalysisRun,
) -> list[Initiative]:
    initiatives: list[Initiative] = []

    for opportunity in opportunities:
        if not list(getattr(opportunity, "evidence", []) or []):
            continue

        initiative_name = f"Pilot: {opportunity.title}"
        initiative = (
            db.query(Initiative)
            .filter(
                Initiative.organisation_id == organisation.id,
                Initiative.opportunity_id == opportunity.id,
                Initiative.name == initiative_name,
            )
            .first()
        )

        context = build_initiative_context(organisation, opportunity)

        if initiative is None:
            initiative = Initiative(
                organisation_id=organisation.id,
                opportunity_id=opportunity.id,
                name=initiative_name,
            )
            db.add(initiative)

        initiative.description = (
            f"Pilot initiative to validate the opportunity: "
            f"{opportunity.description or opportunity.title}\n\n"
            f"Context:\n{context}"
        )
        initiative.expected_outcome = (
            f"Validate the business value of {opportunity.title}."
        )
        initiative.success_metric = (
            "Define a baseline, run the pilot, and compare measured "
            "results against the baseline."
        )
        initiative.implementation_phase = "pilot"
        initiative.status = "proposed"
        initiative.model_used = opportunity.model_used or MODEL_USED
        initiative.analysis_version = ANALYSIS_VERSION

        initiatives.append(initiative)

    db.flush()
    return initiatives


def run_intelligence_analysis(
    db: Session,
    organisation: Organisation,
) -> dict[str, Any]:
    """Run the legacy evidence-driven pipeline for one organisation."""
    analysis_run: AnalysisRun | None = None

    try:
        analysis_run = create_analysis_run(db, organisation)

        issues = create_strategic_issues(db, organisation)
        for issue in issues:
            issue.analysis_run_id = analysis_run.id

        db.flush()

        opportunities = create_opportunities(db, organisation, issues)
        for opportunity in opportunities:
            opportunity.analysis_run_id = analysis_run.id

        db.flush()

        ranked_opportunities = calculate_and_rank_opportunities(
            db,
            opportunities,
        )

        initiatives = create_initiatives(
            db,
            organisation,
            ranked_opportunities,
            analysis_run,
        )

        analysis_run.status = "completed"
        db.commit()

        return {
            "organisation": organisation,
            "analysis_run": analysis_run,
            "issues": issues,
            "opportunities": ranked_opportunities,
            "initiatives": initiatives,
        }

    except Exception as exc:
        db.rollback()
        logger.exception(
            "Intelligence analysis failed for organisation %s",
            organisation.id,
        )

        # Try to record the failed run without masking the original exception.
        try:
            failed_run = AnalysisRun(
                organisation_id=organisation.id,
                model_used=MODEL_USED,
                analysis_version=ANALYSIS_VERSION,
                status="failed",
            )
            db.add(failed_run)
            db.commit()
        except Exception:
            db.rollback()

        raise exc
