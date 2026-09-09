# macOS Mail Job Hunter & Career Matcher 🎯

Tự động quét email tuyển dụng nhận được từ **Apple Mail (Mail.app)** trên macOS, phân tích các đường link đính kèm và đối chiếu tự động với 3 hồ sơ năng lực (CV):
1. **IT Manager / Infrastructure Head** (15+ năm kinh nghiệm, MNCs)
2. **IT Project Manager / Regional Operations** (Mô hình khu vực VN/Cambodia/Myanmar, PMP, ITIL)
3. **Cyber Security & Technology Risk Manager** (CISA certified, ISO 27001, BCP/DRP)

---

## 🌟 Tính Năng Nổi Bật

- **Tự động trích xuất trực tiếp từ Apple Mail:** Không cần cung cấp mật khẩu ứng dụng Gmail (App Password) hay bật IMAP không an toàn.
- **Thuật toán đối chiếu trọng số (Profile Matching):** Phân loại và gán nhãn mức độ phù hợp với từng định hướng CV.
- **Trích xuất link ứng tuyển thực tế (MIME/HTML Parsing):** Bóc tách email nguồn để lấy link ứng tuyển gốc trên Indeed, LinkedIn, VietnamWorks, ITviec...
- **Báo cáo HTML trực quan & Tự động mở:** Xuất kết quả ra giao diện web đẹp mắt `latest_report.html` và tự động bật trên trình duyệt.
- **Thông báo âm thanh macOS:** Bắn popup notification và chuông alert (`Glass`) trên máy tính mỗi khi quét xong.

---

## 🚀 Cấu Trúc Thư Mục

```text
job_hunter/
├── job_hunter.py       # Script Python chính xử lý quét Mail, bóc tách link và tạo báo cáo
├── run_job_hunter.sh   # Script Shell khởi động nhanh kiểm tra môi trường
├── reports/            # Thư mục lưu trữ lịch sử các file báo cáo HTML
│   └── latest_report.html
└── README.md           # Hướng dẫn sử dụng
```

---

## 🛠️ Hướng Dẫn Sử Dụng

### 1. Chạy thủ công từ Terminal
```bash
# Di chuyển vào thư mục hoặc chạy trực tiếp
~/.gemini/antigravity/scratch/job_hunter/run_job_hunter.sh
```

### 2. Tạo phím tắt `timviec` trên Terminal
Thêm lệnh tắt vào `~/.zshrc`:
```bash
echo "alias timviec='~/.gemini/antigravity/scratch/job_hunter/run_job_hunter.sh'" >> ~/.zshrc
source ~/.zshrc
```
Từ các lần sau, mỗi sáng bạn chỉ cần mở Terminal và gõ:
```bash
timviec
```

### 3. Tự động hóa mỗi sáng với Cronjob (Khuyên dùng)
Để máy tính tự động chạy quét vào **8:00 sáng mỗi ngày** từ Thứ 2 đến Thứ 7:
1. Gõ `crontab -e`
2. Thêm dòng sau:
```cron
0 8 * * 1-6 ~/.gemini/antigravity/scratch/job_hunter/run_job_hunter.sh >/dev/null 2>&1
```

---
*Tác giả:* [tuanweb2026](https://github.com/tuanweb2026)
