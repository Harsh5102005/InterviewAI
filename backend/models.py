"""
SQLAlchemy ORM models — direct conversion of the JPA @Entity classes.
Table/column names match the existing MySQL schema created by Hibernate's ddl-auto=update.
"""

from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """Mirrors com.interview.ai.entities.User"""

    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)

    interviews = relationship("Interview", back_populates="user")


class Interview(Base):
    """Mirrors com.interview.ai.entities.Interview"""

    __tablename__ = "interview"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role = Column(String(255), nullable=True)
    difficulty = Column(String(255), nullable=True)
    start_time = Column("start_time", DateTime, nullable=True)

    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="interviews")

    questions = relationship("Question", back_populates="interview", order_by="Question.id")


class Question(Base):
    """Mirrors com.interview.ai.entities.Question"""

    __tablename__ = "question"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question_text = Column("question_text", Text, nullable=True)

    interview_id = Column(BigInteger, ForeignKey("interview.id"), nullable=True)
    interview = relationship("Interview", back_populates="questions")

    answer = relationship("Answer", back_populates="question", uselist=False)

    def set_question_text(self, text: str):
        """Mirrors the custom setter in the Java entity."""
        self.question_text = "" if text is None else text.strip()


class Answer(Base):
    """Mirrors com.interview.ai.entities.Answer"""

    __tablename__ = "answer"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    answer_text = Column("answer_text", Text, nullable=True)
    feedback = Column(Text, nullable=True)
    score = Column(Integer, default=0)

    question_id = Column(BigInteger, ForeignKey("question.id"), nullable=True)
    question = relationship("Question", back_populates="answer")


class Result(Base):
    """
    Mirrors com.interview.ai.entities.Result.
    Note: This entity exists in the original Java code but is never used anywhere.
    Kept here for schema compatibility.
    """

    __tablename__ = "result"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    total_score = Column("total_score", Integer, default=0)
    final_feedback = Column("final_feedback", String(255), nullable=True)

    interview_id = Column(BigInteger, ForeignKey("interview.id"), nullable=True)
    interview = relationship("Interview")
