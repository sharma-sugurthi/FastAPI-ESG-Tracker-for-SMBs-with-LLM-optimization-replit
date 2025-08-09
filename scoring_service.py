"""
Enhanced ESG scoring service with detailed analytics and recommendations.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

try:
    from app.models.esg import ESGAnswer, DEFAULT_ESG_QUESTIONS
    from app.models.tasks import (
        EnhancedESGScore, ESGBadge, UserProgress, ScoreHistory,
        TaskCategory, DEFAULT_BADGES
    )
    from app.core.config import settings
except Exception:
    from esg import ESGAnswer, DEFAULT_ESG_QUESTIONS
    from tasks import (
        EnhancedESGScore, ESGBadge, UserProgress, ScoreHistory,
        TaskCategory, DEFAULT_BADGES
    )
    from config import settings


class ScoringService:
    """Enhanced ESG scoring service with detailed analytics."""
    
    def __init__(self):
        self.weights = {
            "environmental": settings.emissions_weight,
            "social": settings.dei_weight,
            "governance": settings.packaging_weight
        }
        
        # Sub-category weights within each main category
        self.sub_weights = {
            "environmental": {
                "emissions": 0.4,
                "energy": 0.3,
                "waste": 0.3
            },
            "social": {
                "diversity": 0.4,
                "employee": 0.4,
                "community": 0.2
            },
            "governance": {
                "ethics": 0.5,
                "transparency": 0.5
            }
        }
    
    def calculate_enhanced_score(
        self, 
        answers: List[ESGAnswer], 
        industry: str = "retail",
        company_size: str = "small"
    ) -> EnhancedESGScore:
        """
        Calculate enhanced ESG score with detailed breakdown.
        """
        # Create question lookup
        question_lookup = {q.id: q for q in DEFAULT_ESG_QUESTIONS}
        
        # Initialize scores
        category_scores = {
            "environmental": [],
            "social": [],
            "governance": []
        }
        
        sub_category_scores = {
            "emissions": [],
            "energy": [],
            "waste": [],
            "diversity": [],
            "employee": [],
            "community": [],
            "ethics": [],
            "transparency": []
        }
        
        # Process answers
        for answer in answers:
            question = question_lookup.get(answer.question_id)
            if not question or answer.value is None:
                continue
            
            # Normalize score
            normalized_score = self._normalize_answer_score(answer.value, question)
            weighted_score = normalized_score * question.weight
            
            # Categorize by main ESG category
            category = question.category.value
            if category in category_scores:
                category_scores[category].append(weighted_score)
            
            # Categorize by sub-category
            sub_category = self._map_to_sub_category(question.id)
            if sub_category in sub_category_scores:
                sub_category_scores[sub_category].append(normalized_score)
        
        # Calculate category scores
        env_score = self._calculate_average(category_scores["environmental"])
        social_score = self._calculate_average(category_scores["social"])
        gov_score = self._calculate_average(category_scores["governance"])
        
        # Calculate sub-category scores
        emissions_score = self._calculate_average(sub_category_scores["emissions"])
        energy_score = self._calculate_average(sub_category_scores["energy"])
        waste_score = self._calculate_average(sub_category_scores["waste"])
        diversity_score = self._calculate_average(sub_category_scores["diversity"])
        employee_score = self._calculate_average(sub_category_scores["employee"])
        community_score = self._calculate_average(sub_category_scores["community"])
        ethics_score = self._calculate_average(sub_category_scores["ethics"])
        transparency_score = self._calculate_average(sub_category_scores["transparency"])
        
        # Calculate overall score
        overall_score = (
            env_score * self.weights["environmental"] +
            social_score * self.weights["social"] +
            gov_score * self.weights["governance"]
        )
        
        # Determine badge and level
        badge = self._determine_badge(overall_score)
        level = self._calculate_level(overall_score)
        
        # Generate improvement areas and strengths
        improvement_areas, strengths = self._analyze_performance(
            env_score, social_score, gov_score,
            emissions_score, energy_score, waste_score,
            diversity_score, employee_score, community_score,
            ethics_score, transparency_score
        )
        
        # Calculate industry percentile (mock calculation)
        industry_percentile = self._calculate_industry_percentile(overall_score, industry)
        
        # Generate recommendations
        quick_wins, long_term_goals = self._generate_recommendations(
            category_scores, sub_category_scores, industry, company_size
        )
        
        return EnhancedESGScore(
            overall_score=round(overall_score, 1),
            environmental_score=round(env_score, 1),
            social_score=round(social_score, 1),
            governance_score=round(gov_score, 1),
            emissions_score=round(emissions_score, 1),
            energy_score=round(energy_score, 1),
            waste_score=round(waste_score, 1),
            diversity_score=round(diversity_score, 1),
            employee_score=round(employee_score, 1),
            community_score=round(community_score, 1),
            ethics_score=round(ethics_score, 1),
            transparency_score=round(transparency_score, 1),
            badge=badge,
            level=level,
            improvement_areas=improvement_areas,
            strengths=strengths,
            industry_percentile=industry_percentile,
            trend="stable",  # Would be calculated from historical data
            calculated_at=datetime.utcnow(),
            quick_wins=quick_wins,
            long_term_goals=long_term_goals
        )
    
    def _normalize_answer_score(self, value: Any, question) -> float:
        """Normalize answer value to 0-100 score."""
        if question.question_type.value == "boolean":
            return 100.0 if value else 0.0
        
        elif question.question_type.value == "percentage":
            return min(float(value), 100.0) if value is not None else 0.0
        
        elif question.question_type.value == "numeric":
            # Context-specific scoring for numeric values
            if question.id in ["co2_emissions"]:
                # Lower is better for emissions
                default_val = question.industry_default or 10
                score = max(0, 100 - (float(value) / default_val) * 50)
                return min(score, 100.0)
            else:
                # Higher is generally better for other metrics
                default_val = question.industry_default or 1
                if default_val > 0:
                    score = (float(value) / default_val) * 50
                    return min(score, 100.0)
        
        return 50.0  # Default middle score
    
    def _map_to_sub_category(self, question_id: str) -> str:
        """Map question ID to sub-category."""
        mapping = {
            "energy_consumption": "energy",
            "co2_emissions": "emissions",
            "packaging_recyclability": "waste",
            "diversity_percentage": "diversity",
            "female_leadership": "diversity",
            "employee_satisfaction": "employee",
            "data_privacy_compliance": "ethics",
            "ethics_training": "ethics",
            "supplier_code": "ethics",
            "transparency_reporting": "transparency"
        }
        return mapping.get(question_id, "other")
    
    def _calculate_average(self, scores: List[float]) -> float:
        """Calculate average score, handling empty lists."""
        return sum(scores) / len(scores) if scores else 50.0
    
    def _determine_badge(self, score: float) -> str:
        """Determine ESG badge based on overall score."""
        if score >= 90:
            return "ESG Champion"
        elif score >= 80:
            return "Green Leader"
        elif score >= 70:
            return "Sustainability Star"
        elif score >= 60:
            return "Eco Improver"
        elif score >= 50:
            return "ESG Starter"
        else:
            return "ESG Beginner"
    
    def _calculate_level(self, score: float) -> int:
        """Calculate user level based on score."""
        return min(int(score / 10) + 1, 10)
    
    def _analyze_performance(
        self, 
        env_score: float, 
        social_score: float, 
        gov_score: float,
        *sub_scores
    ) -> Tuple[List[str], List[str]]:
        """Analyze performance to identify improvement areas and strengths."""
        improvement_areas = []
        strengths = []
        
        # Main categories
        if env_score < 60:
            improvement_areas.append("Environmental impact reduction")
        elif env_score >= 75:
            strengths.append("Strong environmental practices")
        
        if social_score < 60:
            improvement_areas.append("Social responsibility and employee welfare")
        elif social_score >= 75:
            strengths.append("Excellent social impact")
        
        if gov_score < 60:
            improvement_areas.append("Governance and transparency")
        elif gov_score >= 75:
            strengths.append("Robust governance framework")
        
        # Sub-categories analysis
        emissions_score, energy_score, waste_score, diversity_score, employee_score, community_score, ethics_score, transparency_score = sub_scores
        
        if emissions_score < 50:
            improvement_areas.append("Carbon emissions reduction")
        if energy_score < 50:
            improvement_areas.append("Energy efficiency")
        if waste_score < 50:
            improvement_areas.append("Waste management and recycling")
        if diversity_score < 50:
            improvement_areas.append("Workplace diversity and inclusion")
        if employee_score < 50:
            improvement_areas.append("Employee satisfaction and development")
        if ethics_score < 50:
            improvement_areas.append("Ethics and compliance training")
        if transparency_score < 50:
            improvement_areas.append("Transparency and reporting")
        
        return improvement_areas, strengths
    
    def _calculate_industry_percentile(self, score: float, industry: str) -> float:
        """Calculate industry percentile (mock calculation)."""
        # In a real implementation, this would compare against industry database
        industry_averages = {
            "retail": 65.0,
            "manufacturing": 60.0,
            "technology": 70.0,
            "finance": 68.0,
            "healthcare": 72.0
        }
        
        industry_avg = industry_averages.get(industry, 65.0)
        
        # Simple percentile calculation
        if score >= industry_avg + 20:
            return 95.0
        elif score >= industry_avg + 10:
            return 80.0
        elif score >= industry_avg:
            return 60.0
        elif score >= industry_avg - 10:
            return 40.0
        else:
            return 20.0
    
    def _generate_recommendations(
        self, 
        category_scores: Dict[str, List[float]], 
        sub_category_scores: Dict[str, List[float]],
        industry: str,
        company_size: str
    ) -> Tuple[List[str], List[str]]:
        """Generate quick wins and long-term goals."""
        quick_wins = []
        long_term_goals = []
        
        # Analyze weakest areas for recommendations
        env_avg = self._calculate_average(category_scores["environmental"])
        social_avg = self._calculate_average(category_scores["social"])
        gov_avg = self._calculate_average(category_scores["governance"])
        
        # Quick wins (easy, low-cost improvements)
        if env_avg < 60:
            quick_wins.extend([
                "Switch to LED lighting",
                "Implement basic recycling program",
                "Set up energy monitoring"
            ])
        
        if social_avg < 60:
            quick_wins.extend([
                "Conduct employee satisfaction survey",
                "Create diversity and inclusion policy",
                "Organize team building activities"
            ])
        
        if gov_avg < 60:
            quick_wins.extend([
                "Develop code of conduct",
                "Implement basic data privacy measures",
                "Create supplier guidelines"
            ])
        
        # Long-term goals (strategic, higher-impact initiatives)
        if env_avg < 70:
            long_term_goals.extend([
                "Achieve carbon neutrality",
                "Implement circular economy practices",
                "Install renewable energy systems"
            ])
        
        if social_avg < 70:
            long_term_goals.extend([
                "Establish comprehensive DEI program",
                "Create employee development pathways",
                "Launch community investment initiative"
            ])
        
        if gov_avg < 70:
            long_term_goals.extend([
                "Obtain ESG certification",
                "Implement comprehensive ESG reporting",
                "Establish ESG governance committee"
            ])
        
        return quick_wins[:5], long_term_goals[:5]  # Limit to 5 each
    
    def calculate_user_progress(
        self, 
        user_id: str, 
        completed_tasks: int, 
        total_points: int,
        current_score: float
    ) -> UserProgress:
        """Calculate user's overall progress and achievements."""
        # Calculate level based on points
        level = min(int(total_points / 100) + 1, 20)
        
        # Determine earned badges
        earned_badges = []
        for badge in DEFAULT_BADGES:
            if total_points >= badge.points_required:
                badge.earned_at = datetime.utcnow()
                earned_badges.append(badge)
        
        # Mock data for demonstration
        return UserProgress(
            user_id=user_id,
            total_points=total_points,
            level=level,
            badges_earned=earned_badges,
            completed_tasks=completed_tasks,
            pending_tasks=max(0, 10 - completed_tasks),
            current_streak=7,  # Mock streak
            last_activity=datetime.utcnow()
        )


# Global scoring service instance
scoring_service = ScoringService()

