import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Firebase settings
    firebase_key_path: str = "firebase_key.json"

    # JWT settings
    jwt_secret_key: str = "your-super-secret-jwt-key-change-this-in-production-please"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    project_name: str = "Smart Parking Admin API"

    # CORS settings - parse comma-separated string to list
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # Environment
    environment: str = "development"

    @property
    def cors_origins(self) -> List[str]:
        """Parse allowed_origins string to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
