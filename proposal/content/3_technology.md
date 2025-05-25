# Công nghệ

## Công nghệ sử dụng

### Hệ thống phần cứng

- **Camera ESP32-CAM (AI Thinker ESP32-CAM)**

  - Sử dụng **2 module ESP32-CAM** cho mỗi cổng (vào và ra):
    - Một module quét và nhận diện khuôn mặt tài xế
    - Một module quét và nhận diện biển số xe
    
  - Mỗi ESP32-CAM hoạt động độc lập, được nạp sẵn chương trình với khả năng:
    - Nhận diện sự xuất hiện của xe
    - Tự động chụp ảnh
    - Thực hiện nhận diện khuôn mặt hoặc biển số trực tiếp trên thiết bị
    - Gửi kết quả nhận diện và ảnh lên server thông qua kết nối Wi-Fi

- **ESP32 trung tâm (ESP32 DevKit V1)**

  - Là bộ điều khiển chính của toàn hệ thống, sử dụng chip ESP32-WROOM-32, tích hợp lõi xử lý kép 32-bit, hỗ trợ kết nối Wi-Fi và Bluetooth, và hoạt động ở mức điện áp logic 3.3V.
  - Board có sẵn chip USB-to-Serial CP2102 cho phép nạp code trực tiếp qua cổng USB-C mà không cần phần cứng nạp ngoài.

    - **Giao tiếp với các ESP32-CAM** qua Wi-Fi (MQTT/HTTP)
    - Nhận kết quả nhận diện (khuôn mặt hoặc biển số) từ các ESP32-CAM đã xử lý xong
    - Điều khiển các thiết bị ngoại vi:
      - Mở/đóng barrier qua servo motor
      - Hiển thị trạng thái lên màn hình OLED
      - Phát âm báo thành công hoặc lỗi qua buzzer
    
  - Board này có đủ chân GPIO để kết nối đồng thời servo, buzzer, OLED

- **Màn hình OLED**

  - Là màn hình đơn sắc kích thước 0.96 inch, giao tiếp bằng chuẩn **I2C (SDA, SCL)** với ESP32 trung tâm (thường là GPIO21 và GPIO22).
  - Có chức năng hiển thị:
    - Khi xe vào: Hiển thị số chỗ còn trống, hoặc báo "đã hết chỗ" nếu không còn slot đỗ
    - Khi xe ra: Hiển thị lời chào hoặc hiển thị lỗi nếu quá trình nhận diện không hợp lệ

- **Servo motor MG90S**

  - Loại servo có mô-men mạnh hơn SG90, sử dụng điện áp 5V.
  - Được điều khiển bằng tín hiệu PWM từ ESP32 trung tâm
  - Nối VCC và GND vào breadboard (nguồn từ MB102) để tránh sụt áp hoặc reset mạch.
  - Dùng để mở hoặc đóng barrier khi xác thực thành công.

- **Buzzer**

  - Sử dụng 2 buzzer loại Active 5V, mỗi chiếc được điều khiển bởi ESP32 trung tâm thông qua chân GPIO.
  - **Active buzzer** là loại có sẵn mạch dao động bên trong, chỉ cần cấp tín hiệu HIGH/LOW là phát tiếng (dễ dùng hơn loại passive).
  - ESP32 điều khiển 2 buzzer để:

    - **Báo hiệu thành công** khi xe được nhận diện và barrier mở
    - **Báo lỗi hoặc cảnh báo** khi khuôn mặt/biển số không hợp lệ

- **MB102 Breadboard Power Supply Module**

  - Dùng để **cấp nguồn 5V ổn định cho toàn bộ hệ thống** từ laptop (USB).
  - Hỗ trợ cấp nguồn thông qua cổng USB-A hoặc microUSB 
  - Có thể chọn mức điện áp đầu ra là 5V hoặc 3.3V tùy theo loại thiết bị sử dụng, thông qua jumper chọn mức điện áp và công tắc bật/tắt nguồn tích hợp.

- **Breadboard**

  - Là bảng mạch kết nối không cần hàn, được sử dụng để phân phối nguồn điện từ MB102 đến các thiết bị như ESP32, servo, buzzer và màn hình OLED.
  - Cho phép kết nối linh kiện một cách linh hoạt thông qua dây jumper, giúp xây dựng và tổ chức hệ thống điện tử một cách gọn gàng, dễ bảo trì và dễ mở rộng.

- **Dây jumper (male-male, male-female, female-female)**

  - Dây jumper được sử dụng để kết nối các thành phần trong mạch với nhau mà không cần hàn, đặc biệt phù hợp cho hệ thống kết nối qua breadboard.
  - Các loại jumper dây phổ biến bao gồm:

    - Male-male: dùng để nối giữa các hàng chân trên breadboard
    - Male-female: dùng để nối board mạch với thiết bị có đầu cắm đực như module, cảm biến
    - Female-female: dùng khi kết nối giữa hai thiết bị có chân cắm là male.

- **FTDI FT232RL**

  - Là module chuyển đổi tín hiệu USB và UART, cho phép kết nối giữa máy tính và các thiết bị không có cổng USB trực tiếp như ESP32-CAM.
  - Được sử dụng để nạp chương trình cho ESP32-CAM vì ESP32-CAM không có cổng USB trực tiếp. Mỗi ESP32-CAM chỉ cần nạp code 1 lần duy nhất, sau đó có thể hoạt động độc lập bằng Wi-Fi.
  - Kết nối với máy tính qua USB, sau đó nối 4 chân TX, RX, GND, 5V đến ESP32-CAM.
  - Khi nạp code cần nối chân IO0 của ESP32-CAM xuống GND để vào chế độ lập trình.
  - Ngoài nạp code, module này cũng giúp giao tiếp Serial (debug) khi cần thiết.


### Ứng dụng AI phân tích hình ảnh **(chỉnh sửa thêm)**

- **Nhận diện khuôn mặt**
    - **Phát hiện khuôn mặt**: Sử dụng mô hình **YOLOv6** để phát hiện vùng chứa khuôn mặt (bounding box) trong ảnh. Mô hình có tốc độ nhanh, độ chính xác cao, phù hợp xử lý ảnh thời gian thực.

    - **Nhận diện khuôn mặt**: Dựa trên các vector đặc trưng được tạo bởi mô hình **FaceNet**, so sánh với database để xác định danh tính.


- **Nhận diện biển số xe**
    - **Phát hiện biển số xe**: Sử dụng mô hình **YOLOv8** để phát hiện vùng chứa biển số xe trong ảnh.
    - **Nhận dạng ký tự biển số**: Cắt vùng biển số từ ảnh dựa trên kết quả phát hiện, áp dụng thuật toán nhận dạng ký tự **Tesseract OCR** để trích xuất chuỗi ký tự.

### Giao diện người dùng và quản trị **(chưa quyết định)**

- **Frontend:**
Sử dụng các công nghệ phổ biến HTML, CSS, JavaScript để xây dựng giao diện thân thiện, dễ sử dụng cho tài xế và quản trị viên.

- **Backend:**
Sử dụng Django làm framework backend, xử lý các logic nghiệp vụ như xác thực người dùng, quản lý dữ liệu xe và vị trí bãi đỗ, cung cấp API cho frontend và thiết bị IoT kết nối.
 
### Kết nối và nền tảng lưu trữ **(chưa quyết định)**

- **MQTT (Message Queuing Telemetry Transport):**
Giao thức truyền thông nhẹ, tối ưu cho các thiết bị IoT với băng thông hạn chế. MQTT hỗ trợ kết nối ổn định, truyền dữ liệu theo dạng publish-subscribe, rất phù hợp để truyền trạng thái cảm biến, điều khiển thiết bị trong hệ thống bãi đỗ xe thông minh.

- **MongoDB:**
Cơ sở dữ liệu NoSQL dạng tài liệu, linh hoạt trong việc lưu trữ dữ liệu phi cấu trúc như log hệ thống, dữ liệu người dùng, thông tin xe, hình ảnh. Được sử dụng phổ biến trong các hệ thống backend nhờ khả năng mở rộng và thao tác linh hoạt với dữ liệu JSON.

## Thiết bị

| STT | Tên thiết bị                                 | Số lượng        | Giá/cái | Hình ảnh                               | Nguồn liên kết                                                                                                                                   |
|--------------|--------------------------------------------------------------------|---------------------------------|--------------------------------------|--------------------------------------------------------|-------------------------------------------------------------|
| 1   | **AI Thinker ESP32-CAM**                     | 4               | 165,000        | ![](images/ESP32-CAM.jpg){ height=120px }              | [Xem tại đây](https://shopee.vn/Module-thu-ph%C3%A1t-wifi-camera-ESP32-CAM-t%C3%ADch-h%E1%BB%A3p-wifi-camera-OV2640-chuy%C3%AAn-d%E1%BB%A5ng-v%C3%A0-bluetooth-4-i.16504852.4665567596) |
| 2   | **ESP32 DevKit V1 (CP2102, Type-C)**         | 2               | 97,000         | ![](images/ESP32.jpg){ height=120px }                  | [Xem tại đây](https://shopee.vn/-P0006-ESP32-Devkit-V1-Bo-M%E1%BA%A1ch-Ph%C3%A1t-Tri%E1%BB%83n-%C4%90a-N%C4%83ng-Cho-D%E1%BB%B1-%C3%81n-IoT-Gi%C3%A1-T%E1%BB%91t-Nh%E1%BA%A5t-i.135851482.26959755297) |
| 3   | **Màn hình OLED 0.96 inch**                  | 2               | 55,000         | ![](images/OLED.jpg){ height=120px }                   | [Xem tại đây](https://shopee.vn/M%C3%A0n-h%C3%ACnh-hi%E1%BB%83n-th%E1%BB%8B-128x64-Oled-0.96-Inch-giao-Ti%E1%BA%BFp-I2C-chuy%C3%AAn-d%E1%BB%A5ng-SSD1315-SSD1306-i.16504852.12103032615) |
| 4   | **Servo motor MG90S**                        | 2               | 37,000         | ![](images/SERVO.jpg){ height=120px }                  | [Xem tại đây](https://shopee.vn/%C4%90%E1%BB%99ng-C%C6%A1-Servo-MG90S-i.243949145.19090357136) |
| 5   | **Buzzer 5V**                                | 2               | 3,000          | ![](images/BUZZER.jpg){ height=120px }                 | [Xem tại đây](https://shopee.vn/-C%C3%B3-s%E1%BA%B5n-R%E1%BA%BB-v%C3%B4-%C4%91%E1%BB%8Bch-Module-buzzer-5V-thegioimodule-i.951399259.25120210346) |
| 6   | **Mô đun nguồn MB102**                       | 2               | 17,000         | ![](images/MB102_Power_Supply.jpg){ height=120px }     | [Xem tại đây](https://shopee.vn/M%C3%B4-%C4%91un-ngu%E1%BB%93n-%C4%91i%E1%BB%87n-m%E1%BA%A1ch-c%E1%BA%AFm-d%C3%A2y-MB102-hai-chi%E1%BB%81u-3.3V-5V-i.325406709.11021689837) |
| 7   | **Breadboard MB-102 830 lỗ**                 | 2               | 17,000         | ![](images/BREADBOARD.jpg){ height=120px }             | [Xem tại đây](https://shopee.vn/Breadboard-MB-102-830-L%E1%BB%97-165x55x10mm-(Board-test-c%E1%BA%AFm-linh-ki%E1%BB%87n-bo-test-b%E1%BA%A3ng-m%E1%BA%A1ch-th%E1%BB%AD-nghi%E1%BB%87m-)-i.301053603.21250257237) |
| 8   | **Dây jumper (male-male, male-female, female-female)**                      | 40 sợi/loại   | 66,000         | ![](images/JUMPER.jpg){ height=120px }                 | [Xem tại đây](https://shopee.vn/-40-s%E1%BB%A3i-d%C3%A2y-c%E1%BA%AFm-testboard-bread-board-jumper-dupont-wire-10-20-30-40-cm-i.494330825.9381418486) |
| 9   | **FTDI FT232RL (USB - UART)**                | 1               | 37,000         | ![](images/USB_TO_UART.jpg){ height=120px }            | [Xem tại đây](https://shopee.vn/M%E1%BA%A1ch-Chuy%E1%BB%83n-USB-UART-TTL-FT232-FT232RL-i.301053603.21350504517) |
