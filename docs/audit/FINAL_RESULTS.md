# Kết quả cuối trên TEST (P4b) — hm500k, protocol mốc thời gian chung

- Chạy: `python scripts/11_final.py --reason "..."` ở commit `7805907` (tree sạch), 3 seed (42, 2024, 2025),
  mỗi seed 1 dòng trong `docs/audit/test_access_log.csv` (3 dòng, không có lần truy cập test nào khác).
- Mỗi mô hình dùng cấu hình tốt nhất trên val (`best_configs.json`), train trên train, early stopping trên val,
  chấm test: 2.893 user, candidate = 10.345 item có trong train, loại item user đã có trong train ∪ val.
- Kiểm định: `python scripts/12_significance.py` (PREREG mục 6/8). Số liệu: `neumf_project_v2/outputs/final/`
  (`summary.csv`, `significance.csv`, `seed*/results_per_user.csv`, `seed*/topk.json`, checkpoint từng seed).
- Thời gian: 64,8 phút (24,1 + 21,0 + 19,7).

## Bảng 1 — mean ± std qua 3 seed (test)

| Mô hình | NDCG@10 | Recall@10 | HR@10 | Precision@10 | NDCG@5 |
|---|---|---|---|---|---|
| BPR-MF | **0,01062 ± 0,00009** | **0,01579 ± 0,00015** | **0,04666 ± 0,00035** | **0,00510 ± 0,00011** | **0,00811 ± 0,00045** |
| NeuMF-Pretrained | 0,01001 ± 0,00041 | 0,01443 ± 0,00081 | 0,04471 ± 0,00208 | 0,00487 ± 0,00016 | 0,00787 ± 0,00075 |
| MostPopular | 0,00998 ± 0,00000 | 0,01469 ± 0,00000 | 0,04666 ± 0,00000 | 0,00501 ± 0,00000 | 0,00799 ± 0,00000 |
| MLP | 0,00959 ± 0,00005 | 0,01382 ± 0,00074 | 0,04275 ± 0,00100 | 0,00479 ± 0,00016 | 0,00758 ± 0,00059 |
| NeuMF-Scratch | 0,00958 ± 0,00017 | 0,01404 ± 0,00072 | 0,03964 ± 0,00121 | 0,00425 ± 0,00027 | 0,00768 ± 0,00029 |
| GMF | 0,00945 ± 0,00080 | 0,01425 ± 0,00121 | 0,04252 ± 0,00419 | 0,00461 ± 0,00047 | 0,00704 ± 0,00061 |
| Random | 0,00063 ± 0,00004 | 0,00092 ± 0,00011 | 0,00300 ± 0,00040 | 0,00030 ± 0,00004 | 0,00046 ± 0,00016 |

## Bảng 2 — kiểm định paired theo user (NDCG@10 TB qua 3 seed, 2.893 user; Holm trên 8 so sánh)

| A | B | NDCG@10 A | NDCG@10 B | Chênh tương đối | CI 95% bootstrap của chênh lệch | p Wilcoxon | p Holm | Kết luận |
|---|---|---|---|---|---|---|---|---|
| NeuMF-Pretrained | BPR-MF | 0,01001 | 0,01062 | −5,8% | [−0,00172; 0,00055] | 0,021 | 0,168 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | MostPopular | 0,01001 | 0,00998 | +0,2% | [−0,00088; 0,00095] | 0,701 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | GMF | 0,01001 | 0,00945 | +5,9% | [−0,00005; 0,00119] | 0,112 | 0,787 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | MLP | 0,01001 | 0,00959 | +4,3% | [−0,00067; 0,00152] | 0,325 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | NeuMF-Scratch | 0,01001 | 0,00958 | +4,4% | [−0,00108; 0,00195] | 0,739 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Scratch | BPR-MF | 0,00958 | 0,01062 | −9,8% | [−0,00278; 0,00070] | 0,227 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Scratch | GMF | 0,00958 | 0,00945 | +1,4% | [−0,00138; 0,00164] | 0,539 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Scratch | MLP | 0,00958 | 0,00959 | −0,1% | [−0,00184; 0,00181] | 0,721 | 1,000 | không khác biệt có ý nghĩa |

## Kết luận (đúng quy tắc PREREG mục 6)
- **Không có so sánh nào đạt "tốt hơn"**: cả 8 đều có CI chứa 0 và p Holm ≥ 0,05.
- NeuMF (cả Scratch lẫn Pretrained) **không vượt** baseline BPR-MF, và ngang MostPopular. BPR-MF có trung bình cao
  nhất (0,01062), nhưng NeuMF-Pretrained thấp hơn 5,8% vẫn là "không khác biệt có ý nghĩa" (p Holm 0,168).
- Mô hình lai được chọn theo val (mục 7) là NeuMF-Scratch (val 0,01107). Trên test nó đứng dưới NeuMF-Pretrained
  (0,00958 vs 0,01001). Thứ hạng trên val không giữ được trên test: chênh lệch giữa các mô hình nhỏ hơn nhiễu.
- Kết hợp GMF + MLP (NeuMF) không tốt hơn từng nhánh riêng một cách có ý nghĩa (so sánh 3, 4, 7, 8).
- Hạn chế: dữ liệu thưa (201.801 cặp train, 7.519 user); mô hình neural đạt đỉnh sau 1–9 epoch; test cách train
  4 tuần (val nằm giữa, không đưa vào train). Kết quả chỉ nói về mẫu hm500k và protocol này.
