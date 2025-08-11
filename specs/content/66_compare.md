# So sánh

## Bảng tổng hợp khác biệt

| Nội dung                     | Trước (Spec 1)                                   | Sau (Spec mới)                                              | Mức thay đổi        |
|-----------------------------|--------------------------------------------------|-------------------------------------------------------------|---------------------|
| Mục tiêu cốt lõi            | Giữ nguyên                                       | Giữ nguyên                                                  | –                   |
| Độ chính xác ban ngày       | ≥ 80%                                            | ≥ 90%                                                       | ↑ ~12%              |
| Số lượt test                | 6 lượt                                           | ≥ 100 lượt đa dạng                                          | ↑ nhiều             |
| Thời gian xử lý             | ≤ 5s                                             | ≤ 15s                                                       | Nới nhẹ             |
| Thời gian cập nhật slot     | ≤ 3s                                             | ≤ 5s                                                        | Nới nhẹ             |
| Mô hình AI                  | ESP-WHO, MobileFaceNet                           | ESP-FACE MTMN, FaceNet                                      | Đổi công nghệ       |
| Màn hình                    | OLED 0.96”                                       | LCD 16×2                                                    | Đổi linh kiện       |
| Servo                       | MG90S                                            | SG90                                                        | Đổi linh kiện       |
| Luồng xử lý                 | ESP32-CAM → Cloudinary → Firebase → Backend AI   | ESP32-CAM → Cloudinary → ESP32 trung tâm → AI → Firebase    | Thêm bước điều phối |

## Tóm tắt định lượng

- **Điểm giữ nguyên:** mục tiêu cốt lõi, mô hình 3 tầng, chức năng chính.
- **Điều chỉnh chính:** tăng nhẹ yêu cầu độ chính xác, mở rộng quy mô test, nới thời gian xử lý để phù hợp thực tế.
- **Thay đổi công nghệ:** cập nhật mô hình AI, thay một số linh kiện, tinh chỉnh luồng xử lý để tăng khả năng điều phối.
- **Tác động:** thay đổi mang tính tinh chỉnh và tối ưu, không ảnh hưởng đến định hướng ban đầu.

\pagebreak
