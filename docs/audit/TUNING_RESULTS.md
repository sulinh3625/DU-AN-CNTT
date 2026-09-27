# Kết quả tuning (P4a) — CHỈ validation, seed 42

> **Loop 14:** theo quyết định người dùng, iALS, MostPopular-Recent, CFNet (C) và fusion B đã bỏ khỏi đề tài
> và code (PREREG mục 8). Số của chúng dưới đây giữ lại để minh bạch; không đánh giá trên test.

Nguồn: `docs/audit/tuning_log.csv` (57 dòng, toàn bộ ở commit `d1cfa3f`, git_dirty = False) và
`docs/audit/best_configs.json`; chạy bằng `python scripts/10_tune.py --model all` (protocol mốc thời gian chung,
2.275 user val, Full Ranking trên 10.345 item train). Tổng thời gian 1,90 giờ GPU (≤ 4,5 giờ PREREG → không cắt cấu hình).
**Chưa có số test nào.** Số val của cấu hình tốt nhất lạc quan (chọn trên chính val) — không dùng để kết luận.

| Hạng | Mô hình | Cấu hình tốt nhất | NDCG@10 | Recall@10 | HR@10 | Prec@10 | NDCG@5 | best epoch các cấu hình | Thời gian tune |
|---|---|---|---|---|---|---|---|---|---|
| 1 | B: fusion iALS + NeuMF-Scratch | w(MF) = 0,6 | **0,01260** | **0,01835** | **0,04396** | 0,00457 | **0,01011** | — | 0,6 phút |
| 2 | C: CFNet | lr 5e-4, neg 4, d 32, wd 1e-6, dropout 0,2, rl [256,64] | 0,01169 | 0,01630 | 0,04352 | **0,00479** | 0,00911 | 2,2,3,4,3,2 | 26,7 phút |
| 3 | iALS | factors 64, λ 0,001, α 10 | 0,01141 | 0,01560 | 0,04000 | 0,00422 | 0,00915 | — | 0,8 phút |
| 4 | NeuMF-Scratch | lr 5e-4, neg 4, d 64, wd 1e-6, dropout 0,2 | 0,01107 | 0,01515 | 0,04088 | 0,00453 | 0,00867 | 2,2,8,3,5,7 | 19,9 phút |
| 5 | NeuMF-Pretrained | GMF d64 + MLP d32; lr 1e-4, α 0,3, neg 8, wd 0 | 0,00913 | 0,01255 | 0,03341 | 0,00374 | 0,00786 | 1,1,2,2,2,7 | 18,5 phút |
| 6 | BPR-MF | d 32, lr 0,03, reg 0,005, 20 epoch (= mặc định) | 0,00912 | 0,01386 | 0,03824 | 0,00444 | 0,00688 | — | 17,4 phút |
| 7 | MostPopular-Recent | cửa sổ 56 ngày | 0,00845 | 0,01258 | 0,03209 | 0,00352 | 0,00651 | — | 0,1 phút |
| 8 | GMF | lr 5e-4, neg 4, d 64, wd 0 | 0,00843 | 0,01213 | 0,03033 | 0,00343 | 0,00665 | 1,1,8,6,4,9 | 15,1 phút |
| 9 | MLP | lr 1e-3, neg 8, d 32, wd 0, dropout 0,2 | 0,00837 | 0,01420 | 0,03648 | 0,00413 | 0,00580 | 2,5,3,3,1,1 | 15,1 phút |

Tham chiếu không tune (không có siêu tham số, loop 9): MostPopular 0,0079; iALS mặc định 0,00906.

## Nhận xét (mô tả, chưa kiểm định)
- **iALS đã tune là baseline MF mạnh** (+26% so với mặc định), đúng như Rendle 2020/2022. NeuMF-Scratch (0,01107)
  **chưa vượt** iALS trên val; NeuMF-Pretrained còn thấp hơn Scratch — pretrain GMF/MLP không giúp trên dữ liệu này.
- Chênh lệch giữa các mô hình top đầu ~0,0003–0,0015 NDCG@10 trên 2.275 user: rất có thể nằm trong nhiễu;
  chỉ kết luận sau P4b (3 seed, test, Wilcoxon + bootstrap + Holm).
- Mô hình neural đạt đỉnh rất sớm (epoch 1–3 phần lớn) → quá khớp nhanh với dữ liệu thưa (201.801 cặp train).
- Fusion B: w = 0 cho đúng NeuMF-Scratch (0,01107), w = 1 cho đúng iALS (0,01141) → trộn đúng; mọi w ∈ [0,1; 0,8]
  đều cao hơn cả hai thành phần → hai mô hình bổ sung cho nhau. Lưu ý: w chọn trên cùng tập val → lạc quan hơn C.
- MLP ≈ GMF về NDCG@10 nhưng Recall/HR cao hơn — thứ hạng phụ thuộc metric.

## Hệ quả theo PREREG
- Mục 7 — "mô hình lai tốt nhất" (val NDCG@10 cao nhất trong {NeuMF-Scratch, NeuMF-Pretrained, B, C}): **B
  (fusion iALS + NeuMF-Scratch, w = 0,6)**.
- Mục 6 — so sánh 8: mô hình MF tốt nhất trên val = **iALS**.
- Cấu hình cho P4b: `docs/audit/best_configs.json` (checkpoint seed 42 ở `neumf_project_v2/outputs/tuning/`).
