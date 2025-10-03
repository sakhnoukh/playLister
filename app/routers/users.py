"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse)
def create_or_get_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Create a new user or return existing user by name (idempotent)."""
    # Check if user already exists
    statement = select(User).where(User.name == user_data.name)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        return existing_user
    
    # Create new user
    user = User(name=user_data.name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get user by ID."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
