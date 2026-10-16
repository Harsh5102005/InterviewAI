"""
Question router — direct conversion of com.interview.ai.controller.QuestionController.

Endpoints:
  POST /api/question
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import GenerateQuestionRequest, QuestionResponse
from services import question_service

router = APIRouter(prefix="/api/question", tags=["question"])


@router.post("", response_model=QuestionResponse)
def create_question(req: GenerateQuestionRequest, db: Session = Depends(get_db)):
    """Mirrors QuestionController.createQuestion()."""

    try:
        question = question_service.generate_question(db, req.interviewId)
        return QuestionResponse(id=question.id, questionText=question.question_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
