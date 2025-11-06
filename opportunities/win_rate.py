"""
Win rate calculation based on match quality
"""
from .matching import calculate_match_score, bucket_of


def calculate_win_rate(opportunity, profile, match_score=None):
    """
    Calculate win rate percentage based on how well the opportunity matches user criteria
    
    Args:
        opportunity: Dictionary with opportunity data
        profile: User profile dictionary
        match_score: Pre-calculated match score (optional)
    
    Returns:
        dict with 'win_rate' (0-100) and 'reasoning' (explanation)
    """
    if match_score is None:
        match_score = calculate_match_score(opportunity, profile)
    
    # Base win rate starts from match score
    # Normalize score to 0-100 range (assuming max score around 200)
    base_rate = min(100, (match_score / 200) * 100)
    
    reasoning_parts = []
    
    # Factor 1: Keyword match quality
    interests_main = profile.get('interestsMain', []) or []
    interests_sub = profile.get('interestsSub', []) or []
    
    search_text = " ".join([
        opportunity.get('title', ''),
        opportunity.get('description', ''),
        opportunity.get('summary', ''),
    ]).lower()
    
    main_matches = sum(1 for keyword in interests_main if keyword and keyword.lower() in search_text)
    sub_matches = sum(1 for keyword in interests_sub if keyword and keyword.lower() in search_text)
    
    keyword_factor = 0
    if main_matches > 0:
        keyword_factor += 15
        reasoning_parts.append(f"Matches {main_matches} main interest(s)")
    if sub_matches > 0:
        keyword_factor += 10
        reasoning_parts.append(f"Matches {sub_matches} sub-interest(s)")
    
    # Factor 2: Urgency/Deadline
    deadline = opportunity.get('closeDate') or opportunity.get('deadline')
    bucket = bucket_of(deadline)
    urgency_factor = 0
    if bucket == "urgent":
        urgency_factor = 5
        reasoning_parts.append("Urgent deadline (within 30 days)")
    elif bucket == "soon":
        urgency_factor = 3
        reasoning_parts.append("Approaching deadline (within 92 days)")
    elif bucket == "ongoing":
        urgency_factor = 2
        reasoning_parts.append("Ongoing opportunity")
    
    # Factor 3: Application form availability
    application_url = (
        opportunity.get('applicationUrl') or 
        opportunity.get('applyUrl') or
        opportunity.get('formUrl')
    )
    form_factor = 0
    if application_url:
        form_factor = 10
        reasoning_parts.append("Direct application form available")
    else:
        form_factor = -5
        reasoning_parts.append("Application form not directly available")
    
    # Factor 4: Profile completeness
    profile_completeness = 0
    if interests_main:
        profile_completeness += 5
    if interests_sub:
        profile_completeness += 5
    if profile.get('fundingTypes'):
        profile_completeness += 5
    
    # Factor 5: Match score quality
    score_factor = 0
    if match_score >= 50:
        score_factor = 15
        reasoning_parts.append("Strong keyword match")
    elif match_score >= 20:
        score_factor = 10
        reasoning_parts.append("Moderate keyword match")
    elif match_score > 0:
        score_factor = 5
        reasoning_parts.append("Weak keyword match")
    else:
        score_factor = -10
        reasoning_parts.append("No keyword matches found")
    
    # Calculate final win rate
    win_rate = base_rate + keyword_factor + urgency_factor + form_factor + score_factor
    
    # Clamp between 0 and 100
    win_rate = max(0, min(100, win_rate))
    
    # Generate reasoning
    if not reasoning_parts:
        reasoning = "Limited match criteria available for calculation."
    else:
        reasoning = "Win rate calculated based on: " + "; ".join(reasoning_parts) + "."
    
    # Add overall assessment
    if win_rate >= 70:
        reasoning += " High probability of success - strong match."
    elif win_rate >= 50:
        reasoning += " Moderate probability of success - good match."
    elif win_rate >= 30:
        reasoning += " Lower probability - weak match."
    else:
        reasoning += " Low probability - poor match."
    
    return {
        'win_rate': round(win_rate, 1),
        'reasoning': reasoning,
        'factors': {
            'base_rate': round(base_rate, 1),
            'keyword_factor': keyword_factor,
            'urgency_factor': urgency_factor,
            'form_factor': form_factor,
            'score_factor': score_factor,
        }
    }
