from fastapi import APIRouter, File, UploadFile
import cloudinary.uploader
import cloudinary
from fastapi.responses import JSONResponse

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name="dc3jq3pit",
    api_key="865864472685123",
    api_secret="uPDfAdjii4RCN-FKR9woTH0UAK4"
)

router = APIRouter(
    tags=["Post Cloud"]
)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Upload file lên Cloudinary
        response = cloudinary.uploader.upload(file.file, resource_type="auto")
        
        # Trả về URL của file đã upload
        return JSONResponse(content={"url": response["secure_url"]})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

