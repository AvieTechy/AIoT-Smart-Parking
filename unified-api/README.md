# Unified FastAPI Server

## Mục đích
Gộp 2 backend FastAPI (face-matching-api và number-plate-ocr-api) thành một server duy nhất, gọi nội bộ qua httpx.

## Cấu trúc API

### 1. POST /face-matching
- Input:
```json
{
  "url": "https://domain.com/image.jpg",
  "gate": "in"
}
```
- Output:
```json
{
  "match": true
}
```

### 2. POST /plate-ocr
- Input:
```json
{
  "url": "https://domain.com/image.jpg"
}
```
- Output:
```json
{
  "plate": "51G12345"
}
```

## Cài đặt
```bash
cd unified-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Chạy server
```bash
uvicorn main:app --reload --port 8000
```

## Cấu hình địa chỉ backend cũ
- Sửa các biến `FACE_MATCHING_API_URL` và `PLATE_OCR_API_URL` trong `main.py` cho đúng địa chỉ thực tế của 2 backend cũ.

## Test API

### Test nhận diện khuôn mặt
```bash
curl -X POST http://localhost:8000/face-matching \
  -H "Content-Type: application/json" \
  -d '{"url": "https://domain.com/image.jpg", "gate": "in"}'
```

### Test nhận diện biển số
```bash
curl -X POST http://localhost:8000/plate-ocr \
  -H "Content-Type: application/json" \
  -d '{"url": "https://domain.com/image.jpg"}'
```
