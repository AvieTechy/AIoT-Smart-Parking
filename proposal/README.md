# Proposal: Hệ Thống Bãi Đỗ Xe Thông Minh

## Cấu trúc thư mục

```
proposal/
├── Makefile              # File tự động hóa biên dịch báo cáo
├── README.md             # Tài liệu hướng dẫn (file này)
├── content/              # Thư mục chứa nội dung báo cáo
│   ├── introduction.md   # Phần giới thiệu dự án
│   ├── metadata.yaml     # Metadata và thông tin định dạng báo cáo
│   └── ...               # Các phần nội dung khác
└── release/              # Thư mục chứa file báo cáo sau khi biên dịch
    └── proposal.pdf      # File PDF báo cáo đề xuất dự án
```


### Yêu cầu hệ thống

- **Pandoc**: Công cụ chuyển đổi định dạng văn bản
- **LaTeX**: Hệ thống soạn thảo tài liệu (để tạo PDF)
- **Make**: Công cụ tự động hóa quy trình biên dịch


## Cách sử dụng

Dự án này sử dụng công cụ `pandoc` để chuyển đổi từ Markdown sang định dạng PDF hoặc TEX. Để biên dịch báo cáo.

### Thêm nội dung

Bạn chỉ cần tạo file markdown là nội dung của bạn trong folder `content`, đặt tên theo cấu trúc `<stt>_<tên file>.md`

### Biên dịch báo cáo

Sử dụng các lệnh sau tại thư mục gốc (`./proposal`):

```bash
# Tạo file PDF (mặc định)
make

# Tạo file TEX
make tex

# Xóa các file đã tạo
make clean
```

File pdf sẽ được tạo ra ở thư mục `release`.
