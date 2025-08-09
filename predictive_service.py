"""
Predictive Compliance Service - Transform reactive reporting to proactive guidance.

This service implements the core business differentiator: predictive compliance alerts
that forecast potential gaps and offer tailored, actionable fixes before issues arise.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
import asyncio

try:
    from app.models.esg import ESGAnswer, DEFAULT_ESG_QUESTIONS
    from app.models.tasks import EnhancedESGScore, TaskCategory
    from app.services.llm_service import llm_service
    from app.services.scoring_service import scoring_service
except Exception:
    from esg import ESGAnswer, DEFAULT_ESG_QUESTIONS
    from tasks import EnhancedESGScore, TaskCategory
    from llm_service import llm_service
    from scoring_service import scoring_service


class RiskLevel(str, Enum):
    """Risk levels for compliance alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of predictive alerts."""
    COMPLIANCE_GAP = "compliance_gap"
    REGULATORY_DEADLINE = "regulatory_deadline"
    PERFORMANCE_DECLINE = "performance_decline"
    INDUSTRY_SHIFT = "industry_shift"
    PROACTIVE_OPPORTUNITY = "proactive_opportunity"
    PENALTY_RISK = "penalty_risk"


@dataclass
class PredictiveAlert:
    """Model for predictive compliance alerts."""
    id: str
    user_id: str
    alert_type: AlertType
    risk_level: RiskLevel
    title: str
    description: str
    predicted_impact: str
    recommended_actions: List[str]
    timeline_days: int  # Days until predicted issue
    confidence_score: float  # 0.0-1.0
    data_sources: List[str]
    created_at: datetime
    expires_at: datetime
    is_resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "alert_type": self.alert_type.value,
            "risk_level": self.risk_level.value,
            "title": self.title,
            "description": self.description,
            "predicted_impact": self.predicted_impact,
            "recommended_actions": self.recommended_actions,
            "timeline_days": self.timeline_days,
            "confidence_score": self.confidence_score,
            "data_sources": self.data_sources,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_resolved": self.is_resolved
        }


class ComplianceRiskModel:
    """Risk modeling engine for ESG compliance prediction."""
    
    def __init__(self):
        # Industry-specific compliance deadlines and regulations
        self.compliance_calendar = {
            "retail": {
                "CSRD_reporting": {"deadline_months": [3, 6, 9, 12], "criticality": "high"},
                "carbon_disclosure": {"deadline_months": [6, 12], "criticality": "medium"},
                "diversity_reporting": {"deadline_months": [12], "criticality": "medium"},
                "packaging_regulations": {"deadline_months": [1, 4, 7, 10], "criticality": "medium"}
            }
        }
        
        # Risk thresholds for different ESG categories
        self.risk_thresholds = {
            "environmental": {"critical": 30, "high": 45, "medium": 60},
            "social": {"critical": 35, "high": 50, "medium": 65},
            "governance": {"critical": 40, "high": 55, "medium": 70}
        }
        
        # Trend analysis windows
        self.trend_windows = {
            "short_term": 30,  # days
            "medium_term": 90,
            "long_term": 180
        }

        # Penalty model (simplified, non-legal)
        # Contains indicative penalty severity and lead-times for early warning
        self.penalty_catalog = {
            "retail": {
                "CSRD_reporting": {
                    "severity": "high",
                    "typical_penalty": "Administrative fines and disclosure orders",
                    "lead_times": [90, 60, 30, 14, 7, 3]
                },
                "carbon_disclosure": {
                    "severity": "medium",
                    "typical_penalty": "Fines or corrective action mandates",
                    "lead_times": [60, 30, 14, 7]
                },
                "packaging_regulations": {
                    "severity": "medium",
                    "typical_penalty": "Waste compliance fines",
                    "lead_times": [60, 30, 14, 7]
                },
                "diversity_reporting": {
                    "severity": "low",
                    "typical_penalty": "Notices and improvement plans",
                    "lead_times": [60, 30, 14]
                }
            }
        }
    
    def analyze_compliance_risks(
        self, 
        current_score: EnhancedESGScore,
        historical_scores: List[EnhancedESGScore],
        industry: str = "retail",
        company_size: str = "small"
    ) -> List[Dict[str, Any]]:
        """Analyze potential compliance risks and gaps."""
        risks = []
        
        # 1. Score-based risk analysis
        score_risks = self._analyze_score_risks(current_score)
        risks.extend(score_risks)
        
        # 2. Trend-based risk analysis
        if len(historical_scores) >= 3:
            trend_risks = self._analyze_trend_risks(historical_scores)
            risks.extend(trend_risks)
        
        # 3. Calendar-based compliance deadlines
        calendar_risks = self._analyze_calendar_risks(industry, current_score)
        risks.extend(calendar_risks)
        
        # 4. Industry benchmark risks
        benchmark_risks = self._analyze_benchmark_risks(current_score, industry)
        risks.extend(benchmark_risks)
        
        return sorted(risks, key=lambda x: x["priority_score"], reverse=True)
    
    def _analyze_score_risks(self, score: EnhancedESGScore) -> List[Dict[str, Any]]:
        """Analyze risks based on current ESG scores."""
        risks = []
        
        # Check each main category
        categories = {
            "environmental": score.environmental_score,
            "social": score.social_score,
            "governance": score.governance_score
        }
        
        for category, category_score in categories.items():
            thresholds = self.risk_thresholds[category]
            
            if category_score <= thresholds["critical"]:
                risks.append({
                    "type": "critical_score",
                    "category": category,
                    "current_score": category_score,
                    "risk_level": "critical",
                    "priority_score": 95,
                    "timeline_days": 30,
                    "description": f"Critical {category} performance requiring immediate attention"
                })
            elif category_score <= thresholds["high"]:
                risks.append({
                    "type": "low_score",
                    "category": category,
                    "current_score": category_score,
                    "risk_level": "high",
                    "priority_score": 80,
                    "timeline_days": 60,
                    "description": f"Low {category} score increasing compliance risk"
                })
        
        # Check sub-category specific risks
        sub_categories = {
            "emissions": score.emissions_score,
            "energy": score.energy_score,
            "diversity": score.diversity_score,
            "ethics": score.ethics_score
        }
        
        for sub_cat, sub_score in sub_categories.items():
            if sub_score <= 40:
                risks.append({
                    "type": "subcategory_risk",
                    "category": sub_cat,
                    "current_score": sub_score,
                    "risk_level": "medium",
                    "priority_score": 65,
                    "timeline_days": 90,
                    "description": f"Poor {sub_cat} performance may impact compliance"
                })
        
        return risks
    
    def _analyze_trend_risks(self, historical_scores: List[EnhancedESGScore]) -> List[Dict[str, Any]]:
        """Analyze risks based on performance trends."""
        risks = []
        
        if len(historical_scores) < 3:
            return risks
        
        # Sort by date (most recent first)
        sorted_scores = sorted(historical_scores, key=lambda x: x.calculated_at, reverse=True)
        recent_scores = sorted_scores[:3]
        
        # Analyze overall score trend
        overall_trend = self._calculate_trend([s.overall_score for s in recent_scores])
        
        if overall_trend < -5:  # Declining by more than 5 points
            risks.append({
                "type": "declining_trend",
                "category": "overall",
                "trend_slope": overall_trend,
                "risk_level": "high",
                "priority_score": 85,
                "timeline_days": 45,
                "description": f"ESG performance declining by {abs(overall_trend):.1f} points over recent periods"
            })
        
        # Analyze category trends
        categories = ["environmental_score", "social_score", "governance_score"]
        for category in categories:
            scores = [getattr(s, category) for s in recent_scores]
            trend = self._calculate_trend(scores)
            
            if trend < -3:
                risks.append({
                    "type": "category_decline",
                    "category": category.replace("_score", ""),
                    "trend_slope": trend,
                    "risk_level": "medium",
                    "priority_score": 70,
                    "timeline_days": 60,
                    "description": f"{category.replace('_score', '').title()} performance declining"
                })
        
        return risks
    
    def _analyze_calendar_risks(self, industry: str, score: EnhancedESGScore) -> List[Dict[str, Any]]:
        """Analyze risks based on upcoming compliance deadlines."""
        risks = []
        
        if industry not in self.compliance_calendar:
            return risks
        
        calendar = self.compliance_calendar[industry]
        current_date = datetime.utcnow()
        current_month = current_date.month
        
        for compliance_type, info in calendar.items():
            for deadline_month in info["deadline_months"]:
                # Calculate days until next deadline
                if deadline_month >= current_month:
                    days_until = (deadline_month - current_month) * 30
                else:
                    days_until = (12 - current_month + deadline_month) * 30
                
                # If deadline is within 90 days and scores are low, flag as risk
                if days_until <= 90:
                    readiness_score = self._calculate_readiness_score(compliance_type, score)
                    
                    if readiness_score < 70:
                        risk_level = "critical" if days_until <= 30 else "high"
                        risks.append({
                            "type": "upcoming_deadline",
                            "category": compliance_type,
                            "deadline_days": days_until,
                            "readiness_score": readiness_score,
                            "risk_level": risk_level,
                            "priority_score": 90 if risk_level == "critical" else 75,
                            "timeline_days": days_until,
                            "description": f"{compliance_type.replace('_', ' ').title()} deadline in {days_until} days with low readiness"
                        })
        
        return risks
    
    def _analyze_benchmark_risks(self, score: EnhancedESGScore, industry: str) -> List[Dict[str, Any]]:
        """Analyze risks based on industry benchmarks."""
        risks = []
        
        # Industry averages (would be dynamic in production)
        industry_benchmarks = {
            "retail": {
                "overall": 65,
                "environmental": 62,
                "social": 68,
                "governance": 66
            }
        }
        
        if industry in industry_benchmarks:
            benchmarks = industry_benchmarks[industry]
            
            # Check if significantly below industry average
            if score.overall_score < benchmarks["overall"] - 15:
                risks.append({
                    "type": "below_benchmark",
                    "category": "overall",
                    "current_score": score.overall_score,
                    "benchmark": benchmarks["overall"],
                    "gap": benchmarks["overall"] - score.overall_score,
                    "risk_level": "medium",
                    "priority_score": 60,
                    "timeline_days": 120,
                    "description": f"Overall ESG performance {benchmarks['overall'] - score.overall_score:.1f} points below industry average"
                })
        
        return risks
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope for a series of values."""
        if len(values) < 2:
            return 0
        
        # Simple linear trend calculation
        n = len(values)
        x_vals = list(range(n))
        
        # Calculate slope using least squares
        x_mean = sum(x_vals) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_vals[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def _calculate_readiness_score(self, compliance_type: str, score: EnhancedESGScore) -> float:
        """Calculate readiness score for specific compliance requirements."""
        # Map compliance types to relevant ESG scores
        compliance_mapping = {
            "CSRD_reporting": (score.overall_score * 0.5 + score.governance_score * 0.3 + score.transparency_score * 0.2),
            "carbon_disclosure": (score.environmental_score * 0.7 + score.emissions_score * 0.3),
            "diversity_reporting": (score.social_score * 0.6 + score.diversity_score * 0.4),
            "packaging_regulations": (score.environmental_score * 0.5 + score.waste_score * 0.5)
        }
        
        return compliance_mapping.get(compliance_type, score.overall_score)

    def calculate_penalty_risk(
        self,
        compliance_type: str,
        readiness_score: float,
        days_until_deadline: int,
        industry: str = "retail"
    ) -> Dict[str, Any]:
        """Estimate penalty risk based on readiness and time to deadline."""
        catalog = self.penalty_catalog.get(industry, {}).get(compliance_type, None)
        if not catalog:
            return {
                "penalty_severity": "unknown",
                "typical_penalty": "",
                "escalation_level": "normal",
                "miss_probability": 0.2
            }

        # Miss probability: lower readiness + closer deadline => higher risk
        # Readiness 100 -> 0 risk; readiness 0 -> base 0.7 risk, boosted by time pressure
        base = max(0.0, 0.7 - readiness_score / 100.0)
        time_factor = 0.0
        if days_until_deadline <= 7:
            time_factor = 0.25
        elif days_until_deadline <= 14:
            time_factor = 0.2
        elif days_until_deadline <= 30:
            time_factor = 0.15
        elif days_until_deadline <= 60:
            time_factor = 0.1
        elif days_until_deadline <= 90:
            time_factor = 0.05

        miss_probability = min(0.95, max(0.05, base + time_factor))

        # Escalation level based on time remaining
        if days_until_deadline <= 7:
            escalation = "critical"
        elif days_until_deadline <= 14:
            escalation = "high"
        elif days_until_deadline <= 30:
            escalation = "elevated"
        else:
            escalation = "normal"

        return {
            "penalty_severity": catalog["severity"],
            "typical_penalty": catalog["typical_penalty"],
            "escalation_level": escalation,
            "miss_probability": round(miss_probability, 2)
        }


class PredictiveAlertService:
    """Main service for generating and managing predictive compliance alerts."""
    
    def __init__(self):
        self.risk_model = ComplianceRiskModel()
        self.active_alerts = {}  # In-memory storage (use database in production)
    
    async def generate_predictive_alerts(
        self,
        user_id: str,
        current_score: EnhancedESGScore,
        historical_scores: List[EnhancedESGScore],
        industry: str = "retail",
        company_size: str = "small"
    ) -> List[PredictiveAlert]:
        """Generate predictive compliance alerts for a user."""
        
        # Analyze compliance risks
        risks = self.risk_model.analyze_compliance_risks(
            current_score, historical_scores, industry, company_size
        )
        
        alerts = []
        
        for risk in risks[:5]:  # Limit to top 5 risks
            alert = await self._create_alert_from_risk(user_id, risk, industry)
            if alert:
                alerts.append(alert)
        
        # Store active alerts
        self.active_alerts[user_id] = alerts
        
        return alerts
    
    async def _create_alert_from_risk(
        self, 
        user_id: str, 
        risk: Dict[str, Any], 
        industry: str
    ) -> Optional[PredictiveAlert]:
        """Create a predictive alert from a risk analysis."""
        
        alert_id = str(uuid.uuid4())
        
        # Generate LLM-enhanced description and recommendations
        enhanced_content = await self._enhance_alert_with_llm(risk, industry)
        
        # Map risk data to alert
        alert_type_mapping = {
            "critical_score": AlertType.COMPLIANCE_GAP,
            "low_score": AlertType.COMPLIANCE_GAP,
            "declining_trend": AlertType.PERFORMANCE_DECLINE,
            "upcoming_deadline": AlertType.REGULATORY_DEADLINE,
            "below_benchmark": AlertType.INDUSTRY_SHIFT,
            "subcategory_risk": AlertType.COMPLIANCE_GAP
        }
        
        alert_type = alert_type_mapping.get(risk["type"], AlertType.COMPLIANCE_GAP)
        
        # Create alert
        alert = PredictiveAlert(
            id=alert_id,
            user_id=user_id,
            alert_type=alert_type,
            risk_level=RiskLevel(risk["risk_level"]),
            title=enhanced_content["title"],
            description=enhanced_content["description"],
            predicted_impact=enhanced_content["predicted_impact"],
            recommended_actions=enhanced_content["recommended_actions"],
            timeline_days=risk["timeline_days"],
            confidence_score=enhanced_content["confidence_score"],
            data_sources=["esg_scoring", "trend_analysis", "industry_benchmarks"],
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=risk["timeline_days"])
        )
        
        return alert

    async def generate_penalty_warnings(
        self,
        user_id: str,
        current_score: EnhancedESGScore,
        industry: str = "retail"
    ) -> List[PredictiveAlert]:
        """Generate early warnings focused on penalty prevention for upcoming deadlines."""
        warnings: List[PredictiveAlert] = []
        current_month = datetime.utcnow().month

        # Iterate over compliance calendar for industry
        calendar = self.risk_model.compliance_calendar.get(industry, {})
        for compliance_type, info in calendar.items():
            for deadline_month in info["deadline_months"]:
                if deadline_month >= current_month:
                    days_until = (deadline_month - current_month) * 30
                else:
                    days_until = (12 - current_month + deadline_month) * 30

                # Only warn within 90 days horizon
                if days_until > 90:
                    continue

                readiness = self.risk_model._calculate_readiness_score(compliance_type, current_score)
                penalty_meta = self.risk_model.calculate_penalty_risk(compliance_type, readiness, days_until, industry)

                # Determine risk level
                risk_level = RiskLevel.MEDIUM
                if penalty_meta["escalation_level"] == "critical" or penalty_meta["miss_probability"] >= 0.7:
                    risk_level = RiskLevel.CRITICAL
                elif penalty_meta["escalation_level"] == "high" or penalty_meta["miss_probability"] >= 0.5:
                    risk_level = RiskLevel.HIGH

                # Build title/description
                title = f"Penalty Risk: {compliance_type.replace('_', ' ').title()} in {days_until} days"
                description = (
                    f"Readiness {readiness:.0f}%. Estimated miss probability {penalty_meta['miss_probability']*100:.0f}% "
                    f"with {penalty_meta['penalty_severity']} severity if missed."
                )

                # Recommended actions tailored to compliance type
                recommended_actions = [
                    f"Assign an owner for {compliance_type.replace('_', ' ')}",
                    "Prepare required documentation and evidence",
                    "Schedule an internal review within 7 days"
                ]

                alert = PredictiveAlert(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    alert_type=AlertType.PENALTY_RISK,
                    risk_level=risk_level,
                    title=title,
                    description=description,
                    predicted_impact=penalty_meta["typical_penalty"],
                    recommended_actions=recommended_actions,
                    timeline_days=days_until,
                    confidence_score=max(0.5, 1 - abs(readiness - 50) / 100),
                    data_sources=["regulatory_calendar", "readiness_score"],
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=days_until if days_until > 0 else 1)
                )

                warnings.append(alert)

        # Prioritize by risk and urgency
        warnings.sort(key=lambda a: (a.risk_level.value, -a.timeline_days))
        self.active_alerts[user_id] = self.active_alerts.get(user_id, []) + warnings
        return warnings

    def get_benchmarking_insights(
        self,
        current_score: EnhancedESGScore,
        industry: str = "retail",
        company_size: str = "small"
    ) -> Dict[str, Any]:
        """Provide anonymized benchmarking vs. industry cohort to build a data moat."""
        # Mocked cohort baselines – in production use aggregated anonymized dataset
        baselines = {
            "retail": {
                "overall": 65,
                "environmental": 62,
                "social": 68,
                "governance": 66
            }
        }
        baseline = baselines.get(industry, baselines["retail"])

        def percentile(score: float, mean: float) -> float:
            # Simple mock percentile function around baseline
            if score >= mean + 20:
                return 95.0
            if score >= mean + 10:
                return 85.0
            if score >= mean:
                return 70.0
            if score >= mean - 10:
                return 40.0
            return 20.0

        insights = {
            "cohort": {
                "industry": industry,
                "company_size": company_size,
                "sample_size": 500  # mock dataset size
            },
            "percentiles": {
                "overall": percentile(current_score.overall_score, baseline["overall"]),
                "environmental": percentile(current_score.environmental_score, baseline["environmental"]),
                "social": percentile(current_score.social_score, baseline["social"]),
                "governance": percentile(current_score.governance_score, baseline["governance"]),
            },
            "benchmarks": baseline
        }

        return insights

    def calculate_readiness_index(
        self,
        current_score: EnhancedESGScore,
        industry: str = "retail"
    ) -> Dict[str, Any]:
        """Aggregate readiness across key compliance tracks into a single index."""
        calendar = self.risk_model.compliance_calendar.get(industry, {})
        current_month = datetime.utcnow().month

        tracks: List[Dict[str, Any]] = []
        for compliance_type, info in calendar.items():
            # Next deadline days
            days_until = min(
                ((m - current_month) * 30 if m >= current_month else (12 - current_month + m) * 30)
                for m in info["deadline_months"]
            ) if info.get("deadline_months") else 180

            readiness = self.risk_model._calculate_readiness_score(compliance_type, current_score)
            penalty_meta = self.risk_model.calculate_penalty_risk(compliance_type, readiness, days_until, industry)

            tracks.append({
                "track": compliance_type,
                "readiness": round(readiness, 1),
                "days_until_deadline": days_until,
                "penalty_severity": penalty_meta["penalty_severity"],
                "miss_probability": penalty_meta["miss_probability"],
            })

        # Weighted readiness index – nearer deadlines and higher severity weigh more
        def weight(t: Dict[str, Any]) -> float:
            severity_w = {"low": 1.0, "medium": 1.25, "high": 1.5}
            time_w = 1.5 if t["days_until_deadline"] <= 30 else (1.2 if t["days_until_deadline"] <= 60 else 1.0)
            return severity_w.get(t["penalty_severity"], 1.0) * time_w

        total_w = sum(weight(t) for t in tracks) or 1.0
        index = sum(t["readiness"] * weight(t) for t in tracks) / total_w

        return {
            "readiness_index": round(index, 1),
            "tracks": tracks
        }

    def estimate_roi(
        self,
        current_score: EnhancedESGScore,
        industry: str = "retail"
    ) -> Dict[str, Any]:
        """Estimate potential ROI from acting on alerts: avoided penalties + operational savings."""
        # Expected avoided penalties over next 60 days
        calendar = self.risk_model.compliance_calendar.get(industry, {})
        current_month = datetime.utcnow().month
        severity_amount = {"low": 2000, "medium": 5000, "high": 10000}

        expected_penalty = 0.0
        for compliance_type, info in calendar.items():
            for deadline_month in info.get("deadline_months", []):
                days_until = (deadline_month - current_month) * 30 if deadline_month >= current_month else (12 - current_month + deadline_month) * 30
                if days_until <= 60:
                    readiness = self.risk_model._calculate_readiness_score(compliance_type, current_score)
                    penalty_meta = self.risk_model.calculate_penalty_risk(compliance_type, readiness, days_until, industry)
                    expected_penalty += penalty_meta["miss_probability"] * severity_amount.get(penalty_meta["penalty_severity"], 3000)

        # Operational savings proxy (energy + waste improvements to reach 70)
        target = 70.0
        energy_gap = max(0.0, target - current_score.energy_score)
        waste_gap = max(0.0, target - current_score.waste_score)
        energy_savings = energy_gap * 30  # $30 per point gap proxy
        waste_savings = waste_gap * 20    # $20 per point gap proxy

        total_roi = expected_penalty + energy_savings + waste_savings

        return {
            "avoided_penalties_estimate": round(expected_penalty, 2),
            "operational_savings_estimate": round(energy_savings + waste_savings, 2),
            "total_potential_roi": round(total_roi, 2)
        }
    
    async def _enhance_alert_with_llm(self, risk: Dict[str, Any], industry: str) -> Dict[str, Any]:
        """Use LLM to enhance alert content with specific recommendations."""
        
        prompt = f"""
        You are an ESG compliance expert for {industry} SMBs. Based on this risk analysis, create a predictive compliance alert:
        
        Risk Type: {risk['type']}
        Category: {risk['category']}
        Risk Level: {risk['risk_level']}
        Timeline: {risk['timeline_days']} days
        Description: {risk['description']}
        
        Generate a JSON response with:
        {{
            "title": "<concise alert title>",
            "description": "<detailed description of the predicted issue>",
            "predicted_impact": "<what will happen if not addressed>",
            "recommended_actions": ["<action 1>", "<action 2>", "<action 3>"],
            "confidence_score": <0.0-1.0>
        }}
        
        Make it specific to {industry} businesses and actionable for SMBs.
        """
        
        try:
            response = await llm_service.get_provider().generate_text(prompt, max_tokens=400)
            
            # Parse LLM response
            import json
            enhanced = json.loads(response)
            
            # Validate required fields
            required_fields = ["title", "description", "predicted_impact", "recommended_actions", "confidence_score"]
            if all(field in enhanced for field in required_fields):
                return enhanced
            
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
        
        # Fallback to template-based content
        return self._generate_fallback_content(risk)
    
    def _generate_fallback_content(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback alert content when LLM is unavailable."""
        
        templates = {
            "critical_score": {
                "title": f"Critical {risk['category'].title()} Performance Alert",
                "description": f"Your {risk['category']} score of {risk.get('current_score', 'N/A')} is critically low and may impact compliance.",
                "predicted_impact": "Potential regulatory penalties, stakeholder concerns, and compliance violations",
                "recommended_actions": [
                    f"Immediately review {risk['category']} practices",
                    "Develop improvement action plan",
                    "Consider expert consultation"
                ]
            },
            "declining_trend": {
                "title": f"Declining {risk['category'].title()} Performance",
                "description": f"Your {risk['category']} performance is declining and may create compliance risks.",
                "predicted_impact": "Continued decline may lead to compliance gaps and stakeholder concerns",
                "recommended_actions": [
                    "Investigate causes of decline",
                    "Implement corrective measures",
                    "Monitor progress closely"
                ]
            },
            "upcoming_deadline": {
                "title": f"Upcoming {risk['category'].replace('_', ' ').title()} Deadline",
                "description": f"Compliance deadline in {risk['timeline_days']} days with readiness score of {risk.get('readiness_score', 'N/A')}%",
                "predicted_impact": "Risk of missing compliance deadline and potential penalties",
                "recommended_actions": [
                    "Review compliance requirements",
                    "Prepare necessary documentation",
                    "Consider professional assistance"
                ]
            }
        }
        
        template = templates.get(risk["type"], templates["critical_score"])
        template["confidence_score"] = 0.7  # Default confidence for fallback
        
        return template
    
    def get_active_alerts(self, user_id: str) -> List[PredictiveAlert]:
        """Get active alerts for a user."""
        alerts = self.active_alerts.get(user_id, [])
        
        # Filter out expired alerts
        current_time = datetime.utcnow()
        active_alerts = [alert for alert in alerts if alert.expires_at > current_time and not alert.is_resolved]
        
        return active_alerts
    
    def resolve_alert(self, user_id: str, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        alerts = self.active_alerts.get(user_id, [])
        
        for alert in alerts:
            if alert.id == alert_id:
                alert.is_resolved = True
                return True
        
        return False
    
    async def get_proactive_recommendations(
        self,
        user_id: str,
        current_score: EnhancedESGScore,
        industry: str = "retail"
    ) -> List[Dict[str, Any]]:
        """Generate proactive recommendations to prevent future issues."""
        
        recommendations = []
        
        # Identify areas approaching risk thresholds
        risk_thresholds = self.risk_model.risk_thresholds
        
        for category in ["environmental", "social", "governance"]:
            score = getattr(current_score, f"{category}_score")
            thresholds = risk_thresholds[category]
            
            # If score is approaching medium risk threshold
            if thresholds["medium"] < score <= thresholds["medium"] + 10:
                recommendations.append({
                    "type": "preventive_action",
                    "category": category,
                    "priority": "medium",
                    "title": f"Strengthen {category.title()} Performance",
                    "description": f"Your {category} score is approaching risk levels. Take preventive action now.",
                    "actions": await self._get_category_recommendations(category, industry)
                })
        
        return recommendations
    
    async def _get_category_recommendations(self, category: str, industry: str) -> List[str]:
        """Get specific recommendations for a category."""
        
        category_actions = {
            "environmental": [
                "Conduct energy audit",
                "Implement waste reduction program",
                "Explore renewable energy options",
                "Improve packaging sustainability"
            ],
            "social": [
                "Review diversity and inclusion policies",
                "Conduct employee satisfaction survey",
                "Enhance community engagement",
                "Improve worker safety programs"
            ],
            "governance": [
                "Update code of conduct",
                "Strengthen data privacy measures",
                "Improve board oversight",
                "Enhance transparency reporting"
            ]
        }
        
        return category_actions.get(category, [])


# Global service instance
predictive_service = PredictiveAlertService()
