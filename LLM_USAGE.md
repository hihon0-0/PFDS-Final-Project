# Sử dụng công cụ LLM trong đồ án

Đề yêu cầu mỗi thành viên khai báo trung thực cách dùng LLM. Bảng dưới có sẵn một dòng mô tả bản nháp ban đầu; **mỗi thành viên tự bổ sung các lần dùng của mình** (công cụ, mục đích, đã kiểm chứng gì, đã sửa gì).

| Ngày | Thành viên | Công cụ | Dùng để làm gì | Đã kiểm chứng / chỉnh sửa như thế nào |
|---|---|---|---|---|
| 20/11/2026 | Hoàng Hùng Quân | Claude (Anthropic) | Sinh bản nháp đầu tiên của 3 notebook, module `src/`, README từ đề bài và dataset: đề xuất 6 câu hỏi, code làm sạch/ghép bảng, phân tích, mô hình, biểu đồ, phần kết luận | *(TODO: ghi rõ nhóm đã chạy lại, đọc hiểu, kiểm tra con số, sửa/viết lại những phần nào)* |
| 23/11/2026 | Huỳnh Huy Hoàng | Gemini (Antigravity) | Thảo luận bản chất Nghịch lý Simpson ở Q4, gợi ý các biến kiểm soát confounder và thiết kế kiểm tra độ vững (robustness checks) cho Q3 & Q4 | Tự chạy lại toàn bộ mô hình OLS cluster-robust và bootstrap trên máy, đối chiếu khớp từng con số % với output notebook và tự viết lại nhận định |
| | | | | |

## Nguyên tắc nhóm áp dụng
- Mọi con số trong phần kết luận phải được **chạy lại và đối chiếu** với output notebook.
- Mỗi người phải **giải thích được toàn bộ code** của câu hỏi mình phụ trách (và hiểu các câu khác) – giảng viên có thể hỏi bất kỳ phần nào trong buổi Q&A.
- Phần **phản tư cá nhân** (cuối notebook 03) do từng người tự viết.
