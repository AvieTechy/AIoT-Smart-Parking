from fastapi import FastAPI
from app.routers.face_matching import router as face_matching_router
from app.routers.ocr import router as ocr_router

app = FastAPI()

# Chỉ include tags, KHÔNG include prefix (prefix đã nằm trong router)
app.include_router(face_matching_router, tags=["Face Matching"])
app.include_router(ocr_router, tags=["OCR"])

@app.get("/")
def read_root():
    return {"message": "Smart Parking API is running"}
