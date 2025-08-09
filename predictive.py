"""
Predictive Compliance API endpoints.

This module provides the REST API interface for the predictive compliance system,
enabling proactive ESG guidance and early warning alerts.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

try:
    from app.core.security import get_current_user
    from app.models.user import User
    from app.models.tasks import EnhancedESGScore
    from app.services.predictive_service import predictive_service, PredictiveAlert, RiskLevel, AlertType
except Exception:
    from security import get_current_user
    from user import User
    from tasks import EnhancedESGScore
    from predictive_service import predictive_service, PredictiveAlert, RiskLevel, AlertType

router = APIRouter()


class PredictiveAlertResponse(BaseModel):
    """Response model for predictive alerts."""
    id: str
    alert_type: str
    risk_level: str
    title: str
    description: str
    predicted_impact: str
    recommended_actions: List[str]
    timeline_days: int
    confidence_score: float = Field(ge=0.0, le=1.0)
    data_sources: List[str]
    created_at: datetime
    expires_at: datetime
    is_resolved: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProactiveRecommendation(BaseModel):
    """Model for proactive recommendations."""
    type: str
    category: str
    priority: str
    title: str
    description: str
    actions: List[str]


class AlertsRequest(BaseModel):
    """Request model for generating predictive alerts."""
    current_score: Dict[str, Any]
    historical_scores: Optional[List[Dict[str, Any]]] = None
    industry: str = "retail"
    company_size: str = "small"


class ResolveAlertRequest(BaseModel):
    """Request model for resolving alerts."""
    alert_id: str


@router.post("/alerts/generate", response_model=List[PredictiveAlertResponse])
async def generate_predictive_alerts(
    request: AlertsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate predictive compliance alerts based on ESG performance data.
    
    This endpoint analyzes current and historical ESG scores to predict potential
    compliance issues and provide proactive guidance.
    """
    try:
        # Convert dict to EnhancedESGScore object
        current_score = _dict_to_enhanced_score(request.current_score)
        
        # Convert historical scores if provided
        historical_scores = []
        if request.historical_scores:
            historical_scores = [
                _dict_to_enhanced_score(score_dict) 
                for score_dict in request.historical_scores
            ]
        
        # Generate predictive alerts
        alerts = await predictive_service.generate_predictive_alerts(
            user_id=current_user.id,
            current_score=current_score,
            historical_scores=historical_scores,
            industry=request.industry,
            company_size=request.company_size
        )
        
        # Convert to response format
        alert_responses = []
        for alert in alerts:
            alert_responses.append(PredictiveAlertResponse(
                id=alert.id,
                alert_type=alert.alert_type.value,
                risk_level=alert.risk_level.value,
                title=alert.title,
                description=alert.description,
                predicted_impact=alert.predicted_impact,
                recommended_actions=alert.recommended_actions,
                timeline_days=alert.timeline_days,
                confidence_score=alert.confidence_score,
                data_sources=alert.data_sources,
                created_at=alert.created_at,
                expires_at=alert.expires_at,
                is_resolved=alert.is_resolved
            ))
        
        return alert_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate alerts: {str(e)}")


@router.get("/alerts/active", response_model=List[PredictiveAlertResponse])
async def get_active_alerts(
    current_user: User = Depends(get_current_user)
):
    """
    Get all active predictive alerts for the current user.
    
    Returns alerts that haven't expired and haven't been resolved.
    """
    try:
        alerts = predictive_service.get_active_alerts(current_user.id)
        
        alert_responses = []
        for alert in alerts:
            alert_responses.append(PredictiveAlertResponse(
                id=alert.id,
                alert_type=alert.alert_type.value,
                risk_level=alert.risk_level.value,
                title=alert.title,
                description=alert.description,
                predicted_impact=alert.predicted_impact,
                recommended_actions=alert.recommended_actions,
                timeline_days=alert.timeline_days,
                confidence_score=alert.confidence_score,
                data_sources=alert.data_sources,
                created_at=alert.created_at,
                expires_at=alert.expires_at,
                is_resolved=alert.is_resolved
            ))
        
        return alert_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active alerts: {str(e)}")


@router.post("/alerts/penalty-warnings", response_model=List[PredictiveAlertResponse])
async def generate_penalty_warnings(
    current_score: Dict[str, Any],
    industry: str = "retail",
    current_user: User = Depends(get_current_user)
):
    """
    Generate early-warning penalty risk alerts focused on preventing fines.

    Uses readiness vs. regulatory calendar to surface escalating warnings (90/60/30/14/7/3 days).
    """
    try:
        score = _dict_to_enhanced_score(current_score)
        warnings = await predictive_service.generate_penalty_warnings(
            user_id=current_user.id,
            current_score=score,
            industry=industry
        )

        return [
            PredictiveAlertResponse(
                id=a.id,
                alert_type=a.alert_type.value,
                risk_level=a.risk_level.value,
                title=a.title,
                description=a.description,
                predicted_impact=a.predicted_impact,
                recommended_actions=a.recommended_actions,
                timeline_days=a.timeline_days,
                confidence_score=a.confidence_score,
                data_sources=a.data_sources,
                created_at=a.created_at,
                expires_at=a.expires_at,
                is_resolved=a.is_resolved,
            ) for a in warnings
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate penalty warnings: {str(e)}")


@router.post("/alerts/resolve")
async def resolve_alert(
    request: ResolveAlertRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Mark a predictive alert as resolved.
    
    This indicates that the user has taken action to address the predicted issue.
    """
    try:
        success = predictive_service.resolve_alert(current_user.id, request.alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert resolved successfully", "alert_id": request.alert_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/recommendations/proactive", response_model=List[ProactiveRecommendation])
async def get_proactive_recommendations(
    current_score: Dict[str, Any],
    industry: str = "retail",
    current_user: User = Depends(get_current_user)
):
    """
    Get proactive recommendations to prevent future compliance issues.
    
    This endpoint analyzes current performance to suggest preventive actions
    before issues develop into serious compliance risks.
    """
    try:
        # Convert dict to EnhancedESGScore object
        score = _dict_to_enhanced_score(current_score)
        
        # Get proactive recommendations
        recommendations = await predictive_service.get_proactive_recommendations(
            user_id=current_user.id,
            current_score=score,
            industry=industry
        )
        
        # Convert to response format
        rec_responses = []
        for rec in recommendations:
            rec_responses.append(ProactiveRecommendation(
                type=rec["type"],
                category=rec["category"],
                priority=rec["priority"],
                title=rec["title"],
                description=rec["description"],
                actions=rec["actions"]
            ))
        
        return rec_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/analytics/risk-dashboard")
async def get_risk_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive risk analytics for dashboard display.
    
    Provides an overview of current risk levels, trends, and key metrics
    for the user's ESG compliance status.
    """
    try:
        # Get active alerts
        alerts = predictive_service.get_active_alerts(current_user.id)
        
        # Calculate risk metrics
        total_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a.risk_level == RiskLevel.CRITICAL])
        high_alerts = len([a for a in alerts if a.risk_level == RiskLevel.HIGH])
        
        # Calculate average timeline
        avg_timeline = sum(a.timeline_days for a in alerts) / total_alerts if total_alerts > 0 else 0
        
        # Get alert distribution by category
        alert_categories = {}
        for alert in alerts:
            alert_type = alert.alert_type.value
            alert_categories[alert_type] = alert_categories.get(alert_type, 0) + 1
        
        dashboard = {
            "risk_summary": {
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "high_risk_alerts": high_alerts,
                "average_timeline_days": round(avg_timeline, 1)
            },
            "alert_distribution": alert_categories,
            "risk_trends": {
                "improving": 0,  # Would calculate from historical data
                "stable": 0,
                "declining": total_alerts
            },
            "next_actions": [
                alert.recommended_actions[0] if alert.recommended_actions else "No actions"
                for alert in alerts[:3]  # Top 3 priority actions
            ],
            "compliance_readiness": {
                "overall_score": 75,  # Would calculate based on multiple factors
                "next_deadline_days": min(a.timeline_days for a in alerts) if alerts else None,
                "risk_level": "medium" if total_alerts > 0 else "low"
            }
        }
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk dashboard: {str(e)}")


@router.post("/analytics/benchmarking")
async def get_benchmarking(
    current_score: Dict[str, Any],
    industry: str = "retail",
    company_size: str = "small",
    current_user: User = Depends(get_current_user)
):
    """
    Get anonymized industry benchmarking insights to create a defensible data moat.
    """
    try:
        score = _dict_to_enhanced_score(current_score)
        insights = predictive_service.get_benchmarking_insights(score, industry, company_size)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get benchmarking insights: {str(e)}")


@router.post("/analytics/readiness-index")
async def get_readiness_index(
    current_score: Dict[str, Any],
    industry: str = "retail",
    current_user: User = Depends(get_current_user)
):
    """
    Get Compliance Readiness Index aggregating near-term obligations and severity.
    """
    try:
        score = _dict_to_enhanced_score(current_score)
        index = predictive_service.calculate_readiness_index(score, industry)
        return index
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get readiness index: {str(e)}")


@router.post("/analytics/roi-estimate")
async def estimate_roi(
    current_score: Dict[str, Any],
    industry: str = "retail",
    current_user: User = Depends(get_current_user)
):
    """
    Estimate ROI from avoided penalties and operational savings to justify premium pricing.
    """
    try:
        score = _dict_to_enhanced_score(current_score)
        roi = predictive_service.estimate_roi(score, industry)
        return roi
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to estimate ROI: {str(e)}")


@router.get("/health")
async def predictive_health_check():
    """Health check endpoint for predictive service."""
    return {
        "status": "healthy",
        "service": "predictive_compliance",
        "features": [
            "risk_modeling",
            "predictive_alerts",
            "proactive_recommendations",
            "trend_analysis"
        ]
    }


def _dict_to_enhanced_score(score_dict: Dict[str, Any]) -> EnhancedESGScore:
    """Convert dictionary to EnhancedESGScore object."""
    try:
        # Handle datetime fields
        calculated_at = score_dict.get("calculated_at")
        if isinstance(calculated_at, str):
            calculated_at = datetime.fromisoformat(calculated_at.replace('Z', '+00:00'))
        elif calculated_at is None:
            calculated_at = datetime.utcnow()
        
        return EnhancedESGScore(
            overall_score=score_dict.get("overall_score", 50.0),
            environmental_score=score_dict.get("environmental_score", 50.0),
            social_score=score_dict.get("social_score", 50.0),
            governance_score=score_dict.get("governance_score", 50.0),
            emissions_score=score_dict.get("emissions_score", 50.0),
            energy_score=score_dict.get("energy_score", 50.0),
            waste_score=score_dict.get("waste_score", 50.0),
            diversity_score=score_dict.get("diversity_score", 50.0),
            employee_score=score_dict.get("employee_score", 50.0),
            community_score=score_dict.get("community_score", 50.0),
            ethics_score=score_dict.get("ethics_score", 50.0),
            transparency_score=score_dict.get("transparency_score", 50.0),
            badge=score_dict.get("badge", "ESG Beginner"),
            level=score_dict.get("level", 1),
            improvement_areas=score_dict.get("improvement_areas", []),
            strengths=score_dict.get("strengths", []),
            industry_percentile=score_dict.get("industry_percentile"),
            trend=score_dict.get("trend"),
            calculated_at=calculated_at,
            quick_wins=score_dict.get("quick_wins", []),
            long_term_goals=score_dict.get("long_term_goals", [])
        )
    except Exception as e:
        raise ValueError(f"Invalid score data format: {str(e)}")
