"""
Cloudinary service for image upload and management
"""
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import cv2
import numpy as np
import requests
from typing import Optional
import logging
from datetime import datetime
import os
import tempfile
from backend.config.settings import Settings

logger = logging.getLogger(__name__)

class CloudinaryService:
    """Cloudinary service for image operations"""

    def __init__(self):
        self._configured = False
        self.settings = Settings()
        self._configure_cloudinary()

    def _configure_cloudinary(self):
        """Configure Cloudinary with credentials"""
        try:
            # Configure Cloudinary
            cloudinary.config(
                cloud_name=self.settings.CLOUDINARY_CLOUD_NAME,
                api_key=self.settings.CLOUDINARY_API_KEY,
                api_secret=self.settings.CLOUDINARY_API_SECRET,
                secure=True
            )

            self._configured = True
            logger.info("Cloudinary configured successfully")

        except Exception as e:
            logger.error(f"Failed to configure Cloudinary: {str(e)}")
            self._configured = False

    def is_configured(self) -> bool:
        """Check if Cloudinary is configured"""
        return self._configured

    async def download_image(self, image_url: str) -> np.ndarray:
        """
        Download image from URL and convert to OpenCV format

        Args:
            image_url: URL of the image to download

        Returns:
            Image as numpy array in BGR format (OpenCV format)
        """
        try:
            # Download image
            response = requests.get(str(image_url), timeout=30)
            response.raise_for_status()

            # Convert to numpy array
            image_array = np.frombuffer(response.content, np.uint8)

            # Decode with OpenCV
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError("Failed to decode image")

            logger.info(f"Successfully downloaded image from: {image_url}")
            return image

        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            raise e

    async def upload_evidence(
        self,
        image: np.ndarray,
        plate_number: str,
        is_registration: bool = True
    ) -> str:
        """
        Upload evidence image to Cloudinary

        Args:
            image: Image as numpy array (BGR format)
            plate_number: Vehicle plate number
            is_registration: True for registration, False for verification

        Returns:
            Secure URL of uploaded image
        """
        if not self._configured:
            raise RuntimeError("Cloudinary not configured")

        try:
            # Generate timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            # Determine file prefix
            prefix = "register" if is_registration else "verify"

            # Create filename
            filename = f"{prefix}_{timestamp}"

            # Create folder path
            folder_path = f"parking/{plate_number}"

            # Encode image to bytes
            _, buffer = cv2.imencode('.jpg', image)
            image_bytes = buffer.tobytes()

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name

            try:
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    temp_file_path,
                    folder=folder_path,
                    public_id=filename,
                    overwrite=True,
                    resource_type="image",
                    format="jpg",
                    quality="auto:good"
                )

                secure_url = upload_result["secure_url"]
                logger.info(f"Successfully uploaded evidence image: {secure_url}")

                return secure_url

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error uploading evidence image: {str(e)}")
            raise e

    async def upload_from_url(
        self,
        image_url: str,
        plate_number: str,
        is_registration: bool = True
    ) -> str:
        """
        Download image from URL and re-upload as evidence

        Args:
            image_url: Source image URL
            plate_number: Vehicle plate number
            is_registration: True for registration, False for verification

        Returns:
            Secure URL of uploaded evidence image
        """
        try:
            # Download image
            image = await self.download_image(image_url)

            # Upload as evidence
            evidence_url = await self.upload_evidence(
                image, plate_number, is_registration
            )

            return evidence_url

        except Exception as e:
            logger.error(f"Error in upload_from_url: {str(e)}")
            raise e

    def delete_image(self, public_id: str) -> bool:
        """
        Delete image from Cloudinary

        Args:
            public_id: Public ID of the image to delete

        Returns:
            True if successful, False otherwise
        """
        if not self._configured:
            raise RuntimeError("Cloudinary not configured")

        try:
            result = cloudinary.uploader.destroy(public_id)
            success = result.get("result") == "ok"

            if success:
                logger.info(f"Successfully deleted image: {public_id}")
            else:
                logger.warning(f"Failed to delete image: {public_id}")

            return success

        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")
            return False

    def delete_folder(self, folder_path: str) -> bool:
        """
        Delete entire folder from Cloudinary

        Args:
            folder_path: Path of the folder to delete

        Returns:
            True if successful, False otherwise
        """
        if not self._configured:
            raise RuntimeError("Cloudinary not configured")

        try:
            # First, delete all images in the folder
            result = cloudinary.api.delete_resources_by_prefix(folder_path)

            # Then delete the folder itself
            cloudinary.api.delete_folder(folder_path)

            logger.info(f"Successfully deleted folder: {folder_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting folder: {str(e)}")
            return False

    def generate_url(
        self,
        public_id: str,
        transformation: Optional[dict] = None
    ) -> str:
        """
        Generate Cloudinary URL with optional transformations

        Args:
            public_id: Public ID of the image
            transformation: Optional transformation parameters

        Returns:
            Generated URL
        """
        if not self._configured:
            raise RuntimeError("Cloudinary not configured")

        try:
            url = cloudinary.utils.cloudinary_url(
                public_id,
                transformation=transformation,
                secure=True
            )[0]

            return url

        except Exception as e:
            logger.error(f"Error generating URL: {str(e)}")
            raise e
