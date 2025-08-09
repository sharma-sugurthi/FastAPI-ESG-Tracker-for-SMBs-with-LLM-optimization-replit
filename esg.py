"""
ESG (Environmental, Social, Governance) data models.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ESGCategory(str, Enum):
    """ESG categories."""
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"


class QuestionType(str, Enum):
    """Question types for ESG questionnaire."""
    NUMERIC = "numeric"
    PERCENTAGE = "percentage"
    BOOLEAN = "boolean"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"


class ESGQuestion(BaseModel):
    """ESG questionnaire question model."""
    id: str
    category: ESGCategory
    question: str
    question_type: QuestionType
    unit: Optional[str] = None
    options: Optional[List[str]] = None  # For multiple choice questions
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    industry_default: Optional[Any] = None
    help_text: Optional[str] = None
    required: bool = True


class ESGAnswer(BaseModel):
    """ESG questionnaire answer model."""
    question_id: str
    value: Optional[Any] = None
    is_llm_suggested: bool = False
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source: Optional[str] = None  # Source of the data (user input, LLM, industry default)


class ESGQuestionnaire(BaseModel):
    """Complete ESG questionnaire model."""
    user_id: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    answers: List[ESGAnswer]
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ESGScore(BaseModel):
    """ESG scoring result model."""
    overall_score: float = Field(ge=0.0, le=100.0)
    environmental_score: float = Field(ge=0.0, le=100.0)
    social_score: float = Field(ge=0.0, le=100.0)
    governance_score: float = Field(ge=0.0, le=100.0)
    badge: str
    improvement_areas: List[str]
    strengths: List[str]
    calculated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ESGMetrics(BaseModel):
    """ESG metrics for retail SMBs."""
    # Environmental metrics
    annual_energy_consumption: Optional[float] = Field(default=None, description="kWh per year")
    co2_emissions: Optional[float] = Field(default=None, description="tonnes CO2 per year")
    water_usage: Optional[float] = Field(default=None, description="liters per year")
    waste_generated: Optional[float] = Field(default=None, description="kg per year")
    recycling_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="percentage")
    renewable_energy_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="percentage")
    packaging_recyclability: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="percentage")
    
    # Social metrics
    employee_count: Optional[int] = Field(default=None, ge=0)
    diversity_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="DEI percentage")
    female_leadership_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="percentage")
    training_hours_per_employee: Optional[float] = Field(default=None, ge=0.0, description="hours per year")
    employee_satisfaction_score: Optional[float] = Field(default=None, ge=0.0, le=10.0, description="1-10 scale")
    community_investment: Optional[float] = Field(default=None, ge=0.0, description="USD per year")
    
    # Governance metrics
    board_independence: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="percentage")
    ethics_training_completion: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="percentage")
    data_privacy_compliance: Optional[bool] = Field(default=None, description="GDPR/CCPA compliance")
    supplier_code_of_conduct: Optional[bool] = Field(default=None, description="has supplier code")
    transparency_reporting: Optional[bool] = Field(default=None, description="publishes ESG reports")


# Default ESG questions for retail SMBs
DEFAULT_ESG_QUESTIONS = [
    ESGQuestion(
        id="energy_consumption",
        category=ESGCategory.ENVIRONMENTAL,
        question="What is your annual energy consumption?",
        question_type=QuestionType.NUMERIC,
        unit="kWh",
        weight=0.15,
        industry_default=50000,
        help_text="Include electricity, gas, and other energy sources used in your operations"
    ),
    ESGQuestion(
        id="co2_emissions",
        category=ESGCategory.ENVIRONMENTAL,
        question="What are your annual CO2 emissions?",
        question_type=QuestionType.NUMERIC,
        unit="tonnes CO2",
        weight=0.20,
        industry_default=10,
        help_text="Include direct and indirect emissions from your business operations"
    ),
    ESGQuestion(
        id="packaging_recyclability",
        category=ESGCategory.ENVIRONMENTAL,
        question="What percentage of your packaging is recyclable?",
        question_type=QuestionType.PERCENTAGE,
        unit="%",
        weight=0.15,
        industry_default=60,
        help_text="Percentage of product packaging that can be recycled by consumers"
    ),
    ESGQuestion(
        id="diversity_percentage",
        category=ESGCategory.SOCIAL,
        question="What is your workforce diversity percentage (DEI)?",
        question_type=QuestionType.PERCENTAGE,
        unit="%",
        weight=0.15,
        industry_default=35,
        help_text="Percentage of employees from underrepresented groups"
    ),
    ESGQuestion(
        id="female_leadership",
        category=ESGCategory.SOCIAL,
        question="What percentage of leadership positions are held by women?",
        question_type=QuestionType.PERCENTAGE,
        unit="%",
        weight=0.10,
        industry_default=30,
        help_text="Percentage of management and executive roles held by women"
    ),
    ESGQuestion(
        id="employee_satisfaction",
        category=ESGCategory.SOCIAL,
        question="What is your employee satisfaction score?",
        question_type=QuestionType.NUMERIC,
        unit="1-10 scale",
        weight=0.10,
        industry_default=7.5,
        help_text="Average employee satisfaction rating from surveys (1-10 scale)"
    ),
    ESGQuestion(
        id="data_privacy_compliance",
        category=ESGCategory.GOVERNANCE,
        question="Are you compliant with data privacy regulations (GDPR/CCPA)?",
        question_type=QuestionType.BOOLEAN,
        weight=0.05,
        industry_default=True,
        help_text="Do you have proper data privacy policies and procedures in place?"
    ),
    ESGQuestion(
        id="ethics_training",
        category=ESGCategory.GOVERNANCE,
        question="What percentage of employees completed ethics training?",
        question_type=QuestionType.PERCENTAGE,
        unit="%",
        weight=0.05,
        industry_default=85,
        help_text="Percentage of employees who completed ethics and compliance training"
    ),
    ESGQuestion(
        id="supplier_code",
        category=ESGCategory.GOVERNANCE,
        question="Do you have a supplier code of conduct?",
        question_type=QuestionType.BOOLEAN,
        weight=0.03,
        industry_default=False,
        help_text="Do you require suppliers to follow ethical and sustainable practices?"
    ),
    ESGQuestion(
        id="transparency_reporting",
        category=ESGCategory.GOVERNANCE,
        question="Do you publish ESG or sustainability reports?",
        question_type=QuestionType.BOOLEAN,
        weight=0.02,
        industry_default=False,
        help_text="Do you regularly publish reports on your ESG performance?"
    )
]

