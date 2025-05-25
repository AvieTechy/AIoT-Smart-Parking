# Mô hình mô phỏng và luồng hoạt động

## Mô hình hệ thống

Hệ thống bãi đỗ xe thông minh sử dụng nhận diện **khuôn mặt kết hợp biển số xe**, với các thiết bị phần cứng như sau:

1. **Cổng vào:**
- **ESP32-CAM_1**: quét và nhận diện **biển số xe**.
- **ESP32-CAM_2**: quét và nhận diện **khuôn mặt tài xế**.
- **Màn hình OLED**: hiển thị số lượng ô đỗ xe còn trống hoặc báo lỗi.
- **Servo motor**: điều khiển barrier tự động mở nếu xác thực thành công.
- **Buzzer**: phát âm báo xác nhận **thành công hoặc lỗi**.

2. **Khu vực đỗ xe:**
- Các ô giữ xe được xếp thành các hàng.

3. **Cổng ra:**
- **ESP32-CAM_3**: quét lại **biển số xe**.
- **ESP32-CAM_4**: quét lại **khuôn mặt tài xế**.
- **Màn hình OLED**: hiển thị số lượng ô đỗ xe còn trống hoặc báo lỗi.
- **Servo motor**: điều khiển barrier tự động mở nếu xác thực thành công.
- **Buzzer**: phát âm báo xác nhận **thành công hoặc lỗi**.

## Luồng hoạt động chính của hệ thống

### Entry flow (luồng hoạt động ở cổng vào)
- ESP32-CAM_1 quét **biển số xe**.
- ESP32-CAM_2 quét **khuôn mặt tài xế**.
- Hệ thống xử lý và kiểm tra:
  - Nếu **cả hai đều nhận diện thành công**:
    - Map dữ liệu: `face_id` ↔ `license_plate`.
    - Lưu vào cơ sở dữ liệu tạm thời.
    - Servo mở barrier cho xe vào.
    - Buzzer phát âm báo thành công.
    - Màn hình OLED hiển thị số ô trống hiện tại.
  - Nếu **không nhận diện được**:
    - Hiển thị thông báo lỗi trên màn hình OLED.
    - Buzzer phát cảnh báo nhẹ.
    - Chờ người dùng điều chỉnh vị trí xe để quét lại.
\pagebreak

![Flowchart cho entry flow](images/entry-flow.png){ width=75% .center }

### Exit flow (luồng hoạt động ở cổng ra):
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

![Flowchart cho exit flow](images/exit-flow.png){ width=75% .center }
