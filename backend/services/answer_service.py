"""
AnswerService — direct conversion of com.interview.ai.service.AnswerService.

Handles:
- Pre-AI answer validation (non-answer, question repetition, unrelatedness)
- AI-powered answer evaluation with rubric scoring (0-10)
- AI response parsing (JSON-first with regex fallback)
- Answer history retrieval
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set

from sqlalchemy.orm import Session

from models import Question, Answer
from services.ai_service import call_ai


# ── Constants ────────────────────────────────────────────────────

STOP_WORDS: Set[str] = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "the", "to", "what", "when", "where", "why",
    "with", "you", "your", "explain", "define", "describe", "difference", "between",
}

UNCERTAIN_ANSWER_PATTERN = re.compile(
    r"\b(i do not know|i dont know|dont know|do not know|no idea|not sure|cannot answer|cant answer|skip|pass)\b"
)


@dataclass
class Evaluation:
    """Mirrors the Java record Evaluation(int score, String feedback)."""
    score: int
    feedback: str


# ── Public API ───────────────────────────────────────────────────

def submit_answer(db: Session, question_id: int, answer_text: str) -> Answer:
    """Mirrors AnswerService.submitAnswer(questionId, answerText)."""

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError("Question not found")

    submitted = answer_text.strip() if answer_text else ""

    # Pre-AI validation — saves API calls for obviously bad answers
    if _is_non_answer(submitted):
        return _save_answer(
            db, question, submitted, 0,
            "The answer does not provide enough information to evaluate. Please explain the concept in your own words.",
        )

    if _is_question_repeated(question.question_text, submitted):
        return _save_answer(
            db, question, submitted, 0,
            "Repeating the question is not an answer. Explain the concept or reasoning in your own words.",
        )

    if _is_likely_unrelated(question.question_text, submitted):
        return _save_answer(
            db, question, submitted, 0,
            "The answer appears unrelated to the question. Address the topic asked before submitting.",
        )

    # Determine role for the grading prompt
    role = "the selected role"
    if (
        question.interview_id is not None
        and question.interview is not None
        and question.interview.role
        and question.interview.role.strip()
    ):
        role = question.interview.role.strip()

    prompt = (
        f"You are grading an interview candidate for this role: {role}.\n\n"
        f"Grade only the candidate answer. Do not answer the question yourself.\n"
        f"Give credit only for concepts that are explicitly present in the candidate answer.\n"
        f"Grade according to the role and question topic, not as a Java-only interview unless the role or question is about Java.\n"
        f"Penalize vague answers, memorized buzzwords without explanation, factual errors, and unrelated content.\n"
        f"If the candidate answer is blank, says they do not know, repeats the question, or is unrelated, score must be 0.\n\n"
        f"Use this rubric:\n"
        f"0 = no answer, unrelated, repeated question, or \"I don't know\"\n"
        f"1-3 = mostly incorrect or too vague\n"
        f"4-6 = partially correct but missing important points\n"
        f"7-8 = mostly correct with minor gaps\n"
        f"9-10 = complete, accurate, and clear\n\n"
        f"Return only valid JSON in this exact shape:\n"
        f'{{\"score\":0,\"feedback\":\"short, specific feedback\"}}\n\n'
        f"Question: {question.question_text}\n"
        f"Candidate answer: {submitted}"
    )

    ai_response = call_ai(prompt)
    evaluation = _parse_evaluation(ai_response)

    return _save_answer(db, question, submitted, evaluation.score, evaluation.feedback)


def get_history_by_interview_id(db: Session, interview_id: int) -> List[Dict[str, Any]]:
    """Mirrors AnswerService.getHistoryByInterviewId(interviewId)."""

    questions = (
        db.query(Question)
        .filter(Question.interview_id == interview_id)
        .order_by(Question.id.asc())
        .all()
    )

    result = []
    for q in questions:
        answer = db.query(Answer).filter(Answer.question_id == q.id).first()

        item: Dict[str, Any] = {
            "questionId": q.id,
            "questionText": q.question_text,
        }

        if answer is not None:
            item["answerText"] = answer.answer_text
            item["score"] = answer.score
            item["feedback"] = answer.feedback
        else:
            item["answerText"] = None
            item["score"] = None
            item["feedback"] = None

        result.append(item)

    return result


# ── Save helper ──────────────────────────────────────────────────

def _save_answer(
    db: Session,
    question: Question,
    submitted_answer: str,
    score: int,
    feedback: str | None,
) -> Answer:
    """Mirrors AnswerService.saveAnswer(question, submittedAnswer, score, feedback)."""

    answer = db.query(Answer).filter(Answer.question_id == question.id).first()
    if answer is None:
        answer = Answer()

    answer.question_id = question.id
    answer.answer_text = submitted_answer
    answer.score = max(0, min(10, score))
    answer.feedback = (
        feedback.strip()
        if feedback and feedback.strip()
        else "Unable to evaluate the answer. Please try again with a clearer response."
    )

    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


# ── Pre-AI validation ────────────────────────────────────────────

def _is_non_answer(answer_text: str) -> bool:
    """Mirrors AnswerService.isNonAnswer(answerText)."""
    if not answer_text.strip():
        return True

    normalized = re.sub(r"[^a-z0-9\s]", " ", answer_text.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()

    words = normalized.split()
    word_count = len(words)

    if word_count < 3:
        return True

    return word_count <= 8 and bool(UNCERTAIN_ANSWER_PATTERN.search(normalized))


def _is_question_repeated(question_text: str, answer_text: str) -> bool:
    """Mirrors AnswerService.isQuestionRepeated(questionText, answerText)."""
    q = _normalize(question_text)
    a = _normalize(answer_text)
    return bool(q) and q == a


def _is_likely_unrelated(question_text: str, answer_text: str) -> bool:
    """Mirrors AnswerService.isLikelyUnrelated(questionText, answerText)."""
    question_terms = _meaningful_terms(question_text)
    answer_terms = _meaningful_terms(answer_text)

    if not question_terms or len(answer_terms) < 2:
        return False

    shared = sum(1 for t in answer_terms if t in question_terms)
    return shared == 0 and len(answer_terms) <= 8


def _meaningful_terms(text: str) -> Set[str]:
    """Mirrors AnswerService.meaningfulTerms(text)."""
    normalized = _normalize(text)
    return {
        match.group()
        for match in re.finditer(r"[a-z0-9]+", normalized)
        if len(match.group()) > 2 and match.group() not in STOP_WORDS
    }


def _normalize(text: str | None) -> str:
    """Mirrors AnswerService.normalize(text)."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── AI response parsing ─────────────────────────────────────────

def _parse_evaluation(text: str) -> Evaluation:
    """Mirrors AnswerService.parseEvaluation(text)."""
    json_eval = _parse_json_evaluation(text)
    if json_eval is not None:
        return json_eval
    return Evaluation(score=_extract_score(text), feedback=_extract_feedback(text))


def _parse_json_evaluation(text: str | None) -> Optional[Evaluation]:
    """Mirrors AnswerService.parseJsonEvaluation(text)."""
    if not text or not text.strip():
        return None

    json_str = _extract_json_object(text)

    score_match = re.search(r'"score"\s*:\s*(\d{1,2})', json_str, re.IGNORECASE)
    if not score_match:
        return None

    score = int(score_match.group(1))

    feedback = ""
    feedback_match = re.search(r'"feedback"\s*:\s*"((?:\\.|[^"])*)"', json_str, re.IGNORECASE)
    if feedback_match:
        feedback = _unescape_json_string(feedback_match.group(1))

    return Evaluation(score=max(0, min(10, score)), feedback=feedback)


def _extract_json_object(text: str) -> str:
    """Mirrors AnswerService.extractJsonObject(text)."""
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start:end + 1]
    return text


def _unescape_json_string(value: str) -> str:
    """Mirrors AnswerService.unescapeJsonString(value)."""
    return (
        value.replace('\\"', '"')
        .replace("\\\\", "\\")
        .replace("\\n", " ")
        .replace("\\r", " ")
        .replace("\\t", " ")
        .strip()
    )


def _extract_score(text: str | None) -> int:
    """Mirrors AnswerService.extractScore(text)."""
    if not text or not text.strip():
        return 0

    match = re.search(r"(?i)score\s*[:=]?\s*(\d{1,2})(?:\s*/\s*10)?", text)
    if not match:
        return 0

    score = int(match.group(1))
    return max(0, min(10, score))


def _extract_feedback(text: str | None) -> str:
    """Mirrors AnswerService.extractFeedback(text)."""
    if not text or not text.strip():
        return ""

    match = re.search(r"(?is)feedback\s*:\s*(.*)", text)
    if match:
        return match.group(1).strip()

    return text.strip()
