## Hệ thống phần cứng

### Chi tiết thiết bị

1. **ESP32-CAM (AI Thinker ESP32-CAM)**

![ESP32-CAM](images/ESP32-CAM.jpg){ height=200px }

ESP32-CAM là một module phát triển nhỏ gọn của hãng **AI. Thinker**, tích hợp sẵn: **Wi-Fi, Bluetooth, camera OV2640, khe cắm thẻ microSD, GPIO** đa năng.

Module này được thiết kế chuyên dụng cho các ứng dụng thị giác máy tính, IoT, nhận diện khuôn mặt, giám sát an ninh, …

ESP32-CAM là lựa chọn phổ biến nhờ giá rẻ, tính năng mạnh, và khả năng chạy AI trực tiếp trên thiết bị.

| **Thành phần** | **Thông tin chi tiết** | **Ghi chú** |
| --- | --- | ------ |
| **Vi xử lý chính** | ESP32-WROOM-32 | Xử lý  chương trình nạp vào |
| **Tốc độ xung nhịp** | Lên tới 240 MHz | Xử lý được **240 triệu lệnh mỗi giây** |
| **RAM** | 520 KB SRAM nội | Lưu dữ liệu tạm thời khi chương trình đang chạy, tự động mất khi tắt nguồn |
| **Flash** | 4 MB (SPI flash) | Lưu trữ chương trình được nạp vào chip, không mất khi tắt nguồn |
| **Camera** | OV2640, độ phân giải tối đa 1600x1200 (UXGA), hỗ trợ nhiều chế độ JPEG | Có LED flash trắng tích hợp (nối chân GPIO nếu dùng), không tự động lấy nét, hình bị mờ nếu đặt sai khoảng cách. |
| **GPIO** | ~9 chân GPIO khả dụng | Các chân đa năng trên chip, cho phép nhận tín hiệu vào và gửi tín hiệu ra |
| **Nguồn hoạt động** | 3.3V  | Khi dùng nguồn 5V, cấp nguồn vào chân VCC/5V, bo mạch ESP32-CAM có sẵn mạch ổn áp AMS1117, chuyển 5V thành 3.3V cấp cho chip |
| **Dòng tiêu thụ** | 160–250mA khi hoạt động | Nên dùng nguồn ổn định từ MB102 hoặc pin sạc 5V - 1A trở lên |
| **Cổng USB** | Không có  | Cần dùng **USB to UART** để nạp code |
| **Kích thước** | 27 x 40.5 x 4.5 mm |  |

Hệ thống sử dụng **2 module ESP32-CAM** tại cổng:

- Một module quét và nhận diện khuôn mặt tài xế.
- Một module quét và nhận diện biển số xe.

Mỗi ESP32-CAM hoạt động độc lập, được nạp sẵn chương trình, luôn bật camera và model nhận diện, có khả năng:

- Nhận diện sự xuất hiện của xe
- Tự động chụp ảnh
- Thực hiện nhận diện khuôn mặt hoặc biển số trực tiếp trên thiết bị
- Truyền tải thông tin:
  - Gửi hình chụp khuôn mặt và biển số xe tới **Cloudinary** qua giao thức **HTTP POST**.
  - Nhận `url` hình ảnh từ **Cloudinary**, thực hiện nhận diện khuôn mặt và gửi gói tin gồm `url` và kết quả nhận diện vừa xử lý về **Firebase**.

ESP32 trung tâm sẽ kết nối chung mạng Wi-Fi với 2 ESP32-CAM, đóng vai trò nhận thông tin từ các module này. Sau khi nhận được kết quả nhận diện thông qua Wi-Fi, ESP32 trung tâm xử lý và điều khiển các thiết bị output liên quan như màn hình OLED và servo.

**Nạp code**:

![Đế nạp ESP32-CAM](images/Programming_Adapter.jpg){ height=200px }

- Vì ESP32-CAM không có cổng USB, nên ta cần thiết bị trung gian để nạp code là **Đế Nạp ESP32-CAM**, sau khi nạp ESP32-CAM sẽ chạy độc lập và không mất code khi tắt nguồn. Đây là module chuyển đổi tín hiệu USB và UART, cho phép kết nối giữa máy tính và các thiết bị không có cổng USB trực tiếp như ESP32-CAM.

Lưu ý khi vừa nạp code, ESP32-CAM đang ở chế độ bootloader, cần ấn nút *reset* để chip khởi động lại chế độ chạy bình thường.

2. **ESP32 trung tâm (ESP32 DevKit V1)**

![ESP32 DevKit V1](images/ESP32.jpg){ height=200px }

ESP32 trung tâm là **bộ điều khiển chính** của toàn hệ thống, xử lý và điều phối giữa các thiết bị. Board sử dụng **chip ESP32-WROOM-32**, có thể xử lý nhiều tác vụ song song.

| **Thành phần** | **Thông tin chi tiết** | **Ghi chú** |
| --- | --- | ------ |
| **Chip chính** | ESP32-WROOM-32  |  |
| **RAM** | 520 KB |  |
| **Flash** | 4MB SPI Flash |  |
| **Tốc độ xử lý** | Lên đến 240MHz |  |
| **Điện áp logic** | 3.3V  | Thiết bị gửi tín hiệu 5V vào ESP32 GPIO có thể gây cháy GPIO, cần sử dụng mạch chia áp |
| **USB-to-Serial** | Tích hợp sẵn CP2102  | Có thể **nạp code trực tiếp qua cổng USB-C / microUSB** |
| **GPIO khả dụng** | ~25 chân, đủ dùng cho nhiều ngoại vi đồng thời |  |
| **Wi-Fi / Bluetooth** | Tích hợp sẵn, dùng được ở chế độ Station và Access Point | Với ESP32 và 4 ESP32-CAM, ta sẽ dùng chế độ Station, nghĩa là cùng kết nối wifi có sẵn |

3. **Breadboard**

Là bảng mạch kết nối không cần hàn, được sử dụng để phân phối nguồn điện và kết nối các thiết bị với nhau.

Cho phép kết nối linh kiện một cách linh hoạt thông qua dây jumper, giúp xây dựng và tổ chức hệ thống điện tử một cách gọn gàng, dễ bảo trì và dễ mở rộng.

Trong hệ thống này, breadboard sẽ được cấp nguồn trực tiếp từ adapter 5V – 3A thông qua cáp chia nguồn, sử dụng dây jumper để kết nối các thành phần trong mạch breadboard.

| **Loại dây** | **Đầu cắm** | **Ứng dụng** |
| --- | --- | ------ |
| **Male-Male** | Đầu cắm kim 2 bên | Dùng để cắm từ chân này sang chân khác **trên breadboard** hoặc từ **breadboard đến board mạch** (ESP32, MB102…) |
| **Male-Female** | Một đầu kim, một đầu lỗ | Dùng để nối **module/cảm biến (có chân đực)** với **breadboard hoặc board mạch** |
| **Female-Female** | Hai đầu lỗ | Dùng để **nối giữa 2 thiết bị đều có chân đực**, ví dụ **ESP32-CAM và FTDI**, hoặc giữa **module logic với module khác** |

**4. Màn hình LCD**

Là màn hình **LCD 16x2** sử dụng giao tiếp **I2C (SDA, SCL)** với ESP32 trung tâm (thường là GPIO21 và GPIO22). Màn hình có module chuyển đổi I2C tích hợp giúp đơn giản hóa kết nối và tiết kiệm chân GPIO.

Trong hệ thống này, LCD có chức năng hiển thị:

* **Khi xe vào:** Hiển thị số chỗ còn trống hoặc thông báo “Đã hết chỗ” nếu không còn slot đỗ.
* **Khi xe ra:** Hiển thị lời chào (VD: “Tạm biệt”) hoặc hiển thị lỗi nếu quá trình nhận diện không hợp lệ.

Điện áp hoạt động là **5V** (tương thích tốt với ESP32 thông qua module I2C).

**5. Servo motor SG90**

**SG90** là một loại **servo mini phổ biến** với cấu trúc bánh răng nhựa, trọng lượng nhẹ, phù hợp với các cơ cấu điều khiển như **thanh chắn xe** trong mô hình nhỏ.

Servo hoạt động ở **điện áp 5V**, tiêu thụ dòng khoảng **100–250mA khi tải nhẹ**, do đó vẫn cần cấp nguồn ổn định để đảm bảo hoạt động liên tục và không ảnh hưởng đến ESP32.

**ESP32 trung tâm điều khiển servo qua tín hiệu PWM** từ một chân GPIO bất kỳ (thường dùng GPIO13 hoặc GPIO14). Tín hiệu PWM xác định góc quay của servo trong khoảng từ **0° đến 180°**, dùng để mở hoặc đóng thanh chắn.

### Tổng hợp

| STT | Tên thiết bị | Số lượng | Giá/cái | Hình ảnh | Nguồn liên kết |
|-----|--------------|----------|---------|----------|----------------|
| 1 | **AI Thinker ESP32-CAM** | 2 | 165,000 | ![](images/ESP32-CAM.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/Module-thu-ph%C3%A1t-wifi-camera-ESP32-CAM-t%C3%ADch-h%E1%BB%A3p-wifi-camera-OV2640-chuy%C3%AAn-d%E1%BB%A5ng-v%C3%A0-bluetooth-4-i.16504852.4665567596) |
| 2 | **ESP32 DevKit V1** | 1 | 154,000 | ![](images/ESP32.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/ESP32-WROOM-32-MICRO-C-30PIN-CP2102-DEVKIT-WIFI-BLUETOOTH-i.1045034041.27478340900) |
| 3 | **Màn hình LCD** | 1 | 81,000 | ![](images/lcd.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/1-C%C3%81I-LCD2004-I2C-2004-20x4-2004A-M%C3%A0n-h%C3%ACnh-xanh-v%C3%A0ng-xanh-HD44780-cho-nh%C3%A2n-v%E1%BA%ADt-arduino-LCD-IIC-I2C-v%E1%BB%9Bi-m%C3%B4-%C4%91un-chuy%E1%BB%83n-%C4%91%E1%BB%95i-I2C-i.1309911405.28106013829) |
| 4 | **Servo motor SG90** | 1 | 69,000 | ![](images/sg90.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/%C4%90%E1%BB%99ng-c%C6%A1-servo-RC-SG90-g%C3%B3c-xoay-180-i.66748910.29735003334) |
| 5 | **Adapter 5V - 3A** | 1 | 52,000 | ![](images/ADAPTER.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/Ngu%E1%BB%93n-adapter-5V-3A-i.60387211.1319208358) |
| 6 | **Breadboard** | 1 | 20,000 | ![](images/BREADBOARD.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/TESTBOARD-MB-102-165x55MM-830-L%E1%BB%96-BREADBOARD-TR%E1%BA%AENG-i.1045034041.28809287633) |
| 7 | **Dây jumper** | 40 sợi | 66,000 | ![](images/JUMPER.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/-40-s%E1%BB%A3i-d%C3%A2y-c%E1%BA%AFm-testboard-bread-board-jumper-dupont-wire-10-20-30-40-cm-i.494330825.9381418486) |
| 8 | **Đế Nạp ESP32-CAM** | 1 | 30,000 | ![](images/Programming_Adapter.jpg){ height=120px } | [Xem tại đây](https://shopee.vn/%C4%90%E1%BA%BF-n%E1%BA%A1p-ch%C6%B0%C6%A1ng-tr%C3%ACnh-ESP32-CAM-micro-USB-i.60387211.29470543694) |

## Luồng thực thi hệ thống

**1. Phát hiện & chụp ảnh**

- ESP32-CAM liên tục quét khung hình tại lối vào/ra.
- Khi phát hiện có khuôn mặt (MTMN – ESP-FACE), thiết bị sẽ chụp ảnh.

**2. Upload ảnh & gửi URL**

- ESP32-CAM upload ảnh lên Cloudinary qua REST API.
- Cloudinary trả về URL ảnh.
- ESP32-CAM gửi URL ảnh + metadata (thời gian, loại ảnh, ID thiết bị…) cho ESP32 trung tâm qua giao thức (HTTP/MQTT).

**3. Gọi AI model**

- ESP32 trung tâm nhận URL ảnh.
- Gọi API AI model (đã deploy trên server) với URL ảnh để thực hiện:
    - **Nhận diện khuôn mặt** (MobileFaceNet + DeepFace) → xác định danh tính.
    - **Nhận dạng biển số** (Plate Recognizer API) → trích xuất ký tự.

**4. Nhận & xử lý kết quả**

- API AI model trả về dữ liệu nhận diện (tên, biển số, trạng thái hợp lệ/không hợp lệ).
- ESP32 trung tâm ghi kết quả vào Firebase để lưu trữ và đồng bộ với Dashboard.

**5. Điều khiển thiết bị**

- Dựa trên kết quả nhận diện, ESP32 trung tâm điều khiển Servo (Barrier), LCD, và còi cảnh báo.

**6. Hiển thị & giám sát**

- Dashboard (ReactJS) kết nối Firebase để hiển thị lịch sử vào/ra, ảnh chụp, biển số, trạng thái slot, và thống kê theo thời gian thực.
