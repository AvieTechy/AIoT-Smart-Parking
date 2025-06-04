# Kiến trúc phần mềm

Hệ thống được thiết kế bao gồm các thành phần chính: thiết bị đầu vào, phần xử lý trung tâm, và thiết bị điều khiển - phản hồi.

## Thiết bị đầu vào (Input)

- Người dùng tương tác trực tiếp với hệ thống thông qua camera.
- Camera OV2640 tích hợp trên ESP32-CAM: Ghi nhận hình ảnh đầu vào (biển số và khuôn mặt).

## Xử lý trung tâm (Processing)

- **AI Model tích hợp tại ESP32-CAM**:
  - **Nhận diện khuôn mặt**
    - **Phát hiện khuôn mặt**: Sử dụng mô hình **YOLOv6** để phát hiện vùng chứa khuôn mặt (bounding box) trong ảnh. Mô hình có tốc độ nhanh, độ chính xác cao, phù hợp xử lý ảnh thời gian thực.

    - **Nhận diện khuôn mặt**: Dựa trên các vector đặc trưng được tạo bởi mô hình **FaceNet**, so sánh với database để xác định danh tính.

  - **Nhận diện biển số xe**
    - **Phát hiện biển số xe**: Sử dụng mô hình **YOLOv8** để phát hiện vùng chứa biển số xe trong ảnh.
    - **Nhận dạng ký tự biển số**: Cắt vùng biển số từ ảnh dựa trên kết quả phát hiện, áp dụng thuật toán nhận dạng ký tự **Tesseract OCR** để trích xuất chuỗi ký tự.
  
  - ESP32-CAM gửi hình ảnh chụp được lên **Cloudinary**, nhận lại URL ảnh, gửi gói tin gồm URL ảnh và kết quả xử lý về cho ESP32 trung tâm.

- **ESP32 (vi điều khiển trung tâm)**:
  - Nhận gói tin từ ESP32-CAM.
  - Phản hồi dữ liệu về Firebase.
  - Truyền dữ liệu đến các thiết bị IoT điều khiển.

- **Backend Django**:
  - Giao tiếp với Dashboard qua API.
  - Nhận dữ liệu nhận diện từ Firebase.
  - Điều phối hoạt động của hệ thống.
  - Lưu trữ/truy xuất dữ liệu trạng thái và nhật ký hệ thống lên **Firebase**.

## Thiết bị điều khiển - phản hồi (Output)

- **Thiết bị IoT** gồm:
  - **Servo (Barrier):** mở/đóng rào chắn tự động.
  - **OLED Display:** hiển thị thông tin trực quan (số ô trống, lỗi, trạng thái...).
  - **Buzzer:** cảnh báo âm thanh cho các trạng thái khác nhau.

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

![Sơ đồ kiến trúc hệ thống](images/aiot_system.png){ width=100% .center }

## Luồng hoạt động chính của hệ thống

### Entry flow (luồng hoạt động ở cổng vào)
- ESP32-CAM_1 quét **biển số xe**.
- ESP32-CAM_2 quét **khuôn mặt tài xế**.
- Hệ thống xử lý và kiểm tra:
  - Nếu **cả hai đều nhận diện thành công**:
    - Map dữ liệu: `face_id` - `license_plate`.
    - Lưu vào cơ sở dữ liệu tạm thời.
    - Servo mở barrier cho xe vào.
    - Buzzer phát âm báo thành công.
    - Màn hình OLED hiển thị số ô trống hiện tại.
  - Nếu **không nhận diện được**:
    - Hiển thị thông báo lỗi trên màn hình OLED.
    - Buzzer phát cảnh báo nhẹ.
    - Chờ người dùng điều chỉnh vị trí xe để quét lại.

### Exit flow (luồng hoạt động ở cổng ra)
- ESP32-CAM_3 quét **biển số xe**.
- ESP32-CAM_4 quét **khuôn mặt tài xế**.
- Hệ thống kiểm tra:
  - Biển số và khuôn mặt có được nhận diện không?
  - Có khớp với dữ liệu đã lưu khi vào không?
  - Nếu **có khớp**:
    - Mở barrier cho xe ra.
    - Buzzer phát âm báo thành công.
    - Xóa dữ liệu mapping khỏi hệ thống.
    - Cập nhật số lượng ô trống trên màn hình OLED ở cổng vào.
  - Nếu **không khớp**:
    - Barrier không mở.
    - Buzzer phát âm báo nguy hiểm để cảnh báo vi phạm.
    - Màn hình OLED hiển thị thông tin lỗi.