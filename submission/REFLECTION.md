# Reflection — Lab 19

**Tên:** Tran Dai Nhan
**Cohort:** A20-K4
**Path đã chạy:** Lite (Python 3.13, Windows)

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên 50 câu hỏi, hybrid đạt Precision@10 **78,6%**, so với BM25 **77,8%** và vector **73,2%**. Với `exact`, BM25 và hybrid cùng **96,7%**: thuật ngữ xuất hiện nguyên văn nên BM25 đã đủ mạnh. Với `mixed`, hybrid đạt **100%**, vượt BM25 **97,0%** và vector **98,5%** vì RRF kết hợp tín hiệu từ khóa và ngữ nghĩa. Bất ngờ là `paraphrase` trên path Lite lại có BM25 **33,3%**, hybrid **32,0%**, vector **24,0%**. Model `bge-small-en-v1.5` thiên về tiếng Anh, nên không thể khẳng định vector luôn thắng với câu Việt diễn đạt lại. Tôi sẽ đo lại bằng embedding đa ngữ và lập chỉ mục mới trước khi chọn model. Tôi dùng BM25 thuần khi query có mã lỗi, tên API hoặc thuật ngữ chính xác và cần latency thấp; dùng vector thuần khi đã kiểm chứng chất lượng paraphrase, còn phần từ khóa không đem thêm tín hiệu đáng kể.

---

## Điều ngạc nhiên nhất khi làm lab này

Kết quả paraphrase đi ngược dự đoán của rubric; phép đo theo từng nhóm query giúp thấy giới hạn của model mặc định thay vì chỉ nhìn trung bình.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work
