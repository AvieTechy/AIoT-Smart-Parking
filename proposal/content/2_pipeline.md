# Mô hình mô phỏng và luồng hoạt động

## Mô hình hệ thống

Hệ thống bãi đỗ xe thông minh ứng dụng nhận diện khuôn mặt được chia làm 3 khu vực chính:

1. **Cổng vào:**
- Camera AI: quét và nhận diện khuôn mặt người điều khiển xe.
- Màn hình hiển thị: thông báo vị trí chỗ đỗ xe đã được gán.
- Barrier tự động: mở khi xác minh khuôn mặt thành công.
- ESP32 / Raspberry Pi: xử lý tín hiệu từ camera, gửi dữ liệu đến server và điều khiển barrier.

2. **Khu đỗ xe:**
- Cảm biến hiện diện (IR / siêu âm): phát hiện xe đã đỗ vào slot.
- LED chỉ dẫn: sáng lên ở slot được cấp để hỗ trợ người lái điều hướng.
- Các thiết bị kết nối về server trung tâm để cập nhật trạng thái slot.

3. **Cổng ra:**
- Camera AI: quét khuôn mặt lần nữa để xác thực người rời bãi.
- Barrier tự động: mở nếu khuôn mặt trùng khớp với faceID đã gán slot trước đó.
- Sau khi xe rời khỏi slot, hệ thống cập nhật trạng thái trả slot thành trống.

![Mô hình tham khảo cho hệ thống](images/smart-parking.png){ width=100% .center }

## Luồng hoạt động chính của hệ thống

1. **Xe đến cổng vào:**
    - Camera quét khuôn mặt người điều khiển.
    - Hệ thống AI xử lý ảnh → tạo `face_vector` (mã đặc trưng khuôn mặt).
    - Lưu tạm thời `face_vector` vào bộ nhớ đệm hoặc cơ sở dữ liệu tạm.

2. **Tìm và gán ô đỗ xe trống:**
    - Kiểm tra cảm biến tại các ô → tìm ô trống (ví dụ: B3).
    - Gán `face_vector → slot_id (B3)`.
    - Màn hình LCD hiển thị: **“Chỗ đậu: B3”**.
    - Hệ thống mở barrier → cho xe đi vào.
    - Đèn LED tại ô B3 bật sáng để hướng dẫn.

3. **Trong quá trình đỗ xe:**
     - Cảm biến xác nhận có xe trong ô → cập nhật trạng thái ô là “ĐÃ ĐỖ”.

4. **Xe rời bãi (cổng ra):**
    - Camera tại cổng ra quét lại khuôn mặt.
    - Hệ thống AI so sánh ảnh với danh sách `face_vector` đã lưu.
    - Nếu khớp:
        - Tìm ra ô đã gán (VD: B3).
        - Cập nhật B3 là “TRỐNG”.
        - Xóa `face_vector` khỏi bộ nhớ.
        - Mở barrier cho xe ra khỏi bãi.