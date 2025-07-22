from fastapi import APIRouter, UploadFile, File
from app.schemas.ocr_schemas import OCRResponse

router = APIRouter()

@router.get("/health")
def ocr_health():
    return {"status": "ok"}

@router.post("")
async def ocr_infer(file: UploadFile = File(...)):
    # TODO: Replace with actual OCR logic
    # For now, just return dummy string
    return OCRResponse(text="dummy_plate_number")
