"""
Firebase Firestore service for storing and retrieving face data
"""
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json
import os
from backend.config.settings import Settings

logger = logging.getLogger(__name__)

class FirebaseService:
    """Firebase Firestore service for face data management"""

    def __init__(self):
        self.db: Optional[Client] = None
        self.collection_name = "faces"
        self._connected = False
        self.settings = Settings()
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                # Try to find firebase key file
                key_file_paths = [
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'firebase-key.json'),
                    'firebase-key.json',
                    '/app/src/backend/config/firebase-key.json'
                ]

                firebase_key_path = None
                for path in key_file_paths:
                    if os.path.exists(path):
                        firebase_key_path = path
                        break

                if firebase_key_path:
                    logger.info(f"Using Firebase key file: {firebase_key_path}")
                    cred = credentials.Certificate(firebase_key_path)
                else:
                    # Fall back to environment credentials
                    logger.warning("Firebase key file not found. Using environment credentials.")
                    cred = credentials.ApplicationDefault()

                firebase_admin.initialize_app(cred)

            # Get Firestore client
            self.db = firestore.client()
            self._connected = True
            logger.info("Firebase Firestore initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            self._connected = False

    def is_connected(self) -> bool:
        """Check if Firebase is connected"""
        return self._connected and self.db is not None

    async def save_face_data(
        self,
        plate_number: str,
        embedding: List[float],
        image_url: str
    ) -> bool:
        """
        Save face embedding and metadata to Firestore

        Args:
            plate_number: Vehicle plate number (used as document ID)
            embedding: 512-dimensional face embedding
            image_url: URL of the uploaded image

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            raise RuntimeError("Firebase not connected")

        try:
            doc_data = {
                "plate_number": plate_number,
                "embedding": embedding,
                "registration_image_url": image_url,
                "registration_date": datetime.utcnow().isoformat(),
                "last_image_url": image_url,
                "last_verification_date": None,
                "verification_count": 0,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
            }

            # Save to Firestore using plate_number as document ID
            doc_ref = self.db.collection(self.collection_name).document(plate_number)
            doc_ref.set(doc_data)

            logger.info(f"Successfully saved face data for plate: {plate_number}")
            return True

        except Exception as e:
            logger.error(f"Error saving face data: {str(e)}")
            return False

    async def get_face_data(self, plate_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve face data from Firestore

        Args:
            plate_number: Vehicle plate number

        Returns:
            Face data dictionary or None if not found
        """
        if not self.is_connected():
            raise RuntimeError("Firebase not connected")

        try:
            doc_ref = self.db.collection(self.collection_name).document(plate_number)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                logger.info(f"Retrieved face data for plate: {plate_number}")
                return data
            else:
                logger.info(f"No face data found for plate: {plate_number}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving face data: {str(e)}")
            return None

    async def update_last_image(self, plate_number: str, image_url: str) -> bool:
        """
        Update last verification image and timestamp

        Args:
            plate_number: Vehicle plate number
            image_url: URL of the new verification image

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            raise RuntimeError("Firebase not connected")

        try:
            doc_ref = self.db.collection(self.collection_name).document(plate_number)

            # Increment verification count and update last image
            doc_ref.update({
                "last_image_url": image_url,
                "last_verification_date": datetime.utcnow().isoformat(),
                "verification_count": firestore.Increment(1),
                "updated_at": firestore.SERVER_TIMESTAMP
            })

            logger.info(f"Updated last image for plate: {plate_number}")
            return True

        except Exception as e:
            logger.error(f"Error updating last image: {str(e)}")
            return False

    async def delete_face_data(self, plate_number: str) -> bool:
        """
        Delete face data from Firestore

        Args:
            plate_number: Vehicle plate number

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            raise RuntimeError("Firebase not connected")

        try:
            doc_ref = self.db.collection(self.collection_name).document(plate_number)
            doc = doc_ref.get()

            if doc.exists:
                doc_ref.delete()
                logger.info(f"Deleted face data for plate: {plate_number}")
                return True
            else:
                logger.info(f"No face data found to delete for plate: {plate_number}")
                return False

        except Exception as e:
            logger.error(f"Error deleting face data: {str(e)}")
            return False

    async def list_all_plates(self) -> List[str]:
        """
        List all registered plate numbers

        Returns:
            List of plate numbers
        """
        if not self.is_connected():
            raise RuntimeError("Firebase not connected")

        try:
            docs = self.db.collection(self.collection_name).stream()
            plate_numbers = [doc.id for doc in docs]

            logger.info(f"Retrieved {len(plate_numbers)} registered plates")
            return plate_numbers

        except Exception as e:
            logger.error(f"Error listing plates: {str(e)}")
            return []

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Statistics dictionary
        """
        if not self.is_connected():
            raise RuntimeError("Firebase not connected")

        try:
            # Get total count
            docs = self.db.collection(self.collection_name).stream()
            docs_list = list(docs)
            total_count = len(docs_list)

            # Calculate total verifications
            total_verifications = sum(
                doc.to_dict().get("verification_count", 0)
                for doc in docs_list
            )

            stats = {
                "total_registered_vehicles": total_count,
                "total_verifications": total_verifications,
                "last_updated": datetime.utcnow().isoformat()
            }

            logger.info(f"Retrieved statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                "total_registered_vehicles": 0,
                "total_verifications": 0,
                "error": str(e)
            }
