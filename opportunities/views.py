from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import logging

from .models import (
    UserProfile, Opportunity, OpportunityMatch,
    Application, SavedOpportunity, ApplicationPathway
)
from .matching import OpportunityMatcher
from .firebase_integration import FirebaseService
from .app_scraper import find_application_form

logger = logging.getLogger(__name__)


# HTML Template Views
def index(request):
    """Main landing/dashboard page"""
    return render(request, 'opportunities/index.html', {
        'firebase_config': {
            'apiKey': settings.FIREBASE_API_KEY,
            'authDomain': settings.FIREBASE_AUTH_DOMAIN,
            'projectId': settings.FIREBASE_PROJECT_ID,
        }
    })


def explore(request):
    """Explore opportunities page"""
    return render(request, 'opportunities/explore.html', {
        'firebase_config': {
            'apiKey': settings.FIREBASE_API_KEY,
            'authDomain': settings.FIREBASE_AUTH_DOMAIN,
            'projectId': settings.FIREBASE_PROJECT_ID,
        }
    })


def applied(request):
    """Applied opportunities page"""
    return render(request, 'opportunities/applied.html', {
        'firebase_config': {
            'apiKey': settings.FIREBASE_API_KEY,
            'authDomain': settings.FIREBASE_AUTH_DOMAIN,
            'projectId': settings.FIREBASE_PROJECT_ID,
        }
    })


def saved(request):
    """Saved opportunities page"""
    return render(request, 'opportunities/saved.html', {
        'firebase_config': {
            'apiKey': settings.FIREBASE_API_KEY,
            'authDomain': settings.FIREBASE_AUTH_DOMAIN,
            'projectId': settings.FIREBASE_PROJECT_ID,
        }
    })


# API Endpoints
@api_view(['POST'])
def auth_verify(request):
    """Verify Firebase token and get/create Django user"""
    try:
        id_token = request.data.get('idToken')
        if not id_token:
            return Response({'error': 'No token provided'}, status=400)
        
        # Verify token with Firebase
        decoded_token = FirebaseService.verify_firebase_token(id_token)
        if not decoded_token:
            return Response({'error': 'Invalid token'}, status=401)
        
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Get or create Django user
        user, created = User.objects.get_or_create(
            username=firebase_uid,
            defaults={'email': email}
        )
        
        # Sync profile from Firebase
        profile = FirebaseService.sync_user_profile(firebase_uid, user)
        
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'firebase_uid': firebase_uid
            },
            'profile': {
                'id': profile.id if profile else None,
                'organization_name': profile.organization_name if profile else '',
                'funding_types': profile.funding_types if profile else [],
                'interests_main': profile.interests_main if profile else [],
                'interests_sub': profile.interests_sub if profile else [],
            } if profile else None
        })
        
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def match_opportunities(request):
    """Run matching algorithm for user"""
    try:
        firebase_uid = request.data.get('firebase_uid')
        if not firebase_uid:
            return Response({'error': 'Firebase UID required'}, status=400)
        
        # Get user profile
        profile = UserProfile.objects.filter(firebase_uid=firebase_uid).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=404)
        
        # Run matching
        matcher = OpportunityMatcher(profile)
        matches = matcher.match_opportunities()
        
        # Get already applied/saved IDs
        applied_ids = set(Application.objects.filter(
            user_profile=profile
        ).values_list('opportunity__firebase_id', flat=True))
        
        saved_ids = set(SavedOpportunity.objects.filter(
            user_profile=profile
        ).values_list('opportunity__firebase_id', flat=True))
        
        # Filter out applied/saved
        filtered_matches = [
            m for m in matches 
            if m.opportunity.firebase_id not in applied_ids 
            and m.opportunity.firebase_id not in saved_ids
        ]
        
        # Serialize matches
        results = []
        for match in filtered_matches[:50]:  # Limit to top 50
            opp = match.opportunity
            results.append({
                'id': opp.firebase_id,
                'collection': opp.collection_name,
                'title': opp.title,
                'description': opp.description,
                'summary': opp.summary,
                'agency': opp.agency,
                'department': opp.department,
                'posted_date': opp.posted_date.isoformat() if opp.posted_date else None,
                'close_date': opp.close_date.isoformat() if opp.close_date else None,
                'deadline': opp.deadline.isoformat() if opp.deadline else None,
                'city': opp.city,
                'state': opp.state,
                'place': opp.place,
                'url': opp.url,
                'synopsis_url': opp.synopsis_url,
                'link': opp.link,
                'contact_email': opp.contact_email,
                'contact_phone': opp.contact_phone,
                'urgency': opp.urgency_bucket,
                'relevance_score': match.relevance_score,
                'win_rate': match.win_rate,
                'win_rate_reasoning': match.win_rate_reasoning,
            })
        
        return Response({
            'success': True,
            'count': len(results),
            'matches': results
        })
        
    except Exception as e:
        logger.error(f"Matching error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def apply_opportunity(request):
    """Apply to an opportunity"""
    try:
        firebase_uid = request.data.get('firebase_uid')
        opportunity_id = request.data.get('opportunity_id')
        
        if not firebase_uid or not opportunity_id:
            return Response({'error': 'Missing required fields'}, status=400)
        
        profile = UserProfile.objects.filter(firebase_uid=firebase_uid).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=404)
        
        opportunity = Opportunity.objects.filter(firebase_id=opportunity_id).first()
        if not opportunity:
            return Response({'error': 'Opportunity not found'}, status=404)
        
        # Find application form
        app_info = find_application_form(opportunity)
        
        # Create application record
        application, created = Application.objects.get_or_create(
            user_profile=profile,
            opportunity=opportunity,
            defaults={
                'application_url': app_info.get('application_url'),
                'application_instructions': app_info.get('instructions'),
            }
        )
        
        # Update profile stats
        if created:
            profile.total_applied += 1
            profile.save()
        
        return Response({
            'success': True,
            'application_url': app_info.get('application_url'),
            'instructions': app_info.get('instructions'),
            'confidence': app_info.get('confidence', 0),
        })
        
    except Exception as e:
        logger.error(f"Apply error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def save_opportunity(request):
    """Save an opportunity for later"""
    try:
        firebase_uid = request.data.get('firebase_uid')
        opportunity_id = request.data.get('opportunity_id')
        
        if not firebase_uid or not opportunity_id:
            return Response({'error': 'Missing required fields'}, status=400)
        
        profile = UserProfile.objects.filter(firebase_uid=firebase_uid).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=404)
        
        opportunity = Opportunity.objects.filter(firebase_id=opportunity_id).first()
        if not opportunity:
            return Response({'error': 'Opportunity not found'}, status=404)
        
        # Save opportunity
        saved, created = SavedOpportunity.objects.get_or_create(
            user_profile=profile,
            opportunity=opportunity
        )
        
        # Update profile stats
        if created:
            profile.total_saved += 1
            profile.save()
        
        return Response({'success': True})
        
    except Exception as e:
        logger.error(f"Save error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def pass_opportunity(request):
    """Mark opportunity as dismissed/passed"""
    try:
        firebase_uid = request.data.get('firebase_uid')
        opportunity_id = request.data.get('opportunity_id')
        
        if not firebase_uid or not opportunity_id:
            return Response({'error': 'Missing required fields'}, status=400)
        
        profile = UserProfile.objects.filter(firebase_uid=firebase_uid).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=404)
        
        opportunity = Opportunity.objects.filter(firebase_id=opportunity_id).first()
        if not opportunity:
            return Response({'error': 'Opportunity not found'}, status=404)
        
        # Mark as dismissed
        match = OpportunityMatch.objects.filter(
            user_profile=profile,
            opportunity=opportunity
        ).first()
        
        if match:
            match.is_dismissed = True
            match.save()
        
        return Response({'success': True})
        
    except Exception as e:
        logger.error(f"Pass error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_applications(request):
    """Get user's applications"""
    try:
        firebase_uid = request.GET.get('firebase_uid')
        if not firebase_uid:
            return Response({'error': 'Firebase UID required'}, status=400)
        
        profile = UserProfile.objects.filter(firebase_uid=firebase_uid).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=404)
        
        applications = Application.objects.filter(user_profile=profile).select_related('opportunity')
        
        results = []
        for app in applications:
            opp = app.opportunity
            results.append({
                'id': opp.firebase_id,
                'collection': opp.collection_name,
                'title': opp.title,
                'description': opp.description,
                'agency': opp.agency,
                'department': opp.department,
                'close_date': opp.close_date.isoformat() if opp.close_date else None,
                'url': opp.url,
                'application_url': app.application_url,
                'application_instructions': app.application_instructions,
                'status': app.status,
                'applied_at': app.applied_at.isoformat(),
            })
        
        return Response({'success': True, 'applications': results})
        
    except Exception as e:
        logger.error(f"Get applications error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_saved(request):
    """Get user's saved opportunities"""
    try:
        firebase_uid = request.GET.get('firebase_uid')
        if not firebase_uid:
            return Response({'error': 'Firebase UID required'}, status=400)
        
        profile = UserProfile.objects.filter(firebase_uid=firebase_uid).first()
        if not profile:
            return Response({'error': 'Profile not found'}, status=404)
        
        saved = SavedOpportunity.objects.filter(user_profile=profile).select_related('opportunity')
        
        results = []
        for item in saved:
            opp = item.opportunity
            results.append({
                'id': opp.firebase_id,
                'collection': opp.collection_name,
                'title': opp.title,
                'description': opp.description,
                'agency': opp.agency,
                'department': opp.department,
                'close_date': opp.close_date.isoformat() if opp.close_date else None,
                'url': opp.url,
                'saved_at': item.saved_at.isoformat(),
            })
        
        return Response({'success': True, 'saved': results})
        
    except Exception as e:
        logger.error(f"Get saved error: {e}")
        return Response({'error': str(e)}, status=500)
