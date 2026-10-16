"""
Auth router — direct conversion of com.interview.ai.controller.AuthController.

Endpoints:
  POST /api/auth/register
  POST /api/auth/login
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import RegisterRequest, LoginRequest, UserResponse
from services import user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Mirrors AuthController.register()."""
    try:
        user = user_service.register_user(db, req.name, req.email, req.password)
        return UserResponse(id=user.id, name=user.name, email=user.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to register user")


@router.post("/login", response_model=UserResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Mirrors AuthController.login()."""
    try:
        user = user_service.login_user(db, req.email, req.password)
        return UserResponse(id=user.id, name=user.name, email=user.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to log in")
