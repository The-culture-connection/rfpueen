"""
Opportunity Matching Algorithm
This module handles matching opportunities to user profiles based on:
- Funding types (Contracts, Grants, RFPs, Bids)
- Keyword matching (main and sub interests)
- Urgency buckets (urgent, soon, ongoing)
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple


class OpportunityMatcher:
    """Handles opportunity matching and scoring"""
    
    # Collection mapping based on funding types
    COLLECTION_MAP = {
        "Contracts": ["SAM"],
        "Grants": ["grants.gov", "grantwatch"],
        "RFPs": ["PND_RFPs", "rfpmart"],
        "Bids": ["bid"]
    }
    
    @staticmethod
    def get_collections_for_funding_types(funding_types: List[str]) -> List[str]:
        """Get Firebase collections to search based on selected funding types"""
        collections = set()
        for funding_type in funding_types:
            cols = OpportunityMatcher.COLLECTION_MAP.get(funding_type, [])
            collections.update(cols)
        return list(collections)
    
    @staticmethod
    def calculate_match_score(
        opportunity: Dict[str, Any],
        interests_main: List[str],
        interests_sub: List[str]
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate relevance score based on keyword matches
        Returns: (score, match_details)
        """
        # Combine all searchable text
        search_text = " ".join([
            str(opportunity.get('title', '')),
            str(opportunity.get('description', '')),
            str(opportunity.get('summary', '')),
            str(opportunity.get('agency', '')),
            str(opportunity.get('department', '')),
        ]).lower()
        
        score = 0
        match_details = {
            'main_keyword_matches': [],
            'sub_keyword_matches': [],
            'total_matches': 0,
            'matched_keywords': set()
        }
        
        # Check main interest keywords (higher weight)
        for keyword in interests_main:
            keyword_lower = keyword.lower()
            # Use word boundary regex for exact matches
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            matches = re.findall(pattern, search_text, re.IGNORECASE)
            if matches:
                count = len(matches)
                score += count * 3  # Main keywords get 3x weight
                match_details['main_keyword_matches'].append({
                    'keyword': keyword,
                    'count': count
                })
                match_details['matched_keywords'].add(keyword_lower)
        
        # Check sub-interest keywords
        for keyword in interests_sub:
            keyword_lower = keyword.lower()
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            matches = re.findall(pattern, search_text, re.IGNORECASE)
            if matches:
                count = len(matches)
                score += count  # Sub keywords get 1x weight
                match_details['sub_keyword_matches'].append({
                    'keyword': keyword,
                    'count': count
                })
                match_details['matched_keywords'].add(keyword_lower)
        
        match_details['total_matches'] = (
            sum(m['count'] for m in match_details['main_keyword_matches']) +
            sum(m['count'] for m in match_details['sub_keyword_matches'])
        )
        match_details['matched_keywords'] = list(match_details['matched_keywords'])
        
        return score, match_details
    
    @staticmethod
    def get_urgency_bucket(deadline: Any) -> str:
        """
        Categorize opportunity by deadline urgency
        Returns: 'urgent', 'soon', or 'ongoing'
        """
        if not deadline:
            return 'ongoing'
        
        try:
            if isinstance(deadline, str):
                # Try to parse date string
                if re.match(r'^\d{4}-\d{2}-\d{2}', deadline):
                    deadline_date = datetime.strptime(deadline[:10], '%Y-%m-%d')
                else:
                    deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            else:
                deadline_date = deadline
            
            now = datetime.now()
            if deadline_date.tzinfo:
                from django.utils import timezone
                now = timezone.now()
            
            days_until_deadline = (deadline_date - now).days
            
            if days_until_deadline <= 30:
                return 'urgent'
            elif days_until_deadline <= 92:
                return 'soon'
            else:
                return 'ongoing'
        except Exception:
            return 'ongoing'
    
    @staticmethod
    def calculate_win_rate(
        opportunity: Dict[str, Any],
        match_score: int,
        match_details: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate win rate based on how well the opportunity matches user criteria
        Returns: (win_rate, reasoning)
        """
        reasoning = {
            'factors': [],
            'score_breakdown': {},
            'total_score': 0,
            'max_score': 0
        }
        
        total_score = 0
        max_score = 0
        
        # Factor 1: Keyword match strength (40 points)
        max_score += 40
        keyword_score = min(40, match_score * 2)  # Cap at 40
        total_score += keyword_score
        reasoning['score_breakdown']['keyword_match'] = {
            'score': keyword_score,
            'max': 40,
            'description': f"Found {match_details['total_matches']} keyword matches"
        }
        if keyword_score >= 30:
            reasoning['factors'].append("Excellent keyword match - highly relevant to your interests")
        elif keyword_score >= 20:
            reasoning['factors'].append("Good keyword match - relevant to your profile")
        elif keyword_score >= 10:
            reasoning['factors'].append("Moderate keyword match - partially relevant")
        else:
            reasoning['factors'].append("Limited keyword matches - may be less relevant")
        
        # Factor 2: Main keyword matches (30 points)
        max_score += 30
        main_keyword_score = min(30, len(match_details.get('main_keyword_matches', [])) * 10)
        total_score += main_keyword_score
        reasoning['score_breakdown']['main_keywords'] = {
            'score': main_keyword_score,
            'max': 30,
            'description': f"Matched {len(match_details.get('main_keyword_matches', []))} main interests"
        }
        if main_keyword_score >= 20:
            reasoning['factors'].append("Strong match with your primary interests")
        
        # Factor 3: Deadline urgency (15 points)
        max_score += 15
        urgency = OpportunityMatcher.get_urgency_bucket(
            opportunity.get('closeDate') or opportunity.get('deadline')
        )
        urgency_score = {
            'urgent': 5,   # Less time means more competition
            'soon': 15,    # Sweet spot - enough time to apply well
            'ongoing': 10  # No immediate deadline
        }.get(urgency, 10)
        total_score += urgency_score
        reasoning['score_breakdown']['urgency'] = {
            'score': urgency_score,
            'max': 15,
            'urgency_level': urgency,
            'description': f"Deadline urgency: {urgency}"
        }
        
        # Factor 4: Complete opportunity information (15 points)
        max_score += 15
        completeness_score = 0
        has_description = bool(opportunity.get('description') or opportunity.get('summary'))
        has_contact = bool(opportunity.get('contactEmail') or opportunity.get('contactPhone'))
        has_location = bool(opportunity.get('place') or opportunity.get('city') or opportunity.get('state'))
        has_url = bool(opportunity.get('url') or opportunity.get('synopsisUrl'))
        
        completeness_score += 5 if has_description else 0
        completeness_score += 3 if has_contact else 0
        completeness_score += 3 if has_location else 0
        completeness_score += 4 if has_url else 0
        
        total_score += completeness_score
        reasoning['score_breakdown']['completeness'] = {
            'score': completeness_score,
            'max': 15,
            'description': "Opportunity has complete information"
        }
        if completeness_score >= 12:
            reasoning['factors'].append("Opportunity has detailed information available")
        
        # Calculate final win rate (0-100%)
        win_rate = (total_score / max_score * 100) if max_score > 0 else 0
        
        reasoning['total_score'] = total_score
        reasoning['max_score'] = max_score
        reasoning['win_rate_percentage'] = round(win_rate, 2)
        
        # Add overall assessment
        if win_rate >= 80:
            reasoning['overall_assessment'] = "Excellent match - highly recommended"
        elif win_rate >= 60:
            reasoning['overall_assessment'] = "Good match - worth pursuing"
        elif win_rate >= 40:
            reasoning['overall_assessment'] = "Fair match - consider applying"
        else:
            reasoning['overall_assessment'] = "Limited match - may not be ideal"
        
        return win_rate, reasoning
    
    @staticmethod
    def rank_opportunities(
        opportunities: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank and score all opportunities for a user
        Returns: List of opportunities with scores and win rates
        """
        interests_main = user_profile.get('interestsMain', [])
        interests_sub = user_profile.get('interestsSub', []) or user_profile.get('grantsByInterest', [])
        
        ranked_opportunities = []
        
        for opp in opportunities:
            # Calculate match score
            score, match_details = OpportunityMatcher.calculate_match_score(
                opp, interests_main, interests_sub
            )
            
            # Only include opportunities with at least some match
            if score > 0:
                # Calculate win rate
                win_rate, reasoning = OpportunityMatcher.calculate_win_rate(
                    opp, score, match_details, user_profile
                )
                
                # Add scoring data to opportunity
                opp_with_score = {
                    **opp,
                    'match_score': score,
                    'match_details': match_details,
                    'win_rate': win_rate,
                    'win_rate_reasoning': reasoning,
                    'urgency': OpportunityMatcher.get_urgency_bucket(
                        opp.get('closeDate') or opp.get('deadline')
                    )
                }
                
                ranked_opportunities.append(opp_with_score)
        
        # Sort by score descending, then by win rate
        ranked_opportunities.sort(
            key=lambda x: (x['match_score'], x['win_rate']),
            reverse=True
        )
        
        return ranked_opportunities
