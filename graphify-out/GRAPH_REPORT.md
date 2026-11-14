# Graph Report - DU-AN-CNTT  (2026-11-14)

## Corpus Check
- 107 files · ~605,672 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 113 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 20)

## Summary
- 2300 nodes · 5496 edges · 107 communities (88 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 225 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5d753211`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- torch
- app.js
- build_poster.py
- run.py
- eo
- routes.py
- .getParsed
- Đăng ký trước (pre-registration) — giao thức v2, bản cuối
- .getProps
- DataContext
- mau_kiem_dinh
- e
- test_prepare.py
- da
- download_hm_images.py
- test_v2_final.py
- 19_check_report.py
- test_bosung.py
- NeuMFF
- 25_bosung.py
- reviews_Beauty_5
- 23_final_v2.py
- test_evaluation.py
- va
- Trang
- chart.umd.min.js
- hinh_bao_cao.py
- features.py
- Si
- ns
- .getDatasetMeta
- pathlib
- i
- hop
- jn
- pytest
- u
- no
- amazon.yaml
- .constructor
- Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty
- an
- zt
- Đăng ký trước (pre-registration) — thực nghiệm hm500k
- Demo web — shop thời trang H&M (kèm Amazon Beauty)
- Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F
- README.md
- Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)
- test_models.py
- Đăng ký trước (pre-registration) — giao thức v2
- user_time_features
- numpy
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- 22_tune_v2.py
- 24_report_v2.py
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- s
- __main__.py
- build_slides.py
- MLP
- 9. Đánh giá, kiểm định và chống thiên lệch
- Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)
- test_demo.py
- subprocess
- o
- tn
- BPRMFBaseline
- Phần 5. Câu hỏi hội đồng hay hỏi
- update
- .get
- v2_common.py
- user_filter
- 2. Tiến độ (12/11/2026)
- 13. Lịch sử phát triển
- hybrid_features.py
- LateFusion
- Precomputed
- test_baselines.py
- Table
- metrics_io.py
- pandas
- re
- slide
- n
- bam
- Sơ đồ của đề tài
- 3. Chạy thực nghiệm
- ket_qua
- Phần 2. Nắm toàn bộ đề tài
- rs
- main.py
- download_amazon_images.py
- ItemKNNBaseline
- summary
- kien_truc_demo

## God Nodes (most connected - your core abstractions)
1. `an()` - 64 edges
2. `ns()` - 57 edges
3. `s()` - 43 edges
4. `n()` - 37 edges
5. `no` - 35 edges
6. `DataContext` - 34 edges
7. `esc()` - 32 edges
8. `va` - 31 edges
9. `main()` - 29 edges
10. `Trang` - 28 edges

## Surprising Connections (you probably didn't know these)
- `2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026` --references--> `make_stage()`  [INFERRED]
  tong_hop.md → neumf_project/src/data_pipeline/protocol_v2.py
- `13.4 Dọn mã (10/10/2026)` --references--> `evaluate_v2()`  [INFERRED]
  tong_hop.md → neumf_project/src/evaluation/v2.py
- `10.3 Kiểm thử` --references--> `final_result()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/inference.py
- `10.1 Quy trình thực nghiệm` --references--> `tune()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/25_bosung.py
- `10.1 Quy trình thực nghiệm` --references--> `final()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/25_bosung.py

## Import Cycles
- None detected.

## Communities (107 total, 19 thin omitted)

### Community 0 - "torch"
Cohesion: 0.09
Nodes (15): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), popular(), rank_from_scores(), recommend() (+7 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (95): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+87 more)

### Community 2 - "build_poster.py"
Cohesion: 0.09
Nodes (7): add_par(), bullets(), chu_thich(), ribbon(), set_runs(), style(), textbox()

### Community 3 - "run.py"
Cohesion: 0.07
Nodes (29): _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report() (+21 more)

### Community 4 - "eo"
Cohesion: 0.11
Nodes (9): Bi(), ca(), Ci(), Do(), eo(), Fi(), getBasePixel(), Oe() (+1 more)

### Community 5 - "routes.py"
Cohesion: 0.07
Nodes (30): unavailable_reason(), context(), ctx(), dashboard(), datasets(), example(), _filtered(), has_images() (+22 more)

### Community 6 - ".getParsed"
Cohesion: 0.12
Nodes (12): Ae(), _calculateBarIndexPixels(), _calculateBarValuePixels(), getLabelAndValue(), getLabelForValue(), getPixelForTick(), getPixelForValue(), _getRuler() (+4 more)

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2, bản cuối"
Cohesion: 0.12
Nodes (16): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo (+8 more)

### Community 8 - ".getProps"
Cohesion: 0.11
Nodes (21): ai(), ao(), average(), getCenterPoint(), ho(), Hs, _i(), inRange() (+13 more)

### Community 9 - "DataContext"
Cohesion: 0.08
Nodes (10): DataContext, best_rank_series(), pick_example(), saved_best_series(), showcase_users(), user_profile(), main(), test_history_is_training_data_before_cutoff() (+2 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "e"
Cohesion: 0.09
Nodes (14): dn(), e(), ei(), En, gi(), ia(), init(), je() (+6 more)

### Community 12 - "test_prepare.py"
Cohesion: 0.07
Nodes (33): export(), Catalog, DailySales, group_by_product(), item_time_features(), product_code_of(), build_from_pairs(), build_v2() (+25 more)

### Community 13 - "da"
Cohesion: 0.11
Nodes (15): beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), da(), ea(), fa(), ga(), ha (+7 more)

### Community 14 - "download_hm_images.py"
Cohesion: 0.12
Nodes (6): fetch(), get_range(), main(), member_bytes(), RangeFile, zip_url()

### Community 15 - "test_v2_final.py"
Cohesion: 0.09
Nodes (8): _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_report_beyond_late_fusion_time_is_sum_of_branches(), test_report_metric_bars_share_one_color(), test_report_runs_end_to_end_on_tiny_results()

### Community 16 - "19_check_report.py"
Cohesion: 0.13
Nodes (15): check_claims(), claims(), by_k_order(), hyb_fifth(), compare_with_committed(), Data, load(), find_line() (+7 more)

### Community 17 - "test_bosung.py"
Cohesion: 0.14
Nodes (14): tune(), combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic() (+6 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 19 - "25_bosung.py"
Cohesion: 0.18
Nodes (9): component_check(), file_md5(), final(), lock_errors(), main(), opened_tags(), provenance(), test_dirty_files_ignores_outputs_and_test_log() (+1 more)

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - "23_final_v2.py"
Cohesion: 0.14
Nodes (12): ablations(), beyond(), cpu_name(), dirty_files(), git(), lock_errors(), machine_info(), opened_seeds() (+4 more)

### Community 22 - "test_evaluation.py"
Cohesion: 0.10
Nodes (24): _append(), build_full_ranking_records_multi(), _empty_metric_lists(), EvalRecord, evaluate_score_function(), evaluate_torch_model(), _per_user_row(), hr_at_k() (+16 more)

### Community 23 - "va"
Cohesion: 0.18
Nodes (4): afterDraw(), afterEvent(), f(), va

### Community 24 - "Trang"
Cohesion: 0.13
Nodes (8): cac_buoc(), chia_thoi_gian(), demo_ngang(), duong_ong(), tinh_chinh_danh_gia(), Trang, vien_(), xu_ly_du_lieu()

### Community 25 - "chart.umd.min.js"
Cohesion: 0.04
Nodes (35): at(), be(), cn(), d(), destroy(), draw(), es(), fe() (+27 more)

### Community 26 - "hinh_bao_cao.py"
Cohesion: 0.16
Nodes (13): du_lieu_amazon_ngang(), du_lieu_hm_ngang(), _du_lieu_ngang(), hop_nhat(), kien_truc_neumf(), kien_truc_neumf_f(), _neumf(), neumf_f_ngang() (+5 more)

### Community 27 - "features.py"
Cohesion: 0.10
Nodes (22): build_amazon(), main(), build_features(), category_path(), build_catalog(), build_daily_sales(), build_user_profile(), category_codes() (+14 more)

### Community 28 - "Si"
Cohesion: 0.14
Nodes (12): afterUpdate(), Ee(), generateLabels(), ki(), Le(), oa(), Oi(), Si() (+4 more)

### Community 29 - "ns"
Cohesion: 0.06
Nodes (12): As(), bn, labelColor(), labelPointStyle(), ns(), on(), pn(), rt() (+4 more)

### Community 30 - ".getDatasetMeta"
Cohesion: 0.18
Nodes (3): afterDatasetsUpdate(), Mn(), onClick()

### Community 31 - "pathlib"
Cohesion: 0.10
Nodes (8): AmazonAdapter, asin_list(), item_info(), read_meta(), read_reviews(), DatasetAdapter, HMAdapter, test_hm_adapter_rejects_excel()

### Community 32 - "i"
Cohesion: 0.16
Nodes (11): ct(), fs(), ge(), gs(), ms(), ps(), i(), vs() (+3 more)

### Community 33 - "hop"
Cohesion: 0.11
Nodes (14): bong(), chan_trang(), chu_thich(), chuoi_buoc(), hop(), khung_cam(), khung_tren_hinh(), mui_ten() (+6 more)

### Community 36 - "u"
Cohesion: 0.14
Nodes (8): addBox(), beforeUpdate(), initialize(), removeBox(), reset(), start(), stop(), u()

### Community 37 - "no"
Cohesion: 0.10
Nodes (11): buildLookupTable(), Fo(), _generate(), _getTimestampsForTable(), initOffsets(), lt(), no, nt() (+3 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 41 - "an"
Cohesion: 0.12
Nodes (3): an(), ke(), wn()

### Community 42 - "zt"
Cohesion: 0.06
Nodes (14): bt, color(), Cs, Ft(), It(), kt(), mt(), os() (+6 more)

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.20
Nodes (9): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 9. Mở rộng sau khi xem test (+1 more)

### Community 44 - "Demo web — shop thời trang H&M (kèm Amazon Beauty)"
Cohesion: 0.29
Nodes (6): 1. Chuẩn bị, 2. Chạy, 3. Màn hình, 5. Biến môi trường, 6. Ảnh sản phẩm (tuỳ chọn), Demo web — shop thời trang H&M (kèm Amazon Beauty)

### Community 45 - "Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F"
Cohesion: 0.18
Nodes (10): 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F, Phần 1. Thông điệp chính, Phần 3. Số liệu cần nhớ, Phần 4. Nội dung nào nói trong báo cáo, nội dung nào chỉ nói khi được hỏi, Phần 6. Câu không được nói (+2 more)

### Community 46 - "README.md"
Cohesion: 0.25
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - "test_models.py"
Cohesion: 0.18
Nodes (5): GMF, NeuMF, test_forward_shapes_and_logits(), test_neumf_uses_four_independent_embeddings(), test_refit_runs_fixed_epochs_without_validation()

### Community 49 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.20
Nodes (9): 0. Vì sao có giao thức v2, 10. Lệch kế hoạch, 1. Dữ liệu, 3. Mô hình, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký (+1 more)

### Community 50 - "user_time_features"
Cohesion: 0.21
Nodes (4): FeatureTrainDataset, user_time_features(), test_feature_dataset_negatives_launched_and_not_positive(), test_user_time_features_strictly_before_day()

### Community 51 - "numpy"
Cohesion: 0.09
Nodes (12): TrainDataset, iterative_k_core(), available_negatives(), build_user_positive_sets(), sample_train_negatives(), aggregate_unique_user_item(), test_aggregate_before_kcore_counts_unique_edges(), test_negative_sampler_never_returns_positive() (+4 more)

### Community 52 - "Tổng hợp đồ án: phương pháp, kết quả và tiến độ"
Cohesion: 0.25
Nodes (8): 11. Hạn chế đã biết, 12. Đối chiếu 17 góp ý trước của GVHD, 14.1 File, 14.2 Tài liệu tham khảo chính, 14. Danh sách file và tài liệu tham khảo, 1. Đồ án làm gì — nói ngắn, 5. Những điều phải nói thẳng khi bảo vệ, Tổng hợp đồ án: phương pháp, kết quả và tiến độ

### Community 53 - "3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định"
Cohesion: 0.25
Nodes (8): 3.1 Lần chạy, 3.2 NDCG@10 của 14 mô hình (trung bình ± độ lệch chuẩn qua 5 seed), 3.3 Theo K (báo cáo mục 4.3.2, Bảng 4.5–4.6 chỉ trình bày K = 10, 15, 20; cột K = 5 dưới đây để tham khảo), 3.4 Họ 10 so sánh đăng ký trước, 3.5 Phân tích phụ (chỉ mô tả, không kiểm định), 3.6 Trả lời câu hỏi nghiên cứu, 3.7 Phân tích bổ sung: mô hình lai truyền thống Hybrid-CBCF (báo cáo mục 4.3.4, Bảng 4.8), 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định

### Community 54 - "v2.yaml"
Cohesion: 0.08
Nodes (25): data_dir, evaluation, k_values, tie_break_seed, features, catalog, customers, sales (+17 more)

### Community 55 - "4. Kiểm chứng trên Amazon Beauty"
Cohesion: 0.29
Nodes (7): 4.1 Lần chạy, 4.2 Kết quả trên tập kiểm thử Amazon (5 seed; báo cáo Bảng 4.13), 4.3 Họ 10 so sánh, đặt cạnh kết luận của H&M (báo cáo Bảng 4.17–4.18), 4.4 Ba kết luận của H&M có còn đúng không (báo cáo mục 4.4.3), 4.5 Ablation và độ phủ (seed 42; báo cáo Bảng 4.19), 4.6 Hybrid-CBCF trên Amazon (phân tích bổ sung; báo cáo mục 4.4.2, Bảng 4.16), 4. Kiểm chứng trên Amazon Beauty

### Community 56 - "7. Dữ liệu"
Cohesion: 0.29
Nodes (7): 7.1 Nguồn H&M và lý do lấy mẫu, 7.2 Hai mẫu khách hàng, 7.3 Tiền xử lý (`scripts/02_prepare_data.py`; báo cáo Thuật toán 3.1), 7.4 Giai đoạn đánh giá và tập ứng viên, 7.5 Đặc trưng theo thời điểm (H&M), 7.6 Amazon Beauty (`audit/PREREG_amazon.md`), 7. Dữ liệu

### Community 57 - "22_tune_v2.py"
Cohesion: 0.17
Nodes (9): load_best(), log_row(), logged(), main(), ensure_dir(), log_test_access(), prereg_committed(), test_log_test_access_appends_rows() (+1 more)

### Community 58 - "24_report_v2.py"
Cohesion: 0.06
Nodes (49): ablation(), beyond(), bootstrap_ci(), by_k(), cell(), dev_info(), ensure(), export_by_k() (+41 more)

### Community 59 - "10. Code, demo, kiểm thử và báo cáo"
Cohesion: 0.40
Nodes (5): 10.1 Quy trình thực nghiệm, 10.2 Demo (`demo/README.md`), 10.4 Báo cáo LaTeX (`Report DACNTT/`), 10.5 Lưu ý khi làm tiếp, 10. Code, demo, kiểm thử và báo cáo

### Community 60 - "6. Bài toán, câu hỏi nghiên cứu và phạm vi"
Cohesion: 0.33
Nodes (6): 6.1 Bài toán, 6.2 Câu hỏi nghiên cứu, 6.3 Yêu cầu R1–R9, 6.4 Phạm vi, 6.5 Vì sao thiết kế như vậy, 6. Bài toán, câu hỏi nghiên cứu và phạm vi

### Community 61 - "8. Mô hình"
Cohesion: 0.33
Nodes (6): 8.1 NeuMF-F — mô hình đề xuất (`src/models/hybrid_features.py`), 8.2 Hợp nhất sớm và hợp nhất muộn, 8.3 Mô hình đối chứng và cấu hình đã chọn, 8.4 Ablation NeuMF-F, 8.5 Mô hình lai truyền thống Hybrid-CBCF — bổ sung sau đánh giá cuối, 8. Mô hình

### Community 62 - "s"
Cohesion: 0.07
Nodes (13): bo, configure(), et(), getValueForPixel(), H(), s(), j(), ko (+5 more)

### Community 64 - "build_slides.py"
Cohesion: 0.11
Nodes (10): bieu_do(), cat_anh(), ghi_hieu_ung(), _hien(), _hieu_ung(), macros(), morph(), so_voi_truyen_thong() (+2 more)

### Community 65 - "MLP"
Cohesion: 0.38
Nodes (3): 8. Lệch kế hoạch, MLP, test_mlp_dropout_is_configurable()

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 67 - "Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)"
Cohesion: 0.33
Nodes (5): graphify, Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script), Quy ước báo cáo (`Report DACNTT/`), Ranh giới, Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

### Community 74 - "test_demo.py"
Cohesion: 0.05
Nodes (25): amazon_table(), product_table(), results_dir(), saved_final_ranks(), user_table(), v2_available(), v2_data_mismatch(), answers() (+17 more)

### Community 75 - "subprocess"
Cohesion: 0.22
Nodes (6): _ghi(), _edge(), _html(), _khung(), xuat(), main()

### Community 76 - "o"
Cohesion: 0.15
Nodes (13): a(), aa(), Di(), g(), m(), g(), o(), p() (+5 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.13
Nodes (4): BPRMFBaseline, MostPopularBaseline, RandomBaseline, test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 79 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 80 - "update"
Cohesion: 0.18
Nodes (11): beforeLayout(), dataset(), hi(), index(), ji(), qo(), Re(), ts() (+3 more)

### Community 81 - ".get"
Cohesion: 0.18
Nodes (6): b(), ce(), de, dt(), he(), qs()

### Community 82 - "v2_common.py"
Cohesion: 0.08
Nodes (23): base_key(), build_torch(), configs_for(), data_name(), device(), eval_kw(), evaluate(), fit_torch() (+15 more)

### Community 84 - "2. Tiến độ (12/11/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (12/11/2026)

### Community 85 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 86 - "hybrid_features.py"
Cohesion: 0.09
Nodes (9): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), score_fn(), ContentProfile, MaskedScoreFn, MaskedScorer, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_masked_scorer_puts_unscoreable_items_last() (+1 more)

### Community 87 - "LateFusion"
Cohesion: 0.21
Nodes (6): late_fusion(), LateFusion, minmax(), model_scores(), test_late_fusion_extremes_reproduce_component_ranking(), test_minmax_constant_is_zero()

### Community 89 - "test_baselines.py"
Cohesion: 0.16
Nodes (9): interaction_matrix(), topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors(), _topk_dense() (+1 more)

### Community 91 - "metrics_io.py"
Cohesion: 0.33
Nodes (5): _block(), _by_k(), dashboard(), _named(), test_dashboard_reads_result_files()

### Community 93 - "pandas"
Cohesion: 0.14
Nodes (8): bucket_of(), main(), select_buckets(), main(), foreign_results(), main(), check_product_code(), write_json()

### Community 96 - "re"
Cohesion: 0.29
Nodes (4): _net(), o(), check_macros_and_tables(), defined_macros()

### Community 98 - "slide"
Cohesion: 0.24
Nodes (7): anh(), anh_vua(), hinh(), logo(), nen(), ra_sau(), slide()

### Community 99 - "n"
Cohesion: 0.11
Nodes (16): buildTicks(), determineDataLimits(), Fn(), Gn(), go(), ii(), n(), l() (+8 more)

### Community 100 - "bam"
Cohesion: 0.33
Nodes (3): bam(), pha(), phang()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.50
Nodes (3): Lối vẽ, Sơ đồ của đề tài, Sửa và xuất lại

### Community 103 - "3. Chạy thực nghiệm"
Cohesion: 0.15
Nodes (12): 1. Cài đặt, 2. Dữ liệu, 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển, 3.2 Chạy thử (tuỳ chọn), 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần, 3.4 Sau khi chạy, 3.5 Kiểm chứng trên Amazon Beauty (dữ liệu đối chứng), 3.6 Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF (+4 more)

### Community 108 - "ket_qua"
Cohesion: 0.20
Nodes (7): bt(), du_lieu(), ket_qua(), n_better(), the(), the_so(), vong()

### Community 109 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 116 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

## Knowledge Gaps
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `7. Cấu trúc mã và API` connect `.getProps` to `.get`, `test_demo.py`, `o`, `Demo web — shop thời trang H&M (kèm Amazon Beauty)`?**
  _High betweenness centrality (0.392) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `torch` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Why does `test_results_page_matches_report_macros()` connect `test_demo.py` to `.getProps`?**
  _High betweenness centrality (0.367) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06600877192982456 - nodes in this community are weakly interconnected._
- **Why does `a()` connect `o` to `i`, `n`, `eo`, `no`, `.getParsed`, `u`, `.getProps`, `e`, `rs`, `.get`, `chart.umd.min.js`, `Si`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09116809116809117 - nodes in this community are weakly interconnected._