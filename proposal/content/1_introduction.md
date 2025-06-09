# Giới thiệu

## Bối cảnh

Trong bối cảnh đô thị hóa diễn ra mạnh mẽ, việc quản lý hiệu quả các bãi đỗ xe tại các khu vực tập trung đông người như chung cư, trường học, và tòa nhà văn phòng ngày càng trở nên cấp thiết. Hiện nay, nhiều bãi đỗ xe đã ứng dụng công nghệ thẻ từ (RFID) và phần mềm quản lý cơ bản, tuy nhiên, các giải pháp này thường gặp phải những hạn chế đáng kể:

- **Thiếu tự động hóa:** Quy trình vận hành vẫn phụ thuộc nhiều vào thao tác thủ công như quét thẻ, ghi nhận thông tin, dễ dẫn đến sai sót (mất thẻ, quên thẻ, ghi nhận sai) và tốn thời gian.
- **Thiếu thông tin thời gian thực:** Hệ thống không giám sát được tình trạng thực tế của từng vị trí đỗ, khiến người dùng không biết trước bãi xe còn chỗ hay không, gây bất tiện và lãng phí thời gian tìm kiếm.
- **Lưu trữ dữ liệu cục bộ:** Dữ liệu thường được lưu trữ nội bộ, thiếu khả năng đồng bộ lên các nền tảng trực tuyến, gây khó khăn trong việc truy xuất và phân tích khi cần thiết, đặc biệt khi có sự cố.

Những hạn chế này không chỉ làm giảm hiệu quả quản lý mà còn ảnh hưởng tiêu cực đến trải nghiệm của người dùng. Do đó, nhu cầu về một giải pháp quản lý bãi đỗ xe thông minh, tự động hóa cao và cung cấp thông tin chính xác theo thời gian thực là vô cùng lớn. Công nghệ AIoT (Artificial Intelligence of Things), với sự kết hợp giữa Trí tuệ Nhân tạo (AI) và Internet Vạn vật (IoT), mở ra tiềm năng to lớn để giải quyết những thách thức này, hướng tới xây dựng một hệ thống hạ tầng đô thị hiện đại và hiệu quả hơn.

## Mục đích

Đề tài này nhằm mục đích nghiên cứu, thiết kế và xây dựng một mô hình thử nghiệm (prototype) **Hệ thống Bãi đỗ xe Thông minh** ứng dụng công nghệ AIoT. Hệ thống hướng đến việc tự động hóa toàn diện quy trình quản lý phương tiện ra vào, tối ưu hóa việc sử dụng không gian đỗ xe, giảm thiểu sự can thiệp của con người, đồng thời nâng cao trải nghiệm người dùng và hiệu quả vận hành cho đơn vị quản lý.

## Mục tiêu

Để đạt được mục đích đã đề ra, hệ thống tập trung vào ba nhóm mục tiêu chính. Mỗi mục tiêu được cụ thể hóa bằng các tiêu chí định lượng nhằm đảm bảo khả năng kiểm chứng trong quá trình phát triển và đánh giá hệ thống.

### Nhận diện tự động

Xây dựng chức năng nhận diện gương mặt, biển số xe hoạt động ổn định trong điều kiện thực tế.

**Các tiêu chí đánh giá:**

- Tỷ lệ nhận diện chính xác gương mặt và biển số xe đạt trên 80% trong điều kiện ánh sáng ban ngày.
- Tỷ lệ nhận diện chính xác đạt trên 70% trong điều kiện ánh sáng yếu (ví dụ: buổi tối có đèn chiếu sáng của bãi xe).
- Hệ thống được kiểm thử trên một tập dữ liệu 6 lượt xe vào/ra khác nhau.

### Đảm bảo hiệu suất và tính thời gian thực

Đảm bảo hệ thống phản hồi nhanh và cập nhật kịp thời các thay đổi từ thực tế.

**Các tiêu chí đánh giá:**

- Thời gian xử lý trung bình cho một lượt xe (tính từ lúc xe dừng đúng vị trí đến khi hệ thống xử lý xong) không vượt quá 5 giây.
- Trạng thái của các vị trí đỗ xe (trống hoặc có xe) được cập nhật lên giao diện quản lý trong vòng tối đa 3 giây kể từ khi có sự thay đổi thực tế từ cảm biến.

### Hoàn thiện tính năng quản lý bãi xe quy mô nhỏ

Xây dựng đầy đủ các chức năng cần thiết để vận hành một mô hình bãi xe nhỏ (5–10 vị trí đỗ xe).

**Các tiêu chí đánh giá:**

- Xây dựng và kiểm thử đầy đủ 100% các mô-đun chính của hệ thống.
- Ghi nhận thông tin xe vào/ra (biển số, thời gian) một cách tự động.
- Giám sát và hiển thị trực quan trạng thái của từng vị trí đỗ xe.
- Lưu trữ lịch sử các lượt gửi xe trên nền tảng cloud.
- Cung cấp giao diện dashboard cho phép người quản lý theo dõi hoạt động và truy xuất dữ liệu cơ bản.

## Phát biểu bài toán

### Dữ liệu đầu vào

- Hình ảnh chất lượng cao từ camera giám sát tại các lối vào và lối ra của bãi xe.

### Kết quả đầu ra

- Thông tin nhận diện chính xác (biển số xe, khuôn mặt) tại thời điểm phương tiện vào – ra.
- Bản ghi chi tiết về thời gian vào – ra của từng phương tiện.
- Trạng thái cập nhật liên tục của từng vị trí đỗ (còn trống/đã chiếm chỗ).
- Giao diện dashboard trực quan, dễ sử dụng cho người quản lý và thông tin cho người dùng.
- Cơ sở dữ liệu được lưu trữ an toàn và có khả năng truy xuất hiệu quả trên nền tảng cloud.

## Phạm vi và Giới hạn của Hệ thống

### Phạm vi triển khai

Hệ thống được thiết kế với định hướng triển khai tại các tổ chức và doanh nghiệp có nhu cầu kiểm soát an ninh và quản lý phương tiện ra vào một cách tự động và hiệu quả, ví dụ như:

- Công ty, tòa nhà văn phòng.
- Nhà máy, khu công nghiệp.
- Trường học, bệnh viện.

Mô hình hoạt động phù hợp với các đơn vị có sẵn hạ tầng mạng cục bộ ổn định và có khả năng đầu tư cơ bản vào thiết bị như ESP32-CAM, ESP32 điều khiển trung tâm và màn hình hiển thị. Ban đầu, hệ thống sẽ được phát triển dưới dạng một mô hình thử nghiệm (prototype) cho một bãi đỗ xe quy mô nhỏ (5-10 chỗ) để kiểm chứng tính khả thi và hiệu quả của các giải pháp công nghệ được lựa chọn.

*Lưu ý: Trong giai đoạn hiện tại, hệ thống chưa tích hợp chức năng thu phí tự động. Tuy nhiên, đây là một hướng phát triển tiềm năng trong tương lai, đặc biệt khi ứng dụng tại các bãi xe công cộng hoặc dịch vụ.*

### Giới hạn của Hệ thống

Hệ thống nhận diện và quản lý tự động có thể gặp một số giới hạn sau:

- **Điều kiện môi trường:** Độ chính xác của module nhận diện hình ảnh (biển số, khuôn mặt) có thể bị ảnh hưởng bởi các yếu tố như ánh sáng yếu (ban đêm, khu vực thiếu sáng), điều kiện thời tiết bất lợi (mưa lớn, sương mù dày đặc), hoặc góc quay camera không tối ưu.
- **Chất lượng camera:** Yêu cầu camera có độ phân giải đủ tốt và được lắp đặt ở vị trí phù hợp để đảm bảo chất lượng hình ảnh đầu vào cho quá trình nhận diện.
- **Tài nguyên phần cứng:** Hệ thống cần được cung cấp đủ tài nguyên xử lý (CPU, RAM), dung lượng lưu trữ và băng thông mạng để đảm bảo hoạt động ổn định và đáp ứng yêu cầu thời gian thực.
- **Độ trễ hệ thống:** Mặc dù mục tiêu là giảm thiểu độ trễ, một khoảng trễ nhất định trong quá trình xử lý dữ liệu và phản hồi là khó tránh khỏi, cần được tối ưu để không ảnh hưởng đến trải nghiệm người dùng.

## Đóng góp chính của Đề tài

Đề tài dự kiến mang lại những đóng góp khoa học và thực tiễn sau:

- **Đề xuất mô hình hệ thống bãi đỗ xe thông minh toàn diện:** Tích hợp công nghệ AIoT một cách hiệu quả, có khả năng ứng dụng vào thực tế tại Việt Nam.
- **Tự động hóa quy trình vận hành:** Kết hợp nhận diện hình ảnh (biển số/khuôn mặt) để giảm thiểu tối đa sự can thiệp thủ công, nâng cao độ chính xác.
- **Nâng cao hiệu quả quản lý và trải nghiệm người dùng:** Cung cấp công cụ giám sát trực quan cho người quản lý và thông tin hữu ích cho người dùng (ví dụ: tình trạng chỗ trống).
- **Định hướng phát triển và mở rộng:** Tạo tiền đề cho việc triển khai hệ thống tại các loại hình bãi đỗ xe khác nhau (trường học, tòa nhà, trung tâm thương mại) và tích hợp thêm các tính năng nâng cao trong tương lai.
- **Giảm thiểu sai sót và tối ưu hóa nguồn lực:** Góp phần giảm thiểu các lỗi thường gặp trong quản lý thủ công và sử dụng hiệu quả hơn nguồn nhân lực.

\pagebreak
