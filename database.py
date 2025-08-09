
"""
Database setup with PostgreSQL support for production.
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

try:
    from config import settings
except ImportError:
    from app.core.config import settings

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ESGAssessment(Base):
    __tablename__ = "esg_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    assessment_data = Column(JSON, nullable=False)
    overall_score = Column(Float, nullable=False)
    category_scores = Column(JSON, nullable=True)
    badge = Column(String, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    priority = Column(String, default="medium")
    status = Column(String, default="pending")
    points = Column(Integer, default=10)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    severity = Column(String, default="medium")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class IndustryTemplate(Base):
    __tablename__ = "industry_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, nullable=False, index=True)
    template_name = Column(String, nullable=False)
    questions = Column(JSON, nullable=False)
    scoring_weights = Column(JSON, nullable=False)
    compliance_requirements = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database connection setup
def get_database_url():
    """Get database URL, preferring PostgreSQL if available."""
    # Check for Replit PostgreSQL database
    if os.getenv('DATABASE_URL'):
        return os.getenv('DATABASE_URL')
    
    # Fallback to SQLite for development
    return "sqlite:///./esg_tracker.db"

# Create engine
DATABASE_URL = get_database_url()
if DATABASE_URL.startswith("postgresql://"):
    # Use PostgreSQL with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600
    )
else:
    # Use SQLite for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on import
create_tables()
