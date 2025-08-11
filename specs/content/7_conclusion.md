# Kết luận, Hạn chế và Hướng phát triển

## Kết luận

Nghiên cứu đã triển khai thành công hệ thống bãi đỗ xe thông minh sử dụng công nghệ AIoT, bao gồm các module ESP32/ESP32-CAM, dịch vụ xử lý trung tâm, lưu trữ đám mây và giao diện quản lý.

**Kết quả thực nghiệm:**

- Nhận diện khuôn mặt: Precision = 1.0, Recall = 0.94
- Khớp khuôn mặt: Accuracy = 96.2%, F1-score = 96.8%
- Nhận diện biển số: Accuracy = 100%
- Thời gian xử lý trung bình: 12 giây
- Hệ thống hoạt động ổn định với các chức năng cơ bản

## Hạn chế

- Hiệu suất giảm đáng kể với ảnh chất lượng thấp hoặc điều kiện ánh sáng kém
- Ngưỡng nhận diện cần được điều chỉnh dựa trên dữ liệu thực tế
- Quy mô dữ liệu huấn luyện còn hạn chế
- Thiếu các tính năng thu phí tự động và quản lý đa cổng vào

## Hướng phát triển

- **Nâng cao độ chính xác**: Mở rộng bộ dữ liệu với mẫu Việt Nam, cải thiện thuật toán xử lý ảnh
- **Tối ưu hiệu năng**: Giảm thời gian phản hồi xuống dưới 10 giây
- **Tăng độ tin cậy**: Bổ sung cơ chế backup và monitoring hệ thống
- **Mở rộng chức năng**: Tích hợp thanh toán tự động và hỗ trợ nhiều camera đồng thời
