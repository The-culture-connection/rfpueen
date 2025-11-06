"""
Firebase Integration Service
Handles connections to Firebase Firestore and syncing opportunity data
"""
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import logging
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class FirebaseService:
    """Service for interacting with Firebase Firestore"""
    
    _db = None
    _initialized = False
    
    @classmethod
    def initialize(cls, credentials_path: Optional[str] = None):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return
        
        try:
            # Use provided credentials or look for environment variable
            cred_path = credentials_path or os.getenv('FIREBASE_CREDENTIALS_PATH')
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized with credentials file")
            else:
                # Try to use default credentials or service account from settings
                if hasattr(settings, 'FIREBASE_CONFIG'):
                    cred = credentials.Certificate(settings.FIREBASE_CONFIG)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized with Django settings")
                else:
                    # Initialize with default credentials (for GCP environments)
                    firebase_admin.initialize_app()
                    logger.info("Firebase initialized with default credentials")
            
            cls._db = firestore.client()
            cls._initialized = True
            logger.info("Firebase Firestore client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    @classmethod
    def get_db(cls):
        """Get Firestore database instance"""
        if not cls._initialized:
            cls.initialize()
        return cls._db
    
    @classmethod
    def get_opportunities_from_collections(
        cls,
        collections: List[str],
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch opportunities from specified Firebase collections
        
        Args:
            collections: List of collection names to fetch from
            limit: Maximum number of docs per collection
            
        Returns:
            List of opportunity dictionaries
        """
        db = cls.get_db()
        all_opportunities = []
        
        for collection_name in collections:
            try:
                docs = db.collection(collection_name).limit(limit).stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    data['collection'] = collection_name
                    all_opportunities.append(data)
                
                logger.info(f"Fetched opportunities from {collection_name}")
                
            except Exception as e:
                logger.error(f"Error fetching from {collection_name}: {e}")
                continue
        
        logger.info(f"Total opportunities fetched: {len(all_opportunities)}")
        return all_opportunities
    
    @classmethod
    def get_user_profile(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from Firebase
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            User profile dictionary or None
        """
        db = cls.get_db()
        
        try:
            profile_ref = db.collection('profiles').document(user_id)
            profile_doc = profile_ref.get()
            
            if profile_doc.exists:
                return profile_doc.to_dict()
            else:
                logger.warning(f"Profile not found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching user profile {user_id}: {e}")
            return None
    
    @classmethod
    def save_applied_opportunity(
        cls,
        user_id: str,
        opportunity_id: str,
        opportunity_data: Dict[str, Any]
    ) -> bool:
        """
        Save applied opportunity to Firebase
        
        Args:
            user_id: Firebase user ID
            opportunity_id: Opportunity ID
            opportunity_data: Opportunity data to save
            
        Returns:
            True if successful, False otherwise
        """
        db = cls.get_db()
        
        try:
            applied_ref = (
                db.collection('profiles')
                .document(user_id)
                .collection('Applied')
                .document(opportunity_id)
            )
            
            applied_ref.set(opportunity_data)
            logger.info(f"Saved applied opportunity {opportunity_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving applied opportunity: {e}")
            return False
    
    @classmethod
    def save_saved_opportunity(
        cls,
        user_id: str,
        opportunity_id: str,
        opportunity_data: Dict[str, Any]
    ) -> bool:
        """
        Save opportunity for later to Firebase
        
        Args:
            user_id: Firebase user ID
            opportunity_id: Opportunity ID
            opportunity_data: Opportunity data to save
            
        Returns:
            True if successful, False otherwise
        """
        db = cls.get_db()
        
        try:
            saved_ref = (
                db.collection('profiles')
                .document(user_id)
                .collection('Saved')
                .document(opportunity_id)
            )
            
            saved_ref.set(opportunity_data)
            logger.info(f"Saved opportunity {opportunity_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving opportunity: {e}")
            return False
    
    @classmethod
    def get_applied_opportunities(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get list of opportunities user has applied to"""
        db = cls.get_db()
        
        try:
            applied_docs = (
                db.collection('profiles')
                .document(user_id)
                .collection('Applied')
                .stream()
            )
            
            applied = []
            for doc in applied_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                applied.append(data)
            
            return applied
            
        except Exception as e:
            logger.error(f"Error fetching applied opportunities: {e}")
            return []
    
    @classmethod
    def get_saved_opportunities(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get list of opportunities user has saved"""
        db = cls.get_db()
        
        try:
            saved_docs = (
                db.collection('profiles')
                .document(user_id)
                .collection('Saved')
                .stream()
            )
            
            saved = []
            for doc in saved_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                saved.append(data)
            
            return saved
            
        except Exception as e:
            logger.error(f"Error fetching saved opportunities: {e}")
            return []
    
    @classmethod
    def delete_saved_opportunity(cls, user_id: str, opportunity_id: str) -> bool:
        """Delete a saved opportunity"""
        db = cls.get_db()
        
        try:
            saved_ref = (
                db.collection('profiles')
                .document(user_id)
                .collection('Saved')
                .document(opportunity_id)
            )
            saved_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting saved opportunity: {e}")
            return False
    
    @classmethod
    def delete_applied_opportunity(cls, user_id: str, opportunity_id: str) -> bool:
        """Delete an applied opportunity"""
        db = cls.get_db()
        
        try:
            applied_ref = (
                db.collection('profiles')
                .document(user_id)
                .collection('Applied')
                .document(opportunity_id)
            )
            applied_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting applied opportunity: {e}")
            return False
