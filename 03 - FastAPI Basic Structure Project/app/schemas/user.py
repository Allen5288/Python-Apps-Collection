from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List

from .base import BaseSchema


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True

    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v

    @validator('username')
    def username_length(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return v


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str

    @validator('password')
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v

    @validator('password')
    def password_length(cls, v):
        if v and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


class User(BaseSchema, UserBase):
    """Schema for returning user data"""
    pass


class UserList(BaseModel):
    """Schema for paginated user list"""
    users: List[User]
    total: int
    page: int
    per_page: int
    pages: int


class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None
