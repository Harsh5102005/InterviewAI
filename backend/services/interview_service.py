"""
InterviewService — direct conversion of com.interview.ai.service.InterviewService.

Handles interview session creation and retrieval of user interview history
with enriched stats (question count, answered count, average score).
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from models import Interview, User, Question, Answer


def start_interview(db: Session, user_id: Optional[int], role: str, difficulty: str) -> Interview:
    """Mirrors InterviewService.startInterview(userId, role, difficulty)."""

    interview = Interview(
        role=role,
        difficulty=difficulty,
        start_time=datetime.now(),
    )

    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        interview.user = user

    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def get_interviews_by_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Mirrors InterviewService.getInterviewsByUser(userId).
    Returns enriched interview summaries with question/answer stats.
    """

    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == user_id)
        .order_by(Interview.start_time.desc())
        .all()
    )

    result = []
    for interview in interviews:
        questions = (
            db.query(Question)
            .filter(Question.interview_id == interview.id)
            .order_by(Question.id.asc())
            .all()
        )

        total_questions = len(questions)

        scores = []
        answered_count = 0
        for q in questions:
            answer = db.query(Answer).filter(Answer.question_id == q.id).first()
            if answer is not None:
                answered_count += 1
                scores.append(answer.score)

        avg_score = None
        if scores:
            avg_score = round(sum(scores) / len(scores), 1)

        result.append({
            "id": interview.id,
            "role": interview.role,
            "difficulty": interview.difficulty,
            "startTime": interview.start_time.isoformat() if interview.start_time else None,
            "totalQuestions": total_questions,
            "answeredQuestions": answered_count,
            "avgScore": avg_score,
        })

    return result
