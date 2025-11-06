"""
Intelligent matching algorithm for fundraising opportunities
"""
import re
from typing import List, Dict, Tuple
from .models import Opportunity, UserProfile, OpportunityMatch


class OpportunityMatcher:
    """Matches opportunities to user profiles based on multiple criteria"""
    
    COLLECTION_MAP = {
        "Contracts": ["SAM"],
        "Grants": ["grants.gov", "grantwatch"],
        "RFPs": ["PND_RFPs", "rfpmart"],
        "Bids": ["bid"]
    }
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.interests_main = [k.lower() for k in (user_profile.interests_main or [])]
        self.interests_sub = [k.lower() for k in (user_profile.interests_sub or [])]
        
    def get_relevant_collections(self) -> List[str]:
        """Get collection names based on user's funding type preferences"""
        collections = set()
        for funding_type in (self.user_profile.funding_types or []):
            collections.update(self.COLLECTION_MAP.get(funding_type, []))
        return list(collections)
    
    def calculate_keyword_score(self, opportunity: Opportunity) -> Tuple[float, Dict]:
        """Calculate relevance score based on keyword matches"""
        search_text = ' '.join([
            opportunity.title or "",
            opportunity.description or "",
            opportunity.summary or "",
            opportunity.agency or "",
            opportunity.department or "",
        ]).lower()
        
        match_details = {
            'main_matches': [],
            'sub_matches': [],
            'total_matches': 0
        }
        
        score = 0.0
        
        # Main keywords have higher weight
        for keyword in self.interests_main:
            if not keyword:
                continue
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            matches = pattern.findall(search_text)
            if matches:
                count = len(matches)
                score += count * 3.0  # Main keywords worth 3x
                match_details['main_matches'].append({'keyword': keyword, 'count': count})
        
        # Sub keywords have standard weight
        for keyword in self.interests_sub:
            if not keyword:
                continue
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            matches = pattern.findall(search_text)
            if matches:
                count = len(matches)
                score += count * 1.0
                match_details['sub_matches'].append({'keyword': keyword, 'count': count})
        
        match_details['total_matches'] = len(match_details['main_matches']) + len(match_details['sub_matches'])
        
        return score, match_details
    
    def calculate_win_rate(self, opportunity: Opportunity, keyword_score: float, match_details: Dict) -> Tuple[float, Dict]:
        """Calculate win rate based on how well the opportunity matches user criteria"""
        reasoning = {
            'factors': [],
            'total_score': 0,
            'max_score': 100
        }
        
        # Factor 1: Keyword relevance (0-40 points)
        keyword_points = min(40, keyword_score * 2)
        reasoning['factors'].append({
            'name': 'Keyword Match',
            'score': keyword_points,
            'max': 40,
            'details': f"{match_details['total_matches']} relevant keywords found"
        })
        
        # Factor 2: Main interest alignment (0-25 points)
        main_match_count = len(match_details['main_matches'])
        main_points = min(25, main_match_count * 8)
        reasoning['factors'].append({
            'name': 'Primary Interest Alignment',
            'score': main_points,
            'max': 25,
            'details': f"{main_match_count} primary interests matched"
        })
        
        # Factor 3: Funding type match (0-20 points)
        if opportunity.collection_name in self.get_relevant_collections():
            funding_points = 20
        else:
            funding_points = 0
        reasoning['factors'].append({
            'name': 'Funding Type Match',
            'score': funding_points,
            'max': 20,
            'details': 'Matches preferred funding type' if funding_points > 0 else 'Different funding type'
        })
        
        # Factor 4: Location proximity (0-10 points)
        location_points = 0
        if self.user_profile.state:
            opp_state = (opportunity.state or "").lower()
            user_state = self.user_profile.state.lower()
            if opp_state == user_state:
                location_points = 10
        
        reasoning['factors'].append({
            'name': 'Location Match',
            'score': location_points,
            'max': 10,
            'details': 'Same state' if location_points > 0 else 'Different or unspecified location'
        })
        
        # Factor 5: Timing/Urgency (0-5 points)
        urgency_bucket = opportunity.urgency_bucket
        if urgency_bucket == "urgent":
            timing_points = 5
            timing_detail = "Deadline within 30 days"
        elif urgency_bucket == "soon":
            timing_points = 3
            timing_detail = "Deadline within 3 months"
        else:
            timing_points = 2
            timing_detail = "Ongoing or long-term opportunity"
        
        reasoning['factors'].append({
            'name': 'Timing',
            'score': timing_points,
            'max': 5,
            'details': timing_detail
        })
        
        # Calculate total
        total_score = sum(f['score'] for f in reasoning['factors'])
        reasoning['total_score'] = total_score
        
        # Convert to percentage
        win_rate = (total_score / reasoning['max_score']) * 100
        
        return win_rate, reasoning
    
    def match_opportunities(self, opportunities: List[Opportunity] = None) -> List[OpportunityMatch]:
        """Match opportunities to user profile"""
        if opportunities is None:
            relevant_collections = self.get_relevant_collections()
            if not relevant_collections:
                return []
            
            opportunities = Opportunity.objects.filter(
                collection_name__in=relevant_collections
            )
        
        matches = []
        
        for opportunity in opportunities:
            keyword_score, match_details = self.calculate_keyword_score(opportunity)
            
            if keyword_score == 0:
                continue
            
            urgency_multiplier = 1.2 if opportunity.urgency_bucket == "urgent" else (1.1 if opportunity.urgency_bucket == "soon" else 1.0)
            relevance_score = keyword_score * urgency_multiplier
            
            win_rate, win_rate_reasoning = self.calculate_win_rate(opportunity, keyword_score, match_details)
            
            match, created = OpportunityMatch.objects.get_or_create(
                user_profile=self.user_profile,
                opportunity=opportunity,
                defaults={
                    'relevance_score': relevance_score,
                    'win_rate': win_rate,
                    'win_rate_reasoning': win_rate_reasoning
                }
            )
            
            if not created:
                match.relevance_score = relevance_score
                match.win_rate = win_rate
                match.win_rate_reasoning = win_rate_reasoning
                match.save()
            
            matches.append(match)
        
        return matches
