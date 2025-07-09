import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client
import os
from typing import Optional

class FirestoreDB:
    def __init__(self):
        self._db: Optional[Client] = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase app is already initialized
            firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase app
            firebase_key_path = os.path.join(os.path.dirname(__file__), '..', '..', 'firebase_key.json')
            
            if os.path.exists(firebase_key_path):
                cred = credentials.Certificate(firebase_key_path)
                firebase_admin.initialize_app(cred)
            else:
                raise FileNotFoundError(
                    f"Firebase service account key not found at {firebase_key_path}. "
                    "Please add your Firebase service account key file."
                )
        
        # Get Firestore client
        self._db = firestore.client()
    
    @property
    def db(self) -> Client:
        """Get Firestore database client"""
        if self._db is None:
            self._initialize_firebase()
        return self._db
    
    def get_collection(self, collection_name: str):
        """Get a reference to a Firestore collection"""
        return self.db.collection(collection_name)
    
    def get_document(self, collection_name: str, document_id: str):
        """Get a reference to a Firestore document"""
        return self.db.collection(collection_name).document(document_id)

# Global instance
firestore_db = FirestoreDB()

# Convenience function to get database instance
def get_db() -> Client:
    return firestore_db.db

def get_collection(collection_name: str):
    return firestore_db.get_collection(collection_name)

def get_document(collection_name: str, document_id: str):
    return firestore_db.get_document(collection_name, document_id)
