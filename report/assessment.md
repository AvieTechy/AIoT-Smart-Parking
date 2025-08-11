# BẢNG ĐÁNH GIÁ TIẾN ĐỘ DỰ ÁN AIoT

## Thông tin chung

- Tên dự án: **VisPart** - Smart Parking System
- Mục tiêu: Xây dựng prototype hệ thống bãi đỗ xe thông minh (nhận diện biển số & khuôn mặt, quản lý slot, đồng bộ cloud, dashboard giám sát) tự động hóa vào/ra.
- Phạm vi: Thiết bị & cảm biến, Firmware, Edge AI (MTMN, FaceNet, ALPR API), Cloud/Backend (FastAPI + Firestore + Cloudinary), Dashboard (React/TS).
- Thời gian: Bắt đầu 17/05/2025 – Kết thúc 02/08/2025.

## Tóm tắt trạng thái

- Trạng thái tổng thể: HOÀN THÀNH đúng tiến độ (seminar 02/08/2025).
- % Hoàn thành: ~100% phạm vi đặt ra.
- Thành tựu: Pipeline end-to-end ổn định (~12s/phiên < mục tiêu 15s); Chính xác AI đạt/ vượt mục tiêu; Dashboard realtime vận hành.
- Vấn đề chính đã xử lý: Latency cao (tối ưu index + batch); timeout thiếu cặp URL (thêm timer reset); false negative face (tối ưu threshold).

## Mốc (Milestones)

| Mốc | Mô tả | Ngày kế hoạch | Ngày thực tế | Trạng thái | Ghi chú |
|-----|-------|---------------|--------------|------------|---------|
| M1 | Thiết kế hệ thống & kiến trúc | 24/05/2025 | 24/05/2025 | Done | Đúng hạn |
| M2 | Thu thập dữ liệu & ghi nhãn | 07/06/2025 | 06/06/2025 | Done | Sớm 1 ngày |
| M3 | Phát triển mô-đun AI Edge | 21/06/2025 | 23/06/2025 | Done | Trễ 2 ngày (tinh chỉnh Face) |
| M4 | Firmware & tích hợp cảm biến | 05/07/2025 | 05/07/2025 | Done | Đúng hạn |
| M5 | Tích hợp Cloud & Dashboard | 20/07/2025 | 19/07/2025 | Done | Sớm |
| M6 | Kiểm thử tổng thể prototype | 27/07/2025 | 29/07/2025 | Done | Trễ 2 ngày (debug CAM) |
| M7 | Seminar & trình diễn | 02/08/2025 | 02/08/2025 | Done | Đạt mục tiêu |

## Tiến độ nhiệm vụ chính

| ID | Hạng mục | Nhiệm vụ | Owner | Bắt đầu | Deadline | % | Trạng thái | Ghi chú |
|----|----------|----------|-------|---------|----------|----|-----------|--------|
| T1 | Thiết bị | Lắp đặt ESP32-CAM, ESP32 gateway, LCD, servo | Cát Tường | 17/05 | 05/07 | 100 | Done | Ổn định |
| T2 | Firmware | Capture, upload, TCP, servo control | Thanh Thuý | 17/05 | 05/07 | 100 | Done | - |
| T3 | Edge AI | MTMN detect + FaceNet + ALPR tích hợp | Cao Nhi, Thanh Thuý | 21/06 | 23/06 | 100 | Done | Tối ưu threshold |
| T4 | Cloud | Firestore schema + API FastAPI | Cát Tường, Việt Tú | 05/07 | 20/07 | 100 | Done | - |
| T5 | Dashboard | UI realtime + analytics + search | Việt Tú | 05/07 | 20/07 | 100 | Done | Cần tối ưu UX |
| T6 | Model eval | Evaluate Face/ALPR, chọn threshold | Cao Nhi | 01/06 | 07/06 | 100 | Done | - |

## Thành phần kỹ thuật

### Thiết bị & cảm biến

| Thiết bị | Vai trò | Ghi chú chính |
|----------|---------|---------------|
| 2x ESP32-CAM (Gate In / Out) | Chụp face + plate | QVGA, HTTP upload |
| ESP32 trung tâm | Gateway | TCP nhận event, gọi OCR & Face |
| LCD 16x2 | Hiển thị | Slot, match, lỗi |
| Servo SG90 | Barrier | Mở 3s |
| Counter slot (giả lập) | Quản lý slot | Firestore meta |
| Nguồn + dây | Cấp nguồn | Ổn định |

Flow: ESP32-CAM → Upload ảnh → URL → Gateway TCP event → OCR + Face → Firestore Session & slot.

### Thu thập dữ liệu

| Dataset | Nguồn | Quy mô | Nhận xét | Dùng cho |
|---------|-------|--------|---------|----------|
| Face Detection | Nội bộ (UART script) | 285 | 70% tốt, 30% nhiễu | Đánh giá MTMN |
| Face Matching | LFW subset | 500 cặp | Chuẩn hoá | Threshold & accuracy |
| VN Plate | Roboflow | 101 test | Annotation chuẩn | Test ALPR API |

### Mô hình AI

| Phiên bản | Kiến trúc | Dataset | Metric | Kết quả | Latency | Ghi chú |
|-----------|-----------|---------|--------|---------|---------|---------|
| FD v1 | MTMN | 285 nội bộ | P / R | 1.000 / 0.944 | Edge vài trăm ms | ESP32-CAM |
| FM v1 | FaceNet + RetinaFace | 500 LFW pairs | Accuracy | 96.2% | 0.8–1.2s | Thr 0.576 |
| ALPR v1 | Plate Recognizer API | 101 VN plates | Accuracy | 100% | 0.4–0.6s | External |

### Firebase

| Thành phần | Vai trò | Ghi chú |
|-----------|--------|--------|
| Session | Lưu In/Out | isOut khi exit hợp lệ |
| PlateMap | Plate→entry | Tra cứu exit |
| SessionMap | Entry↔Exit | Thời lượng |
| MatchingVerify | Kết quả face | Evidence |
| IsNewSession | Trigger | Giảm polling |
| ParkingSlot/Meta | Slot | Counter trống |

Bottleneck: External OCR & Face; Firestore multiple reads. Đề xuất: cache, queue async, index.

### Dashboard

| Hạng mục | Trạng thái | Ghi chú |
|----------|-----------|--------|
| Auth | Done | JWT basic |
| Realtime Stats | Done | SessionService |
| History | Done | Parked/Exited |
| Analytics | Done | Hour→Year |
| Search/Filter | Done | Debounce |
| Update total slots | Done | Patch API |
| Export CSV/PDF | Planned | A3 |
| Role-based access | Planned | A4 |
| Notifications | Planned | WebSocket cần |
| Slot map | Planned | A5 |
| Dark mode | Planned | UX |
| Lazy load / Virtual scroll | Planned | A9 |

## Rủi ro & Giảm thiểu

| ID | Rủi ro | Xác suất | Ảnh hưởng | Mức độ | Giảm thiểu | Trạng thái |
|----|--------|----------|-----------|--------|-----------|-----------|
| R1 | Phụ thuộc ALPR API | Trung bình | Cao | Medium-High | Self-host fallback, cache | Chưa xảy ra |
| R2 | WiFi congestion | Trung bình | Trung bình | Medium | Giới hạn tần suất, retry | Đã giảm |
| R3 | Thiếu dữ liệu đêm | Cao | Trung bình | Medium | Thu thêm + augment | Mở |
| R4 | Firestore latency | Thấp | Trung bình | Low-Med | Index + batch + cache | Một phần |
| R5 | RAM ESP32-CAM | Thấp | Thấp | Low | Frame size/QC tune | Kiểm soát |
| R6 | External API downtime | Thấp | Cao | Medium | Retry + queue | Chưa làm |
| R7 | Thiếu audit log | Trung bình | Trung bình | Medium | Thêm audit layer | Chưa làm |

## Kết luận & Đề xuất

Prototype đạt mục tiêu (hiệu năng, chính xác, ổn định). Mạnh: modular, accuracy cao. Yếu: phụ thuộc external, thiếu dữ liệu khó, ít test tự động.

Đề xuất ưu tiên:
1. Dataset mở rộng (đêm/góc/mưa) – tăng recall.
2. Cache + queue async giảm độ trễ.
3. Monitoring & logging chuẩn (Prometheus / OpenTelemetry).
4. Role-based access + audit log.
5. Self-host ALPR fallback.
6. Mở rộng test & nâng coverage ≥70%.

Cần hỗ trợ: hạ tầng monitoring, thời gian thu thập dữ liệu, tài khoản ALPR dự phòng, security review.

Quyết định chờ duyệt: Chọn stack queue; lộ trình self-host ALPR; phạm vi phase 2 (pricing, multi-lot).
