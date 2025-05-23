# Công nghệ

## Công nghệ sử dụng

### Hệ thống phần cứng

- **Camera ESP32-CAM**

  - Sử dụng 2 module ESP32-CAM tại mỗi cổng (vào và ra), một camera chụp khuôn mặt tài xế, một camera chụp biển số xe.
  - ESP32-CAM sẽ **đợi tín hiệu từ nút bấm** để chụp, sau đó gửi ảnh lên server qua kết nối Wi-Fi.

- **Board điều khiển trung tâm ESP32**

  - Một board ESP32 dùng để điều khiển các thiết bị ngoại vi như màn hình OLED hiển thị thông tin hướng dẫn tài xế và nhận tín hiệu nút bấm từ người dùng.
  - Board giao tiếp không dây qua Wi-Fi với các ESP32-CAM để điều phối hoạt động chung như ra lệnh chụp ảnh, nhận dữ liệu, điều khiển barrier.
  - Ngoài ra, board điều khiển relay để đóng/mở thanh chắn barrier tự động khi nhận diện thành công.

- **Màn hình OLED**

  - Màn hình OLED nhỏ gọn được kết nối với board ESP32 trung tâm để hiển thị thông tin trực quan như số ô đỗ được phân, trạng thái chỗ đỗ, hoặc các thông báo hướng dẫn cho tài xế.
  - OLED phù hợp để hiển thị đồ họa đơn giản, tiết kiệm năng lượng, dễ dàng kết nối qua giao tiếp I2C hoặc SPI.

- **Nút bấm**

  - Nút bấm được gắn với board ESP32 điều khiển trung tâm, cho phép người dùng nhấn khi đã đứng đúng vị trí chờ quét để kích hoạt camera.

- **Servo motor**

  - Servo motor được điều khiển bởi board ESP32 trung tâm.
  - Servo sẽ quay mở hoặc đóng khi hệ thống xác nhận thành công khuôn mặt hoặc biển số xe hợp lệ, đảm bảo an ninh và quản lý xe ra/vào chính xác.

- **Cảm biến siêu âm HC-SR04**

  - Cảm biến siêu âm HC-SR04 được lắp tại các vị trí đỗ xe để xác định xem ô đó đang có xe đậu hay trống. 
  - Cảm biến hoạt động bằng cách phát sóng siêu âm từ đó tính khoảng cách đến vật thể phía trước. Nếu khoảng cách nhỏ hơn ngưỡng định sẵn, hệ thống sẽ xác định ô đã có vật thể chiếm.

### Ứng dụng AI phân tích hình ảnh

- **Nhận diện khuôn mặt**
    - **Phát hiện khuôn mặt**: Sử dụng mô hình **YOLOv6** để phát hiện vùng chứa khuôn mặt (bounding box) trong ảnh. Mô hình có tốc độ nhanh, độ chính xác cao, phù hợp xử lý ảnh thời gian thực.

    - **Nhận diện khuôn mặt**: Dựa trên các vector đặc trưng được tạo bởi mô hình **FaceNet**, so sánh với database để xác định danh tính.


- **Nhận diện biển số xe**
    - **Phát hiện biển số xe**: Sử dụng mô hình **YOLOv8** để phát hiện vùng chứa biển số xe trong ảnh.
    - **Nhận dạng ký tự biển số**: Cắt vùng biển số từ ảnh dựa trên kết quả phát hiện, áp dụng thuật toán nhận dạng ký tự **Tesseract OCR** để trích xuất chuỗi ký tự.

### Giao diện người dùng và quản trị

- **Frontend:**
Sử dụng các công nghệ phổ biến HTML, CSS, JavaScript để xây dựng giao diện thân thiện, dễ sử dụng cho tài xế và quản trị viên.

- **Backend:**
Sử dụng Django làm framework backend, xử lý các logic nghiệp vụ như xác thực người dùng, quản lý dữ liệu xe và vị trí bãi đỗ, cung cấp API cho frontend và thiết bị IoT kết nối.

### Kết nối và nền tảng lưu trữ

- **MQTT (Message Queuing Telemetry Transport):**
Giao thức truyền thông nhẹ, tối ưu cho các thiết bị IoT với băng thông hạn chế. MQTT hỗ trợ kết nối ổn định, truyền dữ liệu theo dạng publish-subscribe, rất phù hợp để truyền trạng thái cảm biến, điều khiển thiết bị trong hệ thống bãi đỗ xe thông minh.

- **MongoDB:**
Cơ sở dữ liệu NoSQL dạng tài liệu, linh hoạt trong việc lưu trữ dữ liệu phi cấu trúc như log hệ thống, dữ liệu người dùng, thông tin xe, hình ảnh. Được sử dụng phổ biến trong các hệ thống backend nhờ khả năng mở rộng và thao tác linh hoạt với dữ liệu JSON.

## Thiết bị

| STT | Tên thiết bị              | Số lượng | Giá tiền | Hình ảnh                                  | Nguồn                                                                 |
|-------|--------------------------------------|-------------------|-----------------------|----------------------------------------|-------------------------------------------|
| 1   | Camera ESP32-CAM          | 4        | 269,000        | ![](images/ESP32-CAM.jpg)                 | [Xem tại đây](https://chotroihn.vn/module-wifi-esp32-cam-ov2640-bluetooth) |
| 2   | Board điều khiển ESP32    | 2        | 170,000        | ![](images/ESP32.jpg)                      | [Xem tại đây](https://hshop.vn/mach-mtiny-esp32-wrover-ie-arduino-compatible) |
| 3   | Màn hình OLED 0.96 inch    | 2        | 105,000        | ![](images/OLED.jpg)                       | [Xem tại đây](https://chotroihn.vn/man-hinh-oled-v2-0-96-inch-stm32)  |
| 4   | Nút bấm                   | 2        | 4,000          | ![](images/BUTTON.jpg)                     | [Xem tại đây](https://hshop.vn/mach-1-nut-nhan-tact-switch-6x6mm)    |
| 5   | Servo motor MG90S          | 2        | 39,000         | ![](images/SERVO.jpg)                      | [Xem tại đây](https://chotroihn.vn/dong-co-servo-mg90s)              |
| 6   | Cảm biến siêu âm HC-SR04  | Theo số ô đỗ | 20,000        | ![](images/HCSR04.jpg)                     | [Xem tại đây](https://hshop.vn/cam-bien-sieu-am-srf04)               |
| 7   | Dây dẫn                   | Theo nhu cầu | 8,000          | ![](images/WIRE.jpg)                       | [Xem tại đây](https://chotroihn.vn/day-noi-7-mau-30cm-day-cam-testboard) |
