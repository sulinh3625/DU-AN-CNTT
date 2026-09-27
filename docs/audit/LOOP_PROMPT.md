# Prompt vòng lặp kiểm định + cải tiến (bản lưu, có điền quyết định người dùng)

Mỗi lượt: đọc file này + LOOP_STATE.md, làm MỘT hạng mục, kiểm chứng, cập nhật LOOP_STATE.md,
đúng 1 commit "[loop N] <hạng mục>" trên nhánh `loop/hm500k-audit` (KHÔNG push).
Kết thúc lượt bằng 3 dòng: đã làm gì / bằng chứng / lượt sau làm gì.

DỪNG khi: mọi tiêu chí nghiệm thu PASS; hoặc mọi hạng mục còn lại bị chặn; hoặc hết ngân sách (Q4);
hoặc 3 lượt liên tiếp không hạng mục nào đổi trạng thái.

## Yêu cầu đề tài (R1–R8)
- R1. H&M Personalized Fashion Recommendations là dataset chính và duy nhất cho kết quả chính.
- R2. Thuần CF: chỉ học từ tương tác user–item (ID, số lần mua, thời điểm). Không dùng articles.csv,
  customers.csv, văn bản, ảnh, tuổi, danh mục làm đầu vào hay thành phần điểm số. "Lai" = MF + DNN theo NCF.
- R3. GMF + MLP → NeuMF, có pre-training (He et al., 2017).
- R4. Đặc trưng lịch sử mua (tần suất, recency, confidence weight) chỉ từ transactions, chỉ tính trên train.
- R5. Huấn luyện & tinh chỉnh có hệ thống, toàn bộ trail vào tuning_log.csv.
- R6. Precision@K, Recall@K, NDCG@K (giữ HR@K). Protocol chính: Full Ranking.
- R7. Khả năng triển khai: bằng chứng đo được (API/demo, độ trễ đo thật); không có thì hạ khẳng định.
- R8. Báo cáo LaTeX (C1–C5, abstract, phụ lục) khớp code + file kết quả; không nhắc đề tài/dự án khác.

## Nguyên tắc bất biến
- Không bịa số; số trong báo cáo sinh từ file kết quả, chưa có thì ghi "chưa có".
- Pipeline: aggregate unique user–item → k-core (lặp đến hội tụ) → temporal split → assert_disjoint_splits.
- Mọi thống kê/đặc trưng/popularity chỉ tính trên train. Val để tuning, test chỉ đánh giá cuối.
- So sánh công bằng: cùng split, item pool, quy tắc loại item đã xem, cùng ngân sách tuning.
- So với kết quả ngoài: nêu khác biệt metric, cách chia, kích thước item pool trước khi đặt số cạnh nhau.
- Cold-start ngoài phạm vi MÔ HÌNH; onboarding rule-based ở demo gắn nhãn "không phải mô hình".

## Khoá tập test
- Chọn mô hình/siêu tham số chỉ dựa trên validation.
- Test chỉ đánh giá qua một đường duy nhất (cờ --final); mỗi lần gọi ghi 1 dòng docs/audit/test_access_log.csv
  (thời gian, git commit, config hash, model, lý do).
- Không sửa kiến trúc/siêu tham số sau khi xem số test mà không khai báo trong log + báo cáo.
- PREREG.md (Pha 3) commit TRƯỚC lần đánh giá test đầu tiên của mô hình mới.

## Quyết định của người dùng (27/09/2026)
- Q1: protocol CHÍNH = chia theo mốc thời gian chung (configs/hm500k_global.yaml: train < 2020-07-01 ≤ val
  < 2020-07-29 ≤ test, đến 2020-09-22), mỗi user nhiều test item. Item user đã mua trong train/val không là
  đích (xếp cặp user-item theo lần mua đầu tiên; chỉ dự đoán món MỚI với user). Leave-one-out giữ làm phụ.
- Q2: dữ liệu hm500k (mẫu ~500k dòng lấy theo khách hàng trên toàn 2 năm, scripts/00_sample_hm.py),
  **k-core = 10** (lệch khỏi bất biến k=5 để vừa RAM 16 GB — ghi rõ trong báo cáo). Không lấy mẫu con user test.
- Q3: (a) xoá thành phần content khỏi code (đã làm ở loop 0).
- Q4: GPU NVIDIA RTX 3050 Laptop 4 GB; tối đa ~8 giờ tính toán; 3 seed (Wilcoxon theo seed không đạt
  p<0,05 → kiểm định chính là paired bootstrap / Wilcoxon theo user, hiệu chỉnh Holm).
- Khác: được `pip install implicit` (iALS); bỏ DataCo hoàn toàn khỏi báo cáo; LightGCN/SASRec: xoá khỏi code
  (F6); làm trên nhánh loop/hm500k-audit, mỗi lượt 1 commit, không push.
- Xoá file bị hệ thống chặn → ghi vào mục "Cần người dùng làm" kèm lệnh.

## Các pha
- Pha 0: COMPLIANCE_MATRIX.md (R1–R8 + checklist V3: results_per_user.csv, multi-seed, n_candidates mỗi user,
  tuning_log.csv, config hash + git commit mỗi run, kiểm định paired per-user); truy vết R2; grep đề tài khác
  (khóa luận, KLTN, tồn kho, inventory, reinforcement, MARL) = 0.
- Pha 1: thuần CF theo Q3; pytest khẳng định config chính không đọc metadata; confidence/recency chỉ train;
  lưu checkpoint BPR-MF.
- Pha 2: split theo Q1 (đã cài); Full Ranking chính; sampled-99 đối chiếu; log n_candidates; xuất
  results_per_user.csv; metric nhiều item đúng + unit test tính tay (đã có).
- Pha 3: đọc thật các nguồn (NCF + code gốc, MS Recommenders ncf_deep_dive, Rendle 2020, Dacrema 2019,
  Krichene & Rendle 2020, Rendle 2022 iALS, DMF, DeepCF, RecBole) → REFERENCES.md; CANDIDATES.md (tối đa 2
  kiến trúc mới ngoài họ NeuMF; A: NeuMF tune; B: late fusion MF+NeuMF; C: DeepCF; không ConvNCF); baseline
  mạnh cùng ngân sách: MostPopular (toàn cục + cửa sổ gần), BPR-MF, iALS; PREREG.md commit trước mọi test mới.
- Pha 4: tuning chỉ val → tuning_log.csv; multi-seed; test một lần qua --final (test_access_log.csv); kiểm
  định theo PREREG; đo độ trễ Top-K p50/p95 CPU.
- Pha 5: bảng .tex sinh từ file kết quả, C4 \input; bỏ DataCo khỏi C1–C5/abstract; sửa C1:39, C2:298, C3:54
  (P/R), mô tả hybrid/content, mục độ trễ C3; demo trỏ run được chọn.

## Tiêu chí nghiệm thu
- COMPLIANCE_MATRIX: R1–R8 + V3 PASS (hoặc PARTIAL có lý do người dùng chấp nhận).
- pytest xanh: split không giao + không rò rỉ thời gian; mô hình chính không đọc metadata; metric khớp tính tay.
- PREREG.md commit trước dòng đầu test_access_log.csv của mô hình mới.
- Mọi số trong báo cáo truy được về file kết quả; LaTeX biên dịch không lỗi.
- Grep đề tài/dự án khác = 0.
