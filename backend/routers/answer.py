"""
Answer router — direct conversion of com.interview.ai.controller.AnswerController.

Endpoints:
  POST /api/answer
  GET  /api/answer/history/{interviewId}
"""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import SubmitAnswerRequest, AnswerResponse
from services import answer_service

router = APIRouter(prefix="/api/answer", tags=["answer"])


@router.post("", response_model=AnswerResponse)
def submit_answer(req: SubmitAnswerRequest, db: Session = Depends(get_db)):
    """Mirrors AnswerController.submitAnswer()."""
    try:
        answer = answer_service.submit_answer(db, req.questionId, req.answerText)
        return AnswerResponse(
            id=answer.id,
            answerText=answer.answer_text,
            feedback=answer.feedback,
            score=answer.score,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{interview_id}")
def get_history(interview_id: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Mirrors AnswerController.getHistory()."""
    return answer_service.get_history_by_interview_id(db, interview_id)
