# Bảng đánh giá thành viên

## Tiêu Chí Đánh Giá

| Mã  | Tiêu chí                        | Trọng số | Gợi ý đánh giá (0–10) |
|-----|---------------------|----------|----------------------------|
| C1  | Mức độ hoàn thành công việc     | 0.30     | Hoàn thành scope, đúng yêu cầu |
| C2  | Chất lượng kết quả              | 0.25     | Ít lỗi, ổn định, hiệu quả |
| C3  | Phối hợp & chủ động              | 0.25     | Hỗ trợ nhóm, chủ động xử lý |
| C4  | Kỷ luật tiến độ                  | 0.20     | Đúng hẹn, cập nhật thường xuyên |
|     | **Tổng trọng số**               | **1.00** |                       |

## Hình Thức Đánh Giá

- **Phương pháp**: Mỗi thành viên chấm điểm (0–10) cho các thành viên khác ở từng tiêu chí.
- **Tính điểm theo trọng số**:

  $$\text{Điểm tổng hợp} = (C1 \times 0.30) + (C2 \times 0.25) + (C3 \times 0.25) + (C4 \times 0.20)$$

- **Kết quả (xếp hạng theo điểm giảm dần)**: Xếp hạng từ cao xuống thấp dựa trên điểm tổng hợp (thang 10). Tất cả thành viên hoàn thành 100% phạm vi được giao.

\pagebreak

| Hạng | Thành viên            | % Đóng góp | Điểm | Nhiệm vụ chính đã hoàn thành |
|:---:|------------------------|:----------:|:----------:|--------------------------------|
| 1   | Trần Thị Cát Tường     | 25%        | 10       | Lắp đặt ESP32-CAM (face & plate), ESP32 gateway, LCD, servo; Firestore schema + API FastAPI; Kiểm thử tổng thể, debug, chuẩn bị seminar |
| 2   | Lưu Thanh Thuý         | 25%        | 10       | Tích hợp firmware (ESP32-CAM & gateway): capture, upload Cloudinary, TCP, servo control; Kết nối pipeline Edge AI; Kiểm thử tổng thể, debug, chuẩn bị seminar |
| 3   | Cao Uyển Nhi           | 25%        | 10       | Triển khai FaceNet & ALPR API; Evaluate 3 mô hình (MTMN, FaceNet, ALPR); Kiểm thử tổng thể, debug, chuẩn bị seminar |
| 3   | Võ Lê Việt Tú          | 25%        | 10       | Firestore schema + API FastAPI; Dashboard realtime (UI, analytics, search/filter); Kiểm thử tổng thể, debug, chuẩn bị seminar |

- **Ghi chú**: Ngay từ đầu, nhóm đã thống nhất phân chia công việc dựa trên số lượng và độ phức tạp của từng task để đảm bảo sự công bằng. Trong suốt quá trình làm việc, tất cả các thành viên đều hoàn thành đầy đủ và đúng hạn phần việc của mình, đồng thời không xảy ra bất kỳ xung đột nội bộ nào. Vì vậy, khi chấm điểm, cả nhóm thống nhất đánh giá công bằng và giữ mức điểm ngang nhau cho tất cả thành viên.

## Nhận xét Chi tiết

| Thành viên         | Nhận xét |
|------------|-----------------------------|
| Cao Uyển Nhi       | Chủ động, kỷ luật cao; nghiên cứu và triển khai ổn định FaceNet & ALPR; phối hợp tốt; tích cực kiểm thử và hỗ trợ khi cần. |
| Trần Thị Cát Tường | Hoàn thành nhanh phần cứng, wiring, kết nối; thiết kế schema & API rõ ràng; hỗ trợ nhiều khâu từ code đến triển khai. |
| Lưu Thanh Thuý     | Làm việc trách nhiệm; tích hợp firmware ổn định; xử lý lỗi nhanh; kết nối edge–cloud mượt; hỗ trợ nhóm hiệu quả khi ghép code và kiểm thử. |
| Võ Lê Việt Tú      | Hoàn thành tốt dashboard và backend; UI realtime mượt; phối hợp nhịp nhàng khi ghép và kiểm thử; đảm bảo chất lượng đầu ra. |
