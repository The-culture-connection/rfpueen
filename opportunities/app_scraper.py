"""
Simple application form finder
Since you already have scraping software for opportunities,
this is a lightweight utility to find application URLs
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


def find_application_form(opportunity):
    """
    Find application form URL for an opportunity
    Returns dict with application_url, instructions, confidence
    """
    # Check for direct application URLs in opportunity data
    direct_url = _check_direct_urls(opportunity)
    if direct_url:
        return {
            'application_url': direct_url,
            'instructions': _generate_instructions(opportunity),
            'confidence': 1.0
        }
    
    # Try scraping main URL
    main_url = opportunity.url or opportunity.synopsis_url or opportunity.link
    if main_url:
        try:
            app_url = _scrape_for_application(main_url)
            if app_url:
                return {
                    'application_url': app_url,
                    'instructions': _generate_instructions(opportunity),
                    'confidence': 0.8
                }
        except Exception as e:
            logger.error(f"Scraping error for {main_url}: {e}")
    
    # No direct URL found, return instructions only
    return {
        'application_url': None,
        'instructions': _generate_instructions(opportunity),
        'confidence': 0.0
    }


def _check_direct_urls(opportunity):
    """Check if opportunity data contains application URLs"""
    extra_data = opportunity.extra_data or {}
    
    # Check for application URL fields
    for field in ['applicationUrl', 'applyUrl', 'formUrl', 'submissionUrl']:
        url = extra_data.get(field)
        if url and _is_application_url(url):
            return url
    
    # Check description for application URLs
    description = opportunity.description or opportunity.summary or ""
    urls = re.findall(r'https?://[^\s<>"]+', description)
    
    for url in urls:
        if _is_application_url(url):
            return url
    
    return None


def _is_application_url(url):
    """Check if URL likely points to an application form"""
    url_lower = url.lower()
    
    # Avoid job application URLs
    if any(word in url_lower for word in ['job', 'career', 'employment']):
        return False
    
    # Check for application keywords
    return any(word in url_lower for word in ['apply', 'application', 'submit', 'form', 'proposal'])


def _scrape_for_application(url, timeout=10):
    """Scrape page for application links"""
    try:
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        links = soup.find_all('a', href=True)
        
        best_score = 0
        best_url = None
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            absolute_url = urljoin(url, href)
            
            score = _score_application_link(absolute_url, text)
            if score > best_score:
                best_score = score
                best_url = absolute_url
        
        return best_url if best_score > 5 else None
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return None


def _score_application_link(url, text):
    """Score how likely a link is to be an application form"""
    score = 0
    url_lower = url.lower()
    text_lower = text.lower()
    
    # Negative check
    if any(word in url_lower or word in text_lower for word in ['job', 'career']):
        return 0
    
    # URL keywords
    for keyword in ['apply', 'application', 'submit', 'form', 'proposal']:
        if keyword in url_lower:
            score += 3
    
    # Text keywords
    for keyword in ['apply', 'application', 'submit', 'form']:
        if keyword in text_lower:
            score += 2
    
    # Exact phrases
    if any(phrase in text_lower for phrase in ['apply now', 'submit application', 'application form']):
        score += 5
    
    return score


def _generate_instructions(opportunity):
    """Generate application instructions"""
    instructions = []
    
    if opportunity.url or opportunity.synopsis_url or opportunity.link:
        main_url = opportunity.url or opportunity.synopsis_url or opportunity.link
        instructions.append(f"1. Visit the opportunity page:\n   {main_url}")
        instructions.append("2. Look for 'Apply', 'Submit Proposal', or 'Application Form' links")
    
    if opportunity.agency or opportunity.department:
        agency = opportunity.agency or opportunity.department
        instructions.append(f"3. Contact {agency} directly for application instructions")
    
    if opportunity.contact_email:
        instructions.append(f"4. Email: {opportunity.contact_email}")
    
    if opportunity.contact_phone:
        instructions.append(f"5. Phone: {opportunity.contact_phone}")
    
    if opportunity.close_date or opportunity.deadline:
        deadline = opportunity.close_date or opportunity.deadline
        instructions.append(f"\n⚠️ Application deadline: {deadline.strftime('%B %d, %Y')}")
    
    if not instructions:
        instructions.append("Check the opportunity details for application information.")
    
    return "\n".join(instructions)
