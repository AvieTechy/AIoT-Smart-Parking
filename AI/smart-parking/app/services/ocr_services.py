import requests
from app.utils.config import PLATE_RECOGNIZER_API_URL, API_KEY

def recognize_license_plate(image_content: bytes, filename: str) -> dict:
    """
    Gửi ảnh đến Plate Recognizer API và trả về kết quả
    """
    if not API_KEY:
        return {
            "success": False,
            "error": "API key chưa được cấu hình. Vui lòng cập nhật file .env"
        }

    try:
        headers = {
            "Authorization": f"Token {API_KEY}"
        }
        files = {
            "upload": (filename, image_content, "image/jpeg")
        }
        response = requests.post(
            PLATE_RECOGNIZER_API_URL,
            headers=headers,
            files=files,
            timeout=30
        )
        if response.status_code in [200, 201]:
            data = response.json()
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
