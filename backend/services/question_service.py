"""
QuestionService — direct conversion of com.interview.ai.service.QuestionService.

This is the most sophisticated service. It handles:
- AI-powered question generation with role/difficulty-specific prompts
- Deduplication against previously asked questions (up to 3 retry attempts)
- Question type rotation (theory, practical, comparison, scenario)
- Difficulty-tiered prompt rules (easy/medium/hard/advanced)
- Text cleaning to strip markdown/numbering from AI output
- Fallback questions when the AI fails
"""

import re
from typing import List, Set

from sqlalchemy.orm import Session

from models import Interview, Question
from services.ai_service import call_ai


# ── Question type rotation list ──────────────────────────────────

_QUESTION_TYPES = [
    "theory/concept",
    "practical explanation",
    "comparison",
    "scenario reasoning",
]


def generate_question(db: Session, interview_id: int) -> Question:
    """Mirrors QuestionService.generateQuestion(interviewId)."""

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise ValueError("Interview not found")

    role = interview.role
    difficulty = _normalize_difficulty(interview.difficulty)

    if not role or not role.strip():
        role = "Java developer"

    previous_questions: List[Question] = (
        db.query(Question)
        .filter(Question.interview_id == interview_id)
        .order_by(Question.id.asc())
        .all()
    )

    previous_texts: Set[str] = {
        _normalize(q.question_text) for q in previous_questions
    }

    ai_question = ""
    for attempt in range(1, 4):  # up to 3 attempts
        raw = call_ai(_build_prompt(role, difficulty, previous_questions, attempt))
        cleaned = _clean_text(raw)
        if cleaned.strip() and _normalize(cleaned) not in previous_texts:
            ai_question = cleaned
            break
        ai_question = ""

    if not ai_question.strip():
        ai_question = _fallback_question(len(previous_questions), difficulty, role)

    question = Question()
    question.set_question_text(ai_question)
    question.interview_id = interview_id

    db.add(question)
    db.commit()
    db.refresh(question)
    return question


# ── Prompt building ──────────────────────────────────────────────

def _build_prompt(role: str, difficulty: str, previous_questions: List[Question], attempt: int) -> str:
    """Mirrors QuestionService.buildPrompt(role, difficulty, previousQuestions, attempt)."""

    if previous_questions:
        previous = "\n".join(f"- {q.question_text}" for q in previous_questions)
    else:
        previous = "None"

    question_type = _question_type(len(previous_questions), attempt)

    return (
        f"Generate ONE unique {difficulty} level interview question for the exact role: {role}.\n"
        f"The question must be about {role} skills only. Do not switch to Java unless the role itself asks for Java.\n"
        f"{_difficulty_rules(difficulty)}\n"
        f"Question type for this request: {question_type}.\n"
        f"{_question_type_rules(question_type)}\n"
        f"Do not repeat or closely rephrase any previous question.\n"
        f"Previous questions:\n{previous}\n"
        f"Use a different topic from the selected role than the previous questions when possible.\n"
        f"Question number: {len(previous_questions) + 1}\n"
        f"Variation attempt: {attempt}\n"
        f"Do NOT include headings, difficulty labels, numbering, markdown, or formatting like **.\n"
        f"Return only the question in plain text."
    )


def _normalize_difficulty(difficulty: str | None) -> str:
    """Mirrors QuestionService.normalizeDifficulty(difficulty)."""
    if not difficulty or not difficulty.strip():
        return "medium"

    normalized = difficulty.lower().strip()
    if normalized in ("easy", "medium", "hard", "advanced"):
        return normalized
    return "medium"


def _difficulty_rules(difficulty: str) -> str:
    """Mirrors QuestionService.difficultyRules(difficulty)."""
    rules = {
        "easy": (
            "Difficulty rules: ask a beginner-friendly question about one basic concept from the selected role. "
            "Avoid algorithms, system design, low-level internals, advanced performance tuning, complex framework internals, and code-writing tasks. "
            "The question should be answerable in 2-4 simple sentences."
        ),
        "hard": (
            "Difficulty rules: ask a senior-level question that requires tradeoffs, edge cases, or deeper role-specific reasoning. "
            "It may involve design, performance, debugging, architecture, or testing when relevant to the role, but keep it answerable verbally."
        ),
        "advanced": (
            "Difficulty rules: ask an expert-level question involving role-specific internals, production tradeoffs, "
            "architecture, failure analysis, or advanced debugging."
        ),
    }
    return rules.get(
        difficulty,
        "Difficulty rules: ask an intermediate question. It can include practical examples, but should not require writing a full program.",
    )


def _question_type(previous_count: int, attempt: int) -> str:
    """Mirrors QuestionService.questionType(previousCount, attempt)."""
    return _QUESTION_TYPES[(previous_count + attempt - 1) % len(_QUESTION_TYPES)]


def _question_type_rules(question_type: str) -> str:
    """Mirrors QuestionService.questionTypeRules(questionType)."""
    rules = {
        "theory/concept": "Ask what a concept means, why it exists, or how it works. Do not ask the candidate to write code or implement a method.",
        "comparison": "Ask the candidate to compare two related concepts from the selected role. Do not ask for code.",
        "scenario reasoning": "Ask what the candidate would choose or explain in a small realistic situation. Do not ask for a full implementation.",
    }
    return rules.get(
        question_type,
        "Ask for a practical verbal explanation. A small example is okay, but do not ask for a complete code solution.",
    )


# ── Text cleaning ────────────────────────────────────────────────

def _clean_text(text: str | None) -> str:
    """Mirrors QuestionService.cleanText(text)."""
    if not text:
        return ""

    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"(?i)^question\s*\d*\s*[:.)\-]\s*", "", text)
    text = re.sub(r"(?i)null difficulty level[:\-]*", "", text)
    return text.strip()


def _normalize(text: str | None) -> str:
    """Mirrors QuestionService.normalize(text)."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Fallback questions ───────────────────────────────────────────

def _fallback_question(previous_count: int, difficulty: str, role: str) -> str:
    """Mirrors QuestionService.fallbackQuestion(previousCount, difficulty, role)."""
    topics = _fallback_topics(difficulty)
    topic = topics[previous_count % len(topics)]
    return f"For a {role}, {topic}"


def _fallback_topics(difficulty: str) -> List[str]:
    """Mirrors QuestionService.fallbackTopics(difficulty)."""
    topics = {
        "easy": [
            "what is one basic concept every beginner in this role should understand?",
            "what is the purpose of a common tool or language feature used in this role?",
            "how would you explain a simple workflow used in this role?",
            "what is the difference between two beginner-level concepts in this role?",
            "why is clear structure important when working in this role?",
            "what is a common beginner mistake in this role?",
        ],
        "hard": [
            "what tradeoffs would you consider when solving a complex problem in this role?",
            "how would you debug a production issue related to this role?",
            "how would you choose between two valid approaches in this role?",
            "how would you keep work maintainable when requirements become complex?",
            "what risks would you look for before shipping a role-specific change?",
        ],
        "advanced": [
            "how would you diagnose a difficult production issue in this role?",
            "what architecture tradeoffs matter most for advanced work in this role?",
            "how would you design a resilient solution for a failure-prone workflow?",
            "how would you evaluate performance bottlenecks in this role?",
            "what advanced mistakes can create long-term maintenance problems in this role?",
        ],
    }
    return topics.get(difficulty, [
        "explain an important concept used in this role with a practical example.",
        "what is the difference between two commonly confused concepts in this role?",
        "how would you approach a typical task in this role?",
        "what quality checks matter before completing work in this role?",
        "how would you explain a common tool or pattern used in this role?",
    ])
