from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password
from ..core.exceptions import ConflictException, NotFoundException, AuthenticationException
from .base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """User service with authentication logic"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, user_in: UserCreate) -> User:
        """Create a new user with hashed password"""
        # Check if user already exists
        if self.get_by_email(db, user_in.email):
            raise ConflictException("Email already registered")
        
        if self.get_by_username(db, user_in.username):
            raise ConflictException("Username already taken")
        
        # Create user with hashed password
        user_data = user_in.dict()
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(self, db: Session, db_user: User, user_in: UserUpdate) -> User:
        """Update user with validation"""
        user_data = user_in.dict(exclude_unset=True)
        
        # Check email uniqueness if updating email
        if "email" in user_data and user_data["email"] != db_user.email:
            if self.get_by_email(db, user_data["email"]):
                raise ConflictException("Email already registered")
        
        # Check username uniqueness if updating username
        if "username" in user_data and user_data["username"] != db_user.username:
            if self.get_by_username(db, user_data["username"]):
                raise ConflictException("Username already taken")
        
        # Hash password if updating
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        for field, value in user_data.items():
            setattr(db_user, field, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users only"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def deactivate_user(self, db: Session, user_id: int) -> User:
        """Deactivate a user instead of deleting"""
        user = self.get(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# Create service instance
user_service = UserService()
