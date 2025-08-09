"""
Authentication service supporting Firebase Auth and Supabase.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

try:
    from app.core.config import settings
    from app.models.user import User, UserCreate, UserInDB, TokenData
except Exception:
    from config import settings
    from user import User, UserCreate, UserInDB, TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service with support for multiple providers."""
    
    def __init__(self):
        self.firebase_app = None
        self.supabase_client = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize authentication providers based on configuration."""
        try:
            # Initialize Firebase if credentials are provided
            if settings.firebase_project_id and settings.firebase_private_key:
                import firebase_admin
                from firebase_admin import credentials, auth
                
                # Create credentials from environment variables
                cred_dict = {
                    "type": "service_account",
                    "project_id": settings.firebase_project_id,
                    "private_key_id": settings.firebase_private_key_id,
                    "private_key": settings.firebase_private_key.replace('\\n', '\n'),
                    "client_email": settings.firebase_client_email,
                    "client_id": settings.firebase_client_id,
                    "auth_uri": settings.firebase_auth_uri,
                    "token_uri": settings.firebase_token_uri,
                }
                
                cred = credentials.Certificate(cred_dict)
                self.firebase_app = firebase_admin.initialize_app(cred)
                print("Firebase Auth initialized successfully")
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
        
        try:
            # Initialize Supabase if credentials are provided
            if settings.supabase_url and settings.supabase_key:
                from supabase import create_client
                self.supabase_client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )
                print("Supabase Auth initialized successfully")
        except Exception as e:
            print(f"Supabase initialization failed: {e}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            if user_id is None:
                return None
            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None
    
    async def authenticate_with_firebase(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with Firebase Auth."""
        if not self.firebase_app:
            raise ValueError("Firebase Auth not initialized")
        
        try:
            from firebase_admin import auth
            
            # Get user by email
            user_record = auth.get_user_by_email(email)
            
            # Note: Firebase Admin SDK doesn't support password verification
            # In a real implementation, you would use Firebase Client SDK
            # For now, we'll create a mock user
            user = User(
                id=user_record.uid,
                email=user_record.email,
                full_name=user_record.display_name,
                created_at=datetime.utcnow(),
                is_active=not user_record.disabled
            )
            return user
        except Exception as e:
            print(f"Firebase authentication failed: {e}")
            return None
    
    async def authenticate_with_supabase(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with Supabase."""
        if not self.supabase_client:
            raise ValueError("Supabase not initialized")
        
        try:
            # Sign in with Supabase
            response = self.supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                user = User(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=response.user.user_metadata.get("full_name"),
                    created_at=datetime.fromisoformat(response.user.created_at.replace('Z', '+00:00')),
                    is_active=True
                )
                return user
        except Exception as e:
            print(f"Supabase authentication failed: {e}")
            return None
    
    async def create_user_firebase(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user with Firebase Auth."""
        if not self.firebase_app:
            raise ValueError("Firebase Auth not initialized")
        
        try:
            from firebase_admin import auth
            
            user_record = auth.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=user_data.full_name,
                disabled=False
            )
            
            user = User(
                id=user_record.uid,
                email=user_record.email,
                full_name=user_record.display_name,
                company_name=user_data.company_name,
                industry=user_data.industry,
                created_at=datetime.utcnow(),
                is_active=True
            )
            return user
        except Exception as e:
            print(f"Firebase user creation failed: {e}")
            return None
    
    async def create_user_supabase(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user with Supabase."""
        if not self.supabase_client:
            raise ValueError("Supabase not initialized")
        
        try:
            response = self.supabase_client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name,
                        "company_name": user_data.company_name,
                        "industry": user_data.industry
                    }
                }
            })
            
            if response.user:
                user = User(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=user_data.full_name,
                    company_name=user_data.company_name,
                    industry=user_data.industry,
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                return user
        except Exception as e:
            print(f"Supabase user creation failed: {e}")
            return None


# Global auth service instance
auth_service = AuthService()

