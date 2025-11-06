"""
Application form finder service
Scans website URLs to find direct application forms
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time


class ApplicationFormFinder:
    """Find application forms on opportunity websites"""
    
    # Keywords that indicate application forms
    APPLICATION_KEYWORDS = [
        'apply', 'application', 'submit', 'submission', 'form', 
        'register', 'registration', 'apply now', 'submit proposal',
        'application form', 'apply online', 'submit application'
    ]
    
    # Common form field names that indicate application forms
    FORM_FIELD_KEYWORDS = [
        'name', 'email', 'organization', 'proposal', 'budget',
        'project', 'grant', 'application', 'contact'
    ]
    
    # URL patterns that suggest application pages
    APPLICATION_URL_PATTERNS = [
        r'/apply',
        r'/application',
        r'/submit',
        r'/form',
        r'/register',
        r'/submission',
        r'/proposal',
    ]
    
    def __init__(self, timeout=10, max_depth=2):
        """
        Initialize finder
        
        Args:
            timeout: Request timeout in seconds
            max_depth: Maximum depth to crawl (0 = only main page)
        """
        self.timeout = timeout
        self.max_depth = max_depth
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_application_form(self, opportunity):
        """
        Find application form URL for an opportunity
        
        Args:
            opportunity: Dictionary with opportunity data
        
        Returns:
            dict with 'url' and 'instructions' keys
        """
        # Check direct fields first
        direct_urls = [
            opportunity.get('applicationUrl'),
            opportunity.get('applyUrl'),
            opportunity.get('formUrl'),
            opportunity.get('submissionUrl'),
        ]
        
        for url in direct_urls:
            if url and self._is_valid_url(url):
                if self._check_url_for_form(url):
                    return {
                        'url': url,
                        'instructions': None,
                        'found': True
                    }
        
        # Check main URL
        main_urls = [
            opportunity.get('url'),
            opportunity.get('synopsisUrl'),
            opportunity.get('link'),
        ]
        
        for url in main_urls:
            if url and self._is_valid_url(url):
                result = self._scan_website(url)
                if result:
                    return result
        
        # Generate instructions if no form found
        return self._generate_instructions(opportunity)
    
    def _is_valid_url(self, url):
        """Check if URL is valid"""
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except:
            return False
    
    def _check_url_for_form(self, url):
        """Quick check if URL likely contains a form"""
        url_lower = url.lower()
        for pattern in self.APPLICATION_URL_PATTERNS:
            if re.search(pattern, url_lower):
                return True
        return False
    
    def _scan_website(self, url, depth=0):
        """
        Scan website for application forms
        
        Args:
            url: URL to scan
            depth: Current crawl depth
        """
        if depth > self.max_depth:
            return None
        
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for forms
            forms = soup.find_all('form')
            for form in forms:
                if self._is_application_form(form):
                    form_action = form.get('action', '')
                    if form_action:
                        # Make absolute URL
                        form_url = urljoin(url, form_action)
                        return {
                            'url': form_url,
                            'instructions': f"Found application form on the opportunity page. Fill out the form to apply.",
                            'found': True
                        }
            
            # Look for links that might lead to application forms
            links = soup.find_all('a', href=True)
            for link in links:
                link_text = link.get_text().lower()
                href = link.get('href', '')
                
                # Check if link text suggests application
                if any(keyword in link_text for keyword in self.APPLICATION_KEYWORDS):
                    absolute_url = urljoin(url, href)
                    if self._is_valid_url(absolute_url):
                        # Recursively check this link
                        if depth < self.max_depth:
                            result = self._scan_website(absolute_url, depth + 1)
                            if result:
                                return result
                        else:
                            # Just return the link if we can't go deeper
                            return {
                                'url': absolute_url,
                                'instructions': f"Found application link: '{link_text}'. Click to access the application form.",
                                'found': True
                            }
            
            # Look for buttons with application keywords
            buttons = soup.find_all(['button', 'input'], type='submit')
            for button in buttons:
                button_text = button.get_text().lower() or button.get('value', '').lower()
                if any(keyword in button_text for keyword in self.APPLICATION_KEYWORDS):
                    # Try to find the form this button belongs to
                    form = button.find_parent('form')
                    if form:
                        form_action = form.get('action', '')
                        if form_action:
                            form_url = urljoin(url, form_action)
                            return {
                                'url': form_url,
                                'instructions': f"Found application form on the opportunity page.",
                                'found': True
                            }
            
            return None
            
        except requests.RequestException as e:
            print(f"Error scanning {url}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return None
    
    def _is_application_form(self, form):
        """Check if a form element is likely an application form"""
        form_html = str(form).lower()
        
        # Check for application keywords in form
        keyword_count = sum(1 for keyword in self.APPLICATION_KEYWORDS if keyword in form_html)
        if keyword_count >= 2:
            return True
        
        # Check form fields
        inputs = form.find_all(['input', 'textarea', 'select'])
        field_names = [inp.get('name', '').lower() + inp.get('id', '').lower() for inp in inputs]
        
        field_keyword_matches = sum(
            1 for field_name in field_names 
            for keyword in self.FORM_FIELD_KEYWORDS 
            if keyword in field_name
        )
        
        # If form has multiple relevant fields, it's likely an application form
        if field_keyword_matches >= 3:
            return True
        
        return False
    
    def _generate_instructions(self, opportunity):
        """Generate application instructions when form not found"""
        instructions = []
        
        url = opportunity.get('url') or opportunity.get('synopsisUrl') or opportunity.get('link')
        if url:
            instructions.append(f"Visit the opportunity page: {url}")
            instructions.append("Look for an 'Apply', 'Submit', or 'Application' button or link on the page.")
        
        agency = opportunity.get('agency') or opportunity.get('department')
        if agency:
            instructions.append(f"Contact {agency} directly for application instructions.")
        
        contact_email = opportunity.get('contactEmail')
        if contact_email:
            instructions.append(f"Email: {contact_email}")
        
        contact_phone = opportunity.get('contactPhone')
        if contact_phone:
            instructions.append(f"Phone: {contact_phone}")
        
        deadline = opportunity.get('closeDate') or opportunity.get('deadline')
        if deadline:
            try:
                from dateutil import parser as date_parser
                deadline_date = date_parser.parse(str(deadline))
                instructions.append(f"Application deadline: {deadline_date.strftime('%B %d, %Y')}")
            except:
                instructions.append(f"Application deadline: {deadline}")
        
        if not instructions:
            instructions.append("Check the opportunity page for application details.")
        
        return {
            'url': None,
            'instructions': '\n'.join(instructions),
            'found': False
        }


def find_application_form_for_opportunity(opportunity):
    """
    Convenience function to find application form
    
    Args:
        opportunity: Dictionary with opportunity data
    
    Returns:
        dict with application form info
    """
    finder = ApplicationFormFinder()
    return finder.find_application_form(opportunity)
