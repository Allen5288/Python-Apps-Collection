from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_active_user
from ..models.user import User


def get_db_session() -> Generator:
    """Get database session dependency"""
    return get_db()


def get_current_user_dep() -> User:
    """Get current user dependency"""
    return get_current_active_user
