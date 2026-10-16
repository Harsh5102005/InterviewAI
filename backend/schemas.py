"""
Pydantic schemas — equivalent of the DTOs / request/response Maps used in the Java controllers.
Replaces the raw Map<String, Object> approach from the Spring Boot version.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ── Auth ─────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None


# ── Interview ────────────────────────────────────────────────────

class StartInterviewRequest(BaseModel):
    userId: Optional[int] = None
    role: str = "Java developer"
    difficulty: str = "medium"


class InterviewResponse(BaseModel):
    id: int
    role: Optional[str] = None
    difficulty: Optional[str] = None
    startTime: Optional[str] = None


class InterviewSummary(BaseModel):
    id: int
    role: Optional[str] = None
    difficulty: Optional[str] = None
    startTime: Optional[str] = None
    totalQuestions: int = 0
    answeredQuestions: int = 0
    avgScore: Optional[float] = None


# ── Question ─────────────────────────────────────────────────────

class GenerateQuestionRequest(BaseModel):
    interviewId: int


class QuestionResponse(BaseModel):
    id: int
    questionText: Optional[str] = None


# ── Answer ───────────────────────────────────────────────────────

class SubmitAnswerRequest(BaseModel):
    questionId: int
    answerText: str = ""


class AnswerResponse(BaseModel):
    id: int
    answerText: Optional[str] = None
    feedback: Optional[str] = None
    score: int = 0


# ── History ──────────────────────────────────────────────────────

class HistoryItem(BaseModel):
    questionId: int
    questionText: Optional[str] = None
    answerText: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
