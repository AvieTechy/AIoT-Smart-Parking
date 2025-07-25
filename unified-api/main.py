from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

# Địa chỉ 2 backend cũ (cần sửa lại cho đúng IP/port thực tế)
FACE_MATCHING_API_URL = "http://localhost:8001/match-face"
PLATE_OCR_API_URL = "http://localhost:8002/ocr"

class FaceMatchingRequest(BaseModel):
    url: str
    gate: str

class PlateOCRRequest(BaseModel):
    url: str

@app.post("/face-matching")
async def face_matching(req: FaceMatchingRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                FACE_MATCHING_API_URL,
                json={"url": req.url, "gate": req.gate}
            )
            response.raise_for_status()
            data = response.json()
            # Giả sử backend trả về {'match': true/false}
            return {"match": data.get("match", False)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Face-matching API error: {e}")

@app.post("/plate-ocr")
async def plate_ocr(req: PlateOCRRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                PLATE_OCR_API_URL,
                json={"url": req.url}
            )
            response.raise_for_status()
            data = response.json()
            # Giả sử backend trả về {'plate': 'string'}
            return {"plate": data.get("plate", "")}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Plate-OCR API error: {e}")
