# Kiến trúc phần mềm

Hệ thống được thiết kế dựa trên mô hình phân tầng, bao gồm các thành phần chính: thiết bị đầu vào (người dùng và camera ESP32-CAM), tầng xử lý trung tâm (AI model, ESP32 và Django backend), và tầng điều khiển - phản hồi (thiết bị IoT, Dashboard và lưu trữ).

## Thiết bị đầu vào (Input Layer)

- Người dùng (User) tương tác trực tiếp với hệ thống thông qua camera.
- **ESP32-CAM**:
  - Ghi nhận hình ảnh đầu vào (biển số hoặc khuôn mặt).
  - Gửi hình ảnh tới **mô hình AI** để xử lý nhận diện.

## Tầng xử lý trung tâm (Processing Layer)

- **AI Model (cục bộ hoặc cloud)**:
  - Tiếp nhận hình ảnh từ ESP32-CAM.
  - Thực hiện nhận diện khuôn mặt hoặc biển số xe.
  - Gửi kết quả (hoặc đường dẫn ảnh nếu có dùng Cloudinary) về cho backend.
  - Có thể tải ảnh lên **Cloudinary**, nhận lại URL ảnh phục vụ lưu trữ/hiển thị.

- **ESP32 (vi điều khiển trung gian)**:
  - Nhận kết quả xử lý từ backend Django.
  - Truyền dữ liệu đến các thiết bị IoT điều khiển.
  - Phản hồi dữ liệu cảm biến và trạng thái thiết bị về cho backend.

- **Backend Django**:
  - Giao tiếp với Dashboard qua API.
  - Nhận dữ liệu nhận diện từ AI model.
  - Điều phối hoạt động của hệ thống (mở barrier, phát âm báo, hiển thị OLED...).
  - Lưu trữ/truy xuất dữ liệu trạng thái và nhật ký hệ thống lên **Firebase**.

## Thiết bị điều khiển - phản hồi (Output Layer)

- **Thiết bị IoT** gồm:
  - **Servo (Barrier):** mở/đóng rào chắn tự động.
  - **OLED Display:** hiển thị thông tin trực quan (số ô trống, lỗi, trạng thái...).
  - **Buzzer:** cảnh báo âm thanh cho các trạng thái khác nhau.

- **Dashboard (giao diện quản trị cho Admin):**
  - Giao tiếp với backend qua API.
  - Hiển thị dữ liệu thời gian thực và lịch sử ra vào.
  - Cho phép admin giám sát toàn bộ hệ thống và các thiết bị.

## Nền tảng lưu trữ

- **Firebase**:
  - Lưu trữ dữ liệu hệ thống, nhật ký hoạt động, và thông tin người dùng.
  - Hỗ trợ đồng bộ dữ liệu và hiển thị dashboard.

- **Cloudinary**:
  - Dùng để lưu trữ ảnh chụp từ ESP32-CAM nếu cần gửi đi và truy xuất nhanh bằng URL.

Hệ thống vận hành dựa trên luồng dữ liệu: **User → ESP32-CAM → AI Model → Django Backend → ESP32 → IoT Device**, kết hợp với giao diện **Dashboard** cho quản trị và các nền tảng lưu trữ giúp theo dõi, điều khiển và phân tích hoạt động một cách hiệu quả và an toàn.

\pagebreak

![Sơ đồ kiến trúc hệ thống](images/aiot_system.png){ width=100% .center }
