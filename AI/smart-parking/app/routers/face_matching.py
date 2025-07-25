from fastapi import APIRouter, HTTPException
from app.schemas.face_matching_schemas import FaceMatchingRequest, FaceMatchResponse
from app.services.face_matching_services import checking_matching

router = APIRouter(
    tags=["Face Matching"]
)

@router.get("/health")
def face_matching_health():
    return {"status": "ok"}

@router.post("/", response_model=FaceMatchResponse)
def check_face_matching(request: FaceMatchingRequest):
    try:
        
        # Gọi đúng tham số cho checking_matching
        result = checking_matching(request.image1_path, request.image2_path)
        return FaceMatchResponse(matched=result["matched"], confidence=result["confidence"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
