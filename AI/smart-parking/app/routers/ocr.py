from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.ocr_schemas import OCRResponse
from app.services.ocr_services import recognize_license_plate
import requests

router = APIRouter()

class OCRUrlRequest(BaseModel):
    url: str

@router.get("/health")
def ocr_health():
    return {"status": "ok"}

@router.post("/")
async def ocr_infer(request: OCRUrlRequest):
    url = request.url
    print(f"[OCR] Nhận url: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        contents = response.content
        filename = url.split("/")[-1]
        print(f"[OCR] Tải ảnh thành công: {filename}, size: {len(contents)} bytes")
    except Exception as e:
        print(f"[OCR] Lỗi tải ảnh: {e}")
        return OCRResponse(status=False, plate=f"Lỗi tải ảnh: {e}")

    result = recognize_license_plate(contents, filename)
    if result["success"]:
        plate = result["plates"][0]["plate"] if result["plates"] else ""
        return OCRResponse(status=True, plate=plate)
    else:
        return OCRResponse(status=False, plate=result["error"])
