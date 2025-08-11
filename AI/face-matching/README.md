# Đánh giá Mô hình Face Matching

## Model

- **Kiến trúc**: FaceNet với backend RetinaFace (DeepFace)
- **Đặc điểm**: Nhận diện khuôn mặt và sinh vector embedding 128 chiều cho mỗi ảnh.
- **Cách hoạt động**: So sánh khoảng cách Euclidean giữa hai embedding để xác định mức độ giống nhau.
- **Batching**: Xử lý theo lô nhỏ (batch size = 10) giúp theo dõi tiến trình và tối ưu tốc độ.
- **Framework**: Sử dụng thư viện [DeepFace](https://github.com/serengil/deepface) để tích hợp model và detector.
- **Tiền xử lý**: Kiểm tra sự tồn tại và hợp lệ của ảnh trước khi xác thực.
- **Ngưỡng phân loại**: Khoảng cách tối ưu là 0.5760 (cặp có khoảng cách nhỏ hơn được coi là giống nhau).

## Dataset

> Mô hình này được evalute trên tập dataset [Labelled Faces in the Wild (LFW) Dataset](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset/data)

- **Tổng cặp**: 500
- **Cặp đồng nhất**: 300 (60%)
- **Cặp khác nhau**: 200 (40%)

## Kết quả Đánh giá

| Metric     | Giá trị | Phần trăm |
|------------|---------|-----------|
| Accuracy   | 0.962   | 96.20%    |
| Precision  | 0.970   | 97.00%    |
| Recall     | 0.967   | 96.70%    |
| F1-score   | 0.968   | 96.80%    |

![confusion matrix](image.png)
