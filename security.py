"""
Security utilities and dependencies for authentication.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

try:
    from app.services.auth_service import auth_service
    from app.models.user import User, TokenData
except Exception:
    from auth_service import auth_service
    from user import User, TokenData

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        token_data = auth_service.verify_token(credentials.credentials)
        if token_data is None or token_data.user_id is None:
            raise credentials_exception
        
        # In a real implementation, you would fetch the user from database
        # For now, we'll create a mock user based on token data
        user = User(
            id=token_data.user_id,
            email=token_data.email or "",
            created_at=None,
            is_active=True
        )
        
        return user
    except JWTError:
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def create_user_session(user: User) -> dict:
    """
    Create a user session with JWT token.
    """
    from datetime import timedelta
    try:
        from app.core.config import settings
    except Exception:
        from config import settings
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": user
    }

