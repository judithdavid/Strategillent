from sqlalchemy.orm import Session

from app.models import Organisation

from app.retrieval.search import search_evidence
from app.ai.answer_generator import generate_answer


def answer_question(
    db: Session,
    organisation: Organisation,
    question: str,
):

    evidence_records = search_evidence(
        db=db,
        query=question,
        limit=6,
    )

    result = generate_answer(
        organisation=organisation,
        evidence_records=evidence_records,
        question=question,
    )

    return result