"""
GDPR-compliant web scraping service for ESG content extraction.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import uuid
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time

try:
    from app.models.scraping import (
        ScrapingRequest, ScrapingResult, ScrapedContent, ScrapingStatus,
        GDPRCompliance, DEFAULT_ESG_KEYWORDS
    )
    from app.services.llm_service import llm_service
except Exception:
    from scraping import (
        ScrapingRequest, ScrapingResult, ScrapedContent, ScrapingStatus,
        GDPRCompliance, DEFAULT_ESG_KEYWORDS
    )
    from llm_service import llm_service


class ScrapingService:
    """GDPR-compliant web scraping service."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ESG-Compliance-Tracker/1.0 (Educational/Research Purpose)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.timeout = 10
        self.max_retries = 3
        self.rate_limit_delay = 1  # seconds between requests
    
    async def scrape_url(self, request: ScrapingRequest, user_id: str) -> ScrapingResult:
        """
        Scrape URL with GDPR compliance and ESG content extraction.
        """
        request_id = str(uuid.uuid4())
        
        # Check GDPR compliance
        gdpr_compliance = self._check_gdpr_compliance(request, user_id)
        
        if not request.user_consent:
            return ScrapingResult(
                request_id=request_id,
                status=ScrapingStatus.CONSENT_REQUIRED,
                url=str(request.url),
                gdpr_compliance=gdpr_compliance.dict(),
                created_at=datetime.utcnow(),
                error_message="User consent required for web scraping"
            )
        
        try:
            # Perform scraping
            scraped_content = await self._scrape_content(request)
            
            return ScrapingResult(
                request_id=request_id,
                status=ScrapingStatus.COMPLETED,
                url=str(request.url),
                scraped_content=scraped_content,
                gdpr_compliance=gdpr_compliance.dict(),
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
        
        except Exception as e:
            return ScrapingResult(
                request_id=request_id,
                status=ScrapingStatus.FAILED,
                url=str(request.url),
                gdpr_compliance=gdpr_compliance.dict(),
                created_at=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _check_gdpr_compliance(self, request: ScrapingRequest, user_id: str) -> GDPRCompliance:
        """Check and ensure GDPR compliance for scraping request."""
        return GDPRCompliance(
            user_consent_given=request.user_consent,
            consent_timestamp=datetime.utcnow() if request.user_consent else None,
            data_retention_days=30,
            purpose_limitation="ESG content analysis for compliance tracking",
            data_minimization=request.extract_esg_only,
            user_rights_notice="Data will be deleted after 30 days. Users can request immediate deletion."
        )
    
    async def _scrape_content(self, request: ScrapingRequest) -> ScrapedContent:
        """Scrape content from URL with ESG focus."""
        url = str(request.url)
        
        # Rate limiting
        time.sleep(self.rate_limit_delay)
        
        # Make request with retries
        response = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to fetch URL after {self.max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # Parse content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = None
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract text content
        text_content = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content length
        if len(text_content) > request.max_content_length:
            text_content = text_content[:request.max_content_length] + "..."
        
        # Extract ESG signals
        esg_signals = self._extract_esg_signals(text_content, request.keywords)
        
        # Find keywords
        keywords_found = self._find_keywords(text_content, request.keywords or DEFAULT_ESG_KEYWORDS)
        
        return ScrapedContent(
            url=url,
            title=title,
            content=text_content,
            esg_signals=esg_signals,
            keywords_found=keywords_found,
            content_length=len(text_content),
            scraped_at=datetime.utcnow()
        )
    
    def _extract_esg_signals(self, content: str, custom_keywords: Optional[List[str]] = None) -> List[str]:
        """Extract ESG-related signals from content."""
        keywords = custom_keywords or DEFAULT_ESG_KEYWORDS
        signals = []
        
        content_lower = content.lower()
        
        for keyword in keywords:
            # Find sentences containing the keyword
            sentences = re.split(r'[.!?]+', content)
            for sentence in sentences:
                if keyword.lower() in sentence.lower():
                    # Clean and add sentence
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 20 and len(clean_sentence) < 200:
                        signals.append(clean_sentence)
                        break  # Only add one sentence per keyword
        
        return signals[:10]  # Limit to top 10 signals
    
    def _find_keywords(self, content: str, keywords: List[str]) -> List[str]:
        """Find which keywords are present in the content."""
        content_lower = content.lower()
        found_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt."""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            response = self.session.get(robots_url, timeout=5)
            if response.status_code == 200:
                robots_content = response.text.lower()
                
                # Simple check for disallow rules
                if "disallow: /" in robots_content and "user-agent: *" in robots_content:
                    return False
            
            return True  # Allow if robots.txt not found or doesn't disallow
        except:
            return True  # Allow if can't check robots.txt
    
    def is_url_allowed(self, url: str) -> bool:
        """Check if URL is allowed for scraping."""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Block social media and personal sites
        blocked_domains = [
            'facebook.com', 'twitter.com', 'linkedin.com',
            'instagram.com', 'tiktok.com', 'youtube.com',
            'reddit.com', 'pinterest.com'
        ]
        
        for blocked in blocked_domains:
            if blocked in domain:
                return False
        
        # Check robots.txt
        return self.check_robots_txt(url)


class NewsService:
    """Service for fetching regulatory alerts from news sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ESG-Compliance-Tracker/1.0 (News Aggregation)',
        })
    
    async def fetch_regulatory_alerts(self, keywords: List[str], days_back: int = 7) -> List[Dict[str, Any]]:
        """Fetch regulatory alerts from Google News RSS."""
        alerts = []
        
        try:
            # Build search query
            query = " OR ".join(keywords) if keywords else "ESG regulations"
            
            # Google News RSS URL
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
            
            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()
            
            # Parse RSS feed
            import feedparser
            feed = feedparser.parse(response.content)
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            for entry in feed.entries[:20]:  # Limit to 20 entries
                try:
                    # Parse publication date
                    pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    
                    if pub_date < cutoff_date:
                        continue
                    
                    # Extract content
                    title = entry.title
                    summary = getattr(entry, 'summary', '')
                    link = entry.link
                    
                    # Calculate relevance score
                    relevance_score = self._calculate_relevance(title + " " + summary, keywords)
                    
                    if relevance_score >= 0.3:  # Minimum relevance threshold
                        alert = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "summary": summary,
                            "source_url": link,
                            "relevance_score": relevance_score,
                            "published_at": pub_date,
                            "keywords_found": self._find_keywords_in_text(title + " " + summary, keywords)
                        }
                        alerts.append(alert)
                
                except Exception as e:
                    print(f"Error processing news entry: {e}")
                    continue
            
            # Sort by relevance and date
            alerts.sort(key=lambda x: (x["relevance_score"], x["published_at"]), reverse=True)
            
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        return alerts
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matches."""
        if not keywords:
            return 0.5
        
        text_lower = text.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches += 1
        
        return min(matches / len(keywords), 1.0)
    
    def _find_keywords_in_text(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords appear in the text."""
        text_lower = text.lower()
        found = []
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(keyword)
        
        return found
    
    async def summarize_alert_with_llm(self, title: str, content: str) -> str:
        """Summarize news alert using LLM."""
        try:
            summary = await llm_service.summarize_news(f"Title: {title}\n\nContent: {content}")
            return summary
        except Exception as e:
            return f"Summary unavailable: {str(e)}"


# Global service instances
scraping_service = ScrapingService()
news_service = NewsService()

