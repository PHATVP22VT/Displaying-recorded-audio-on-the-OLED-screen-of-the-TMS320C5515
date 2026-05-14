Chào bạn, xin lỗi vì sự nhầm lẫn ở câu trả lời trước. Dưới đây là nội dung chi tiết để bạn lưu vào file README.txt. Nội dung này tập trung hoàn toàn vào các bước thao tác kỹ thuật để chạy dự án trên MATLAB.

Để tạo file, bạn hãy copy đoạn dưới đây và dán vào Notepad (Windows) hoặc TextEdit (Mac) rồi lưu tên là HUONG_DAN_CHAY_DO_AN.txt.

HƯỚNG DẪN VẬN HÀNH DỰ ÁN NHẬN DẠNG GIỌNG NÓI TRÊN MATLAB
Lưu ý quan trọng: Bạn phải chạy các file theo đúng thứ tự từ 1 đến 7 vì kết quả của bước trước là dữ liệu đầu vào của bước sau.

BƯỚC 1: THIẾT LẬP MÔI TRƯỜNG
Copy tất cả các file có đuôi .m vào một thư mục làm việc duy nhất trên máy tính.

Mở MATLAB và dẫn đường dẫn (Current Folder) vào thư mục đó.

Đảm bảo Microphone của máy tính đang hoạt động.

BƯỚC 2: QUY TRÌNH CHẠY (7 BƯỚC)
Bước 1: Thu âm đầu vào (step1_record.m)

Gõ lệnh hoặc nhấn Run file này.

Nhìn vào cửa sổ Command Window, khi thấy dòng "Nhấn Enter để bắt đầu", hãy nhấn phím Enter và nói một từ bất kỳ vào mic (ví dụ: "hello").

MATLAB sẽ tạo ra file dữ liệu audio_recorded.mat.

Bước 2: Xử lý khung tín hiệu (step2_framing.m)

Chạy file này để chia nhỏ đoạn ghi âm vừa rồi thành các khung (frames) 256 mẫu.

Kiểm tra các hình vẽ hiện ra để xem tín hiệu đã được cắt khung và nhân cửa sổ Hamming chưa.

Bước 3: Biến đổi phổ (step3_fft.m)

Chạy file này để chuyển dữ liệu từ miền thời gian sang miền tần số.

Bạn sẽ thấy biểu đồ Spectrogram (phổ màu) của từ vừa nói.

Bước 4: Trích xuất đặc trưng (step4_mfcc.m)

Chạy file này để tính toán 13 hệ số MFCC. Đây là các thông số quan trọng nhất để máy "hiểu" đặc trưng giọng nói của bạn.

Bước 5: Tạo bộ từ điển mẫu (step5_template.m)

Đây là bước quan trọng nhất. Bạn cần chạy file này để MATLAB học các từ mẫu.

MATLAB sẽ yêu cầu bạn nói lần lượt 5 từ: hello, temperature, ready, error, complete.

Với mỗi từ, nhấn Enter, nói từ đó, chờ ghi âm xong rồi mới sang từ tiếp theo.

Kết quả sẽ được lưu vào file templates.mat.

Bước 6: Nhận dạng thực tế (step6_dtw_recognize.m)

Chạy file này để bắt đầu nhận dạng.

Nhấn Enter và nói một trong các từ có trong từ điển (ví dụ: "ready").

Thuật toán DTW sẽ so khớp và báo kết quả từ nào có khoảng cách (distance) nhỏ nhất.

Gõ q để thoát vòng lặp nhận dạng.

Bước 7: Hiển thị giao diện OLED (step7_oled_display.m)

Chạy file cuối cùng này để xem kết quả được mô phỏng trên màn hình OLED SSD1306 (giống như khi chạy trên kit DSP thực tế).
