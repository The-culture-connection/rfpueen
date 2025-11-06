"""
Firebase integration for syncing opportunity data
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth
from django.conf import settings
from .models import Opportunity, UserProfile
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class FirebaseService:
    """Service for interacting with Firebase"""
    
    _initialized = False
    _db = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return
        
        try:
            # Try to get existing app
            firebase_admin.get_app()
            cls._initialized = True
        except ValueError:
            # Initialize new app
            try:
                service_account_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_PATH', None)
                
                if service_account_path and os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use application default credentials or environment
                    firebase_admin.initialize_app()
                
                cls._initialized = True
                logger.info("Firebase Admin SDK initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                # Don't raise - allow app to continue with limited functionality
                cls._initialized = False
    
    @classmethod
    def get_db(cls):
        """Get Firestore database client"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._db is None and cls._initialized:
            try:
                cls._db = firestore.client()
            except Exception as e:
                logger.error(f"Failed to get Firestore client: {e}")
                return None
        
        return cls._db
    
    @classmethod
    def sync_opportunities_from_collection(cls, collection_name: str, limit: int = None):
        """
        Sync opportunities from a specific Firebase collection
        """
        db = cls.get_db()
        if not db:
            logger.warning("Firestore not available")
            return 0
        
        try:
            collection_ref = db.collection(collection_name)
            
            if limit:
                docs = collection_ref.limit(limit).stream()
            else:
                docs = collection_ref.stream()
            
            synced_count = 0
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    
                    # Parse dates
                    posted_date = cls._parse_date(data.get('openDate') or data.get('postedDate'))
                    close_date = cls._parse_date(data.get('closeDate') or data.get('deadline'))
                    
                    # Create or update opportunity
                    opportunity, created = Opportunity.objects.update_or_create(
                        firebase_id=doc.id,
                        collection_name=collection_name,
                        defaults={
                            'title': data.get('title', 'Untitled'),
                            'description': data.get('description', ''),
                            'summary': data.get('summary', ''),
                            'agency': data.get('agency', ''),
                            'department': data.get('department', ''),
                            'posted_date': posted_date,
                            'close_date': close_date,
                            'deadline': close_date,
                            'city': data.get('city', ''),
                            'state': data.get('state', ''),
                            'place': data.get('place', ''),
                            'url': data.get('url') or data.get('synopsisUrl') or data.get('link', ''),
                            'synopsis_url': data.get('synopsisUrl', ''),
                            'link': data.get('link', ''),
                            'contact_email': data.get('contactEmail', ''),
                            'contact_phone': data.get('contactPhone', ''),
                            'extra_data': data
                        }
                    )
                    
                    synced_count += 1
                    
                    if created:
                        logger.info(f"Created new opportunity: {opportunity.title[:50]}")
                    else:
                        logger.debug(f"Updated opportunity: {opportunity.title[:50]}")
                        
                except Exception as e:
                    logger.error(f"Error syncing opportunity {doc.id}: {e}")
                    continue
            
            logger.info(f"Synced {synced_count} opportunities from {collection_name}")
            return synced_count
        except Exception as e:
            logger.error(f"Error accessing collection {collection_name}: {e}")
            return 0
    
    @classmethod
    def sync_all_opportunities(cls, collections: list = None, limit_per_collection: int = None):
        """
        Sync opportunities from all or specified collections
        """
        if collections is None:
            collections = ["SAM", "grants.gov", "grantwatch", "PND_RFPs", "rfpmart", "bid"]
        
        total_synced = 0
        
        for collection_name in collections:
            try:
                count = cls.sync_opportunities_from_collection(collection_name, limit_per_collection)
                total_synced += count
            except Exception as e:
                logger.error(f"Error syncing collection {collection_name}: {e}")
                continue
        
        logger.info(f"Total opportunities synced: {total_synced}")
        return total_synced
    
    @classmethod
    def get_user_profile_from_firebase(cls, firebase_uid: str):
        """
        Get user profile data from Firebase
        """
        db = cls.get_db()
        if not db:
            return None
        
        try:
            profile_ref = db.collection('profiles').document(firebase_uid)
            profile_doc = profile_ref.get()
            
            if profile_doc.exists:
                return profile_doc.to_dict()
            else:
                logger.warning(f"No Firebase profile found for UID: {firebase_uid}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Firebase profile: {e}")
            return None
    
    @classmethod
    def sync_user_profile(cls, firebase_uid: str, django_user):
        """
        Sync user profile from Firebase to Django
        """
        firebase_data = cls.get_user_profile_from_firebase(firebase_uid)
        
        if not firebase_data:
            return None
        
        # Create or update Django profile
        profile, created = UserProfile.objects.update_or_create(
            firebase_uid=firebase_uid,
            defaults={
                'user': django_user,
                'organization_name': firebase_data.get('organizationName', ''),
                'organization_type': firebase_data.get('organizationType', ''),
                'city': firebase_data.get('city', ''),
                'state': firebase_data.get('state', ''),
                'funding_types': firebase_data.get('fundingTypes', []),
                'interests_main': firebase_data.get('interestsMain', []),
                'interests_sub': firebase_data.get('interestsSub', []) or firebase_data.get('grantsByInterest', []),
            }
        )
        
        if created:
            logger.info(f"Created new profile for Firebase UID: {firebase_uid}")
        else:
            logger.info(f"Updated profile for Firebase UID: {firebase_uid}")
        
        return profile
    
    @classmethod
    def verify_firebase_token(cls, id_token: str):
        """
        Verify Firebase ID token and return user info
        """
        if not cls._initialized:
            cls.initialize()
        
        if not cls._initialized:
            return None
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Error verifying Firebase token: {e}")
            return None
    
    @staticmethod
    def _parse_date(date_value):
        """Parse various date formats"""
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_value.replace('Z', '+00:00')).date()
            except:
                try:
                    # Try common formats
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            return datetime.strptime(date_value[:10], fmt).date()
                        except:
                            continue
                except:
                    pass
        
        return None
