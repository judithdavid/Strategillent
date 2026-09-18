from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Organisation
from app.schemas.question import (
    QuestionRequest,
    QuestionResponse,
)
from app.services.question_service import answer_question


router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"],
)


@router.post(
    "/{organisation_id}",
    response_model=QuestionResponse,
)
def ask_question(
    organisation_id: int,
    data: QuestionRequest,
    db: Session = Depends(get_db),
):

    organisation = (
        db.query(Organisation)
        .filter(
            Organisation.id == organisation_id
        )
        .first()
    )

    if organisation is None:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found",
        )

    if not data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    result = answer_question(
        db=db,
        organisation=organisation,
        question=data.question,
    )

    return {
        "question": data.question,
        "answer": result["answer"],
        "evidence_ids": result["evidence_ids"],
        "model_used": result["model_used"],
    }