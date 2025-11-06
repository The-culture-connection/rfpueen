"""
Management command to sync opportunities from Firebase
"""
from django.core.management.base import BaseCommand
from opportunities.models import Opportunity
from opportunities.views import get_firebase_opportunities, _convert_firebase_fields
from django.conf import settings
from django.utils import timezone


class Command(BaseCommand):
    help = 'Sync opportunities from Firebase Firestore'

    def add_arguments(self, parser):
        parser.add_argument(
            '--collections',
            type=str,
            nargs='+',
            help='Specific collections to sync (default: all from COLLECTION_MAP)',
        )

    def handle(self, *args, **options):
        collections = options.get('collections')
        
        if not collections:
            # Get all collections from COLLECTION_MAP
            collection_map = settings.COLLECTION_MAP
            collections = set()
            for cols in collection_map.values():
                collections.update(cols)
            collections = list(collections)
        
        self.stdout.write(f"Syncing opportunities from collections: {', '.join(collections)}")
        
        # Fetch opportunities
        opportunities_data = get_firebase_opportunities(collections)
        
        self.stdout.write(f"Found {len(opportunities_data)} opportunities")
        
        # Sync to database
        created_count = 0
        updated_count = 0
        
        for opp_data in opportunities_data:
            firebase_id = opp_data.get('id')
            if not firebase_id:
                continue
            
            collection = opp_data.get('collection', '')
            title = opp_data.get('title', 'Untitled')
            
            opportunity, created = Opportunity.objects.get_or_create(
                firebase_id=firebase_id,
                defaults={
                    'collection': collection,
                    'title': title,
                    'raw_data': opp_data,
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
            
            # Update fields
            opportunity.collection = collection
            opportunity.title = title
            opportunity.description = opp_data.get('description', '')
            opportunity.summary = opp_data.get('summary', '')
            opportunity.agency = opp_data.get('agency', '') or opp_data.get('department', '')
            opportunity.department = opp_data.get('department', '')
            opportunity.url = opp_data.get('url', '') or opp_data.get('synopsisUrl', '') or opp_data.get('link', '')
            opportunity.synopsis_url = opp_data.get('synopsisUrl', '')
            opportunity.link = opp_data.get('link', '')
            opportunity.application_url = opp_data.get('applicationUrl', '')
            opportunity.contact_email = opp_data.get('contactEmail', '')
            opportunity.contact_phone = opp_data.get('contactPhone', '')
            opportunity.place = opp_data.get('place', '')
            opportunity.city = opp_data.get('city', '')
            opportunity.state = opp_data.get('state', '')
            opportunity.raw_data = opp_data
            opportunity.last_scanned_at = timezone.now()
            
            # Parse dates
            from opportunities.matching import parse_date
            opportunity.open_date = parse_date(opp_data.get('openDate') or opp_data.get('postedDate'))
            opportunity.posted_date = parse_date(opp_data.get('postedDate'))
            opportunity.close_date = parse_date(opp_data.get('closeDate') or opp_data.get('deadline'))
            opportunity.deadline = parse_date(opp_data.get('deadline'))
            
            opportunity.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synced: {created_count} created, {updated_count} updated'
            )
        )
