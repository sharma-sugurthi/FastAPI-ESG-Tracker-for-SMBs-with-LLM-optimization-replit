"""
Web scraping and regulatory alerts data models.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field, validator
from datetime import datetime
from enum import Enum
from fastapi import APIRouter, HTTPException, Depends

# Create the router
router = APIRouter()


class ScrapingStatus(str, Enum):
    """Web scraping status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONSENT_REQUIRED = "consent_required"


class ESGKeyword(str, Enum):
    """ESG-related keywords for content extraction."""
    EMISSIONS = "emissions"
    CARBON = "carbon"
    SUSTAINABILITY = "sustainability"
    GREEN = "green"
    RENEWABLE = "renewable"
    DIVERSITY = "diversity"
    INCLUSION = "inclusion"
    GOVERNANCE = "governance"
    ETHICS = "ethics"
    TRANSPARENCY = "transparency"
    PACKAGING = "packaging"
    RECYCLING = "recycling"
    WASTE = "waste"
    ENERGY = "energy"
    WATER = "water"


class ScrapingRequest(BaseModel):
    """Web scraping request model."""
    url: HttpUrl
    user_consent: bool = False
    extract_esg_only: bool = True
    keywords: Optional[List[str]] = None
    max_content_length: int = Field(default=10000, le=50000)
    
    @validator('url')
    def validate_url(cls, v):
        """Validate that URL is accessible and not blocked."""
        url_str = str(v)
        
        # Block certain domains for privacy/legal reasons
        blocked_domains = [
            'facebook.com', 'twitter.com', 'linkedin.com',
            'instagram.com', 'tiktok.com', 'youtube.com'
        ]
        
        for domain in blocked_domains:
            if domain in url_str.lower():
                raise ValueError(f"Scraping not allowed for domain: {domain}")
        
        return v


class ScrapedContent(BaseModel):
    """Scraped content model."""
    url: str
    title: Optional[str] = None
    content: str
    esg_signals: List[str]
    keywords_found: List[str]
    content_length: int
    scraped_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapingResult(BaseModel):
    """Web scraping result model."""
    request_id: str
    status: ScrapingStatus
    url: str
    scraped_content: Optional[ScrapedContent] = None
    error_message: Optional[str] = None
    gdpr_compliance: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NewsSource(str, Enum):
    """News sources for regulatory alerts."""
    GOOGLE_NEWS = "google_news"
    RSS_FEEDS = "rss_feeds"
    MANUAL = "manual"


class AlertCategory(str, Enum):
    """Alert categories."""
    REGULATORY = "regulatory"
    COMPLIANCE = "compliance"
    INDUSTRY_NEWS = "industry_news"
    ESG_TRENDS = "esg_trends"
    POLICY_CHANGES = "policy_changes"


class RegulatoryAlert(BaseModel):
    """Regulatory alert model."""
    id: str
    title: str
    summary: str
    full_content: Optional[str] = None
    source: NewsSource
    source_url: Optional[str] = None
    category: AlertCategory
    keywords: List[str]
    relevance_score: float = Field(ge=0.0, le=1.0)
    published_at: datetime
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertsRequest(BaseModel):
    """Request model for regulatory alerts."""
    keywords: Optional[List[str]] = None
    categories: Optional[List[AlertCategory]] = None
    max_results: int = Field(default=10, le=50)
    days_back: int = Field(default=7, le=30)
    min_relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)


class AlertsResponse(BaseModel):
    """Response model for regulatory alerts."""
    alerts: List[RegulatoryAlert]
    total_found: int
    search_keywords: List[str]
    generated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GDPRCompliance(BaseModel):
    """GDPR compliance tracking model."""
    user_consent_given: bool
    consent_timestamp: Optional[datetime] = None
    data_retention_days: int = 30
    purpose_limitation: str = "ESG analysis only"
    data_minimization: bool = True
    user_rights_notice: str = "Users can request data deletion at any time"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Default ESG keywords for content extraction
DEFAULT_ESG_KEYWORDS = [
    "emissions", "carbon footprint", "co2", "greenhouse gas",
    "sustainability", "sustainable", "green energy", "renewable",
    "diversity", "inclusion", "dei", "equal opportunity",
    "governance", "ethics", "transparency", "compliance",
    "packaging", "recyclable", "recycling", "waste reduction",
    "energy efficiency", "water conservation", "environmental",
    "social responsibility", "corporate governance", "esg",
    "climate change", "net zero", "carbon neutral"
]

# Default news RSS feeds for regulatory alerts
DEFAULT_NEWS_FEEDS = [
    {
        "name": "Environmental News",
        "url": "https://news.google.com/rss/search?q=environmental+regulations&hl=en&gl=US&ceid=US:en",
        "category": AlertCategory.REGULATORY
    },
    {
        "name": "ESG News",
        "url": "https://news.google.com/rss/search?q=ESG+compliance&hl=en&gl=US&ceid=US:en",
        "category": AlertCategory.ESG_TRENDS
    },
    {
        "name": "Sustainability Regulations",
        "url": "https://news.google.com/rss/search?q=sustainability+regulations&hl=en&gl=US&ceid=US:en",
        "category": AlertCategory.POLICY_CHANGES
    },
    {
        "name": "Corporate Governance",
        "url": "https://news.google.com/rss/search?q=corporate+governance+regulations&hl=en&gl=US&ceid=US:en",
        "category": AlertCategory.COMPLIANCE
    }
]


# Scraping API Endpoints
@router.post("/scrape")
async def scrape_url_endpoint(request: ScrapingRequest):
    """Scrape a URL for ESG content with GDPR compliance."""
    try:
        # Import scraping service
        from scraping_service import scraping_service
        
        # For demo purposes, use a dummy user_id
        result = await scraping_service.scrape_url(request, "demo_user")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_regulatory_alerts(
    keywords: Optional[str] = None,
    max_results: int = 10,
    days_back: int = 7,
    min_relevance_score: float = 0.5
):
    """Get regulatory alerts from news sources."""
    try:
        # Import news service
        from scraping_service import news_service
        
        # Create alerts request
        alerts_request = AlertsRequest(
            keywords=keywords.split(",") if keywords else None,
            max_results=max_results,
            days_back=days_back,
            min_relevance_score=min_relevance_score
        )
        
        alerts = await news_service.get_regulatory_alerts(alerts_request)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gdpr/privacy-notice")
async def get_privacy_notice():
    """Get GDPR privacy notice for web scraping."""
    return {
        "privacy_notice": {
            "purpose": "ESG content analysis for compliance tracking",
            "data_collected": "Public web content, ESG-related text snippets",
            "retention_period": "30 days",
            "user_rights": [
                "Right to access your data",
                "Right to rectification",
                "Right to erasure",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object"
            ],
            "legal_basis": "Legitimate interest for business compliance analysis"
        },
        "consent_form": {
            "required_fields": ["user_consent", "url"],
            "consent_text": "I consent to the collection and processing of publicly available web content for ESG analysis purposes."
        }
    }

