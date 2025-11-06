"""
Application Form Scraper
This module handles finding direct application form URLs from opportunity websites
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ApplicationFormScraper:
    """Scrapes websites to find application form URLs"""
    
    # Common form-related keywords
    FORM_KEYWORDS = [
        'apply', 'application', 'submit', 'submission', 
        'form', 'register', 'registration', 'proposal',
        'bid', 'tender', 'response', 'rfp-response',
        'grant-application', 'apply-now', 'application-form'
    ]
    
    # Common form URL patterns
    FORM_URL_PATTERNS = [
        r'/apply',
        r'/application',
        r'/submit',
        r'/form',
        r'/register',
        r'/proposal',
        r'/bid',
        r'/response',
        r'apply\.php',
        r'application\.aspx',
        r'submit\.html',
    ]
    
    # Headers to mimic a real browser
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    @staticmethod
    def extract_application_url_from_data(opportunity_data: Dict) -> Optional[str]:
        """
        First check if application URL exists in opportunity data
        """
        # Check common field names for application URLs
        url_fields = [
            'applicationUrl', 'applyUrl', 'formUrl', 
            'submissionUrl', 'applicationLink', 'applyLink'
        ]
        
        for field in url_fields:
            if field in opportunity_data and opportunity_data[field]:
                url = opportunity_data[field]
                if ApplicationFormScraper._is_valid_url(url):
                    return url
        
        # Check description and summary for URLs
        text_fields = ['description', 'summary', 'fullDescription']
        for field in text_fields:
            if field in opportunity_data:
                urls = ApplicationFormScraper._extract_urls_from_text(
                    str(opportunity_data[field])
                )
                for url in urls:
                    if ApplicationFormScraper._looks_like_application_form(url):
                        return url
        
        return None
    
    @staticmethod
    def find_application_form(
        opportunity_url: str,
        opportunity_data: Dict = None,
        timeout: int = 10
    ) -> Tuple[Optional[str], Optional[str], List[str]]:
        """
        Find application form URL by scraping the opportunity page
        
        Returns:
            - application_url: Direct URL to application form
            - form_path: Human-readable navigation path to form
            - notes: List of findings/notes
        """
        notes = []
        
        # First, check if URL is already in the data
        if opportunity_data:
            data_url = ApplicationFormScraper.extract_application_url_from_data(opportunity_data)
            if data_url:
                notes.append(f"Found application URL in opportunity data")
                return data_url, "Direct link from opportunity data", notes
        
        # Check if the main URL itself looks like an application form
        if ApplicationFormScraper._looks_like_application_form(opportunity_url):
            notes.append("Main URL appears to be the application form")
            return opportunity_url, "Main opportunity URL", notes
        
        # Try to scrape the page
        try:
            response = requests.get(
                opportunity_url,
                headers=ApplicationFormScraper.HEADERS,
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Strategy 1: Find links with form-related text
            form_links = ApplicationFormScraper._find_form_links_by_text(soup, opportunity_url)
            if form_links:
                notes.append(f"Found {len(form_links)} potential application links")
                return form_links[0], "Link text contains 'apply' or 'application'", notes
            
            # Strategy 2: Find links with form-related URLs
            form_url_links = ApplicationFormScraper._find_form_links_by_url(soup, opportunity_url)
            if form_url_links:
                notes.append(f"Found links with form-related URL patterns")
                return form_url_links[0], "URL pattern suggests application form", notes
            
            # Strategy 3: Find buttons or forms
            form_actions = ApplicationFormScraper._find_form_actions(soup, opportunity_url)
            if form_actions:
                notes.append(f"Found form submission actions")
                return form_actions[0], "Form action URL found", notes
            
            # Strategy 4: Check for iframes with forms
            iframe_urls = ApplicationFormScraper._find_iframe_forms(soup, opportunity_url)
            if iframe_urls:
                notes.append("Found form embedded in iframe")
                return iframe_urls[0], "Embedded form in iframe", notes
            
            notes.append("No application form found on page")
            return None, None, notes
            
        except requests.Timeout:
            notes.append(f"Timeout while fetching URL")
            logger.warning(f"Timeout fetching {opportunity_url}")
            return None, None, notes
        except requests.RequestException as e:
            notes.append(f"Error fetching URL: {str(e)}")
            logger.error(f"Error fetching {opportunity_url}: {e}")
            return None, None, notes
        except Exception as e:
            notes.append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error scraping {opportunity_url}: {e}")
            return None, None, notes
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def _looks_like_application_form(url: str) -> bool:
        """Check if URL looks like an application form"""
        url_lower = url.lower()
        
        # Check against form keywords
        for keyword in ApplicationFormScraper.FORM_KEYWORDS:
            if keyword in url_lower:
                return True
        
        # Check against form URL patterns
        for pattern in ApplicationFormScraper.FORM_URL_PATTERNS:
            if re.search(pattern, url_lower):
                return True
        
        return False
    
    @staticmethod
    def _extract_urls_from_text(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def _find_form_links_by_text(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find links with form-related text"""
        form_links = []
        
        for link in soup.find_all('a', href=True):
            link_text = link.get_text().lower().strip()
            link_href = link['href']
            
            # Check if link text contains form keywords
            for keyword in ApplicationFormScraper.FORM_KEYWORDS:
                if keyword in link_text:
                    full_url = urljoin(base_url, link_href)
                    if ApplicationFormScraper._is_valid_url(full_url):
                        form_links.append(full_url)
                    break
        
        return form_links
    
    @staticmethod
    def _find_form_links_by_url(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find links with form-related URL patterns"""
        form_links = []
        
        for link in soup.find_all('a', href=True):
            link_href = link['href']
            full_url = urljoin(base_url, link_href)
            
            if ApplicationFormScraper._looks_like_application_form(full_url):
                if ApplicationFormScraper._is_valid_url(full_url):
                    form_links.append(full_url)
        
        return form_links
    
    @staticmethod
    def _find_form_actions(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find form action URLs"""
        form_actions = []
        
        for form in soup.find_all('form'):
            action = form.get('action')
            if action:
                full_url = urljoin(base_url, action)
                if ApplicationFormScraper._is_valid_url(full_url):
                    form_actions.append(full_url)
        
        return form_actions
    
    @staticmethod
    def _find_iframe_forms(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find iframes that might contain forms"""
        iframe_urls = []
        
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src:
                full_url = urljoin(base_url, src)
                if ApplicationFormScraper._looks_like_application_form(full_url):
                    if ApplicationFormScraper._is_valid_url(full_url):
                        iframe_urls.append(full_url)
        
        return iframe_urls
    
    @staticmethod
    def generate_application_instructions(opportunity_data: Dict) -> str:
        """
        Generate application instructions when form URL cannot be found
        """
        instructions = []
        
        # Add main URL
        main_url = (
            opportunity_data.get('url') or 
            opportunity_data.get('synopsisUrl') or 
            opportunity_data.get('link')
        )
        if main_url:
            instructions.append(f"1. Visit the opportunity page: {main_url}")
        
        # Add agency contact info
        agency = opportunity_data.get('agency') or opportunity_data.get('department')
        if agency:
            instructions.append(f"2. Contact {agency} directly for application instructions")
        
        # Add contact details
        if opportunity_data.get('contactEmail'):
            instructions.append(f"   Email: {opportunity_data['contactEmail']}")
        
        if opportunity_data.get('contactPhone'):
            instructions.append(f"   Phone: {opportunity_data['contactPhone']}")
        
        # Add deadline
        deadline = opportunity_data.get('closeDate') or opportunity_data.get('deadline')
        if deadline:
            instructions.append(f"3. Application deadline: {deadline}")
        
        # Add location if relevant
        location = (
            opportunity_data.get('place') or 
            ', '.join(filter(None, [
                opportunity_data.get('city'),
                opportunity_data.get('state')
            ]))
        )
        if location:
            instructions.append(f"4. Location: {location}")
        
        if not instructions:
            instructions.append("Check the opportunity page for application details.")
        
        return "\n".join(instructions)
