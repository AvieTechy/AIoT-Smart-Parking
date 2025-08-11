# Smart Parking System – AIoT-based

## Giới thiệu
Smart Parking System là mô hình bãi đỗ xe thông minh ứng dụng AIoT để:
- Tự động nhận diện biển số xe và khuôn mặt tài xế
- Quản lý trạng thái chỗ đỗ theo thời gian thực
- Giảm thao tác thủ công và tối ưu trải nghiệm

Mô hình hướng tới quy mô nhỏ (5–10 chỗ) và có thể mở rộng triển khai thực tế.

---

## Tính năng chính
- Nhận diện khuôn mặt (Face Recognition) độ chính xác ≥ 90% (ban ngày)
- Nhận dạng biển số (License Plate Recognition) qua API
- Cập nhật trạng thái slot gần thời gian thực
- Điều khiển barrier tự động (servo) khi hợp lệ
- Hiển thị thông tin qua LCD 16×2
- Dashboard (ReactJS) kết nối Firebase:
    - Lịch sử vào/ra
    - Ảnh, biển số, timestamp
    - Thống kê

---

## Kiến trúc hệ thống
3 tầng chính:

1. Input Layer
     - ESP32-CAM chụp ảnh biển số & khuôn mặt
     - MTMN (ESP-FACE) phát hiện khuôn mặt on-device

2. Processing Layer
     - ESP32 trung tâm điều phối
     - API: FaceNet (nhận diện), Plate Recognizer (biển số)
     - Lưu dữ liệu Firebase

3. Output Layer
     - Servo SG90 (barrier)
     - LCD 16×2
     - Dashboard web

---

## Công nghệ & Linh kiện

Phần cứng:
- 2× AI Thinker ESP32-CAM (OV2640)
- 1× ESP32 DevKit V1
- LCD 16×2 (I2C)
- Servo SG90
- Breadboard, dây jumper, nguồn 5V–3A, đế nạp ESP32-CAM

Phần mềm:
- Firmware: Arduino IDE + ESP-FACE (MTMN)
- Backend: FastAPI (Python)
- AI:
    - Face Detection: MTMN
    - Face Recognition: FaceNet
    - Plate OCR: Plate Recognizer API
- Cloud Storage: Cloudinary
- Realtime Database: Firebase Realtime Database
- Frontend: ReactJS
- Giao tiếp: HTTP REST, MQTT

---

## Kiểm thử & Đánh giá
- Độ chính xác khuôn mặt: ≥ 90% (ban ngày)
- Độ chính xác biển số: theo tiêu chuẩn API
- Thời gian xử lý lượt vào/ra: ≤ 15s
- Cập nhật trạng thái slot: ≤ 5s

---

## Nhóm phát triển
| Thành viên        | Vai trò                | Nhiệm vụ                               |
|-------------------|------------------------|----------------------------------------|
| Cao Uyển Nhi      | Trưởng nhóm, AI        | Phát triển & tích hợp AI models        |
| Trần Thị Cát Tường| Phần cứng trung tâm    | Mạch điều khiển, servo, cloud          |
| Lưu Thanh Thuý    | ESP32-CAM              | Face detection, giao tiếp module       |
| Võ Lê Việt Tú     | Backend & Dashboard    | Kết nối backend–hardware, UI/UX        |
