"""
Interview router — direct conversion of com.interview.ai.controller.InterviewController.

Endpoints:
  POST /api/interview/start
  GET  /api/interview/{interviewId}/history
  GET  /api/interview/user/{userId}
"""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import StartInterviewRequest, InterviewResponse
from services import interview_service, answer_service

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/start", response_model=InterviewResponse)
def start_interview(req: StartInterviewRequest, db: Session = Depends(get_db)):
    """Mirrors InterviewController.startInterview()."""
    interview = interview_service.start_interview(
        db,
        user_id=req.userId,
        role=req.role or "Java developer",
        difficulty=req.difficulty or "medium",
    )
    return InterviewResponse(
        id=interview.id,
        role=interview.role,
        difficulty=interview.difficulty,
        startTime=interview.start_time.isoformat() if interview.start_time else None,
    )


@router.get("/{interview_id}/history")
def get_interview_history(interview_id: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Mirrors InterviewController.getInterviewHistory()."""
    return answer_service.get_history_by_interview_id(db, interview_id)


@router.get("/user/{user_id}")
def get_user_interviews(user_id: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Mirrors InterviewController.getUserInterviews()."""
    return interview_service.get_interviews_by_user(db, user_id)
