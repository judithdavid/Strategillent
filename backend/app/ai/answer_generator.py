from app.ai.llm import generate_text
from app.ai.prompts import build_question_prompt
from app.models import Organisation, Evidence
from app.core.config import settings

def build_organisation_context(
    organisation: Organisation,
) -> str:

    return f"""
Name: {organisation.name}
Industry: {organisation.industry}
Business model: {", ".join(organisation.business_model or [])}
Markets: {", ".join(organisation.markets or [])}
Customers: {organisation.customers}
Employees: {organisation.employees}
Products: {", ".join(organisation.products or [])}

Known organisational challenges:
{chr(10).join("- " + item for item in (organisation.challenges or []))}

IMPORTANT:
This organisation context is fictional challenge data,
not external research evidence.
"""


def build_evidence_context(
    evidence_records: list[Evidence],
) -> str:

    if not evidence_records:
        return "No relevant evidence was retrieved."

    sections = []

    for evidence in evidence_records:
        sections.append(
            f"""
[EVIDENCE_ID: {evidence.external_id}]

Domain:
{evidence.domain}

Title:
{evidence.title}

Claim:
{evidence.claim}

Evidence:
{evidence.evidence_text}

Strategic implication:
{evidence.strategic_implication}

Source:
{evidence.url}
"""
        )

    return "\n".join(sections)


def generate_answer(
    organisation: Organisation,
    evidence_records: list[Evidence],
    question: str,
):

    organisation_context = build_organisation_context(
        organisation
    )

    evidence_context = build_evidence_context(
        evidence_records
    )

    prompt = build_question_prompt(
        organisation_context=organisation_context,
        evidence_context=evidence_context,
        question=question,
    )

    answer = generate_text(prompt)

    evidence_ids = [
        evidence.external_id
        for evidence in evidence_records
    ]

    return {
        "answer": answer,
        "evidence_ids": evidence_ids,
        # "model_used": "ollama:" + "configured-model",
        "model_used": f"ollama:{settings.ollama_model}",
    }