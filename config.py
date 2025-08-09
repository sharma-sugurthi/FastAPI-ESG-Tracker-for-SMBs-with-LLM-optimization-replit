"""
Configuration settings for the ESG Compliance Tracker application.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    app_name: str = "ESG Compliance Tracker"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_url: Optional[str] = None
    
    # Authentication Configuration
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Firebase Configuration
    firebase_project_id: Optional[str] = None
    firebase_private_key_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    firebase_client_id: Optional[str] = None
    firebase_auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    firebase_token_uri: str = "https://oauth2.googleapis.com/token"
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # LLM Configuration
    model_provider: str = "groq"
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    replicate_api_token: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    
    # News API Configuration
    news_api_key: Optional[str] = None
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # File Upload Configuration
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"
    
    # ESG Scoring Configuration
    emissions_weight: float = 0.4
    dei_weight: float = 0.3
    packaging_weight: float = 0.3
    
    @validator("model_provider")
    def validate_model_provider(cls, v):
        """Validate that the model provider is supported."""
        allowed_providers = ["groq", "gemini", "openai", "replicate", "ollama"]
        if v not in allowed_providers:
            raise ValueError(f"Model provider must be one of: {allowed_providers}")
        return v
    
    @validator("emissions_weight", "dei_weight", "packaging_weight")
    def validate_weights(cls, v):
        """Validate that weights are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Weights must be between 0 and 1")
        return v
    
    def validate_weights_sum(self):
        """Validate that all weights sum to 1.0."""
        total = self.emissions_weight + self.dei_weight + self.packaging_weight
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f"ESG weights must sum to 1.0, got {total}")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()

# Validate weights sum on startup
try:
    settings.validate_weights_sum()
except ValueError as e:
    print(f"Warning: {e}")
    # Auto-adjust weights to sum to 1.0
    total = settings.emissions_weight + settings.dei_weight + settings.packaging_weight
    settings.emissions_weight /= total
    settings.dei_weight /= total
    settings.packaging_weight /= total
    print(f"Auto-adjusted weights: emissions={settings.emissions_weight:.2f}, "
          f"dei={settings.dei_weight:.2f}, packaging={settings.packaging_weight:.2f}")

