"""
Web scraper to find application form pathways
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from typing import Dict, List, Optional, Tuple
from .models import Opportunity, ApplicationPathway

logger = logging.getLogger(__name__)


class ApplicationFormScraper:
    """Scraper to find application form URLs and pathways"""
    
    # Keywords that indicate application forms or submission pages
    APPLICATION_KEYWORDS = [
        'apply', 'application', 'submit', 'form', 'proposal',
        'registration', 'register', 'enrollment', 'entry'
    ]
    
    # Keywords to avoid (false positives)
    AVOID_KEYWORDS = [
        'job', 'career', 'employment', 'resume', 'vacancy'
    ]
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_application_pathway(self, opportunity: Opportunity) -> Tuple[Optional[str], List[str], float]:
        """
        Find the application URL for an opportunity
        Returns: (application_url, pathway_steps, confidence_score)
        """
        # First, check obvious URL fields
        direct_url = self._check_direct_urls(opportunity)
        if direct_url:
            return direct_url, ['Direct application URL found in opportunity data'], 1.0
        
        # Try to scrape the main page
        main_url = opportunity.url or opportunity.synopsis_url or opportunity.link
        if not main_url:
            return None, ['No URL provided for this opportunity'], 0.0
        
        try:
            application_url, steps, confidence = self._scrape_for_application(main_url)
            return application_url, steps, confidence
        except Exception as e:
            logger.error(f"Error scraping {main_url}: {e}")
            return None, [f'Error accessing page: {str(e)}'], 0.0
    
    def _check_direct_urls(self, opportunity: Opportunity) -> Optional[str]:
        """Check if opportunity already has application URL in data"""
        # Check extra_data for application-related URLs
        extra_data = opportunity.extra_data or {}
        
        possible_fields = [
            'applicationUrl', 'application_url', 'applyUrl', 'apply_url',
            'formUrl', 'form_url', 'submissionUrl', 'submission_url'
        ]
        
        for field in possible_fields:
            url = extra_data.get(field)
            if url and self._is_application_url(url):
                return url
        
        # Check description for application URLs
        description = opportunity.description or opportunity.summary or ""
        urls = re.findall(r'https?://[^\s<>"]+', description)
        
        for url in urls:
            if self._is_application_url(url):
                return url
        
        return None
    
    def _is_application_url(self, url: str) -> bool:
        """Check if URL likely points to an application form"""
        url_lower = url.lower()
        
        # Check for avoid keywords
        if any(avoid in url_lower for avoid in self.AVOID_KEYWORDS):
            return False
        
        # Check for application keywords
        return any(keyword in url_lower for keyword in self.APPLICATION_KEYWORDS)
    
    def _scrape_for_application(self, url: str) -> Tuple[Optional[str], List[str], float]:
        """
        Scrape a page looking for application links
        Returns: (application_url, pathway_steps, confidence_score)
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            candidates = []
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                # Make absolute URL
                absolute_url = urljoin(url, href)
                
                # Check if it looks like an application link
                score = self._score_application_link(absolute_url, text)
                
                if score > 0:
                    candidates.append({
                        'url': absolute_url,
                        'text': text,
                        'score': score
                    })
            
            # Sort by score
            candidates.sort(key=lambda x: x['score'], reverse=True)
            
            if candidates:
                best = candidates[0]
                steps = [
                    f'Visit main page: {url}',
                    f'Click on "{best["text"][:50]}"',
                    f'Navigate to: {best["url"]}'
                ]
                confidence = min(best['score'] / 10.0, 1.0)  # Normalize to 0-1
                return best['url'], steps, confidence
            
            # No obvious application link found
            return None, ['No clear application link found on page'], 0.0
            
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return None, [f'Could not access page: {str(e)}'], 0.0
    
    def _score_application_link(self, url: str, text: str) -> float:
        """
        Score how likely a link is to be an application form
        Higher score = more likely
        """
        score = 0.0
        
        url_lower = url.lower()
        text_lower = text.lower()
        
        # Check for avoid keywords (negative score)
        if any(avoid in url_lower or avoid in text_lower for avoid in self.AVOID_KEYWORDS):
            return 0.0
        
        # Check URL for application keywords
        for keyword in self.APPLICATION_KEYWORDS:
            if keyword in url_lower:
                score += 3.0
        
        # Check link text for application keywords
        for keyword in self.APPLICATION_KEYWORDS:
            if keyword in text_lower:
                score += 2.0
        
        # Boost for exact phrases
        exact_phrases = ['apply now', 'submit application', 'application form', 'apply online']
        for phrase in exact_phrases:
            if phrase in text_lower:
                score += 5.0
        
        return score
    
    def generate_instructions(self, opportunity: Opportunity) -> str:
        """Generate application instructions when no direct URL is found"""
        instructions = []
        
        if opportunity.url or opportunity.synopsis_url or opportunity.link:
            main_url = opportunity.url or opportunity.synopsis_url or opportunity.link
            instructions.append(f"1. Visit the opportunity page:\n   {main_url}")
            instructions.append("2. Look for 'Apply', 'Submit Proposal', or 'Application Form' links")
        
        if opportunity.agency or opportunity.department:
            agency = opportunity.agency or opportunity.department
            instructions.append(f"3. Contact {agency} directly for application instructions")
        
        if opportunity.contact_email:
            instructions.append(f"4. Email inquiries: {opportunity.contact_email}")
        
        if opportunity.contact_phone:
            instructions.append(f"5. Phone inquiries: {opportunity.contact_phone}")
        
        if opportunity.close_date or opportunity.deadline:
            deadline = opportunity.close_date or opportunity.deadline
            instructions.append(f"\n⚠️ Application deadline: {deadline.strftime('%B %d, %Y')}")
        
        if not instructions:
            instructions.append("Check the opportunity details for application information.")
        
        return "\n".join(instructions)
    
    def process_opportunity(self, opportunity: Opportunity, force_update: bool = False) -> Optional[ApplicationPathway]:
        """
        Process an opportunity to find and store application pathway
        """
        # Check if pathway already exists
        if not force_update:
            existing = ApplicationPathway.objects.filter(
                opportunity=opportunity,
                is_active=True
            ).first()
            
            if existing:
                return existing
        
        # Find application pathway
        app_url, steps, confidence = self.find_application_pathway(opportunity)
        
        if app_url:
            # Create or update pathway
            pathway, created = ApplicationPathway.objects.update_or_create(
                opportunity=opportunity,
                application_url=app_url,
                defaults={
                    'pathway_steps': steps,
                    'confidence_score': confidence,
                    'is_active': True
                }
            )
            
            logger.info(f"{'Created' if created else 'Updated'} pathway for {opportunity.title[:50]}")
            return pathway
        
        return None


def find_application_form_for_opportunity(opportunity: Opportunity) -> Dict:
    """
    Convenience function to find application form for an opportunity
    Returns a dict with application_url and instructions
    """
    scraper = ApplicationFormScraper()
    
    # Check for existing pathway
    pathway = ApplicationPathway.objects.filter(
        opportunity=opportunity,
        is_active=True
    ).order_by('-confidence_score').first()
    
    if pathway:
        return {
            'application_url': pathway.application_url,
            'instructions': scraper.generate_instructions(opportunity),
            'confidence': pathway.confidence_score,
            'pathway_steps': pathway.pathway_steps
        }
    
    # Try to find pathway
    app_url, steps, confidence = scraper.find_application_pathway(opportunity)
    
    if app_url:
        # Store pathway
        ApplicationPathway.objects.create(
            opportunity=opportunity,
            application_url=app_url,
            pathway_steps=steps,
            confidence_score=confidence
        )
        
        return {
            'application_url': app_url,
            'instructions': scraper.generate_instructions(opportunity),
            'confidence': confidence,
            'pathway_steps': steps
        }
    
    # No URL found, return instructions only
    return {
        'application_url': None,
        'instructions': scraper.generate_instructions(opportunity),
        'confidence': 0.0,
        'pathway_steps': []
    }
