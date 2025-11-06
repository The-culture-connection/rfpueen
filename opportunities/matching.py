"""
Matching algorithm to find most applicable opportunities
"""
from django.conf import settings
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re


def parse_date(date_str):
    """Parse date string to date object"""
    if not date_str:
        return None
    try:
        if isinstance(date_str, str):
            # Try ISO format first
            if re.match(r'^\d{4}-\d{2}-\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y-%m-%d').date()
            # Try parsing with dateutil
            return date_parser.parse(date_str).date()
        return date_str
    except:
        return None


def bucket_of(deadline):
    """Calculate urgency bucket based on deadline"""
    deadline_date = parse_date(deadline)
    if not deadline_date:
        return "ongoing"
    
    days_until = (deadline_date - datetime.now().date()).days
    if days_until <= 30:
        return "urgent"
    elif days_until <= 92:
        return "soon"
    return "ongoing"


def calculate_match_score(opportunity, profile):
    """
    Calculate relevance score based on keyword matches and profile criteria
    
    Returns:
        float: Match score (higher is better)
    """
    score = 0.0
    
    # Get all searchable text from opportunity
    search_text = " ".join([
        opportunity.get('title', ''),
        opportunity.get('description', ''),
        opportunity.get('summary', ''),
        opportunity.get('agency', ''),
        opportunity.get('department', ''),
    ]).lower()
    
    # Get keywords from profile
    interests_main = profile.get('interestsMain', []) or []
    interests_sub = profile.get('interestsSub', []) or []
    grants_by_interest = profile.get('grantsByInterest', []) or []
    
    all_keywords = []
    all_keywords.extend([k.lower() for k in interests_main if k])
    all_keywords.extend([k.lower() for k in interests_sub if k])
    all_keywords.extend([k.lower() for k in grants_by_interest if k])
    
    # Remove duplicates
    all_keywords = list(set(all_keywords))
    
    if not all_keywords:
        return 0.0
    
    # Calculate keyword matches
    keyword_matches = 0
    for keyword in all_keywords:
        if not keyword:
            continue
        # Escape special regex characters
        escaped_keyword = re.escape(keyword)
        # Count word boundary matches
        pattern = r'\b' + escaped_keyword + r'\b'
        matches = len(re.findall(pattern, search_text, re.IGNORECASE))
        keyword_matches += matches
    
    # Base score from keyword matches
    score += keyword_matches * 10
    
    # Boost for main interests
    for keyword in interests_main:
        if keyword and keyword.lower() in search_text:
            score += 5
    
    # Boost for exact phrase matches
    for keyword in all_keywords:
        if len(keyword) > 3 and keyword in search_text:
            score += 2
    
    # Urgency boost (more urgent = slightly higher score)
    deadline = opportunity.get('closeDate') or opportunity.get('deadline')
    bucket = bucket_of(deadline)
    if bucket == "urgent":
        score += 5
    elif bucket == "soon":
        score += 2
    
    return score


def match_opportunities(opportunities_data, profile, funding_types=None):
    """
    Match opportunities based on profile criteria
    
    Args:
        opportunities_data: List of opportunity dictionaries from Firebase
        profile: User profile dictionary
        funding_types: List of funding types to filter by
    
    Returns:
        List of matched opportunities with scores, sorted by score descending
    """
    if not profile:
        return []
    
    # Get funding types from profile if not provided
    if not funding_types:
        funding_types = profile.get('fundingTypes', [])
    
    if not funding_types:
        return []
    
    # Collection mapping
    collection_map = settings.COLLECTION_MAP
    
    # Determine which collections to include
    collections_to_include = set()
    for ft in funding_types:
        collections = collection_map.get(ft, [])
        collections_to_include.update(collections)
    
    matched = []
    
    for opp in opportunities_data:
        # Filter by collection if specified
        collection = opp.get('collection', '')
        if collections_to_include and collection not in collections_to_include:
            continue
        
        # Calculate match score
        score = calculate_match_score(opp, profile)
        
        if score > 0:
            matched.append({
                **opp,
                'score': score,
                'urgency_bucket': bucket_of(opp.get('closeDate') or opp.get('deadline'))
            })
    
    # Sort by score descending
    matched.sort(key=lambda x: x['score'], reverse=True)
    
    return matched
