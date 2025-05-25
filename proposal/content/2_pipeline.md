# Mô hình hệ thống và luồng hoạt động

## Mô hình hệ thống

Hệ thống bãi đỗ xe thông minh sử dụng nhận diện **khuôn mặt kết hợp biển số xe**, với các thiết bị phần cứng như sau:

### Đề xuất bố trí thiết bị

- **Cổng vào:**  
    - **ESP32-CAM_1** (quét biển số): đặt thấp (0.5–1m), hướng vào xe.
    - **ESP32-CAM_2** (nhận diện khuôn mặt): đặt cao hơn (~1.2–1.5m), hướng về cửa sổ tài xế.
    - **Màn hình OLED_1:** hiển thị thông tin cho tài xế.
    - **Buzzer_1:** phát tín hiệu âm thanh khi cần.
    - **Barrier + Servo motor:** điều khiển thanh chắn ra vào.

- **Khu vực đỗ xe:**  
    - Các ô đỗ được kẻ đường ngăn cách rõ ràng, sắp xếp trật tự. Có thể gắn cảm biến nhận diện ô trống (hướng phát triển thêm).

- **Cổng ra:**  
    - **ESP32-CAM_3** (quét biển số): đặt thấp (0.5–1m), hướng vào xe.
    - **ESP32-CAM_4** (nhận diện khuôn mặt): đặt cao hơn (~1.2–1.5m), hướng về cửa sổ tài xế.
    - **Màn hình OLED_2:** hiển thị thông tin cho tài xế.
    - **Buzzer_2:** phát tín hiệu âm thanh khi cần.
    - **Barrier + Servo motor:** điều khiển thanh chắn ra vào.

### Sơ đồ bố trí thiết bị
![Sơ đồ đề xuất bố trí thiết bị](images/parking.png){ width=100% .center }

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

![Flowchart cho entry flow](images/entry-flow.png){ width=90% .center }

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

![Flowchart cho exit flow](images/exit-flow.png){ width=90% .center }
