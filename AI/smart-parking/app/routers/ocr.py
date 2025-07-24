from fastapi import APIRouter, UploadFile, File
from app.schemas.ocr_schemas import OCRResponse
from app.services.ocr_services import recognize_license_plate
router = APIRouter()

@router.get("/health")
def ocr_health():
    return {"status": "ok"}

@router.post("/")
async def ocr_infer(file: UploadFile = File(...)):
    contents = await file.read()
    print(f"[OCR] Nhận file: {file.filename}, size: {len(contents)} bytes")

    result = recognize_license_plate(contents, file.filename)
    if result["success"]:
        plate = result["plates"][0]["plate"] if result["plates"] else ""
        return OCRResponse(status=True, plate=plate)
    else:
        return OCRResponse(status=False, plate=result["error"])
