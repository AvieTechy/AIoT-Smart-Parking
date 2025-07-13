"""
Configuration settings for the Smart Parking Face Recognition API
"""
import os
from typing import Optional
from functools import lru_cache
from pathlib import Path

# Get the config directory path
CONFIG_DIR = Path(__file__).parent

class Settings:
    """Application settings"""

    def __init__(self):
        """Initialize settings and load environment variables"""
        # Load environment variables from .env file
        env_file = CONFIG_DIR / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)

        # Load all settings
        self._load_settings()
        self._validate_config()

    def _load_settings(self):
        """Load all configuration settings"""
        # API Configuration
        self.API_KEY = os.getenv("API_KEY", "smart-parking-api-key-2024")

        # Face Recognition Settings
        self.SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

        # Firebase Configuration
        self.GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

        # Cloudinary Configuration
        self.CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
        self.CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
        self.CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
        self.CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

        # Server Configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"

        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        # Model Configuration
        self.MODEL_DEVICE = os.getenv("MODEL_DEVICE", "auto")  # auto, cpu, cuda
        self.MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./models")

        # Image Processing Configuration
        self.MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "5242880"))  # 5MB
        self.ALLOWED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp"]

        # Request Configuration
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

        # Security Configuration
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    def _validate_config(self):
        """Validate required configuration"""
        required_env_vars = []

        # Check Cloudinary configuration (optional validation)
        if not all([self.CLOUDINARY_CLOUD_NAME, self.CLOUDINARY_API_KEY, self.CLOUDINARY_API_SECRET]):
            print("Warning: Cloudinary configuration incomplete. Image upload will be disabled.")

        # Note: We make Firebase optional for now
        # Check Firebase configuration
        # if not self.GOOGLE_APPLICATION_CREDENTIALS and not self.FIREBASE_PROJECT_ID:
        #     required_env_vars.append("GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_PROJECT_ID")

        if required_env_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(required_env_vars)}"
            )

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG

    def get_database_url(self) -> str:
        """Get Firebase database URL"""
        if self.FIREBASE_PROJECT_ID:
            return f"https://{self.FIREBASE_PROJECT_ID}.firebaseio.com/"
        return ""

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()
