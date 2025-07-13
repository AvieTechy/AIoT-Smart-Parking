"""
FastAPI main application for Smart Parking System with Face Recognition
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import sys
import os
from typing import Optional

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.models.vggface2 import VGGFace2Model
from backend.api.schemas import FaceMatchRequest, FaceMatchResponse, RegisterResponse
from backend.utils.firebase import FirebaseService
from backend.utils.cloudinary import CloudinaryService
from backend.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
vggface_model = VGGFace2Model(model_type="auto")  # Automatically choose best available backend
firebase_service = FirebaseService()
cloudinary_service = CloudinaryService()

app = FastAPI(
    title="Smart Parking Face Recognition API",
    description="Face recognition system for smart parking management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security dependency
async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Smart Parking Face Recognition API...")
    logger.info("Loading VGGFace model...")
    await vggface_model.load_model()
    logger.info("VGGFace model loaded successfully")
    logger.info("API ready to serve requests")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Smart Parking Face Recognition API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": vggface_model.is_loaded(),
        "firebase_connected": firebase_service.is_connected(),
        "cloudinary_configured": cloudinary_service.is_configured()
    }

@app.post("/facematch", response_model=dict)
async def face_match(
    request: FaceMatchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Face matching endpoint for parking system

    Args:
        request: FaceMatchRequest containing image_url, gate, and plate_number

    Returns:
        For gate=0 (registration): {"success": bool, "message": str}
        For gate=1 (verification): {"matched": bool, "score": float}
    """
    try:
        logger.info(f"Processing face match request for plate: {request.plate_number}, gate: {request.gate}")

        # Download and process image with face detection
        image = await cloudinary_service.download_image(request.image_url)

        # Extract face embedding (includes detection, preprocessing, and embedding extraction)
        embedding = await vggface_model.process_image_with_face_detection(image)

        # Upload image as evidence
        is_registration = (request.gate == 0)
        evidence_url = await cloudinary_service.upload_evidence(
            image, request.plate_number, is_registration
        )

        if request.gate == 0:  # Registration
            # Save embedding and metadata to Firebase
            await firebase_service.save_face_data(
                plate_number=request.plate_number,
                embedding=embedding,
                image_url=evidence_url
            )

            logger.info(f"Successfully registered face for plate: {request.plate_number}")
            return {
                "success": True,
                "message": f"Face registered successfully for plate {request.plate_number}",
                "evidence_url": evidence_url
            }

        elif request.gate == 1:  # Verification
            # Retrieve stored embedding
            stored_data = await firebase_service.get_face_data(request.plate_number)

            if not stored_data:
                logger.warning(f"No face data found for plate: {request.plate_number}")
                return {
                    "matched": False,
                    "score": 0.0,
                    "message": "No registered face found for this plate number"
                }

            # Calculate similarity
            similarity_score = vggface_model.calculate_similarity(
                embedding, stored_data["embedding"]
            )

            # Update last verification image
            await firebase_service.update_last_image(
                request.plate_number, evidence_url
            )

            is_matched = similarity_score >= settings.SIMILARITY_THRESHOLD

            logger.info(f"Face verification for plate {request.plate_number}: "
                       f"matched={is_matched}, score={similarity_score:.3f}")

            return {
                "matched": is_matched,
                "score": similarity_score,
                "threshold": settings.SIMILARITY_THRESHOLD,
                "evidence_url": evidence_url
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid gate value. Must be 0 or 1")

    except Exception as e:
        logger.error(f"Error processing face match request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/face/{plate_number}")
async def get_face_info(
    plate_number: str,
    api_key: str = Depends(verify_api_key)
):
    """Get stored face information for a plate number"""
    try:
        face_data = await firebase_service.get_face_data(plate_number)
        if not face_data:
            raise HTTPException(status_code=404, detail="Face data not found")

        # Remove embedding from response for security
        response_data = {k: v for k, v in face_data.items() if k != "embedding"}
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving face info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/face/{plate_number}")
async def delete_face(
    plate_number: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete stored face data for a plate number"""
    try:
        success = await firebase_service.delete_face_data(plate_number)
        if not success:
            raise HTTPException(status_code=404, detail="Face data not found")

        return {"success": True, "message": f"Face data deleted for plate {plate_number}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting face data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
