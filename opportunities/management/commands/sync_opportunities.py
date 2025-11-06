"""
Management command to sync opportunities from Firebase
"""
from django.core.management.base import BaseCommand
from opportunities.firebase_integration import FirebaseService


class Command(BaseCommand):
    help = 'Sync opportunities from Firebase Firestore'

    def add_arguments(self, parser):
        parser.add_argument(
            '--collections',
            nargs='+',
            type=str,
            help='Specific collections to sync (default: all)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of opportunities per collection',
        )

    def handle(self, *args, **options):
        collections = options.get('collections')
        limit = options.get('limit')
        
        self.stdout.write(self.style.WARNING('Starting opportunity sync...'))
        
        try:
            count = FirebaseService.sync_all_opportunities(
                collections=collections,
                limit_per_collection=limit
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully synced {count} opportunities')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing opportunities: {e}')
            )
