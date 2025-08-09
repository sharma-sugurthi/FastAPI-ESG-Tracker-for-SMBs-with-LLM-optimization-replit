"""
AI-generated tasks and enhanced ESG scoring models.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from fastapi import APIRouter, HTTPException, Depends
import uuid

# Create the router
router = APIRouter()


class TaskDifficulty(str, Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskCategory(str, Enum):
    """Task categories aligned with ESG pillars."""
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"


class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ImpactLevel(str, Enum):
    """Expected impact level of tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ESGTask(BaseModel):
    """AI-generated ESG improvement task."""
    id: str
    task: str
    description: Optional[str] = None
    points: int = Field(ge=5, le=100)
    category: TaskCategory
    difficulty: TaskDifficulty
    estimated_impact: ImpactLevel
    estimated_cost: Optional[str] = None
    timeline: Optional[str] = None
    resources_needed: Optional[List[str]] = None
    success_metrics: Optional[List[str]] = None
    industry_specific: bool = False
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskProgress(BaseModel):
    """Task progress tracking."""
    task_id: str
    user_id: str
    status: TaskStatus
    progress_percentage: float = Field(ge=0.0, le=100.0)
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    points_earned: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskGenerationRequest(BaseModel):
    """Request for AI task generation."""
    user_esg_data: Dict[str, Any]
    industry: str = "retail"
    company_size: Optional[str] = "small"  # small, medium, large
    focus_areas: Optional[List[TaskCategory]] = None
    max_tasks: int = Field(default=5, ge=1, le=10)
    difficulty_preference: Optional[TaskDifficulty] = None
    budget_range: Optional[str] = None  # low, medium, high


class TaskGenerationResponse(BaseModel):
    """Response for AI task generation."""
    tasks: List[ESGTask]
    total_points_available: int
    recommendations: List[str]
    priority_order: List[str]  # Task IDs in priority order
    generated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ESGBadge(BaseModel):
    """ESG achievement badge."""
    name: str
    description: str
    icon: str
    points_required: int
    category: Optional[TaskCategory] = None
    earned_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserProgress(BaseModel):
    """User's overall ESG progress."""
    user_id: str
    total_points: int
    level: int
    badges_earned: List[ESGBadge]
    completed_tasks: int
    pending_tasks: int
    current_streak: int  # Days of consecutive activity
    last_activity: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnhancedESGScore(BaseModel):
    """Enhanced ESG scoring with detailed breakdown."""
    overall_score: float = Field(ge=0.0, le=100.0)
    
    # Category scores
    environmental_score: float = Field(ge=0.0, le=100.0)
    social_score: float = Field(ge=0.0, le=100.0)
    governance_score: float = Field(ge=0.0, le=100.0)
    
    # Sub-category scores
    emissions_score: float = Field(ge=0.0, le=100.0)
    energy_score: float = Field(ge=0.0, le=100.0)
    waste_score: float = Field(ge=0.0, le=100.0)
    diversity_score: float = Field(ge=0.0, le=100.0)
    employee_score: float = Field(ge=0.0, le=100.0)
    community_score: float = Field(ge=0.0, le=100.0)
    ethics_score: float = Field(ge=0.0, le=100.0)
    transparency_score: float = Field(ge=0.0, le=100.0)
    
    # Metadata
    badge: str
    level: int
    improvement_areas: List[str]
    strengths: List[str]
    industry_percentile: Optional[float] = None
    trend: Optional[str] = None  # improving, declining, stable
    calculated_at: datetime
    
    # Recommendations
    quick_wins: List[str]
    long_term_goals: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScoreHistory(BaseModel):
    """Historical ESG score tracking."""
    user_id: str
    scores: List[Dict[str, Any]]  # List of score snapshots with timestamps
    trend_analysis: Dict[str, Any]
    improvement_rate: float
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Default ESG badges
DEFAULT_BADGES = [
    ESGBadge(
        name="Green Starter",
        description="Completed your first environmental task",
        icon="🌱",
        points_required=25,
        category=TaskCategory.ENVIRONMENTAL
    ),
    ESGBadge(
        name="Eco Warrior",
        description="Earned 100 environmental points",
        icon="🌍",
        points_required=100,
        category=TaskCategory.ENVIRONMENTAL
    ),
    ESGBadge(
        name="Social Champion",
        description="Completed 5 social responsibility tasks",
        icon="🤝",
        points_required=150,
        category=TaskCategory.SOCIAL
    ),
    ESGBadge(
        name="Governance Guardian",
        description="Implemented strong governance practices",
        icon="⚖️",
        points_required=75,
        category=TaskCategory.GOVERNANCE
    ),
    ESGBadge(
        name="ESG Leader",
        description="Achieved overall ESG score above 80",
        icon="🏆",
        points_required=500
    ),
    ESGBadge(
        name="Sustainability Star",
        description="Maintained high ESG performance for 3 months",
        icon="⭐",
        points_required=1000
    )
]

# Default task templates for different industries
DEFAULT_TASK_TEMPLATES = {
    "retail": [
        {
            "task": "Switch to LED lighting in all store locations",
            "category": TaskCategory.ENVIRONMENTAL,
            "difficulty": TaskDifficulty.EASY,
            "points": 25,
            "estimated_impact": ImpactLevel.MEDIUM,
            "estimated_cost": "Low ($500-2000)",
            "timeline": "2-4 weeks"
        },
        {
            "task": "Implement employee diversity training program",
            "category": TaskCategory.SOCIAL,
            "difficulty": TaskDifficulty.MEDIUM,
            "points": 40,
            "estimated_impact": ImpactLevel.HIGH,
            "estimated_cost": "Medium ($1000-5000)",
            "timeline": "1-2 months"
        },
        {
            "task": "Create supplier code of conduct",
            "category": TaskCategory.GOVERNANCE,
            "difficulty": TaskDifficulty.EASY,
            "points": 30,
            "estimated_impact": ImpactLevel.MEDIUM,
            "estimated_cost": "Low ($0-500)",
            "timeline": "2-3 weeks"
        },
        {
            "task": "Install smart energy monitoring system",
            "category": TaskCategory.ENVIRONMENTAL,
            "difficulty": TaskDifficulty.MEDIUM,
            "points": 50,
            "estimated_impact": ImpactLevel.HIGH,
            "estimated_cost": "Medium ($2000-8000)",
            "timeline": "1-2 months"
        },
        {
            "task": "Launch customer recycling program",
            "category": TaskCategory.ENVIRONMENTAL,
            "difficulty": TaskDifficulty.HARD,
            "points": 75,
            "estimated_impact": ImpactLevel.HIGH,
            "estimated_cost": "High ($5000-15000)",
            "timeline": "3-6 months"
        }
    ]
}


# Task API Endpoints
@router.post("/generate", response_model=TaskGenerationResponse)
async def generate_tasks(request: TaskGenerationRequest):
    """Generate personalized ESG improvement tasks based on user data."""
    try:
        # Import task generation service
        from scoring_service import scoring_service
        
        # Generate tasks based on user data
        tasks = []
        current_time = datetime.utcnow()
        
        # Use default templates for now
        templates = DEFAULT_TASK_TEMPLATES.get(request.industry, DEFAULT_TASK_TEMPLATES["retail"])
        
        # Filter by difficulty preference if specified
        if request.difficulty_preference:
            templates = [t for t in templates if t["difficulty"] == request.difficulty_preference]
        
        # Filter by focus areas if specified
        if request.focus_areas:
            templates = [t for t in templates if t["category"] in request.focus_areas]
        
        # Limit to max_tasks
        templates = templates[:request.max_tasks]
        
        total_points = 0
        for i, template in enumerate(templates):
            task_id = f"task-{uuid.uuid4().hex[:8]}"
            
            esg_task = ESGTask(
                id=task_id,
                task=template["task"],
                description=f"Industry-specific task for {request.industry} businesses",
                points=template["points"],
                category=template["category"],
                difficulty=template["difficulty"],
                estimated_impact=template["estimated_impact"],
                estimated_cost=template.get("estimated_cost"),
                timeline=template.get("timeline"),
                resources_needed=["Planning", "Implementation team"],
                success_metrics=["Performance improvement", "Cost savings"],
                industry_specific=True,
                created_at=current_time
            )
            
            tasks.append(esg_task)
            total_points += template["points"]
        
        # Generate recommendations
        recommendations = [
            "Start with easy tasks to build momentum",
            "Focus on high-impact, low-cost initiatives first",
            f"Target {request.industry}-specific best practices"
        ]
        
        # Priority order (easy tasks first)
        priority_order = [t.id for t in sorted(tasks, key=lambda x: x.difficulty.value)]
        
        return TaskGenerationResponse(
            tasks=tasks,
            total_points_available=total_points,
            recommendations=recommendations,
            priority_order=priority_order,
            generated_at=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/badges", response_model=List[ESGBadge])
async def get_available_badges():
    """Get all available ESG badges."""
    return DEFAULT_BADGES


@router.get("/progress/{user_id}", response_model=UserProgress)
async def get_user_progress(user_id: str):
    """Get user's ESG progress and achievements."""
    try:
        # For demo purposes, return mock progress
        return UserProgress(
            user_id=user_id,
            total_points=150,
            level=2,
            badges_earned=[DEFAULT_BADGES[0], DEFAULT_BADGES[2]],
            completed_tasks=3,
            pending_tasks=2,
            current_streak=5,
            last_activity=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress/{user_id}/update")
async def update_task_progress(user_id: str, progress: TaskProgress):
    """Update progress on a specific task."""
    try:
        # For demo purposes, just return success
        return {
            "message": "Task progress updated successfully",
            "task_id": progress.task_id,
            "status": progress.status,
            "points_earned": progress.points_earned
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

