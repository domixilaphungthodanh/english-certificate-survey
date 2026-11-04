# Khảo sát lựa chọn chứng chỉ tiếng Anh — TDTU

Phân tích dữ liệu thực của 89 phản hồi, tổng hợp toàn bộ 32 câu hỏi.

- [Báo cáo mở offline](reports/report.html)
- [Báo cáo Markdown](reports/findings.md)
- [Notebook đã chạy](notebooks/01_survey_analysis.ipynb)
- [Danh mục 32 câu hỏi](reports/question_catalog.csv)
- [Tần số và tỷ lệ](reports/frequencies.csv)
- [17 mục Likert](reports/likert_summary.csv)
- Cờ mâu thuẫn từng dòng giữ cục bộ, không công khai.

## Chạy lại

Python 3.10+; cài `python -m pip install -r requirements.txt`, sau đó `python run_all.py`.
CSV nguồn nằm trong `data/raw/responses.csv`, xuất từ trang tính liên kết biểu mẫu ngày 04/11/2026. Mỗi dòng là một lần gửi biểu mẫu; không mặc định là một người duy nhất. Kiểm tra 89 dòng chỉ áp dụng snapshot này; khi có phản hồi mới cần cập nhật kiểm tra kỳ vọng.

Notebook cần nbformat, nbclient, ipykernel và Jupyter Notebook để mở tương tác. Dữ liệu gốc giữ nguyên; bảng mapping khoa và cờ mâu thuẫn là phần bổ sung. Cột email và dấu thời gian không được đưa vào báo cáo. Nội dung góp ý mở là dữ liệu người trả lời, cần rà soát trước khi chia sẻ công khai.

## Cách tính

Câu đơn: phần trăm trên số người trả lời câu. Câu nhiều lựa chọn: đếm từng lựa chọn, phần trăm trên số người trả lời câu; tổng có thể vượt 100%. Tách theo dấu phẩy xuất từ Google Forms; câu trả lời khác chứa dấu phẩy có thể cần đối chiếu thủ công. Likert: phân phối 1–5, trung vị, trung bình và tỷ lệ 4–5; chưa gán ý nghĩa các nhãn thang điểm nếu chưa xác minh hướng dẫn gốc.

Q32: phân loại các câu không góp ý bằng danh sách từ quy tắc trong mã; không coi đây là mã hoá chủ đề đã được chuyên gia xác nhận. Không xoá người trả lời vì mâu thuẫn. Không chạy hồi quy/EFA/Cronbach tự động nếu chưa xác minh cấu trúc thang đo và giả định. Không kết luận nhân quả hoặc tính đại diện toàn trường.

Nguồn: Google Form và Google Sheet do người dùng cung cấp. Chi tiết nguồn và SHA-256 ở reports/manifest.json.

## Bản GitHub

Dữ liệu từng người và nguyên văn góp ý không được công khai. Notebook chứa sẵn kết quả; để chạy lại trên dữ liệu gốc, xem data/README.md.

