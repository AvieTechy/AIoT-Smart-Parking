# Giới thiệu

## Bối cảnh

Hiện nay, nhiều bãi đỗ xe tại các khu vực như chung cư, trường học, tòa nhà văn phòng đã bắt đầu áp dụng phần mềm và thẻ từ (hoặc thẻ RFID) để quản lý việc ra vào. Tuy nhiên, các hệ thống này chủ yếu chỉ dừng lại ở mức cơ bản: người dùng quét thẻ khi vào – ra, hệ thống ghi lại thời gian và biển số xe (nếu có camera phụ trợ), sau đó lưu dữ liệu cục bộ. Chúng không kết nối với các cảm biến để giám sát tình trạng từng vị trí đỗ, không cung cấp thông tin theo thời gian thực cho người dùng hoặc người quản lý, và thường thiếu khả năng đồng bộ dữ liệu lên nền tảng trực tuyến để truy xuất khi có sự cố.

Hệ quả là việc vận hành vẫn phụ thuộc nhiều vào thao tác thủ công, dễ xảy ra sai sót như mất thẻ, quên quẹt thẻ, hoặc ghi nhận sai thời gian. Đồng thời, người dùng cũng gặp bất tiện khi không thể biết trước bãi còn chỗ hay không, dẫn đến mất thời gian di chuyển và tìm kiếm chỗ đỗ. Trong bối cảnh đô thị hóa nhanh chóng, nhu cầu tự động hóa và tối ưu hóa quản lý bãi đỗ xe trở nên cấp thiết hơn bao giờ hết.

Công nghệ AIoT – kết hợp giữa trí tuệ nhân tạo (AI) và Internet vạn vật (IoT) – mang đến giải pháp khả thi để xây dựng các bãi đỗ xe thông minh: tự động nhận diện xe qua camera, cập nhật tình trạng chỗ đỗ theo thời gian thực, hỗ trợ giám sát tập trung và nâng cao trải nghiệm người dùng, hướng tới một hệ thống hạ tầng đô thị hiện đại và hiệu quả hơn.

## Giải pháp

Nhóm đề xuất phát triển một hệ thống **Bãi đỗ xe thông minh**, nhằm tự động hóa và tối ưu hóa quy trình quản lý bãi xe. Hệ thống bao gồm các chức năng chính sau:

- **Tự động nhận diện biển số xe** hoặc **khuôn mặt tài xế** khi phương tiện ra vào, giúp loại bỏ thao tác thủ công như quét thẻ hay ghi tay.
- **Ghi nhận thời điểm vào – ra một cách chính xác**, đồng bộ dữ liệu theo thời gian thực.
- **Giám sát tình trạng chỗ đỗ (còn/trống)** thông qua cảm biến đặt tại từng vị trí và hiển thị bằng hệ thống đèn báo trực quan.
- **Lưu trữ toàn bộ dữ liệu** về phương tiện, người dùng và lịch sử ra vào trên nền tảng cloud (ví dụ như Firebase hoặc ThingsBoard), hỗ trợ truy xuất và phân tích khi cần.
- **Cung cấp giao diện dashboard trực quan**, giúp ban quản lý dễ dàng theo dõi tình trạng bãi xe, thống kê lưu lượng phương tiện và kiểm tra lịch sử hoạt động.

Hệ thống này không chỉ giúp **rút ngắn thời gian xử lý**, **giảm sai sót do con người**, mà còn có thể **triển khai linh hoạt** tại các khu vực như **trường học, khu dân cư, bãi xe công cộng hoặc cơ quan hành chính**, góp phần xây dựng hạ tầng đô thị thông minh và hiện đại.

## Phát Biểu Bài toán

### Dữ liệu đầu vào (input)

- Hình ảnh/video từ camera tại lối vào và lối ra bãi xe.

### Kết quả đầu ra (ouput)

- Kết quả nhận diện biển số hoặc khuôn mặt tại thời điểm vào – ra.
- Ghi nhận và lưu trữ thời điểm vào – ra xe.
- Hiển thị trạng thái chỗ đỗ (còn trống hoặc đã chiếm chỗ) theo thời gian thực.
- Giao diện trực quan cho người quản lý và người dùng.
- Dữ liệu được lưu trữ và truy xuất thông qua nền tảng cloud.

### Giới hạn hệ thống

- Môi trường lắp đặt (ánh sáng yếu, thời tiết xấu) ảnh hưởng đến độ chính xác nhận diện.
- Hệ thống cần camera có độ phân giải tối thiểu và lắp đặt đúng góc.
- Tài nguyên xử lý (RAM, bộ nhớ, mạng) cần đảm bảo để hệ thống hoạt động thời gian thực.
- Độ trễ thấp là yêu cầu bắt buộc để đảm bảo trải nghiệm người dùng.

## Đóng góp chính của đề tài

- Đề xuất mô hình hệ thống bãi đỗ xe thông minh tích hợp công nghệ **AIoT**, ứng dụng được vào thực tế.
- Tích hợp **nhận diện hình ảnh (biển số/khuôn mặt)** và **cảm biến IoT** để tự động hóa hoàn toàn quy trình vận hành.
- Thiết kế giao diện dashboard giúp quản lý dễ dàng theo dõi, giám sát và truy xuất lịch sử.
- Định hướng mở rộng và triển khai tại các bãi giữ xe trường học, tòa nhà, trung tâm thương mại...
- Hướng đến việc **giảm sai sót con người, nâng cao hiệu quả quản lý** và **tối ưu trải nghiệm người dùng**.
