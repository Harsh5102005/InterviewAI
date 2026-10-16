"""
UserService — direct conversion of com.interview.ai.service.UserService.

Handles registration and login with the same validation logic.
Passwords are stored as plaintext to match the existing Java implementation
and remain compatible with data already in the database.
"""

from sqlalchemy.orm import Session
from models import User


def register_user(db: Session, name: str, email: str, password: str) -> User:
    """Mirrors UserService.registerUser(name, email, password)."""

    if not name or not name.strip():
        raise ValueError("Name is required")
    if not email or not email.strip():
        raise ValueError("Email is required")
    if not password or not password.strip():
        raise ValueError("Password is required")

    normalized_email = email.strip().lower()

    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise ValueError("An account with this email already exists")

    user = User(
        name=name.strip(),
        email=normalized_email,
        password=password.strip(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> User:
    """Mirrors UserService.loginUser(email, password)."""

    if not email or not email.strip():
        raise ValueError("Email is required")
    if not password or not password.strip():
        raise ValueError("Password is required")

    normalized_email = email.strip().lower()

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        raise ValueError("No account found with this email")

    if user.password != password.strip():
        raise ValueError("Incorrect password")

    return user
