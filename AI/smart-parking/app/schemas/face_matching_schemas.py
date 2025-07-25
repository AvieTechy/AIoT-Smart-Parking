from pydantic import BaseModel

class FaceMatchingRequest(BaseModel):
    image1_path: str
    image2_path: str

class FaceMatchResponse(BaseModel):
    matched: bool
    confidence: float
