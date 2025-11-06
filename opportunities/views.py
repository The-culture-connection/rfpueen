"""
Views for opportunities app
"""
import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, Opportunity, AppliedOpportunity, SavedOpportunity
from .matching import match_opportunities, bucket_of
from .application_finder import find_application_form_for_opportunity
from .win_rate import calculate_win_rate


def get_firebase_opportunities(collection_names):
    """
    Fetch opportunities from Firebase using REST API
    
    Args:
        collection_names: List of collection names to fetch from
    
    Returns:
        List of opportunity dictionaries
    """
    all_opportunities = []
    
    # Firebase REST API endpoint
    project_id = settings.FIREBASE_CONFIG['projectId']
    base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"
    
    for collection_name in collection_names:
        try:
            url = f"{base_url}/{collection_name}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                for doc in documents:
                    doc_id = doc['name'].split('/')[-1]
                    fields = doc.get('fields', {})
                    
                    # Convert Firebase fields to regular dict
                    opp_data = _convert_firebase_fields(fields)
                    opp_data['id'] = doc_id
                    opp_data['collection'] = collection_name
                    all_opportunities.append(opp_data)
        except Exception as e:
            print(f"Error fetching {collection_name}: {e}")
            continue
    
    return all_opportunities


def _convert_firebase_fields(fields):
    """Convert Firebase field format to regular dict"""
    result = {}
    for key, value in fields.items():
        # Firebase stores values in a type-value structure
        if 'stringValue' in value:
            result[key] = value['stringValue']
        elif 'integerValue' in value:
            result[key] = int(value['integerValue'])
        elif 'doubleValue' in value:
            result[key] = float(value['doubleValue'])
        elif 'booleanValue' in value:
            result[key] = value['booleanValue']
        elif 'timestampValue' in value:
            result[key] = value['timestampValue']
        elif 'arrayValue' in value:
            array_items = value['arrayValue'].get('values', [])
            result[key] = [_convert_firebase_fields({'item': item})['item'] for item in array_items]
        elif 'mapValue' in value:
            result[key] = _convert_firebase_fields(value['mapValue'].get('fields', {}))
    return result


@login_required
def dashboard(request):
    """Main dashboard view"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    applied_count = AppliedOpportunity.objects.filter(user=request.user).count()
    saved_count = SavedOpportunity.objects.filter(user=request.user).count()
    
    context = {
        'applied_count': applied_count,
        'saved_count': saved_count,
    }
    return render(request, 'opportunities/dashboard.html', context)


@login_required
def explore(request):
    """Explore opportunities view"""
    return render(request, 'opportunities/explore.html')


@login_required
def dashboard_applied(request):
    """Applied opportunities view"""
    applied = AppliedOpportunity.objects.filter(user=request.user).select_related('opportunity')
    
    # Handle cases where opportunity might not exist
    applied_list = []
    for app in applied:
        if not app.opportunity:
            # Try to get from raw_data or create a minimal opportunity
            try:
                opp = Opportunity.objects.get(firebase_id=app.firebase_opportunity_id)
                app.opportunity = opp
            except Opportunity.DoesNotExist:
                # Create a minimal opportunity object for display
                from django.db import models
                class MinimalOpportunity:
                    title = app.firebase_opportunity_id
                    agency = "Unknown"
                    url = ""
                    close_date = None
                app.opportunity = MinimalOpportunity()
        applied_list.append(app)
    
    context = {
        'applied_opportunities': applied_list,
    }
    return render(request, 'opportunities/dashboard_applied.html', context)


@login_required
def dashboard_saved(request):
    """Saved opportunities view"""
    saved = SavedOpportunity.objects.filter(user=request.user).select_related('opportunity')
    
    context = {
        'saved_opportunities': saved,
    }
    return render(request, 'opportunities/dashboard_saved.html', context)


@login_required
@require_http_methods(["POST"])
def api_match_opportunities(request):
    """API endpoint to match opportunities"""
    try:
        profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # Get profile data
        profile_data = {
            'fundingTypes': profile_obj.funding_types or [],
            'interestsMain': profile_obj.interests_main or [],
            'interestsSub': profile_obj.interests_sub or [],
            'grantsByInterest': profile_obj.grants_by_interest or [],
        }
        
        if not profile_data['fundingTypes']:
            return JsonResponse({
                'error': 'No funding types selected in profile'
            }, status=400)
        
        # Use Firebase Functions if enabled
        if getattr(settings, 'USE_FIREBASE_FUNCTIONS', False):
            try:
                functions_url = settings.FIREBASE_FUNCTIONS['match_opportunities']
                response = requests.post(
                    functions_url,
                    json={
                        **profile_data,
                        'userId': str(request.user.id)  # Optional: for filtering applied/saved
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return JsonResponse({
                        'opportunities': data.get('opportunities', [])[:50],
                        'total': data.get('total', 0),
                    })
                else:
                    # Fallback to local computation
                    print(f"Firebase Functions error: {response.status_code}")
            except Exception as e:
                print(f"Firebase Functions error: {e}")
                # Fallback to local computation
        
        # Local computation (fallback or if Firebase Functions disabled)
        collection_map = settings.COLLECTION_MAP
        collections_to_search = set()
        for ft in profile_data['fundingTypes']:
            collections = collection_map.get(ft, [])
            collections_to_search.update(collections)
        
        # Fetch opportunities from Firebase
        opportunities = get_firebase_opportunities(list(collections_to_search))
        
        # Match opportunities
        matched = match_opportunities(opportunities, profile_data)
        
        # Filter out already applied/saved
        applied_ids = set(
            AppliedOpportunity.objects.filter(user=request.user)
            .values_list('firebase_opportunity_id', flat=True)
        )
        saved_ids = set(
            SavedOpportunity.objects.filter(user=request.user)
            .values_list('firebase_opportunity_id', flat=True)
        )
        
        filtered = [
            opp for opp in matched 
            if opp.get('id') not in applied_ids and opp.get('id') not in saved_ids
        ]
        
        # Calculate win rates
        for opp in filtered:
            win_rate_data = calculate_win_rate(opp, profile_data, opp.get('score'))
            opp['win_rate'] = win_rate_data['win_rate']
            opp['win_rate_reasoning'] = win_rate_data['reasoning']
        
        return JsonResponse({
            'opportunities': filtered[:50],  # Limit to 50
            'total': len(filtered),
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_apply(request, opp_id):
    """API endpoint to apply to an opportunity"""
    try:
        data = json.loads(request.body)
        collection = data.get('collection', '')
        
        # Get or create opportunity in local DB
        opportunity, _ = Opportunity.objects.get_or_create(
            firebase_id=opp_id,
            defaults={
                'collection': collection,
                'title': data.get('title', 'Untitled'),
                'raw_data': data,
            }
        )
        
        # Update opportunity data
        opportunity.title = data.get('title', opportunity.title)
        opportunity.description = data.get('description', '')
        opportunity.agency = data.get('agency', '') or data.get('department', '')
        opportunity.url = data.get('url', '') or data.get('synopsisUrl', '') or data.get('link', '')
        opportunity.close_date = data.get('closeDate') or data.get('deadline')
        opportunity.raw_data = data
        opportunity.save()
        
        # Find application form
        form_result = find_application_form_for_opportunity(data)
        
        # Calculate win rate
        profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_data = {
            'fundingTypes': profile_obj.funding_types or [],
            'interestsMain': profile_obj.interests_main or [],
            'interestsSub': profile_obj.interests_sub or [],
        }
        
        match_score = data.get('score', 0)
        win_rate_data = calculate_win_rate(data, profile_data, match_score)
        
        # Create applied opportunity
        applied, created = AppliedOpportunity.objects.get_or_create(
            user=request.user,
            firebase_opportunity_id=opp_id,
            defaults={
                'opportunity': opportunity,
                'firebase_collection': collection,
                'application_url': form_result.get('url'),
                'application_instructions': form_result.get('instructions'),
                'match_score': match_score,
                'win_rate': win_rate_data['win_rate'],
                'win_rate_reasoning': win_rate_data['reasoning'],
            }
        )
        
        if not created:
            # Update existing
            applied.application_url = form_result.get('url')
            applied.application_instructions = form_result.get('instructions')
            applied.win_rate = win_rate_data['win_rate']
            applied.win_rate_reasoning = win_rate_data['reasoning']
            applied.save()
        
        return JsonResponse({
            'success': True,
            'application_url': form_result.get('url'),
            'application_instructions': form_result.get('instructions'),
            'win_rate': win_rate_data['win_rate'],
            'win_rate_reasoning': win_rate_data['reasoning'],
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_save(request, opp_id):
    """API endpoint to save an opportunity"""
    try:
        data = json.loads(request.body)
        collection = data.get('collection', '')
        
        # Get or create opportunity
        opportunity, _ = Opportunity.objects.get_or_create(
            firebase_id=opp_id,
            defaults={
                'collection': collection,
                'title': data.get('title', 'Untitled'),
                'raw_data': data,
            }
        )
        
        # Create saved opportunity
        saved, created = SavedOpportunity.objects.get_or_create(
            user=request.user,
            firebase_opportunity_id=opp_id,
            defaults={
                'opportunity': opportunity,
                'firebase_collection': collection,
            }
        )
        
        return JsonResponse({
            'success': True,
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_pass(request, opp_id):
    """API endpoint to pass on an opportunity"""
    # Just return success - we don't need to store passed opportunities
    return JsonResponse({
        'success': True,
    })


@login_required
@require_http_methods(["POST"])
def api_remove_applied(request, opp_id):
    """API endpoint to remove an applied opportunity"""
    try:
        AppliedOpportunity.objects.filter(
            user=request.user,
            firebase_opportunity_id=opp_id
        ).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_remove_saved(request, opp_id):
    """API endpoint to remove a saved opportunity"""
    try:
        SavedOpportunity.objects.filter(
            user=request.user,
            firebase_opportunity_id=opp_id
        ).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_find_application_form(request):
    """API endpoint to find application form for an opportunity"""
    try:
        data = json.loads(request.body)
        result = find_application_form_for_opportunity(data)
        
        return JsonResponse(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e)
        }, status=500)
