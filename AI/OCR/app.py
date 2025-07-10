from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import os
from dotenv import load_dotenv
import tempfile
import json
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI(title="License Plate Recognition", description="Ứng dụng nhận diện biển số xe")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Plate Recognizer API configuration
PLATE_RECOGNIZER_API_URL = "https://api.platerecognizer.com/v1/plate-reader/"
API_KEY = os.getenv("PLATE_RECOGNIZER_API_KEY")

if not API_KEY or API_KEY == "YOUR_API_KEY":
    print("WARNING: Vui lòng cập nhật API key trong file .env")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Trang chủ với form upload ảnh"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...)):
    """
    Upload ảnh và nhận diện biển số xe
    """
    # Kiểm tra loại file
    if not file.content_type.startswith("image/"):
        return templates.TemplateResponse("result.html", {
            "request": request,
            "error": "Vui lòng upload file ảnh hợp lệ (jpg, png, etc.)"
        })

    try:
        # Đọc nội dung file
        image_content = await file.read()

        # Gửi request đến Plate Recognizer API
        result = await recognize_license_plate(image_content, file.filename)

        if result["success"]:
            return templates.TemplateResponse("result.html", {
                "request": request,
                "success": True,
                "plates": result["plates"],
                "filename": file.filename
            })
        else:
            return templates.TemplateResponse("result.html", {
                "request": request,
                "error": result["error"]
            })

    except Exception as e:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "error": f"Lỗi xử lý ảnh: {str(e)}"
        })

async def recognize_license_plate(image_content: bytes, filename: str) -> dict:
    """
    Gửi ảnh đến Plate Recognizer API và trả về kết quả
    """
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        return {
            "success": False,
            "error": "API key chưa được cấu hình. Vui lòng cập nhật file .env"
        }

    try:
        # Chuẩn bị headers
        headers = {
            "Authorization": f"Token {API_KEY}"
        }

        # Chuẩn bị files để upload
        files = {
            "upload": (filename, image_content, "image/jpeg")
        }

        # Gửi request đến API
        response = requests.post(
            PLATE_RECOGNIZER_API_URL,
            headers=headers,
            files=files,
            timeout=30
        )

        # API trả về 200 hoặc 201 khi thành công
        if response.status_code in [200, 201]:
            data = response.json()

            # Trích xuất thông tin biển số
            plates = []
            if "results" in data and data["results"]:
                for result in data["results"]:
                    if "plate" in result:
                        plates.append({
                            "plate": result["plate"],
                            "confidence": result.get("score", 0) * 100,
                            "region": result.get("region", {}).get("code", "Unknown")
                        })

            if plates:
                return {
                    "success": True,
                    "plates": plates
                }
            else:
                return {
                    "success": False,
                    "error": "Không phát hiện được biển số xe trong ảnh"
                }

        elif response.status_code == 401:
            return {
                "success": False,
                "error": "API key không hợp lệ. Vui lòng kiểm tra lại."
            }
        elif response.status_code == 403:
            return {
                "success": False,
                "error": "Hết quota API hoặc không có quyền truy cập."
            }
        else:
            # Debug: In ra thông tin response để kiểm tra
            try:
                error_data = response.json()
                return {
                    "success": False,
                    "error": f"Lỗi API: {response.status_code} - Response: {error_data}"
                }
            except:
                return {
                    "success": False,
                    "error": f"Lỗi API: {response.status_code} - {response.text}"
                }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout khi gọi API. Vui lòng thử lại."
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Lỗi kết nối API: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Lỗi không xác định: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "License Plate Recognition"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
