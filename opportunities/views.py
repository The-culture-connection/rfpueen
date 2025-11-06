"""
Django REST Framework Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import logging

from .models import UserProfile, AppliedOpportunity, SavedOpportunity, ApplicationFormCache
from .serializers import (
    UserProfileSerializer, AppliedOpportunitySerializer,
    SavedOpportunitySerializer, OpportunitySerializer,
    ApplicationFormCacheSerializer
)
from .firebase_service import FirebaseService
from .matching_algorithm import OpportunityMatcher
from .form_scraper import ApplicationFormScraper

logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'email': request.user.email}
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class OpportunityViewSet(viewsets.ViewSet):
    """ViewSet for opportunity matching and browsing"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def match(self, request):
        """
        Match opportunities to user profile
        
        Expected request data:
        {
            "funding_types": ["Contracts", "Grants"],
            "interests_main": ["technology", "education"],
            "interests_sub": ["software", "training"],
            "exclude_applied": true,
            "exclude_saved": true,
            "limit": 100
        }
        """
        try:
            # Get user profile data
            funding_types = request.data.get('funding_types', [])
            interests_main = request.data.get('interests_main', [])
            interests_sub = request.data.get('interests_sub', [])
            exclude_applied = request.data.get('exclude_applied', True)
            exclude_saved = request.data.get('exclude_saved', True)
            limit = request.data.get('limit', 100)
            
            if not funding_types:
                return Response(
                    {'error': 'funding_types is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get collections to search
            collections = OpportunityMatcher.get_collections_for_funding_types(funding_types)
            
            if not collections:
                return Response(
                    {'error': 'No collections found for selected funding types'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Fetch opportunities from Firebase
            logger.info(f"Fetching opportunities from collections: {collections}")
            opportunities = FirebaseService.get_opportunities_from_collections(
                collections, limit=limit
            )
            
            # Create user profile dict for matching
            user_profile = {
                'fundingTypes': funding_types,
                'interestsMain': interests_main,
                'interestsSub': interests_sub
            }
            
            # Rank opportunities
            ranked_opportunities = OpportunityMatcher.rank_opportunities(
                opportunities, user_profile
            )
            
            # Exclude applied/saved if requested
            if exclude_applied or exclude_saved:
                applied_ids = set()
                saved_ids = set()
                
                if exclude_applied:
                    applied = AppliedOpportunity.objects.filter(user=request.user)
                    applied_ids = set(a.opportunity_id for a in applied)
                
                if exclude_saved:
                    saved = SavedOpportunity.objects.filter(user=request.user)
                    saved_ids = set(s.opportunity_id for s in saved)
                
                ranked_opportunities = [
                    opp for opp in ranked_opportunities
                    if opp['id'] not in applied_ids and opp['id'] not in saved_ids
                ]
            
            # Serialize and return
            serializer = OpportunitySerializer(ranked_opportunities, many=True)
            
            return Response({
                'count': len(serializer.data),
                'opportunities': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error matching opportunities: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def find_application_form(self, request, pk=None):
        """
        Find application form URL for an opportunity
        
        URL: /api/opportunities/{opportunity_id}/find_application_form/
        """
        try:
            # Get opportunity data from request or Firebase
            opportunity_data = request.query_params.get('data')
            opportunity_url = request.query_params.get('url')
            
            if not opportunity_url:
                return Response(
                    {'error': 'opportunity URL is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check cache first
            cache_entry = ApplicationFormCache.objects.filter(
                opportunity_url=opportunity_url
            ).first()
            
            if cache_entry and cache_entry.is_valid:
                return Response({
                    'application_url': cache_entry.application_url,
                    'form_path': cache_entry.form_path,
                    'cached': True,
                    'notes': cache_entry.notes
                })
            
            # Parse opportunity data if provided
            import json
            opp_data = {}
            if opportunity_data:
                try:
                    opp_data = json.loads(opportunity_data)
                except:
                    pass
            
            # Scrape for application form
            app_url, form_path, notes = ApplicationFormScraper.find_application_form(
                opportunity_url, opp_data
            )
            
            # Cache the result
            ApplicationFormCache.objects.update_or_create(
                opportunity_url=opportunity_url,
                defaults={
                    'application_url': app_url or '',
                    'form_path': form_path or '',
                    'is_valid': bool(app_url),
                    'notes': '\n'.join(notes)
                }
            )
            
            if app_url:
                return Response({
                    'application_url': app_url,
                    'form_path': form_path,
                    'cached': False,
                    'notes': notes
                })
            else:
                # Generate instructions if no form found
                instructions = ApplicationFormScraper.generate_application_instructions(opp_data)
                return Response({
                    'application_url': None,
                    'instructions': instructions,
                    'notes': notes
                })
                
        except Exception as e:
            logger.error(f"Error finding application form: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AppliedOpportunityViewSet(viewsets.ModelViewSet):
    """ViewSet for applied opportunities"""
    serializer_class = AppliedOpportunitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AppliedOpportunity.objects.filter(user=self.request.user)
    
    def create(self, request):
        """
        Mark an opportunity as applied
        
        Expected data:
        {
            "opportunity_id": "abc123",
            "collection": "SAM",
            "title": "Opportunity Title",
            "agency": "Agency Name",
            "url": "https://...",
            "application_url": "https://...",
            "match_score": 45,
            "win_rate": 75.5,
            "win_rate_reasoning": {...},
            "data": {...}
        }
        """
        try:
            data = request.data.copy()
            data['user'] = request.user.id
            
            # Check if already applied
            existing = AppliedOpportunity.objects.filter(
                user=request.user,
                opportunity_id=data.get('opportunity_id')
            ).first()
            
            if existing:
                return Response(
                    {'error': 'Already applied to this opportunity'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create applied opportunity
            applied = AppliedOpportunity.objects.create(
                user=request.user,
                opportunity_id=data.get('opportunity_id'),
                collection=data.get('collection', ''),
                title=data.get('title', ''),
                agency=data.get('agency', ''),
                url=data.get('url', ''),
                application_url=data.get('application_url', ''),
                application_instructions=data.get('application_instructions', ''),
                match_score=data.get('match_score', 0),
                win_rate=data.get('win_rate', 0.0),
                win_rate_reasoning=data.get('win_rate_reasoning', {}),
                data=data.get('data', {})
            )
            
            # Remove from saved if exists
            SavedOpportunity.objects.filter(
                user=request.user,
                opportunity_id=data.get('opportunity_id')
            ).delete()
            
            serializer = self.get_serializer(applied)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating applied opportunity: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SavedOpportunityViewSet(viewsets.ModelViewSet):
    """ViewSet for saved opportunities"""
    serializer_class = SavedOpportunitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SavedOpportunity.objects.filter(user=self.request.user)
    
    def create(self, request):
        """
        Save an opportunity for later
        
        Expected data:
        {
            "opportunity_id": "abc123",
            "collection": "SAM",
            "title": "Opportunity Title",
            "agency": "Agency Name",
            "url": "https://...",
            "match_score": 45,
            "data": {...}
        }
        """
        try:
            data = request.data.copy()
            
            # Check if already saved
            existing = SavedOpportunity.objects.filter(
                user=request.user,
                opportunity_id=data.get('opportunity_id')
            ).first()
            
            if existing:
                return Response(
                    {'error': 'Already saved this opportunity'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create saved opportunity
            saved = SavedOpportunity.objects.create(
                user=request.user,
                opportunity_id=data.get('opportunity_id'),
                collection=data.get('collection', ''),
                title=data.get('title', ''),
                agency=data.get('agency', ''),
                url=data.get('url', ''),
                match_score=data.get('match_score', 0),
                data=data.get('data', {})
            )
            
            serializer = self.get_serializer(saved)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating saved opportunity: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Move a saved opportunity to applied"""
        try:
            saved_opp = self.get_object()
            
            # Create applied opportunity
            applied = AppliedOpportunity.objects.create(
                user=request.user,
                opportunity_id=saved_opp.opportunity_id,
                collection=saved_opp.collection,
                title=saved_opp.title,
                agency=saved_opp.agency,
                url=saved_opp.url,
                application_url=request.data.get('application_url', ''),
                application_instructions=request.data.get('application_instructions', ''),
                match_score=saved_opp.match_score,
                win_rate=request.data.get('win_rate', 0.0),
                win_rate_reasoning=request.data.get('win_rate_reasoning', {}),
                data=saved_opp.data
            )
            
            # Delete from saved
            saved_opp.delete()
            
            serializer = AppliedOpportunitySerializer(applied)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error applying saved opportunity: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'ok', 'message': 'RFPueen API is running'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the user"""
    try:
        applied_count = AppliedOpportunity.objects.filter(user=request.user).count()
        saved_count = SavedOpportunity.objects.filter(user=request.user).count()
        
        # Get recent activities
        recent_applied = AppliedOpportunity.objects.filter(
            user=request.user
        ).order_by('-applied_at')[:5]
        
        recent_saved = SavedOpportunity.objects.filter(
            user=request.user
        ).order_by('-saved_at')[:5]
        
        return Response({
            'applied_count': applied_count,
            'saved_count': saved_count,
            'recent_applied': AppliedOpportunitySerializer(recent_applied, many=True).data,
            'recent_saved': SavedOpportunitySerializer(recent_saved, many=True).data
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
