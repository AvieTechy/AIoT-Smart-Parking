# Ứng dụng Nhận diện Biển số Xe

Ứng dụng FastAPI đơn giản để nhận diện biển số xe sử dụng Plate Recognizer API.

## Tính năng

- Upload ảnh qua giao diện web đơn giản
- Nhận diện biển số xe tự động
- Hiển thị kết quả với độ tin cậy
- Giao diện đẹp và responsive
- Hỗ trợ drag & drop
- Xử lý lỗi toàn diện

## Cài đặt

### 1. Kích hoạt môi trường conda và cài đặt dependencies

```bash
conda activate ocr
pip install -r requirements.txt
```

### 2. Cấu hình API Key

1. Đăng ký tài khoản tại [Plate Recognizer](https://app.platerecognizer.com/)
2. Lấy API key từ dashboard
3. Cập nhật file `.env`:

```env
PLATE_RECOGNIZER_API_KEY=your_actual_api_key_here
```

### 3. Chạy ứng dụng

```bash
conda activate ocr
uvicorn app:app --reload
```

Hoặc:

```bash
conda activate ocr
python app.py
```

## Sử dụng

1. Mở trình duyệt và truy cập: http://localhost:8000
2. Upload ảnh biển số xe (JPG, PNG, GIF)
3. Nhấn "Nhận diện biển số"
4. Xem kết quả

## API Endpoints

- `GET /` - Trang chủ với form upload
- `POST /upload` - Upload và nhận diện ảnh
- `GET /health` - Health check

## Cấu trúc project

```
OCR/
├── app.py                 # Ứng dụng FastAPI chính
├── requirements.txt       # Dependencies
├── .env                  # Cấu hình API key
├── README.md             # Hướng dẫn này
└── templates/
    ├── index.html        # Trang upload
    └── result.html       # Trang kết quả
```

## Lưu ý

- API key của Plate Recognizer có giới hạn request miễn phí
- Ảnh nên có biển số rõ ràng để đạt độ chính xác cao
- Ứng dụng hỗ trợ nhiều biển số trong một ảnh

## Demo

1. **Trang upload:**
   - Giao diện đẹp với drag & drop
   - Hiển thị tên file đã chọn
   - Validation file ảnh

2. **Trang kết quả:**
   - Hiển thị biển số đã nhận diện
   - Độ tin cậy (confidence score)
   - Thông tin khu vực (nếu có)
   - Nút quay lại để thử ảnh khác

## Troubleshooting

### Lỗi API Key
- Kiểm tra API key trong file `.env`
- Đảm bảo API key còn hiệu lực
- Kiểm tra quota của tài khoản

### Lỗi không nhận diện được
- Ảnh quá mờ hoặc biển số không rõ
- Góc chụp quá nghiêng
- Biển số bị che khuất

### Lỗi kết nối
- Kiểm tra kết nối internet
- API Plate Recognizer có thể bị downtime

## License

MIT License
