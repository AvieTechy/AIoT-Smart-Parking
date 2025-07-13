"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

class FaceMatchRequest(BaseModel):
    """Request model for face matching endpoint"""
    image_url: HttpUrl = Field(..., description="Cloudinary URL of the image")
    gate: int = Field(..., ge=0, le=1, description="Gate type: 0=entrance (register), 1=exit (verify)")
    plate_number: str = Field(..., min_length=1, max_length=20, description="Vehicle plate number")

    class Config:
        schema_extra = {
            "example": {
                "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/sample.jpg",
                "gate": 0,
                "plate_number": "ABC123"
            }
        }

class RegisterResponse(BaseModel):
    """Response model for registration (gate=0)"""
    success: bool = Field(..., description="Registration success status")
    message: str = Field(..., description="Status message")
    evidence_url: Optional[str] = Field(None, description="URL of uploaded evidence image")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Face registered successfully for plate ABC123",
                "evidence_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/parking/ABC123/evidence_123456.jpg"
            }
        }

class VerificationResponse(BaseModel):
    """Response model for verification (gate=1)"""
    matched: bool = Field(..., description="Whether faces match")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    threshold: Optional[float] = Field(None, description="Threshold used for matching")
    evidence_url: Optional[str] = Field(None, description="URL of uploaded evidence image")
    message: Optional[str] = Field(None, description="Additional message if needed")

    class Config:
        schema_extra = {
            "example": {
                "matched": True,
                "score": 0.87,
                "threshold": 0.5,
                "evidence_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/parking/ABC123/verify_123456.jpg"
            }
        }

class FaceMatchResponse(BaseModel):
    """Generic response model that can be either registration or verification"""
    # Registration fields
    success: Optional[bool] = None
    message: Optional[str] = None

    # Verification fields
    matched: Optional[bool] = None
    score: Optional[float] = None
    threshold: Optional[float] = None

    # Common fields
    evidence_url: Optional[str] = None

class FaceInfoResponse(BaseModel):
    """Response model for face information retrieval"""
    plate_number: str = Field(..., description="Vehicle plate number")
    registration_date: str = Field(..., description="Date when face was registered")
    last_verification_date: Optional[str] = Field(None, description="Last verification date")
    registration_image_url: str = Field(..., description="URL of registration image")
    last_image_url: Optional[str] = Field(None, description="URL of last verification image")
    verification_count: int = Field(default=0, description="Number of successful verifications")

    class Config:
        schema_extra = {
            "example": {
                "plate_number": "ABC123",
                "registration_date": "2024-01-15T10:30:00Z",
                "last_verification_date": "2024-01-15T15:45:00Z",
                "registration_image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/parking/ABC123/register_123456.jpg",
                "last_image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1/parking/ABC123/verify_789012.jpg",
                "verification_count": 5
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Overall system status")
    model_loaded: bool = Field(..., description="Whether VGGFace model is loaded")
    firebase_connected: bool = Field(..., description="Whether Firebase is connected")
    cloudinary_configured: bool = Field(..., description="Whether Cloudinary is configured")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "firebase_connected": True,
                "cloudinary_configured": True
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid API key",
                "error_code": "AUTH_001"
            }
        }
