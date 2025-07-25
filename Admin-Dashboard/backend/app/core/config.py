import os
from pydantic_settings import BaseSettings

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
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
