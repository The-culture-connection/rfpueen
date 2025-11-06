import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import os

# Initialize Firebase Admin SDK
try:
    # Try to initialize Firebase if not already initialized
    if not firebase_admin._apps:
        # For production, you should use a service account key file
        # For now, we'll use the default credentials or initialize without credentials
        # and use the REST API instead
        pass
except Exception as e:
    print(f"Firebase Admin initialization note: {e}")

def get_firestore_client():
    """Get Firestore client"""
    try:
        if firebase_admin._apps:
            return firestore.client()
        else:
            # Return None if Firebase Admin is not initialized
            # We'll use REST API instead
            return None
    except Exception:
        return None
