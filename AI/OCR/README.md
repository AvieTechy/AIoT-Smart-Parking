# Báo Cáo Mô Hình: Nhận Diện Biển Số Xe

## Plate Recognizer API

[Plate Recognizer](https://platerecognizer.com/) API cho phép các nhà phát triển tích hợp chức năng nhận diện biển số xe tự động vào ứng dụng của mình. API nhận hình ảnh hoặc URL và trả về số biển số xe, thông tin phương tiện, cùng điểm tin cậy dưới dạng JSON. API hỗ trợ nhiều ngôn ngữ lập trình và cung cấp các endpoint cho xử lý thời gian thực và xử lý theo lô.

- **Tham khảo Docker Image:** [platerecognizer/alpr trên Docker Hub](https://hub.docker.com/r/platerecognizer/alpr)

## Bộ Dữ Liệu

- **Nguồn:** [Vietnam License Plate Dataset trên Roboflow Universe](https://universe.roboflow.com/tran-ngoc-xuan-tin-k15-hcm-dpuid/vietnam-license-plate-h8t3n)
- **Annotation:** Các ảnh trong bộ dữ liệu đã được chọn lọc và gán nhãn biển số xe.
- **Kích thước tập kiểm tra:** 101 ảnh

## Kết Quả

- **Nhận diện đúng:** 101 ảnh
- **Nhận diện sai:** 0 ảnh
- **Độ chính xác:** 100%
