from app.ai.llm import generate_text
from app.ai.prompts import build_question_prompt
from app.models import Organisation, Evidence
from app.core.config import settings


def build_organisation_context(
    organisation: Organisation,
) -> str:
    return f"""
Organisation profile:

Name: {organisation.name}
Industry: {organisation.industry}
Business model: {", ".join(organisation.business_model or [])}
Markets: {", ".join(organisation.markets or [])}
Customers: {organisation.customers}
Employees: {organisation.employees}
Products: {", ".join(organisation.products or [])}

Business goals:
{chr(10).join("- " + item for item in (organisation.goals or [])) or "Not provided"}

Current business processes:
{chr(10).join("- " + item for item in (organisation.processes or [])) or "Not provided"}

Current technology and systems:
{chr(10).join("- " + item for item in (organisation.technology or [])) or "Not provided"}

Business constraints:
{chr(10).join("- " + item for item in (organisation.constraints or [])) or "Not provided"}

Known organisational challenges:
{chr(10).join("- " + item for item in (organisation.challenges or [])) or "Not provided"}

Use this profile to tailor answers to this organisation.
Do not assume missing information is known.

IMPORTANT:
The organisation profile is contextual information supplied by the
organisation or demonstration dataset, not external research evidence.
External claims must be supported by the retrieved evidence.
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