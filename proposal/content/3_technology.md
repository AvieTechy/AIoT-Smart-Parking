\pagebreak

# Hệ thống phần cứng

## Chi tiết thiết bị

### ESP32-CAM (AI Thinker ESP32-CAM)

![ESP32-CAM](images/ESP32-CAM.jpg){ height=300px }

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

![Đế nạp ESP32-CAM](images/Programming_Adapter.jpg){ height=300px }

- Vì ESP32-CAM không có cổng USB, nên ta cần thiết bị trung gian để nạp code là **Đế Nạp ESP32-CAM**, sau khi nạp ESP32-CAM sẽ chạy độc lập và không mất code khi tắt nguồn. Đây là module chuyển đổi tín hiệu USB và UART, cho phép kết nối giữa máy tính và các thiết bị không có cổng USB trực tiếp như ESP32-CAM.

Lưu ý khi vừa nạp code, ESP32-CAM đang ở chế độ bootloader, cần ấn nút *reset* để chip khởi động lại chế độ chạy bình thường.

### ESP32 trung tâm (ESP32 DevKit V1)

![ESP32 DevKit V1](images/ESP32.jpg){ height=300px }

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

### Breadboard

Là bảng mạch kết nối không cần hàn, được sử dụng để phân phối nguồn điện và kết nối các thiết bị với nhau.

Cho phép kết nối linh kiện một cách linh hoạt thông qua dây jumper, giúp xây dựng và tổ chức hệ thống điện tử một cách gọn gàng, dễ bảo trì và dễ mở rộng.

Trong hệ thống này, breadboard sẽ được cấp nguồn trực tiếp từ adapter 5V – 3A thông qua cáp chia nguồn, sử dụng dây jumper để kết nối các thành phần trong mạch breadboard.

| **Loại dây** | **Đầu cắm** | **Ứng dụng** |
| --- | --- | ------ |
| **Male-Male** | Đầu cắm kim 2 bên | Dùng để cắm từ chân này sang chân khác **trên breadboard** hoặc từ **breadboard đến board mạch** (ESP32, MB102…) |
| **Male-Female** | Một đầu kim, một đầu lỗ | Dùng để nối **module/cảm biến (có chân đực)** với **breadboard hoặc board mạch** |
| **Female-Female** | Hai đầu lỗ | Dùng để **nối giữa 2 thiết bị đều có chân đực**, ví dụ **ESP32-CAM và FTDI**, hoặc giữa **module logic với module khác** |


### Màn hình OLED

Là màn hình đơn sắc kích thước 0.96 inch, giao tiếp bằng chuẩn **I2C (SDA, SCL)** với ESP32 trung tâm (thường là GPIO21 và GPIO22). Trong hệ thống này ta sử dụng màn hình OLED với IC điều khiển SSD1306, điện áp hoạt động 5V (có tương thích 3.3V).

Có chức năng hiển thị:

- Khi xe vào: Hiển thị số chỗ còn trống, hoặc báo "đã hết chỗ" nếu không còn slot đỗ.
- Khi xe ra: Hiển thị lời chào hoặc hiển thị lỗi nếu quá trình nhận diện không hợp lệ.

### Servo motor MG90S

**MG90S** là một loại **servo mini** với **moment xoắn**, có cấu trúc **bánh răng kim loại**, bền hơn và chịu lực tốt hơn, phù hợp để điều khiển cơ cấu vật lý như **thanh chắn**.

Servo hoạt động ở **điện áp 5V**, tiêu thụ dòng khoảng **250–400mA khi tải nặng**, do đó cần cấp nguồn ổn định để tránh sụt áp hoặc làm **ESP32 reset** đột ngột.

**ESP32 trung tâm điều khiển servo qua tín hiệu PWM** từ một chân GPIO bất kỳ (thường dùng GPIO13 hoặc GPIO14). Tín hiệu PWM xác định góc quay của servo (trong khoảng 0°–180°).

## Tổng hợp 

| STT | Tên thiết bị                                 | Số lượng        | Giá/cái | Hình ảnh                               | Nguồn liên kết                                                                                                                                   |
|--------------|--------------------------------------------------------------------|---------------------------------|--------------------------------------|--------------------------------------------------------|-------------------------------------------------------------|
| 1   | **AI Thinker ESP32-CAM**                     | 2               | 165,000        | ![](images/ESP32-CAM.jpg){ height=120px }              | [Xem tại đây](https://shopee.vn/Module-thu-ph%C3%A1t-wifi-camera-ESP32-CAM-t%C3%ADch-h%E1%BB%A3p-wifi-camera-OV2640-chuy%C3%AAn-d%E1%BB%A5ng-v%C3%A0-bluetooth-4-i.16504852.4665567596) |
| 2   | **ESP32 DevKit V1 (CP2102, microUSB) kèm cáp**         | 1               | 154,000         | ![](images/ESP32.jpg){ height=120px }                  | [Xem tại đây](https://shopee.vn/ESP32-WROOM-32-MICRO-C-30PIN-CP2102-DEVKIT-WIFI-BLUETOOTH-i.1045034041.27478340900) |
| 3   | **Màn hình OLED 0.96 inch**                  | 1               | 66,000         | ![](images/OLED.jpg){ height=120px }                   | [Xem tại đây](https://shopee.vn/OLED-0.96IN-1.3IN-I2C-SH1106-XANH-V%C3%80-TR%E1%BA%AENG-M%C3%80N-H%C3%8CNH-HI%E1%BB%82N-TH%E1%BB%8A-%C4%90I%E1%BB%82M-%E1%BA%A2NH-i.1045034041.27007708527) |
| 4   | **Servo motor MG90S**                        | 1               | 69,000         | ![](images/SERVO.jpg){ height=120px }                  | [Xem tại đây](https://shopee.vn/%C4%90%E1%BB%98NG-C%C6%A0-SERVO-MG90-MG946-MG995-MG996-KIM-LO%E1%BA%A0I-%C4%90%E1%BB%98NG-C%C6%A0-G%C3%93C-0-%E2%80%93-180-%C4%90%E1%BB%98-i.1045034041.27859059953) |
| 5   | **Adapter 5V - 3A**                       | 1               | 52,000         | ![](images/ADAPTER.jpg){ height=120px }     | [Xem tại đây](https://shopee.vn/Ngu%E1%BB%93n-adapter-5V-3A-i.60387211.1319208358?sp_atk=f1f6e536-7633-4c9b-b33d-41d5619ac7a2&xptdk=f1f6e536-7633-4c9b-b33d-41d5619ac7a2) |
| 6   | **Bộ chia nguồn DC male**                       | 1               | 26,000         | ![](images/DC_TO_5_DC.jpg){ height=120px }     | [Xem tại đây](https://shopee.vn/D%C3%A2y-chia-ngu%E1%BB%93n-DC-d%C3%A2y-ngu%E1%BB%93n-5-%C4%91%E1%BA%A7u-ra-jack-tr%C3%B2n-5.5x2.1mm-i.99552004.5975962994?sp_atk=64592bf8-acad-49fb-bc76-e48a0695436e&xptdk=64592bf8-acad-49fb-bc76-e48a0695436e) |
| 7   | **Jack DC cái có dây 5.5x2.1mm**                       | 3               | 3,000         | ![](images/1.jpeg){ height=120px }     | [Xem tại đây](https://nshopvn.com/product/jack-dc-cai-co-day/) |
| 8   | **Breadboard**                 | 1               | 20,000         | ![](images/BREADBOARD.jpg){ height=120px }             | [Xem tại đây](https://shopee.vn/TESTBOARD-MB-102-165x55MM-830-L%E1%BB%96-BREADBOARD-TR%E1%BA%AENG-i.1045034041.28809287633) |
| 9   | **Dây jumper**                      | 40 sợi/loại   | 66,000         | ![](images/JUMPER.jpg){ height=120px }                 | [Xem tại đây](https://shopee.vn/-40-s%E1%BB%A3i-d%C3%A2y-c%E1%BA%AFm-testboard-bread-board-jumper-dupont-wire-10-20-30-40-cm-i.494330825.9381418486) |
| 10   | **Đế Nạp ESP32-CAM**                      | 1   | 30,000         | ![](images/Programming_Adapter.jpg){ height=120px }                 | [Xem tại đây](https://shopee.vn/%C4%90%E1%BA%BF-n%E1%BA%A1p-ch%C6%B0%C6%A1ng-tr%C3%ACnh-ESP32-CAM-micro-USB-i.60387211.29470543694?sp_atk=950b9eda-e15a-4461-839d-33d2b3e608a0&xptdk=950b9eda-e15a-4461-839d-33d2b3e608a0) |
