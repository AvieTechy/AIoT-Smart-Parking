# Mô hình hệ thống và luồng hoạt động

## Mô hình hệ thống

Hệ thống được thiết kế theo kiến trúc phân tầng gồm ba thành phần chính: tầng thiết bị đầu vào (ESP32-CAM), tầng xử lý trung tâm (AI model và backend Django), và tầng điều khiển - phản hồi (thiết bị IoT và Dashboard).

### Thiết bị đầu vào (Input Layer)

- Hệ thống sử dụng các camera ESP32-CAM được lắp đặt tại cổng vào và cổng ra:
    - ESP32-CAM_1 và ESP32-CAM_3 dùng để quét **biển số xe**.
    - ESP32-CAM_2 và ESP32-CAM_4 dùng để quét **khuôn mặt tài xế**.
- Dữ liệu hình ảnh thu được từ các camera này sẽ được gửi đến mô hình AI để nhận dạng.

### Tầng xử lý trung tâm (Processing Layer)

- **AI Model (local hoặc cloud)**:

    - Nhận hình ảnh đầu vào từ ESP32-CAM.
    - Thực hiện xử lý nhận dạng khuôn mặt và biển số xe.
    - Trả về kết quả nhận diện (ID khuôn mặt, chuỗi biển số).
- **Backend Django**:

    - Nhận kết quả từ mô hình AI.
    - Kiểm tra tính hợp lệ và đối chiếu với dữ liệu đã lưu (đối với trường hợp xe ra).
    - Gửi lệnh điều khiển thiết bị (servo, buzzer, OLED).
    - Giao tiếp với Dashboard thông qua API để hiển thị thông tin trạng thái, nhật ký hệ thống.
    - Lưu dữ liệu tạm thời hoặc đồng bộ dữ liệu với hệ thống lưu trữ (Firebase/ThingsBoard).

### Thiết bị điều khiển - phản hồi (Output Layer)

- **Servo (Barrier):** Tự động mở/đóng barrier cho xe ra vào sau khi xác thực.
- **OLED Display:** Hiển thị thông tin thời gian thực như số ô trống còn lại, lỗi nhận diện, cảnh báo...
- **Buzzer:** Phát âm báo tùy vào trạng thái: thành công, cảnh báo nhẹ, hoặc vi phạm.
- **Dashboard (giao diện web cho Admin):**

    - Hiển thị trạng thái thiết bị và số liệu thời gian thực.
    - Cho phép admin xem nhật ký vào/ra, giám sát trạng thái các camera và thiết bị IoT.
    - Tương tác trực tiếp với Backend qua các API.

### Nền tảng lưu trữ và giám sát

- **Firebase hoặc ThingsBoard**:

    - Lưu trữ dữ liệu nhật ký hệ thống (log), trạng thái thiết bị, và thông tin người dùng.
    - Hỗ trợ hiển thị biểu đồ, số liệu và cảnh báo qua giao diện quản lý.

Tổng thể, hệ thống hoạt động theo nguyên tắc nhận diện kết hợp (biển số và khuôn mặt) nhằm đảm bảo độ chính xác và an toàn cao trong việc kiểm soát ra vào tại các khu vực như bãi xe, cổng tòa nhà, v.v.

![Sơ đồ kiến trúc hệ thống](images/architecture.png){ width=90% .center }

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
