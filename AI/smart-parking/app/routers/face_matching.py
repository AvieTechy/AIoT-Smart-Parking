from fastapi import APIRouter, HTTPException
from app.schemas.face_matching_schemas import FaceMatchingRequest, FaceMatchResponse
from app.services.face_matching_services import checking_matching

router = APIRouter(
    tags=["Face Matching"]
)

@router.get("/health")
def face_matching_health():
    return {"status": "ok"}

@router.post("/", response_model=bool)
def check_face_matching(request: FaceMatchingRequest):
    try:
        
        # Gọi đúng tham số cho checking_matching
        result = checking_matching(request.image1_path, request.image2_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
