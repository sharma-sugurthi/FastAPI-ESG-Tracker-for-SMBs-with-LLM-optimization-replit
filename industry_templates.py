
"""
Custom industry templates for ESG assessments.
"""

from typing import Dict, List, Any
import json

class IndustryTemplateService:
    """Service for managing industry-specific ESG templates."""
    
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load default industry templates."""
        return {
            "retail": {
                "name": "Retail & Consumer Goods",
                "description": "ESG framework for retail and consumer goods companies",
                "questions": [
                    {
                        "category": "Environmental",
                        "question": "How do you manage packaging waste and promote circular economy principles?",
                        "weight": 0.25,
                        "industry_specific": True
                    },
                    {
                        "category": "Environmental", 
                        "question": "What sustainable sourcing practices do you implement for your products?",
                        "weight": 0.20,
                        "industry_specific": True
                    },
                    {
                        "category": "Social",
                        "question": "How do you ensure fair labor practices across your supply chain?",
                        "weight": 0.20,
                        "industry_specific": True
                    },
                    {
                        "category": "Social",
                        "question": "What community engagement programs do you support?",
                        "weight": 0.15,
                        "industry_specific": False
                    },
                    {
                        "category": "Governance",
                        "question": "How do you ensure transparency in your sustainability reporting?",
                        "weight": 0.20,
                        "industry_specific": False
                    }
                ],
                "compliance_requirements": [
                    "EU Taxonomy Regulation",
                    "CSRD (Corporate Sustainability Reporting Directive)",
                    "California Transparency in Supply Chains Act",
                    "UK Modern Slavery Act"
                ],
                "key_metrics": [
                    "Carbon footprint per product unit",
                    "Percentage of sustainable materials",
                    "Supply chain transparency score",
                    "Employee satisfaction index"
                ]
            },
            
            "technology": {
                "name": "Technology & Software",
                "description": "ESG framework for technology companies",
                "questions": [
                    {
                        "category": "Environmental",
                        "question": "How do you measure and reduce the carbon footprint of your digital services?",
                        "weight": 0.25,
                        "industry_specific": True
                    },
                    {
                        "category": "Environmental",
                        "question": "What data center sustainability practices do you implement?",
                        "weight": 0.20,
                        "industry_specific": True
                    },
                    {
                        "category": "Social",
                        "question": "How do you ensure digital accessibility and inclusion?",
                        "weight": 0.20,
                        "industry_specific": True
                    },
                    {
                        "category": "Social",
                        "question": "What data privacy and security measures do you have in place?",
                        "weight": 0.15,
                        "industry_specific": True
                    },
                    {
                        "category": "Governance",
                        "question": "How do you govern AI ethics and algorithmic fairness?",
                        "weight": 0.20,
                        "industry_specific": True
                    }
                ],
                "compliance_requirements": [
                    "GDPR (General Data Protection Regulation)",
                    "CCPA (California Consumer Privacy Act)",
                    "EU AI Act",
                    "ISO 27001 (Information Security)"
                ],
                "key_metrics": [
                    "Energy efficiency (PUE) of data centers",
                    "Percentage of renewable energy use",
                    "Diversity in tech roles",
                    "Data breach incident rate"
                ]
            },
            
            "manufacturing": {
                "name": "Manufacturing & Industrial",
                "description": "ESG framework for manufacturing companies",
                "questions": [
                    {
                        "category": "Environmental",
                        "question": "How do you manage industrial waste and implement circular economy practices?",
                        "weight": 0.30,
                        "industry_specific": True
                    },
                    {
                        "category": "Environmental",
                        "question": "What energy efficiency measures have you implemented in your facilities?",
                        "weight": 0.20,
                        "industry_specific": True
                    },
                    {
                        "category": "Social",
                        "question": "How do you ensure workplace safety and health standards?",
                        "weight": 0.25,
                        "industry_specific": True
                    },
                    {
                        "category": "Social",
                        "question": "What training and development programs do you offer employees?",
                        "weight": 0.10,
                        "industry_specific": False
                    },
                    {
                        "category": "Governance",
                        "question": "How do you manage environmental compliance and reporting?",
                        "weight": 0.15,
                        "industry_specific": True
                    }
                ],
                "compliance_requirements": [
                    "ISO 14001 (Environmental Management)",
                    "OSHA Safety Standards",
                    "REACH Regulation (EU)",
                    "RoHS Directive"
                ],
                "key_metrics": [
                    "Water usage per unit produced",
                    "Waste reduction percentage",
                    "Lost time injury frequency rate",
                    "Energy intensity ratio"
                ]
            }
        }
    
    def get_template(self, industry: str) -> Dict[str, Any]:
        """Get template for specific industry."""
        return self.templates.get(industry.lower(), self._get_generic_template())
    
    def get_available_industries(self) -> List[str]:
        """Get list of available industry templates."""
        return list(self.templates.keys())
    
    def _get_generic_template(self) -> Dict[str, Any]:
        """Get generic ESG template for industries not specifically covered."""
        return {
            "name": "Generic ESG Assessment",
            "description": "Standard ESG framework for all industries",
            "questions": [
                {
                    "category": "Environmental",
                    "question": "How do you measure and reduce your environmental impact?",
                    "weight": 0.2,
                    "industry_specific": False
                },
                {
                    "category": "Environmental",
                    "question": "What climate change mitigation strategies do you implement?",
                    "weight": 0.2,
                    "industry_specific": False
                },
                {
                    "category": "Social",
                    "question": "How do you promote diversity, equity, and inclusion?",
                    "weight": 0.2,
                    "industry_specific": False
                },
                {
                    "category": "Social",
                    "question": "What employee wellbeing programs do you offer?",
                    "weight": 0.2,
                    "industry_specific": False
                },
                {
                    "category": "Governance",
                    "question": "How do you ensure ethical business practices and transparency?",
                    "weight": 0.2,
                    "industry_specific": False
                }
            ],
            "compliance_requirements": [
                "Local environmental regulations",
                "Labor law compliance",
                "Corporate governance standards"
            ],
            "key_metrics": [
                "Carbon emissions (Scope 1, 2, 3)",
                "Employee satisfaction score",
                "Board diversity percentage",
                "Ethics training completion rate"
            ]
        }
    
    def create_custom_template(self, industry: str, template_data: Dict[str, Any]) -> bool:
        """Create a new custom industry template."""
        try:
            # Validate template structure
            required_keys = ["name", "description", "questions"]
            if not all(key in template_data for key in required_keys):
                return False
            
            # Validate questions structure
            for question in template_data["questions"]:
                required_question_keys = ["category", "question", "weight"]
                if not all(key in question for key in required_question_keys):
                    return False
            
            # Add template
            self.templates[industry.lower()] = template_data
            return True
            
        except Exception as e:
            print(f"Error creating custom template: {e}")
            return False

# Global template service instance
template_service = IndustryTemplateService()
