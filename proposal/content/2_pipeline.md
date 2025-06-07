# Kiến trúc phần mềm

Hệ thống được thiết kế dựa trên mô hình phân tầng, bao gồm các thành phần chính: tầng thiết bị đầu vào, tầng xử lý trung tâm, và tầng điều khiển - phản hồi.

## Thiết bị đầu vào (Input Layer)

- Người dùng tương tác trực tiếp với hệ thống thông qua camera.
- Camera OV2640 tích hợp trên ESP32-CAM: Ghi nhận hình ảnh đầu vào (biển số và khuôn mặt).

## Tầng xử lý trung tâm (Processing Layer)

Tầng này chịu trách nhiệm xử lý dữ liệu từ thiết bị đầu vào, thực hiện các tác vụ trí tuệ nhân tạo và điều phối hoạt động của hệ thống.

### Các mô hình Trí tuệ Nhân tạo (AI Models)

Hệ thống sử dụng các mô hình AI chuyên biệt cho từng tác vụ, được tóm tắt trong bảng sau:

| Tác vụ AI                      | Tên mô hình sử dụng                 | Mục đích                                                              | Thiết bị triển khai |
| :----------------------------- | :----------------------------------- | :--------------------------------------------------------------------- | :------------------ |
| Phát hiện mặt người (có/không) | Ultralight-FD / Haar Cascade / TFLite model | Kiểm tra có người trong ảnh để kích hoạt chụp ảnh khuôn mặt & biển số | ESP32-CAM           |
| Phát hiện khuôn mặt            | YOLOv6 hoặc YOLOv8                   | Xác định vị trí khuôn mặt trong ảnh (bounding box)                     | Server (Django backend) |
| Nhận diện (so khớp) khuôn mặt   | FaceNet                              | Trích vector đặc trưng và so sánh với database người dùng               | Server (Django backend) |
| Phát hiện biển số xe           | YOLOv8                               | Xác định vùng chứa biển số trong ảnh                                   | Server (Django backend) |
| Nhận dạng ký tự biển số (OCR)  | Tesseract OCR                        | Trích xuất chuỗi ký tự từ vùng ảnh biển số                             | Server (Django backend) |

**Chi tiết các mô hình:**

-   **Nhận diện khuôn mặt:**
    -   **Phát hiện khuôn mặt:** Mô hình **YOLOv6** (hoặc YOLOv8) được sử dụng để xác định vùng chứa khuôn mặt (bounding box) trong ảnh. Ưu điểm của mô hình này là tốc độ nhanh và độ chính xác cao, phù hợp cho việc xử lý ảnh trong thời gian thực.
    -   **Nhận diện (so khớp) khuôn mặt:** Sau khi phát hiện, mô hình **FaceNet** được dùng để trích xuất vector đặc trưng từ khuôn mặt. Vector này sau đó được so sánh với cơ sở dữ liệu người dùng đã đăng ký để xác định danh tính.

-   **Nhận diện biển số xe:**
    -   **Phát hiện biển số xe:** Mô hình **YOLOv8** được triển khai để khoanh vùng vị trí của biển số xe trong ảnh.
    -   **Nhận dạng ký tự biển số (OCR):** Vùng ảnh chứa biển số xe sau khi được cắt ra sẽ được xử lý bởi **Tesseract OCR** để trích xuất chuỗi ký tự trên biển số.

### Luồng xử lý dữ liệu và các thành phần khác

1.  **ESP32-CAM (Thiết bị ghi nhận):**
    -   Chụp ảnh đầu vào.
    -   Thực hiện tác vụ phát hiện có người trong ảnh (sử dụng Ultralight-FD/Haar Cascade/TFLite model).
    -   Nếu phát hiện có người, ESP32-CAM gửi hình ảnh đã chụp lên **Cloudinary**.
    -   Nhận lại URL của ảnh từ Cloudinary.
    -   Gửi gói tin chứa URL ảnh này đến ESP32 trung tâm.

2.  **Server (Django Backend):**
    -   Nhận yêu cầu xử lý ảnh (thông qua URL từ Cloudinary) từ ESP32 trung tâm hoặc trực tiếp từ các luồng khác.
    -   Thực hiện các tác vụ AI nặng:
        -   Phát hiện khuôn mặt (YOLOv6/YOLOv8).
        -   Nhận diện khuôn mặt (FaceNet).
        -   Phát hiện biển số xe (YOLOv8).
        -   Nhận dạng ký tự biển số (Tesseract OCR).
    -   Gửi kết quả nhận diện (danh tính, biển số xe) về cho ESP32 trung tâm và lưu trữ vào **Firebase**.
    -   Cung cấp API cho Dashboard quản trị để theo dõi và quản lý hệ thống.
    -   Lưu trữ/truy xuất dữ liệu trạng thái và nhật ký hệ thống lên **Firebase**.

3.  **ESP32 (Vi điều khiển trung tâm):**
    -   Nhận gói tin (URL ảnh) từ ESP32-CAM.
    -   Yêu cầu Server xử lý ảnh và nhận kết quả nhận diện.
    -   Gửi kết quả xử lý (ví dụ: thông tin người dùng, trạng thái hợp lệ/không hợp lệ) lên **Firebase**.
    -   Truyền tín hiệu điều khiển đến các thiết bị IoT ở tầng Output (ví dụ: mở barrier, hiển thị thông tin lên OLED).

## Thiết bị điều khiển - phản hồi (Output Layer)

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

![Sơ đồ kiến trúc hệ thống](images/aiot_system.png){ width=100% .center }

\pagebreak
