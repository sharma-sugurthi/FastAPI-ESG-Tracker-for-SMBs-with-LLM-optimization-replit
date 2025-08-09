"""
User models for authentication and user management.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User model as stored in database."""
    id: str
    hashed_password: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserBase):
    """User model for API responses."""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class TokenData(BaseModel):
    """Token data for validation."""
    user_id: Optional[str] = None
    email: Optional[str] = None

