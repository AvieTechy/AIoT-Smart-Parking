# Giới thiệu

## Bối cảnh

Trong bối cảnh đô thị hóa nhanh chóng, việc quản lý bãi đỗ xe tại các khu vực đông dân cư như chung cư, trường học, tòa nhà văn phòng đang gặp nhiều thách thức. Các hệ thống hiện tại sử dụng thẻ từ (RFID) và phần mềm quản lý cơ bản vẫn còn nhiều hạn chế:

- **Thiếu tự động hóa:** Phụ thuộc vào thao tác thủ công, dễ sai sót và tốn thời gian.
- **Thiếu thông tin thời gian thực:** Không giám sát được tình trạng từng vị trí đỗ, gây bất tiện cho người dùng.
- **Lưu trữ dữ liệu cục bộ:** Khó khăn trong truy xuất và phân tích dữ liệu khi cần thiết.

Công nghệ AIoT (Artificial Intelligence of Things) với sự kết hợp giữa AI và IoT mở ra tiềm năng lớn để giải quyết những thách thức này, hướng tới xây dựng hệ thống quản lý bãi đỗ xe thông minh, tự động và hiệu quả.

## Mục đích

Đề tài này nhằm mục đích nghiên cứu, thiết kế và xây dựng một mô hình thử nghiệm (prototype) **Hệ thống Bãi đỗ xe Thông minh** ứng dụng công nghệ AIoT. Hệ thống hướng đến việc tự động hóa toàn diện quy trình quản lý phương tiện ra vào, tối ưu hóa việc sử dụng không gian đỗ xe, giảm thiểu sự can thiệp của con người, đồng thời nâng cao trải nghiệm người dùng và hiệu quả vận hành cho đơn vị quản lý.

## Mục tiêu

Để đạt được mục đích đã đề ra, hệ thống tập trung vào ba nhóm mục tiêu chính. Mỗi mục tiêu được cụ thể hóa bằng các tiêu chí định lượng nhằm đảm bảo khả năng kiểm chứng trong quá trình phát triển và đánh giá hệ thống.

| ID   | Mục tiêu                     | Chỉ số đo                  | Điều kiện đạt           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `O-01` | Xây dựng chức năng nhận diện gương mặt và biển số xe hoạt động ổn định trong điều kiện ban ngày và ảnh nhòe/không rõ nét | Accuracy $\ge$ 90% (ban ngày); Accuracy $\ge$ 70% (ảnh nhòe)                                            | Test trên $\ge$ 100 lượt xe vào/ra với dữ liệu đa dạng, gồm ảnh rõ và ảnh nhòe |
| `O-02` | Đảm bảo hệ thống phản hồi nhanh và cập nhật thời gian thực                                                               | Thời gian xử lý 1 lượt $le$ 15 giây; Cập nhật trạng thái slot $\le$ 5 giây                             | Môi trường test chuẩn, kết nối mạng ổn định                                |
| `O-03` | Hoàn thiện đầy đủ tính năng quản lý bãi xe quy mô nhỏ (5–10 vị trí)                                                      | 100% module hoạt động; tự động ghi nhận biển số & thời gian; lưu trữ cloud; dashboard trực quan | Đáp ứng đầy đủ yêu cầu vận hành thử nghiệm                                 |

## Phát biểu bài toán

### Dữ liệu đầu vào

- Hình ảnh chất lượng cao từ camera giám sát tại các lối vào và lối ra của bãi xe.

### Kết quả đầu ra

- Thông tin nhận diện với độ chính xác $\ge$ 90% (điều kiện ban ngày) và $\ge$ 70% (ảnh nhòe/không rõ nét) cho biển số xe và khuôn mặt tại thời điểm phương tiện vào – ra.
- Bản ghi chi tiết về thời gian vào – ra của từng phương tiện với thời gian xử lý ≤ 15 giây/lượt.
- Trạng thái cập nhật liên tục của từng vị trí đỗ (còn trống/đã chiếm chỗ) với thời gian cập nhật ≤ 5 giây.
- Giao diện dashboard trực quan, dễ sử dụng cho người quản lý và thông tin cho người dùng với uptime ≥ 99%.
- Cơ sở dữ liệu được lưu trữ an toàn và có khả năng truy xuất hiệu quả trên nền tảng cloud với tỷ lệ thành công ≥ 95%.

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
