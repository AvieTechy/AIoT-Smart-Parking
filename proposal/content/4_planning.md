# Kế hoạch thực hiện

## Phân công nhân lực

| Thành viên | Vai trò chính | Nhiệm vụ cụ thể |
| --- | ---- | ------ |
| Cao Uyển Nhi | Trưởng nhóm, quản lý tiến độ | Phụ trách AI – Nhận diện biển số/khuôn mặt|
| | | Tổng hợp báo cáo, điều phối nhóm, hỗ trợ kỹ thuật|
| | | Thu thập dữ liệu, huấn luyện mô hình, triển khai xử lý ảnh |
| Võ Lê Việt Tú | Phụ trách IoT – Cảm biến và cloud | Kết nối cảm biến, lập trình ESP32, gửi dữ liệu lên Firebase/ThingsBoard |
| Trần Thị Cát Tường | Thiết kế phần cứng – Mạch, cảm biến | Lắp ráp hệ thống, bố trí camera và sensor thực tế |
| Lưu Thanh Thuý | Phần mềm quản lý & báo cáo | Thiết kế dashboard, lập trình hiển thị và làm tài liệu |

## Timeline

| Tuần | Công việc chính |
| --- | ----------------- |
| 1–2 | Nghiên cứu tài liệu, xác định yêu cầu, phân công nhiệm vụ |
| 3–4 | Thu thập dữ liệu khuôn mặt/biển số, khảo sát thiết bị cần thiết |
| 5–6 | Triển khai mô hình AI nhận diện, kết nối cảm biến với ESP32 |
| 7–8 | Thiết kế giao diện dashboard, xây dựng cơ sở dữ liệu trên cloud |
| 9–10 | Tích hợp toàn hệ thống: AI + IoT + giao diện |
| 11 | Chạy thử, hiệu chỉnh, test toàn bộ quy trình thực tế |
| 12 | Viết báo cáo, chuẩn bị slide thuyết trình, hoàn thiện demo |

Cụ thể, xem timeline dạng [Gantt Chart](https://docs.google.com/spreadsheets/d/1FWV0xb-8idRwTd4VWHoW-UJOVkOGjidVqAgJGw7YVfk/edit?gid=1115838130#gid=1115838130) tại đây

## Chi phí thực hiện (chi phí thiết bị, chi phí làm)

| **Tên thiết bị** | **Số lượng** | **Đơn giá** | **Thành tiền** |
|----------------------|:------:|:---------:|:---------:|
| **AI Thinker ESP32-CAM**                     | 4               | 165,000        | 660,000 |
| **ESP32 DevKit V1 (CP2102, Type-C)**         | 1               | 97,000         | 97,000 |
| **Màn hình OLED 0.96 inch**                  | 2               | 55,000         | 110,000 |
| **Servo motor MG90S**                        | 2               | 37,000         | 74,000 |
| **Buzzer**                                | 2               | 5,000          | 10,000 |
| **Adapter 5V - 3A**                       | 1               | 52,000         | 52,000 |
| **Bộ chia nguồn DC male**                       | 1               | 26,000         | 26,000 |
| **Jack DC cái có dây 5.5x2.1mm**                       | 5               | 3,000         | 15,000 |
| **Breadboard**                 | 1               | 17,000         | 17,000 |
| **Dây jumper**                      | 40 sợi/loại   | 66,000         | 66,000 |
| **Đế Nạp ESP32-CAM**                      | 1   | 30,000         | 30,000 |
| **Module chuyển mạch I2C**                      | 1   | 33,000         | 33,000 |
| **Chi phí lắp đặt, khung mô hình** | - | 200,000 | 200,000 |
| **Tổng chi phí** | | | **1,390,000** |
