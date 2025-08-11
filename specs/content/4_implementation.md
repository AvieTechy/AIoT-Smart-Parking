# Triển khai và Công Nghệ Sử dụng

![Prototype mô hình toàn bộ hệ thống](prototype){width=80%}

## Quy trình triển khai

Hệ thống được triển khai theo quy trình có hệ thống gồm bốn giai đoạn chính:

| Giai đoạn | Tên giai đoạn | Mô tả |
|:---:|:---------|:---------------------|
| 1 | Lắp đặt phần cứng | Camera ESP32-CAM được bố trí tại các điểm lối vào và lối ra. ESP32 trung tâm điều khiển barrier được kết nối với màn hình LCD và servo. |
| 2 | Cài đặt firmware cho ESP32-CAM | Firmware được tích hợp mô hình MTMN (ESP-FACE) để thực hiện phát hiện khuôn mặt trực tiếp trên thiết bị. Hệ thống được cấu hình để upload ảnh lên Cloudinary thông qua REST API và gửi URL ảnh cùng metadata đến ESP32 trung tâm. |
| 3 | Cấu hình ESP32 trung tâm | ESP32 trung tâm nhận URL ảnh từ camera và thực hiện gọi API đến các mô hình AI đã được deploy trên server để nhận diện khuôn mặt và biển số xe. Kết quả xử lý được lưu trữ vào Firebase cho việc truy xuất và phân tích. |
| 4 | Triển khai Dashboard | Giao diện Dashboard được phát triển bằng ReactJS, kết nối trực tiếp với Firebase để hiển thị dữ liệu thời gian thực, thống kê hoạt động và lịch sử ra vào của hệ thống. |

## Công nghệ sử dụng

| Thành phần                  | Công nghệ / Công cụ        | Mục đích                                           |
| --------------------------- | -------------------------- | -------------------------------------------------- |
| **Thiết bị nhúng**          | ESP32-CAM, ESP32 DevKit V1 | Chụp ảnh, điều khiển barrier, giao tiếp với server |
| **Phát hiện khuôn mặt**     | MTMN – ESP-FACE            | Xác định vị trí khuôn mặt trên ảnh                 |
| **Nhận diện khuôn mặt**     | FaceNet                    | So khớp với cơ sở dữ liệu người dùng               |
| **Nhận dạng biển số (OCR)** | Plate Recognizer API       | Trích xuất ký tự từ ảnh biển số                    |
| **Backend**                 | FastAPI (Python)           | Xử lý API, gọi AI model, quản lý logic hệ thống    |
| **Cloud Storage**           | Cloudinary                 | Lưu trữ ảnh, trả về URL                            |
| **Database**       | Firestore DB       | Lưu trữ kết quả nhận diện, đồng bộ dữ liệu         |
| **Dashboard**               | ReactJS                    | Hiển thị dữ liệu và giám sát                       |
| **Giao tiếp**               | HTTP REST, TCP/IP            | Truyền dữ liệu và điều khiển thời gian thực        |

\pagebreak
