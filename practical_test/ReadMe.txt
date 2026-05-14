================================================================================
HUONG DAN CHAY DU AN: NHAN DIEN GIONG NOI HIEN THI LEN OLED (DSP TMS320C5515)
================================================================================

I. YÊU CẦU CHUẨN BỊ
1. Phần cứng:
   - Kit eZdsp TMS320C5515 kết nối với máy tính qua cổng USB (JTAG).
   - Microphone kết nối với máy tính (hoặc micro tích hợp sẵn trên laptop).
2. Phần mềm:
   - Code Composer Studio (CCS) (Phiên bản tương thích với project, ví dụ CCS v4/v5/v6).
   - Python 3.x đã được cài đặt trên máy tính.

II. THIẾT LẬP MÔI TRƯỜNG
1. Cài đặt thư viện Python:
   Mở Command Prompt (cmd) hoặc Terminal và chạy lệnh sau để cài đặt các thư viện cần thiết:
   > pip install SpeechRecognition unidecode pyaudio
   (Lưu ý: pyaudio là thư viện lõi để SpeechRecognition có thể sử dụng microphone).

2. Đồng bộ đường dẫn file giao tiếp (Quan trọng):
   Mã nguồn hiện đang sử dụng đường dẫn tuyệt đối (hardcode) để lưu file `cmd.txt`. 
   Bạn cần đảm bảo thư mục này tồn tại trên máy hoặc sửa lại đường dẫn trong 2 file sau cho khớp với máy của bạn:
   - Trong file `pc_host.py`: Sửa biến `TEMP_DIR`.
   - Trong file `main.c`: Sửa macro `CMD_FILE_PATH`.
   * LƯU Ý: Đường dẫn trong file C phải dùng dấu `\\` thay vì `\`.

III. CÁC BƯỚC CHẠY DỰ ÁN

BƯỚC 1: KHỞI ĐỘNG VÀ NẠP CODE TRÊN DSP (CCS)
1. Mở phần mềm Code Composer Studio (CCS).
2. Import project chứa các file C (`main.c`, `oled_display.c`, `oled_test.c`...) vào workspace.
3. Nhấp chuột phải vào project, chọn "Build Project" (hoặc nhấn biểu tượng cái búa) để biên dịch. Đảm bảo không có lỗi (0 errors).
4. Khởi chạy phiên gỡ lỗi bằng cách chọn "Run" -> "Debug" (hoặc nhấn F11). Chờ CCS kết nối với kit qua JTAG và nạp chương trình vào bộ nhớ DSP.
5. Sau khi nạp xong, nhấn "Resume" (hoặc F8) để cho phép vi điều khiển DSP bắt đầu chạy. 
   - Lúc này, màn hình OLED sẽ được khởi tạo và xóa trắng.
   - Console của CCS sẽ in ra: "=== DSP Dang cho chuoi ky tu tu Python ===".

BƯỚC 2: KHỞI CHẠY SCRIPT NHẬN DIỆN TRÊN PC (PYTHON)
1. Mở Command Prompt (cmd) hoặc Terminal, di chuyển (cd) đến thư mục chứa file `pc_host.py`.
2. Chạy lệnh:
   > python pc_host.py
3. Trên màn hình cmd sẽ hiển thị thông báo "=== HE THONG NHAN DIEN GIONG NOI ===" và bắt đầu lắng nghe "[Dang nghe...]".

BƯỚC 3: THỰC NGHIỆM
1. Khi thấy dòng chữ "[Dang nghe...]" trên terminal Python, hãy nói một câu tiếng Việt rõ ràng vào microphone (Ví dụ: "Xin chào", "Kiểm tra hệ thống").
2. Quan sát luồng hoạt động:
   - Script Python sẽ nhận diện, in hoa, bỏ dấu, cắt phần thừa (giới hạn 50 ký tự) và ghi vào file `cmd.txt`.
   - DSP (đang chạy nền qua JTAG) sẽ tự động đọc sự thay đổi của file `cmd.txt`.
   - Màn hình OLED trên kit TMS320C5515 sẽ ngay lập tức hiển thị nội dung bạn vừa nói.
   - Nếu bạn nói câu dài hơn 20 ký tự, OLED sẽ hiển thị cảnh báo "QUA GIOI HAN 20!".

IV. KẾT THÚC VÀ DỌN DẸP
- Để dừng chương trình Python: Nhấn tổ hợp phím `Ctrl + C` trên cửa sổ cmd.
- Để dừng DSP: Nhấn nút "Suspend" (hoặc Alt+F8) sau đó nhấn "Terminate" (Ctrl+F2) trên giao diện debug của CCS để ngắt kết nối JTAG.
