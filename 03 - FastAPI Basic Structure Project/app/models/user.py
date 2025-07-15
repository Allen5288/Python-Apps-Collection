from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    bio = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
