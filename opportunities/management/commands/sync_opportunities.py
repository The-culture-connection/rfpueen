"""
Django management command to sync opportunities from Firebase to local database
"""
from django.core.management.base import BaseCommand
from opportunities.firebase_service import FirebaseService
from opportunities.models import Opportunity
from datetime import datetime


class Command(BaseCommand):
    help = 'Sync opportunities from Firebase Firestore to local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Maximum number of opportunities to sync per collection'
        )
        parser.add_argument(
            '--collections',
            nargs='+',
            default=['SAM', 'grants.gov', 'grantwatch', 'PND_RFPs', 'rfpmart', 'bid'],
            help='Firebase collections to sync from'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        collections = options['collections']
        
        self.stdout.write(f"Syncing opportunities from {len(collections)} collections...")
        self.stdout.write(f"Limit: {limit} per collection\n")
        
        try:
            # Initialize Firebase
            FirebaseService.initialize()
            
            # Fetch opportunities
            opportunities = FirebaseService.get_opportunities_from_collections(
                collections, limit=limit
            )
            
            self.stdout.write(f"Fetched {len(opportunities)} opportunities from Firebase")
            
            # Sync to database
            synced = 0
            updated = 0
            errors = 0
            
            for opp_data in opportunities:
                try:
                    firebase_id = opp_data.get('id', '')
                    collection = opp_data.get('collection', '')
                    
                    if not firebase_id:
                        errors += 1
                        continue
                    
                    # Parse dates
                    close_date = self._parse_date(opp_data.get('closeDate') or opp_data.get('deadline'))
                    open_date = self._parse_date(opp_data.get('openDate') or opp_data.get('postedDate'))
                    posted_date = self._parse_date(opp_data.get('postedDate'))
                    deadline = self._parse_date(opp_data.get('deadline'))
                    
                    # Create or update opportunity
                    opportunity, created = Opportunity.objects.update_or_create(
                        firebase_id=firebase_id,
                        defaults={
                            'collection': collection,
                            'title': opp_data.get('title', '')[:500],
                            'description': opp_data.get('description', ''),
                            'summary': opp_data.get('summary', ''),
                            'agency': opp_data.get('agency', '')[:500],
                            'department': opp_data.get('department', '')[:500],
                            'url': opp_data.get('url', '')[:1000],
                            'synopsis_url': opp_data.get('synopsisUrl', '')[:1000],
                            'application_url': opp_data.get('applicationUrl', '')[:1000],
                            'open_date': open_date,
                            'close_date': close_date,
                            'posted_date': posted_date,
                            'deadline': deadline,
                            'place': opp_data.get('place', '')[:255],
                            'city': opp_data.get('city', '')[:255],
                            'state': opp_data.get('state', '')[:100],
                            'contact_email': opp_data.get('contactEmail', ''),
                            'contact_phone': opp_data.get('contactPhone', '')[:50],
                            'data': opp_data,
                        }
                    )
                    
                    if created:
                        synced += 1
                    else:
                        updated += 1
                        
                except Exception as e:
                    self.stderr.write(f"Error syncing opportunity {firebase_id}: {str(e)}")
                    errors += 1
                    continue
            
            self.stdout.write(self.style.SUCCESS(f"\nSync complete!"))
            self.stdout.write(f"  New opportunities: {synced}")
            self.stdout.write(f"  Updated opportunities: {updated}")
            if errors > 0:
                self.stdout.write(self.style.WARNING(f"  Errors: {errors}"))
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Sync failed: {str(e)}"))
            raise
    
    def _parse_date(self, date_str):
        """Parse date string to date object"""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, str):
                # Try ISO format first
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                # Try simple date format
                return datetime.strptime(date_str[:10], '%Y-%m-%d').date()
            return None
        except:
            return None
