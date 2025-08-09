"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

try:
    from app.models.user import User, UserCreate, UserLogin, Token
    from app.services.auth_service import auth_service
    from app.core.security import get_current_active_user, create_user_session
except Exception:
    from user import User, UserCreate, UserLogin, Token
    from auth_service import auth_service
    from security import get_current_active_user, create_user_session

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    Supports both Firebase Auth and Supabase based on configuration.
    """
    try:
        # Try Firebase first if available
        if auth_service.firebase_app:
            user = await auth_service.create_user_firebase(user_data)
            if user:
                return create_user_session(user)
        
        # Try Supabase if Firebase failed or not available
        if auth_service.supabase_client:
            user = await auth_service.create_user_supabase(user_data)
            if user:
                return create_user_session(user)
        
        # If no auth provider is available, create a local user (for development)
        if not auth_service.firebase_app and not auth_service.supabase_client:
            # Create a mock user for development
            from datetime import datetime
            user = User(
                id=f"local_{user_data.email.replace('@', '_').replace('.', '_')}",
                email=user_data.email,
                full_name=user_data.full_name,
                company_name=user_data.company_name,
                industry=user_data.industry,
                created_at=datetime.utcnow(),
                is_active=True
            )
            return create_user_session(user)
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Authenticate user and return access token.
    
    Supports both Firebase Auth and Supabase based on configuration.
    """
    try:
        user = None
        
        # Try Firebase authentication first if available
        if auth_service.firebase_app:
            user = await auth_service.authenticate_with_firebase(
                user_credentials.email, 
                user_credentials.password
            )
        
        # Try Supabase if Firebase failed or not available
        if not user and auth_service.supabase_client:
            user = await auth_service.authenticate_with_supabase(
                user_credentials.email, 
                user_credentials.password
            )
        
        # For development, create a mock user if no auth provider is available
        if not user and not auth_service.firebase_app and not auth_service.supabase_client:
            from datetime import datetime
            user = User(
                id=f"local_{user_credentials.email.replace('@', '_').replace('.', '_')}",
                email=user_credentials.email,
                full_name="Development User",
                created_at=datetime.utcnow(),
                is_active=True
            )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return create_user_session(user)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout current user.
    
    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by removing the token. In a production environment, you might want to
    implement token blacklisting.
    """
    return {"message": "Successfully logged out"}


@router.get("/providers")
async def get_auth_providers():
    """
    Get available authentication providers.
    """
    providers = []
    
    if auth_service.firebase_app:
        providers.append("firebase")
    
    if auth_service.supabase_client:
        providers.append("supabase")
    
    if not providers:
        providers.append("local")  # Development mode
    
    return {
        "providers": providers,
        "default": providers[0] if providers else "local"
    }

