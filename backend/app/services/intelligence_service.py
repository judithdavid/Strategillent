from sqlalchemy.orm import Session

from app.models import (
    Organisation,
    StrategicIssue,
    Opportunity,
    TransformationDimension,
)

from app.services.evidence_service import (
    get_evidence_for_domain,
)

from app.services.prioritisation_service import (
    calculate_and_rank_opportunities,
)

from app.models import (
    Organisation,
    StrategicIssue,
    Opportunity,
    TransformationDimension,
    Initiative,
    AnalysisRun,
)

ANALYSIS_VERSION = "1.0"


DOMAIN_ISSUES = {
    "FRAUD": {
        "title": "Rising digital-payment fraud and financial risk",
        "description": (
            "FinNova faces increasing pressure to detect and respond "
            "to fraudulent payment activity as digital transaction "
            "volumes and scam patterns evolve."
        ),
        "severity": 5,
        "urgency": 5,
        "dimension": "T01",
    },
    "LENDING": {
        "title": "Slow and manual lending decision workflows",
        "description": (
            "FinNova's lending operations have opportunities to "
            "reduce manual processing and improve decision speed "
            "while maintaining responsible lending controls."
        ),
        "severity": 4,
        "urgency": 4,
        "dimension": "T02",
    },
    "CX": {
        "title": "High customer-support and complaint volume",
        "description": (
            "FinNova has an opportunity to improve customer-support "
            "efficiency, complaint handling and resolution latency."
        ),
        "severity": 4,
        "urgency": 4,
        "dimension": "T03",
    },
    "DATA": {
        "title": "Fragmented customer and financial data",
        "description": (
            "Fragmented data creates challenges for customer "
            "intelligence, financial profiling and consistent "
            "decision-making."
        ),
        "severity": 4,
        "urgency": 4,
        "dimension": "T04",
    },
    "GOVERNANCE": {
        "title": "Increasing AI governance and regulatory complexity",
        "description": (
            "FinNova needs stronger governance mechanisms as AI "
            "adoption expands across financial decision-making "
            "and customer-facing processes."
        ),
        "severity": 5,
        "urgency": 5,
        "dimension": "T05",
    },
    "AI": {
        "title": "Need to accelerate responsible AI adoption",
        "description": (
            "FinNova can use AI to improve operational efficiency "
            "and customer outcomes while maintaining appropriate "
            "risk, governance and explainability controls."
        ),
        "severity": 4,
        "urgency": 4,
        "dimension": "T06",
    },
}


OPPORTUNITY_TEMPLATES = {
    "T01": {
        "title": "Intelligent Fraud & Risk",
        "description": (
            "Deploy real-time transaction risk scoring, network "
            "analytics and AI-assisted fraud investigation."
        ),
        "business_impact": 5.0,
        "feasibility": 4.0,
        "urgency": 5.0,
        "strategic_alignment": 5.0,
    },
    "T02": {
        "title": "AI-Assisted Lending",
        "description": (
            "Introduce document intelligence, consent-based "
            "financial-data ingestion and explainable AI underwriting "
            "support."
        ),
        "business_impact": 5.0,
        "feasibility": 3.5,
        "urgency": 4.0,
        "strategic_alignment": 5.0,
    },
    "T03": {
        "title": "Customer Intelligence",
        "description": (
            "Use AI for complaint classification, customer-support "
            "assistance, multilingual service and intelligent routing."
        ),
        "business_impact": 4.0,
        "feasibility": 4.5,
        "urgency": 4.0,
        "strategic_alignment": 5.0,
    },
    "T04": {
        "title": "Financial Data Platform",
        "description": (
            "Build a governed financial-data layer supporting "
            "consent orchestration, financial-data APIs and "
            "customer financial profiles."
        ),
        "business_impact": 5.0,
        "feasibility": 3.0,
        "urgency": 4.0,
        "strategic_alignment": 5.0,
    },
    "T05": {
        "title": "Responsible AI Governance",
        "description": (
            "Establish AI inventory, risk classification, model "
            "monitoring, explainability controls and AI incident "
            "management."
        ),
        "business_impact": 5.0,
        "feasibility": 4.0,
        "urgency": 5.0,
        "strategic_alignment": 5.0,
    },
    "T06": {
        "title": "Payment Operations & Resilience",
        "description": (
            "Use anomaly detection, incident intelligence and "
            "operations copilots to improve payment reliability."
        ),
        "business_impact": 4.5,
        "feasibility": 4.0,
        "urgency": 4.5,
        "strategic_alignment": 5.0,
    },
}

INITIATIVE_TEMPLATES = {
    "T01": [
        {
            "name": "Real-Time Fraud Risk Engine",
            "description": (
                "Implement real-time transaction risk scoring "
                "with adaptive fraud detection."
            ),
            "expected_outcome": (
                "Faster identification and intervention against "
                "fraudulent transactions."
            ),
            "success_metric": (
                "Reduction in fraud loss and detection latency"
            ),
            "implementation_phase": "Phase 1",
        },
        {
            "name": "AI Fraud Investigation Copilot",
            "description": (
                "Assist fraud analysts with case summarisation, "
                "pattern discovery and investigation workflows."
            ),
            "expected_outcome": (
                "Reduced analyst investigation time."
            ),
            "success_metric": (
                "Reduction in average fraud investigation time"
            ),
            "implementation_phase": "Phase 2",
        },
    ],
    "T02": [
        {
            "name": "AI Lending Document Intelligence",
            "description": (
                "Automate extraction and validation of lending "
                "documents."
            ),
            "expected_outcome": (
                "Reduced manual document-processing effort."
            ),
            "success_metric": (
                "Reduction in lending processing time"
            ),
            "implementation_phase": "Phase 1",
        },
        {
            "name": "Explainable Lending Decision Support",
            "description": (
                "Provide explainable AI-assisted underwriting "
                "recommendations."
            ),
            "expected_outcome": (
                "Faster and more consistent lending decisions."
            ),
            "success_metric": (
                "Reduction in decision turnaround time"
            ),
            "implementation_phase": "Phase 2",
        },
    ],
    "T03": [
        {
            "name": "AI Customer Support Assistant",
            "description": (
                "Deploy an AI assistant for common customer "
                "support interactions."
            ),
            "expected_outcome": (
                "Faster customer response and resolution."
            ),
            "success_metric": (
                "Reduction in average resolution time"
            ),
            "implementation_phase": "Phase 1",
        },
        {
            "name": "Intelligent Complaint Routing",
            "description": (
                "Automatically classify complaints and route "
                "cases to the appropriate teams."
            ),
            "expected_outcome": (
                "Improved complaint handling efficiency."
            ),
            "success_metric": (
                "Reduction in complaint routing time"
            ),
            "implementation_phase": "Phase 2",
        },
    ],
    "T04": [
        {
            "name": "Governed Financial Data Layer",
            "description": (
                "Create a governed data layer for customer "
                "financial information."
            ),
            "expected_outcome": (
                "More consistent and accessible customer data."
            ),
            "success_metric": (
                "Improvement in data-quality coverage"
            ),
            "implementation_phase": "Phase 1",
        },
    ],
    "T05": [
        {
            "name": "Responsible AI Control Framework",
            "description": (
                "Create AI inventory, risk classification, "
                "monitoring and explainability controls."
            ),
            "expected_outcome": (
                "Improved visibility and control over AI risks."
            ),
            "success_metric": (
                "Percentage of AI systems covered by governance controls"
            ),
            "implementation_phase": "Phase 1",
        },
        {
            "name": "AI Incident Management",
            "description": (
                "Establish a process for detecting, recording "
                "and managing AI-related incidents."
            ),
            "expected_outcome": (
                "Faster identification and response to AI risks."
            ),
            "success_metric": (
                "AI incident detection and resolution time"
            ),
            "implementation_phase": "Phase 2",
        },
    ],
    "T06": [
        {
            "name": "Payment Operations Intelligence",
            "description": (
                "Use anomaly detection and operational intelligence "
                "to identify payment-service issues."
            ),
            "expected_outcome": (
                "Improved payment reliability and operational response."
            ),
            "success_metric": (
                "Reduction in payment incident resolution time"
            ),
            "implementation_phase": "Phase 1",
        },
        {
            "name": "Operations Copilot",
            "description": (
                "Provide operations teams with AI-assisted "
                "incident analysis and resolution guidance."
            ),
            "expected_outcome": (
                "Faster operational decision-making."
            ),
            "success_metric": (
                "Reduction in operational resolution time"
            ),
            "implementation_phase": "Phase 2",
        },
    ],
}

def create_initiatives(
    db: Session,
    organisation: Organisation,
    opportunities: list[Opportunity],
    analysis_run: AnalysisRun,
):
    created_initiatives = []

    for opportunity in opportunities:

        dimension = opportunity.transformation_dimension

        if not dimension:
            continue

        templates = INITIATIVE_TEMPLATES.get(
            dimension.external_id,
            [],
        )

        for template in templates:

            existing = (
                db.query(Initiative)
                .filter(
                    Initiative.organisation_id == organisation.id,
                    Initiative.opportunity_id == opportunity.id,
                    Initiative.name == template["name"],
                )
                .first()
            )

            if existing:
                created_initiatives.append(existing)
                continue

            initiative = Initiative(
                organisation_id=organisation.id,
                opportunity_id=opportunity.id,
                name=template["name"],
                description=template["description"],
                expected_outcome=template["expected_outcome"],
                success_metric=template["success_metric"],
                implementation_phase=template["implementation_phase"],
                status="proposed",
                model_used="deterministic-rule-engine",
                analysis_version=ANALYSIS_VERSION,
            )

            db.add(initiative)
            db.flush()

            created_initiatives.append(initiative)

    db.commit()

    return created_initiatives

def create_analysis_run(
    db: Session,
    organisation: Organisation,
):
    run = AnalysisRun(
        organisation_id=organisation.id,
        model_used="deterministic-rule-engine",
        analysis_version=ANALYSIS_VERSION,
        status="completed",
    )

    db.add(run)
    db.flush()

    return run

def get_dimension_by_external_id(
    db: Session,
    external_id: str,
):
    return (
        db.query(TransformationDimension)
        .filter(
            TransformationDimension.external_id == external_id
        )
        .first()
    )

def get_relevant_issue_domains(organisation: Organisation) -> set[str]:
    """Select issue domains using the organisation's profile."""

    profile_fields = [
        organisation.challenges or [],
        organisation.goals or [],
        organisation.processes or [],
        organisation.technology or [],
        organisation.constraints or [],
    ]

    profile_text = " ".join(
        str(item)
        for field in profile_fields
        for item in field
    ).lower()

    if not profile_text.strip():
        return set(DOMAIN_ISSUES.keys())

    domain_keywords = {
        "FRAUD": [
            "fraud", "risk", "scam", "suspicious", "payment security",
            "financial loss", "transaction monitoring",
        ],
        "LENDING": [
            "loan", "lending", "credit", "underwriting",
            "loan processing", "credit decision",
        ],
        "CX": [
            "customer support", "customer service", "customer experience",
            "complaint", "support volume", "customer satisfaction",
        ],
        "DATA": [
            "data", "fragmented", "silo", "integration",
            "data quality", "customer records",
        ],
        "GOVERNANCE": [
            "compliance", "regulation", "regulatory", "audit",
            "governance", "privacy", "policy",
        ],
        "AI": [
            "artificial intelligence", "machine learning", "automation",
            "manual process", "operational efficiency", "ai adoption",
        ],
    }

    relevant_domains = {
        domain
        for domain, keywords in domain_keywords.items()
        if any(keyword in profile_text for keyword in keywords)
        and domain in DOMAIN_ISSUES
    }

    # Preserve useful output for profiles whose wording doesn't match
    # the initial keyword rules.
    return relevant_domains or set(DOMAIN_ISSUES.keys())



def create_strategic_issues(
    db: Session,
    organisation: Organisation,
):
    created_issues = []

    relevant_domains = get_relevant_issue_domains(organisation)

    for domain, config in DOMAIN_ISSUES.items():
        if domain not in relevant_domains:
            continue

        evidence = get_evidence_for_domain(
            db,
            domain,
        )

        if not evidence:
            continue

        existing = (
            db.query(StrategicIssue)
            .filter(
                StrategicIssue.organisation_id == organisation.id,
                StrategicIssue.title == config["title"],
            )
            .first()
        )

        if existing:
            created_issues.append(existing)
            continue

        issue = StrategicIssue(
            organisation_id=organisation.id,
            title=config["title"],
            description=config["description"],
            rationale=(
                f"Supported by {len(evidence)} external evidence "
                f"records from the {domain} research domain."
            ),
            severity=config["severity"],
            urgency=config["urgency"],
            model_used="deterministic-rule-engine",
            analysis_version=ANALYSIS_VERSION,
        )

        issue.evidence = evidence

        db.add(issue)
        db.flush()

        created_issues.append(issue)

    db.commit()

    return created_issues


def build_opportunity_context(organisation: Organisation) -> str:
    """Build organisation-specific context for an opportunity."""

    fields = {
        "Business goals": organisation.goals or [],
        "Current challenges": organisation.challenges or [],
        "Current processes": organisation.processes or [],
        "Technology and systems": organisation.technology or [],
        "Business constraints": organisation.constraints or [],
    }

    sections = []

    for label, values in fields.items():
        if values:
            sections.append(
                f"{label}: " + "; ".join(str(value) for value in values)
            )

    return "\n".join(sections)

def create_opportunities(
    db: Session,
    organisation: Organisation,
    issues: list[StrategicIssue],
):
    created_opportunities = []

    for issue in issues:

        # Find the dimension associated with this issue.
        dimension_id = None

        for domain, config in DOMAIN_ISSUES.items():
            if config["title"] == issue.title:
                dimension = get_dimension_by_external_id(
                    db,
                    config["dimension"],
                )

                if dimension:
                    dimension_id = dimension.id

                template = OPPORTUNITY_TEMPLATES.get(
                    config["dimension"]
                )

                break
        else:
            continue

        if not template:
            continue

        existing = (
            db.query(Opportunity)
            .filter(
                Opportunity.organisation_id == organisation.id,
                Opportunity.strategic_issue_id == issue.id,
                Opportunity.title == template["title"],
            )
            .first()
        )

        if existing:
            created_opportunities.append(existing)
            continue

        opportunity = Opportunity(
            organisation_id=organisation.id,
            strategic_issue_id=issue.id,
            transformation_dimension_id=dimension_id,
            title=template["title"],
            
            description=(
                f"{template['description']} "
                + (
                    f"This opportunity is being considered in the context of "
                    f"the organisation's profile: "
                    f"{build_opportunity_context(organisation)}"
                    if build_opportunity_context(organisation)
                    else "Organisation-specific goals and constraints were not provided."
                )
            ),
            rationale=(
                f"Derived from the strategic issue: {issue.title}. "
                f"Supported by {len(issue.evidence)} associated evidence records. "
                + (
                    f"Relevant organisation context: "
                    f"{build_opportunity_context(organisation)}"
                    if build_opportunity_context(organisation)
                    else "No additional organisation profile context was provided."
                )
            ),
                
            business_impact=template["business_impact"],
            feasibility=template["feasibility"],
            urgency=template["urgency"],
            strategic_alignment=template["strategic_alignment"],
            evidence_confidence=round(
                sum(
                    evidence.confidence
                    for evidence in issue.evidence
                )
                / len(issue.evidence),
                2,
            ),
            model_used="deterministic-rule-engine",
            analysis_version=ANALYSIS_VERSION,
        )

        opportunity.evidence = list(issue.evidence)

        db.add(opportunity)
        db.flush()

        created_opportunities.append(opportunity)

    db.commit()

    return created_opportunities


def run_intelligence_analysis(
    db: Session,
    organisation: Organisation,
):
    analysis_run = create_analysis_run(
        db,
        organisation,
    )

    issues = create_strategic_issues(
        db,
        organisation,
    )

    for issue in issues:
        issue.analysis_run_id = analysis_run.id

    db.commit()

    opportunities = create_opportunities(
        db,
        organisation,
        issues,
    )

    for opportunity in opportunities:
        opportunity.analysis_run_id = analysis_run.id

    db.commit()

    ranked_opportunities = (
        calculate_and_rank_opportunities(
            db,
            opportunities,
        )
    )

    initiatives = create_initiatives(
        db,
        organisation,
        ranked_opportunities,
        analysis_run,
    )

    return {
        "organisation": organisation,
        "analysis_run": analysis_run,
        "issues": issues,
        "opportunities": ranked_opportunities,
        "initiatives": initiatives,
    }