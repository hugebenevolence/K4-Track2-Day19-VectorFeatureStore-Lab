# Reflection — Lab 19

**Tên:** Tran Dai Nhan
**Cohort:** A20-K4
**Path đã chạy:** Lite và Docker (Python 3.13, Windows)

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên 50 câu hỏi, path Lite có hybrid Precision@10 **78,6%**, BM25 **77,8%**, vector **73,2%**. Với `exact`, BM25 và hybrid cùng **96,7%** vì thuật ngữ xuất hiện nguyên văn. Với `mixed`, hybrid **100%**, vượt BM25 **97,0%** và vector **98,5%** nhờ kết hợp tín hiệu. Bất ngờ là `paraphrase` Lite có BM25 **33,3%**, hybrid **32,0%**, vector **24,0%**: model `bge-small-en-v1.5` thiên tiếng Anh. Đo lại với `bge-m3` trên Docker, vector đạt **95,2%**, hybrid **89,0%**; riêng `paraphrase`, vector **86,7%** so với hybrid **66,7%**. Tôi dùng BM25 thuần cho mã lỗi, tên API và thuật ngữ chính xác khi cần latency thấp; dùng vector thuần khi đã chứng minh chất lượng paraphrase và BM25 không thêm tín hiệu.

---

## Điều ngạc nhiên nhất khi làm lab này

Kết quả paraphrase Lite đi ngược dự đoán; phép đo Docker chứng minh chọn model có thể thay đổi mode thắng. Tôi sẽ đo từng nhóm query thay vì giả định RRF luôn tốt nhất.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work
