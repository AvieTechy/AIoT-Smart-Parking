import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Firebase settings
    firebase_key_path: str = "firebase_key.json"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
