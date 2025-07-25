# Kiến trúc phần mềm

Hệ thống được thiết kế dựa trên mô hình phân tầng, bao gồm các thành phần chính: tầng thiết bị đầu vào, tầng xử lý trung tâm, và tầng điều khiển - phản hồi.


![Sơ đồ kiến trúc hệ thống](images/aiot_system.png){ width=100% .center }

## Thiết bị đầu vào (Input Layer)

- Người dùng tương tác trực tiếp với hệ thống thông qua camera.
- Camera OV2640 tích hợp trên ESP32-CAM: Ghi nhận hình ảnh đầu vào (biển số và khuôn mặt).

## Tầng xử lý trung tâm (Processing Layer)

Tầng này chịu trách nhiệm xử lý dữ liệu từ thiết bị đầu vào, thực hiện các tác vụ trí tuệ nhân tạo và điều phối hoạt động của hệ thống.

### Các mô hình Trí tuệ Nhân tạo (AI Models)

Hệ thống sử dụng các mô hình AI chuyên biệt cho từng tác vụ, được tóm tắt trong bảng sau:

| Tác vụ AI                               | Mô hình / API sử dụng                               | Mục đích                                                                 | Thiết bị triển khai                     |
| :-------------------------------------- | :-------------------------------------------------- | :---------------------------------------------------------------------- | :-------------------------------------- |
| Phát hiện khuôn mặt (có/không + bounding box) | MTMN – mô hình nhúng do ESP-FACE cung cấp | Xác định có khuôn mặt trong ảnh và trả về bounding box để chụp ảnh       | ESP32-CAM (chạy trực tiếp trên thiết bị) |
| Nhận diện khuôn mặt (face matching)      | Deepface                                       | Tự động trích xuất vector đặc trưng và so khớp với cơ sở dữ liệu người dùng      | Server                 |
| Nhận dạng ký tự biển số (OCR)           | Plate Recognizer API (REST API)                     | Gửi ảnh biển số lên server API và nhận lại chuỗi ký tự đã nhận dạng | Server                 |

Hệ thống áp dụng các mô hình AI nhẹ, phù hợp với thiết bị nhúng và backend, để thực hiện hai nhiệm vụ chính: nhận diện khuôn mặt và nhận dạng biển số xe. Cụ thể:

-   **Phát hiện khuôn mặt:**
    Mô hình MTMN từ ESP-FACE được chạy trực tiếp trên ESP32-CAM. Mô hình này có khả năng phát hiện nhanh khuôn mặt và trả về bounding box, giúp thiết bị xác định thời điểm chụp và gửi ảnh về server.
-   **Nhận diện khuôn mặt:**
    Server sử dụng mô hình MobileFaceNet để trích xuất vector đặc trưng từ ảnh khuôn mặt và so sánh với cơ sở dữ liệu người dùng đã đăng ký.
-   **Nhận dạng biển số xe:**
    Hệ thống sử dụng Plate Recognizer API để nhận diện chuỗi ký tự từ ảnh biển số xe. Ảnh được gửi từ server lên API và trả về kết quả nhận dạng dưới dạng văn bản.

### Luồng xử lý dữ liệu và các thành phần chính

1.  **ESP32-CAM (Thiết bị ghi nhận hình ảnh):**
    *   Chụp ảnh từ camera tích hợp.
    *   Chạy mô hình `face_detection` (ESP-WHO) để kiểm tra có khuôn mặt hay không.
    *   Nếu có mặt người, ảnh sẽ được gửi lên Cloudinary, sau đó nhận lại URL ảnh.
    *   Gửi gói dữ liệu chứa URL ảnh và metadata (thời gian, loại ảnh, thiết bị…) lên Firebase.
2.  **Server Backend (FastAPI):**
    *   Theo dõi hoặc được kích hoạt từ sự kiện mới trên Firebase.
    *   Đọc URL ảnh từ Firebase và tiến hành xử lý:
        *   **MobileFaceNet:** trích xuất embedding và xác định danh tính người dùng.
        *   **Plate Recognizer API:** nhận diện chuỗi ký tự biển số xe từ ảnh.
    *   Ghi kết quả trả về vào Firebase: gồm thông tin người dùng, biển số xe, trạng thái xác minh (hợp lệ/không hợp lệ), thời gian xử lý, v.v.
3.  **ESP32 (Thiết bị điều phối trung tâm):**
    *   Theo dõi kết quả từ Firebase.
    *   Khi có kết quả tương ứng với ảnh mình đã gửi, ESP32:
        *   Truy xuất kết quả nhận diện.
        *   Điều khiển thiết bị đầu ra (mở barrier, hiển thị OLED, còi, v.v.).
        *   Ghi lại trạng thái hoạt động (đã xử lý xong) nếu cần.
4.  **Dashboard quản trị (ReactJS):**
    *   Lấy dữ liệu trực tiếp từ Firebase để hiển thị:
        *   Danh sách người vào/ra
        *   Ảnh chụp, biển số, thời gian
        *   Lịch sử, trạng thái, báo cáo thống kê

## Thiết bị điều khiển - phản hồi (Output Layer)

- **Thiết bị IoT** gồm:
  - **Servo (Barrier):** mở/đóng rào chắn tự động.
  - **OLED Display:** hiển thị thông tin trực quan (số ô trống, lỗi, trạng thái...).

- **Dashboard (giao diện quản trị cho Admin):**
  - Sử dụng các công nghệ phổ biến HTML, CSS, JavaScript để xây dựng giao diện thân thiện, dễ sử dụng.
  - Giao tiếp với backend qua API.
  - Hiển thị dữ liệu thời gian thực và lịch sử ra vào.
  - Cho phép admin giám sát toàn bộ hệ thống và các thiết bị.

## Nền tảng lưu trữ

- **Firebase**:
  - Lưu trữ dữ liệu hệ thống, nhật ký hoạt động, và thông tin người dùng.
  - Hỗ trợ đồng bộ dữ liệu và hiển thị dashboard.

- **Cloudinary**:
  - Dùng để lưu trữ ảnh chụp từ ESP32-CAM gửi đến và truy xuất nhanh bằng URL.

\pagebreak
