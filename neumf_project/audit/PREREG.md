# Đăng ký trước (pre-registration) — thực nghiệm hm500k

Ngày đăng ký: 27/09/2026, loop 11, nhánh `loop/hm500k-audit`. File này được commit TRƯỚC mọi lần đánh giá
trên tập test của các mô hình dưới đây (`scripts/03_run_experiment.py --final` từ chối chạy nếu file chưa commit).
Mọi lệch khỏi kế hoạch phải ghi vào mục "Lệch kế hoạch" ở cuối file VÀ vào báo cáo.

## 1. Dữ liệu & protocol
- Dữ liệu: hm500k (`scripts/00_sample_hm.py`, mẫu ~500k dòng theo khách hàng, toàn bộ 2018-09-20 → 2020-09-22),
  aggregate cặp user–item → k-core **10** (lệch bất biến k=5, lý do RAM — Q2) → 7.519 users × 10.345 items.
- **Protocol chính** (`configs/hm500k_global.yaml`): một mốc thời gian chung, xếp cặp theo lần mua đầu:
  train < 2020-07-01 ≤ val < 2020-07-29 ≤ test (đến 2020-09-22). Val/test chỉ giữ user & item đã có trong train;
  mỗi user có thể nhiều item đúng. Full Ranking trên pool = item đã có trong train, loại item user đã có trong
  train (val) hoặc train ∪ val (test). Tie-break xác định (seed 2026).
- **Protocol phụ** (`configs/hm500k.yaml`): leave-one-out theo thời gian từng user (để so với NCF gốc).
  Chạy cùng cấu hình tốt nhất; không dùng để chọn mô hình.
- Sampled-99 chỉ để đối chiếu, không dùng để kết luận.

## 2. Độ đo
- **Metric chính (kết luận):** NDCG@10 Full Ranking trên test của protocol chính, trung bình theo user.
- **Metric chọn mô hình/siêu tham số:** NDCG@10 Full Ranking trên **validation** của protocol chính.
- Metric phụ: Recall@10, Precision@10, HR@10, NDCG@5; long-tail, cold/warm, coverage/novelty (mô tả, không kết luận).
- Định nghĩa nhiều item đúng: HR@K = 1[có ít nhất 1 item đúng trong top-K]; Recall@K = hits/|test_u|;
  Precision@K = hits/K; NDCG@K = DCG/IDCG với IDCG theo min(|test_u|, K) (`src/evaluation/metrics.py`).

## 3. Mô hình
| Nhóm | Mô hình |
|---|---|
| Baseline | Random, MostPopular, BPR-MF |
| Ablation | GMF (MF), MLP (DNN) |
| Mô hình đề tài | NeuMF-Scratch, NeuMF-Pretrained |

(Sửa loop 14 — xem mục 8. Bản đăng ký ban đầu còn MostPopular-Recent, iALS, EarlyFusion, B, C.)

ItemKNN không chạy (10.345 item > ngưỡng dense 5.000) — ghi là hạn chế. (Bản thưa top-k, UserKNN và late fusion
MF + DNN được thêm sau khi đã xem test: mục 9.)

## 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số)
- Tuning chỉ trên validation, seed 42, mỗi mô hình **6 cấu hình**, lấy bằng một lần rút ngẫu nhiên cố định
  (numpy seed 0) từ lưới của mô hình đó; cấu hình mặc định hiện tại luôn là 1 trong 6. Neural: tối đa 20 epoch,
  early stopping patience 5 theo val NDCG@10. Mọi cấu hình ghi vào `tuning_log.csv` (config hash, git commit,
  val metrics, thời gian).
- Lưới:
  - GMF / MLP / EarlyFusion / NeuMF-Scratch / CFNet: lr {1e-3, 5e-4}, negative_ratio {4, 8}, embedding_dim {32, 64},
    weight_decay {0, 1e-6}, dropout {0, 0,2} (không áp dụng cho GMF); CFNet thêm tháp rl {[512,64], [256,64]}.
  - NeuMF-Pretrained: dùng GMF, MLP tốt nhất; fine-tune lr {1e-3, 5e-4, 1e-4}, α {0,3; 0,5; 0,7} (Adam).
  - BPR-MF: embedding_dim {32, 64, 128}, lr {0,01; 0,03; 0,05}, reg {0,001; 0,005; 0,01}, epochs {20, 40}.
  - iALS: factors {32, 64, 128, 256}, regularization {0,001; 0,01; 0,1}, alpha {1, 10, 40}, iterations 15.
  - MostPopular-Recent: window_days {7, 14, 28, 56} (4 cấu hình — lưới chỉ có 4).
  - B: thành phần MF = baseline MF tốt nhất trên val (iALS hoặc BPR-MF), NeuMF = NeuMF tốt nhất trên val;
    trọng số w ∈ {0; 0,1; …; 1} trên val (min-max theo candidate của từng user).
- Giới hạn thời gian: tuning ≤ 4,5 giờ GPU; nếu vượt, giảm số cấu hình **đều** cho mọi mô hình và ghi lệch kế hoạch.

## 5. Đánh giá cuối (test)
- Mỗi mô hình dùng cấu hình tốt nhất trên val, chạy **3 seed** (42, 2024, 2025) qua `--final`, mỗi lần ghi
  `audit/test_access_log.csv` (lúc đăng ký nằm ở `docs/audit/`). Không sửa kiến trúc/siêu tham số sau khi xem số test (nếu phải sửa: ghi log +
  báo cáo, và số sau sửa được đánh dấu "sau khi xem test").
- Báo cáo: mean ± std qua 3 seed; per-user = trung bình NDCG@10 của user qua 3 seed.

## 6. Kiểm định
- Paired per-user trên test: **Wilcoxon signed-rank** (per-user NDCG@10 trung bình qua seed) + **paired bootstrap**
  95% CI (10.000 lần, seed 0). Wilcoxon theo seed không dùng (3 seed không thể đạt p < 0,05).
- Họ so sánh cố định (hiệu chỉnh **Holm** trên toàn họ, α = 0,05) — thay ở loop 14, trước mọi --final:
  1. NeuMF-Pretrained vs BPR-MF, 2. vs MostPopular, 3. vs GMF, 4. vs MLP, 5. vs NeuMF-Scratch,
  6. NeuMF-Scratch vs BPR-MF, 7. vs GMF, 8. vs MLP. (Cài đặt: `scripts/12_significance.py`.)
- "A tốt hơn B" chỉ được viết khi: p Holm < 0,05 **và** CI bootstrap không chứa 0 **và** chênh lệch tương đối
  NDCG@10 ≥ **5%**. Ngược lại viết "không khác biệt có ý nghĩa".

## 7. Chọn "mô hình lai tốt nhất"
- Trong {NeuMF-Scratch, NeuMF-Pretrained}, chọn mô hình có **val** NDCG@10 cao nhất (seed 42). Test chỉ để
  báo cáo, không để chọn lại. (Loop 14: B, C đã bỏ — mục 8.)
- **Nếu mô hình lai không vượt baseline MF đã tune, báo cáo đúng như vậy.**

## 8. Lệch kế hoạch
- **Loop 12 (trước mọi --final, chưa xem test):** EarlyFusion bị bỏ khỏi tuning và khỏi họ so sánh vì kiến trúc
  **trùng hệt MLP** (`src/models/early_fusion.py` vs `MLP` trong `src/models/neumf.py`: cùng 2 embedding → nối →
  cùng tháp MLP → lớp output). Bằng chứng: smoke tuning 1 epoch cùng seed cho val NDCG@10 bằng nhau (0,00770 vs
  0,00770); `tests/test_tuning.py::test_early_fusion_is_architecturally_identical_to_mlp`. Trong báo cáo, MLP
  chính là ablation "early fusion"/DNN-only. Họ 8 so sánh ở mục 6 không có EarlyFusion nên không đổi.
- **Loop 12:** NeuMF-Pretrained cho phép nhánh GMF và MLP khác số chiều (`NeuMF(..., gmf_dim=...)`, như NCF gốc)
  để nạp được GMF/MLP tốt nhất; negative_ratio và weight_decay khi fine-tune lấy theo MLP tốt nhất.
- **Loop 14 (quyết định của người dùng, TRƯỚC mọi --final, chưa xem test):** bỏ iALS, MostPopular-Recent, CFNet (C)
  và late fusion B khỏi đề tài và khỏi code (người dùng: đã quá nhiều baseline). Tập mô hình cuối: Random,
  MostPopular, BPR-MF, GMF, MLP, NeuMF-Scratch, NeuMF-Pretrained. Kết quả tuning val của các mô hình bị bỏ vẫn giữ
  trong `tuning_log.csv` / `TUNING_RESULTS.md` để minh bạch (trên val, iALS 0,01141 và B 0,01260 cao hơn
  NeuMF-Scratch 0,01107) — không chạy test cho chúng. Họ so sánh mục 6 và tập ứng viên mục 7 sửa tương ứng.
  Mô hình lai được chọn (mục 7, theo val): **NeuMF-Scratch** (0,01107 > NeuMF-Pretrained 0,00913).
- **Loop 14:** đánh giá cuối chạy bằng `scripts/11_final.py` (thay 03 --final): cùng khoá test (PREREG đã commit,
  --reason, test_access_log.csv, từ chối khi working tree bẩn), cho phép mỗi mô hình dùng cấu hình tốt nhất riêng;
  train trên train, early stopping trên val như lúc tuning, chấm test với candidate = item train, loại train ∪ val.
- **29/09/2026 (SAU khi đã xem test 27/09):** trước khi chấm test, mỗi mô hình được train lại từ đầu trên
  train ∪ val (mọi cặp < 2020-07-29) đúng best_epoch chọn trên val; MostPopular/BPR-MF fit trên train ∪ val; test giữ
  user/item có trong train ∪ val, candidate = item train ∪ val (2.996 user, 10.216 item thay vì 2.893 / 10.145).
  Lý do dựa trên thí nghiệm chỉ-trên-val: bỏ trống 4 tuần sát ngày chấm làm NDCG@10 giảm 17–19% (MostPopular,
  BPR-MF). Cấu hình (best_configs.json), metric, họ so sánh, tiêu chí giữ nguyên. Số test chạy lại thay số cũ.
- **02/10/2026 (SAU khi đã xem test 27/09 và 29/09) — đăng ký trước lần chạy lại toàn bộ:** chạy lại một lần toàn
  bộ chuỗi đánh giá cuối trên một commit sạch (`python run.py final --reason ...`: 11 → 12 → 17 → 16 → 13 → 14 →
  15 → 19) để mọi số liệu trong báo cáo truy vết về **cùng một commit** — kết quả 29/09 sinh ở `c559c86`, sau đó
  thư mục được đổi tên và thêm phần mở rộng mục 9. Không tune lại; cấu hình (`best_configs.json`), seed, metric, họ
  so sánh, tiêu chí kết luận giữ nguyên. Từ 28/09 (`d689ca5`) huấn luyện chạy ở chế độ GPU tất định
  (`src/utils/seed.py`), và code huấn luyện/đánh giá của 7 mô hình chính không đổi kể từ `c559c86` (chỉ thêm file
  mới), nên chạy lại trên **cùng máy** (máy có GPU RTX 3050 Laptop đã chạy ngày 29/09), cùng phiên bản thư viện
  **kỳ vọng ra đúng cùng số** với lần 29/09 — đây đồng thời là kiểm tra tái lập. Chạy trên máy khác (Colab T4, CPU)
  thì Random, MostPopular, ItemKNN, UserKNN vẫn trùng, BPR-MF (numpy) gần như trùng, còn GMF/MLP/NeuMF có thể lệch nhẹ. `scripts/19_check_report.py` so số mới với bản đã commit; nếu lệch, báo cáo dùng số của
  lần chạy lại và ghi rõ độ lệch. (Tuning 27/09 chạy trước khi có chế độ tất định nên không tái lập được từng bit:
  MLP dựng lại theo đúng cấu hình tốt nhất cho val NDCG@10 0,00922 so với 0,00837 lúc tuning —
  `audit/rebuilt_checkpoints.json`; GMF và BPR-MF dựng lại khớp tuyệt đối. Lựa chọn cấu hình không đổi.)

## 9. Mở rộng sau khi xem test

Đăng ký 02/10/2026, **trước** khi chấm test cho các mô hình dưới đây; **sau** khi đã xem test của 7 mô hình chính
(27/09, 29/09). Kết quả mục này báo cáo là **kết quả mở rộng**, không thay kết luận chính (mục 6–7 giữ nguyên, mô
hình lai được chọn vẫn là NeuMF-Scratch).

**Lý do (góp ý của GVHD):** (i) so sánh hợp nhất ở mức biểu diễn (NeuMF — early fusion) với hợp nhất ở mức điểm
(late fusion) của **cùng** hai thành phần MF và DNN; (ii) baseline láng giềng mà đề cương đặt ra (Item-based CF) và
câu hỏi "Top-K người dùng tương đồng" (UserKNN).

**Mô hình:**
- `LateFusion-GMF-MLP`: w·minmax(điểm GMF) + (1 − w)·minmax(điểm MLP), min-max trên tập ứng viên của từng user
  (`src/models/late_fusion.py`). GMF, MLP là hai mô hình tốt nhất đã tune ở mục 4, huấn luyện **riêng**.
- `LateFusion-BPR-MLP`: như trên với BPR-MF và MLP (thêm DNN vào baseline MF đã tune).
- `ItemKNN`, `UserKNN`: cosine trên vector mua nhị phân, có hệ số co (shrink), giữ top-k láng giềng, ma trận thưa
  (`src/baselines/neighborhood.py`; bản ItemKNN dày cũ bị chặn ở 5.000 item đã gỡ).

**Chọn tham số (chỉ val, seed 42, `scripts/10_tune.py --model extension`):**
- ItemKNN, UserKNN: 6 cấu hình rút từ lưới k ∈ {20, 50, 100, 200, 500} × shrink ∈ {0, 10, 50} (numpy seed 0, cấu
  hình mặc định k = 100, shrink = 0 luôn có) — cùng ngân sách 6 cấu hình như mục 4.
- Late fusion: quét đủ 11 giá trị w ∈ {0; 0,1; …; 1} (một tham số, không huấn luyện thêm mạng nào — như mô hình trộn
  điểm B ở mục 4). Thành phần trên val là checkpoint train-only của GMF, MLP, BPR-MF tốt nhất (`outputs/tuning/`;
  MLP là bản dựng lại, xem mục 8).
- Kết quả (`audit/best_configs.json`, val NDCG@10): UserKNN k = 200, shrink = 0 → 0,01340; ItemKNN k = 100,
  shrink = 50 → 0,01217; LateFusion-GMF-MLP w = 0,1 → 0,01005 (thành phần đứng riêng: GMF 0,00843 khi w = 1, MLP
  0,00922 khi w = 0); LateFusion-BPR-MLP w = 0,3 → 0,00972. Đối chiếu: NeuMF-Scratch 0,01107.
- Truy vết: 34 dòng `tuning_log.csv` của phần này ghi ở commit `922f64f` với working tree đang có code mở rộng chưa
  commit (commit ở `16eb349`). Chạy lại kiểm tra ngày 02/10/2026 trên code đã commit (ghi ra thư mục tạm, không đụng
  `audit/`): **cả 34 cấu hình ra đúng cùng số** (sai lệch tối đa 0), cùng tham số được chọn.

**Chấm test (`scripts/17_extension.py`, một lần, ghi `test_access_log.csv` trước khi chấm):**
- Late fusion nạp đúng GMF, MLP, BPR-MF mà `11_final.py` đã huấn luyện lại trên train ∪ val cho từng seed
  (`outputs/final/seed*/`) — cùng checkpoint của kết quả chính, không huấn luyện thêm; w theo val.
- ItemKNN, UserKNN tính trên train ∪ val với (k, shrink) theo val; tất định nên giống nhau ở mọi seed.
- Cùng tập test, tập ứng viên, quy tắc loại item đã mua, tie-break (mục 1, 5).

**Kiểm định:** họ **7 so sánh riêng**, hiệu chỉnh Holm riêng (α = 0,05), cùng tiêu chí "A tốt hơn B" của mục 6
(p Holm < 0,05, CI bootstrap không chứa 0, chênh lệch tương đối ≥ 5%):
1. LateFusion-GMF-MLP vs NeuMF-Scratch (late vs early fusion, mô hình lai được chọn)
2. LateFusion-GMF-MLP vs NeuMF-Pretrained
3. LateFusion-GMF-MLP vs GMF (sau khi lai vs trước khi lai — nhánh MF)
4. LateFusion-GMF-MLP vs MLP (sau khi lai vs trước khi lai — nhánh DNN)
5. LateFusion-BPR-MLP vs BPR-MF
6. ItemKNN vs NeuMF-Scratch
7. UserKNN vs NeuMF-Scratch

(Cài đặt: `EXT_COMPARISONS` trong `scripts/17_extension.py`.) Họ này không gộp với họ 8 so sánh của mục 6.
