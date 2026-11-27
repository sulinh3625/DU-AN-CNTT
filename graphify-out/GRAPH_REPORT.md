# Graph Report - DU-AN-CNTT  (2026-11-27)

## Corpus Check
- 113 files · ~222,621 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 115 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 20)

## Summary
- 2327 nodes · 5281 edges · 122 communities (90 shown, 32 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 239 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `12abda76`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- recommend
- app.js
- build_poster.py
- run.py
- d
- routes.py
- .isHorizontal
- Đăng ký trước (pre-registration) — giao thức v2
- o
- DataContext
- mau_kiem_dinh
- En
- test_prepare.py
- os
- download_hm_images.py
- benchmark_demo.py
- 8_check_report.py
- test_v2_final.py
- NeuMFF
- bn
- reviews_Beauty_5
- 5_final.py
- n
- test_v2_final.py
- Trang
- chart.umd.min.js
- hinh_bao_cao.py
- features.py
- va
- ns
- 2_prepare.py
- pathlib
- i
- hop
- 7_report.py
- .buildOrUpdateControllers
- bt
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
- draw
- test_v2.py
- numpy
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- 22_tune_v2.py
- metrics_io.py
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- s
- __main__.py
- macros
- user_rows
- 9. Đánh giá, kiểm định và chống thiên lệch
- Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)
- test_demo.py
- subprocess
- o
- tn
- BPRMFBaseline
- data_context.py
- results_dir
- .get
- fit_torch
- user_filter
- 2. Tiến độ (12/11/2026)
- 13. Lịch sử phát triển
- hybrid_features.py
- LateFusion
- .__init__
- test_baselines.py
- test_evaluation.py
- EvalRecord
- pathlib
- u
- summary
- 6_bosung.py
- Cs
- slide
- .getLabels
- bam
- Sơ đồ của đề tài
- .notifyPlugins
- neumf_project — mã nguồn của đề tài
- rs
- cn
- TrainDataset
- history
- ket_qua
- claims
- evaluate_v2
- add_par
- update
- the_bt
- ItemKNNBaseline
- main.py
- argparse
- Kế hoạch phân công tiến độ DACNTT_8d8e062d.md
- morph
- trang_thai
- so_voi_truyen_thong
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
9. `main()` - 30 edges
10. `Trang` - 28 edges

## Surprising Connections (you probably didn't know these)
- `0.3 Câu hỏi xoáy mới (kiểm bằng số liệu và mã nguồn ngày 26/11/2026)` --references--> `fit_torch()`  [INFERRED]
  van_dap.md → neumf_project/scripts/common.py
- `2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026` --references--> `make_stage()`  [INFERRED]
  tong_hop.md → neumf_project/src/data_pipeline/protocol_v2.py
- `13.4 Dọn mã (10/10/2026)` --references--> `evaluate_v2()`  [INFERRED]
  tong_hop.md → neumf_project/src/evaluation/v2.py
- `10.1 Quy trình thực nghiệm` --references--> `tune()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/6_bosung.py
- `10.1 Quy trình thực nghiệm` --references--> `final()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/6_bosung.py

## Import Cycles
- None detected.

## Communities (122 total, 32 thin omitted)

### Community 0 - "recommend"
Cohesion: 0.16
Nodes (8): best_ranks(), candidate_scores(), eval_record(), rank_from_scores(), recommend(), score_items(), test_best_ranks_match_recommend(), test_late_fusion_minmax_on_candidates()

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (95): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+87 more)

### Community 2 - "build_poster.py"
Cohesion: 0.11
Nodes (4): set_runs(), ghi_hieu_ung(), _hien(), _hieu_ung()

### Community 3 - "run.py"
Cohesion: 0.07
Nodes (29): _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report() (+21 more)

### Community 5 - "routes.py"
Cohesion: 0.12
Nodes (18): context(), ctx(), example(), _filtered(), has_images(), health(), image(), neighbors() (+10 more)

### Community 6 - ".isHorizontal"
Cohesion: 0.10
Nodes (4): Do(), Oe(), Xs(), Y()

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.06
Nodes (32): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo (+24 more)

### Community 8 - "o"
Cohesion: 0.10
Nodes (32): b(), e(), ei(), fs(), g(), gi(), Gn(), inRange() (+24 more)

### Community 9 - "DataContext"
Cohesion: 0.10
Nodes (9): DataContext, best_rank_series(), pick_example(), saved_best_series(), showcase_users(), user_profile(), test_history_is_training_data_before_cutoff(), test_neighbors_are_sorted_and_counted() (+1 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 12 - "test_prepare.py"
Cohesion: 0.08
Nodes (21): hybrid_components(), HMAdapter, DailySales, group_by_product(), product_code_of(), build_from_pairs(), build_v2(), DataV2 (+13 more)

### Community 14 - "download_hm_images.py"
Cohesion: 0.12
Nodes (6): fetch(), get_range(), main(), member_bytes(), RangeFile, zip_url()

### Community 16 - "8_check_report.py"
Cohesion: 0.13
Nodes (15): _net(), o(), check_claims(), check_macros_and_tables(), compare_with_committed(), Data, load(), defined_macros() (+7 more)

### Community 17 - "test_v2_final.py"
Cohesion: 0.12
Nodes (15): tune(), combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic() (+7 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - "5_final.py"
Cohesion: 0.12
Nodes (14): ablations(), beyond(), cpu_name(), dirty_files(), foreign_results(), git(), lock_errors(), machine_info() (+6 more)

### Community 22 - "n"
Cohesion: 0.11
Nodes (14): Fn(), getLabelAndValue(), getMaxOverflow(), _getRuler(), In(), lt(), n(), ne() (+6 more)

### Community 23 - "test_v2_final.py"
Cohesion: 0.09
Nodes (8): _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_report_beyond_late_fusion_time_is_sum_of_branches(), test_report_metric_bars_share_one_color(), test_report_runs_end_to_end_on_tiny_results()

### Community 24 - "Trang"
Cohesion: 0.12
Nodes (9): cac_buoc(), chia_thoi_gian(), demo_ngang(), duong_ong(), tinh_chinh_danh_gia(), Trang, vien_(), xu_ly_du_lieu() (+1 more)

### Community 25 - "chart.umd.min.js"
Cohesion: 0.03
Nodes (29): at(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), beforeLayout(), Bi(), da(), destroy() (+21 more)

### Community 26 - "hinh_bao_cao.py"
Cohesion: 0.16
Nodes (13): du_lieu_amazon_ngang(), du_lieu_hm_ngang(), _du_lieu_ngang(), hop_nhat(), kien_truc_neumf(), kien_truc_neumf_f(), _neumf(), neumf_f_ngang() (+5 more)

### Community 27 - "features.py"
Cohesion: 0.14
Nodes (17): build_amazon(), main(), load_data(), build_catalog(), build_daily_sales(), build_user_profile(), Catalog, category_codes() (+9 more)

### Community 28 - "va"
Cohesion: 0.06
Nodes (11): Ee(), eo(), f(), Hs, Le(), Oi(), Si(), start() (+3 more)

### Community 29 - "ns"
Cohesion: 0.05
Nodes (8): As(), _calculateBarValuePixels(), initialize(), jn, ns(), rt(), updateElements(), zs()

### Community 30 - "2_prepare.py"
Cohesion: 0.26
Nodes (6): export(), main(), check_product_code(), to_day(), prepare_pairs(), write_json()

### Community 31 - "pathlib"
Cohesion: 0.11
Nodes (13): AmazonAdapter, asin_list(), build_features(), category_path(), item_info(), read_meta(), read_reviews(), test_adapter_codes_asins_in_sorted_order() (+5 more)

### Community 32 - "i"
Cohesion: 0.12
Nodes (12): be(), ct(), ge(), generateLabels(), gs(), ki(), ms(), pe() (+4 more)

### Community 33 - "hop"
Cohesion: 0.18
Nodes (7): bong(), chu_thich(), hop(), khung_cam(), khung_tren_hinh(), paras(), so_tron()

### Community 34 - "7_report.py"
Cohesion: 0.06
Nodes (50): ablation(), beyond(), bootstrap_ci(), by_k(), cell(), dev_info(), ensure(), export_by_k() (+42 more)

### Community 37 - "no"
Cohesion: 0.09
Nodes (11): buildLookupTable(), ca(), Fo(), _generate(), _getTimestampsForTable(), ha, initOffsets(), no (+3 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - ".constructor"
Cohesion: 0.16
Nodes (8): Ci(), dt(), fe(), ks(), nn(), on(), sn, wn()

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 42 - "zt"
Cohesion: 0.11
Nodes (9): Ft(), It(), kt(), mt(), qt(), _t(), wt(), Xt() (+1 more)

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.18
Nodes (10): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 8. Lệch kế hoạch (+2 more)

### Community 44 - "Demo web — shop thời trang H&M (kèm Amazon Beauty)"
Cohesion: 0.20
Nodes (8): popular(), 1. Chuẩn bị, 2. Chạy, 3. Màn hình, 4. Cách chấm — khớp đánh giá cuối, 5. Biến môi trường, 6. Ảnh sản phẩm (tuỳ chọn), Demo web — shop thời trang H&M (kèm Amazon Beauty)

### Community 45 - "Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F"
Cohesion: 0.05
Nodes (40): 0.1 Bốn điểm yếu hội đồng có thể xoáy sâu (đánh giá 18/11/2026), 0.2 Câu hỏi bám theo từng slide (soạn 26/11/2026), 0.3 Câu hỏi xoáy mới (kiểm bằng số liệu và mã nguồn ngày 26/11/2026), 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2) (+32 more)

### Community 46 - "README.md"
Cohesion: 0.22
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - "test_models.py"
Cohesion: 0.15
Nodes (9): build_torch(), mlp_layers(), GMF, MLP, NeuMF, test_late_fusion_extremes_reproduce_component_ranking(), test_forward_shapes_and_logits(), test_mlp_dropout_is_configurable() (+1 more)

### Community 49 - "draw"
Cohesion: 0.12
Nodes (19): ai(), ao(), dataset(), draw(), hi(), index(), ji(), kn() (+11 more)

### Community 50 - "test_v2.py"
Cohesion: 0.12
Nodes (13): FeatureTrainDataset, item_time_features(), _catalog(), _day(), _sales(), test_feature_dataset_negatives_launched_and_not_positive(), test_group_by_product_merges_colour_variants(), test_item_time_features_use_only_days_before_t() (+5 more)

### Community 51 - "numpy"
Cohesion: 0.13
Nodes (9): DatasetAdapter, iterative_k_core(), available_negatives(), build_user_positive_sets(), sample_train_negatives(), aggregate_unique_user_item(), test_aggregate_before_kcore_counts_unique_edges(), test_negative_sampler_never_returns_positive() (+1 more)

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
Nodes (7): 7.1 Nguồn H&M và lý do lấy mẫu, 7.2 Hai mẫu khách hàng, 7.3 Tiền xử lý (`scripts/2_prepare.py`; báo cáo Thuật toán 3.1), 7.4 Giai đoạn đánh giá và tập ứng viên, 7.5 Đặc trưng theo thời điểm (H&M), 7.6 Amazon Beauty (`audit/PREREG_amazon.md`), 7. Dữ liệu

### Community 57 - "22_tune_v2.py"
Cohesion: 0.18
Nodes (9): load_best(), log_row(), logged(), main(), ensure_dir(), log_test_access(), prereg_committed(), test_log_test_access_appends_rows() (+1 more)

### Community 58 - "metrics_io.py"
Cohesion: 0.29
Nodes (6): _block(), _by_k(), dashboard(), _named(), dashboard(), test_dashboard_reads_result_files()

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
Cohesion: 0.12
Nodes (15): bo, _calculateBarIndexPixels(), et(), _getStackCount(), _getStackIndex(), _getStacks(), H(), ho() (+7 more)

### Community 65 - "user_rows"
Cohesion: 0.18
Nodes (8): filter_users(), user_position(), at(), user_rows(), test_filter_users_search_sort_and_position(), test_short_code_finds_customer(), test_user_table_counts_area_age_and_buckets(), _users()

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 67 - "Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)"
Cohesion: 0.33
Nodes (5): graphify, Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script), Quy ước báo cáo (`Report DACNTT/`), Ranh giới, Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

### Community 74 - "test_demo.py"
Cohesion: 0.08
Nodes (15): unavailable_reason(), v2_available(), answers(), results(), _verdict(), datasets(), 7. Cấu trúc mã và API, _macros() (+7 more)

### Community 75 - "subprocess"
Cohesion: 0.22
Nodes (6): _ghi(), _edge(), _html(), _khung(), xuat(), main()

### Community 76 - "o"
Cohesion: 0.09
Nodes (14): a(), aa(), afterDatasetsUpdate(), configure(), determineDataLimits(), Di(), _i(), j() (+6 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.14
Nodes (3): BPRMFBaseline, MostPopularBaseline, RandomBaseline

### Community 79 - "data_context.py"
Cohesion: 0.21
Nodes (3): deterministic_tie_key(), rank_positives(), test_tie_ranking_is_deterministic()

### Community 80 - "results_dir"
Cohesion: 0.14
Nodes (7): results_dir(), saved_final_ranks(), v2_data_mismatch(), final_result(), metrics_of(), test_results_from_other_data_are_refused(), 10.3 Kiểm thử

### Community 81 - ".get"
Cohesion: 0.19
Nodes (5): ce(), de, he(), qs(), te()

### Community 82 - "fit_torch"
Cohesion: 0.19
Nodes (8): base_key(), fit_torch(), is_feature(), torch_scorer(), count_parameters(), _gpu_mem_str(), make_optimizer(), train_one_model()

### Community 84 - "2. Tiến độ (12/11/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (18/11/2026)

### Community 85 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 86 - "hybrid_features.py"
Cohesion: 0.06
Nodes (18): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), configs_for(), data_name(), device(), eval_kw(), evaluate(), manifest_path(), read_config() (+10 more)

### Community 87 - "LateFusion"
Cohesion: 0.17
Nodes (11): late_fusion(), LateFusion, minmax(), model_scores(), _dense_cosine(), test_itemknn_scores_follow_definition(), test_minmax_constant_is_zero(), test_topk_cosine_matches_dense_bruteforce() (+3 more)

### Community 88 - ".__init__"
Cohesion: 0.15
Nodes (6): amazon_table(), product_table(), user_table(), test_amazon_table_maps_metadata_to_item_columns(), test_product_table_uses_first_variant_and_counts_colours(), test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 89 - "test_baselines.py"
Cohesion: 0.17
Nodes (3): interaction_matrix(), topk_cosine(), UserKNNBaseline

### Community 90 - "test_evaluation.py"
Cohesion: 0.28
Nodes (10): build_full_ranking_records_multi(), hr_at_k(), multi_ranking_metrics(), ndcg_at_k(), precision_at_k(), recall_at_k(), test_full_ranking_excludes_seen_and_keeps_positive(), test_multi_metrics_equal_single_item_formulas() (+2 more)

### Community 91 - "EvalRecord"
Cohesion: 0.16
Nodes (9): _append(), _empty_metric_lists(), EvalRecord, evaluate_score_function(), evaluate_torch_model(), _per_user_row(), test_per_user_rows_match_summary_and_count_candidates(), test_perfect_model_hr_ndcg_one() (+1 more)

### Community 93 - "pathlib"
Cohesion: 0.11
Nodes (6): test_hm_adapter_rejects_excel(), data(), test_report_claims_detect_changed_results(), _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

### Community 96 - "6_bosung.py"
Cohesion: 0.17
Nodes (7): component_check(), file_md5(), final(), lock_errors(), opened_tags(), Precomputed, provenance()

### Community 98 - "slide"
Cohesion: 0.21
Nodes (8): anh(), anh_vua(), hinh(), logo(), nen(), nhan_chuong(), ra_sau(), slide()

### Community 99 - ".getLabels"
Cohesion: 0.10
Nodes (10): Ae(), buildTicks(), getPixelForTick(), getPixelForValue(), getValueForPixel(), go(), init(), parse() (+2 more)

### Community 100 - "bam"
Cohesion: 0.33
Nodes (3): bam(), pha(), phang()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.50
Nodes (3): Lối vẽ, Sơ đồ của đề tài, Sửa và xuất lại

### Community 103 - "neumf_project — mã nguồn của đề tài"
Cohesion: 0.22
Nodes (7): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, 6. Cấu trúc thư mục, neumf_project — mã nguồn của đề tài

### Community 105 - "cn"
Cohesion: 0.18
Nodes (8): cn(), dn(), hn(), ln(), rn(), to(), un(), x()

### Community 107 - "history"
Cohesion: 0.24
Nodes (5): history(), recommend(), _user(), test_customer_without_targets_gets_model_recommendations(), test_new_customer_gets_popular_list_instead_of_error()

### Community 108 - "ket_qua"
Cohesion: 0.20
Nodes (9): bieu_do(), du_lieu(), ket_qua(), n_better(), nhan_xet(), text(), the(), the_so() (+1 more)

### Community 109 - "claims"
Cohesion: 0.28
Nodes (4): claims(), by_k_order(), hyb_fifth(), order()

### Community 110 - "evaluate_v2"
Cohesion: 0.22
Nodes (3): evaluate_v2(), positive_ranks(), _torch_scores()

### Community 111 - "add_par"
Cohesion: 0.25
Nodes (6): add_par(), bullets(), chu_thich(), ribbon(), style(), textbox()

### Community 112 - "update"
Cohesion: 0.29
Nodes (8): addElements(), es(), is(), pt(), Qi(), ss(), ts(), update()

### Community 113 - "the_bt"
Cohesion: 0.25
Nodes (5): chan_trang(), chuoi_buoc(), mui_ten(), the_bt(), vong()

### Community 116 - "argparse"
Cohesion: 0.12
Nodes (8): amazon_image_path(), main(), fetch(), main(), bucket_of(), main(), select_buckets(), main()

## Knowledge Gaps
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` connect `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` to `9. Đánh giá, kiểm định và chống thiên lệch`, `README.md`, `2. Tiến độ (12/11/2026)`, `3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định`, `13. Lịch sử phát triển`, `4. Kiểm chứng trên Amazon Beauty`, `7. Dữ liệu`, `10. Code, demo, kiểm thử và báo cáo`, `6. Bài toán, câu hỏi nghiên cứu và phạm vi`, `8. Mô hình`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06600877192982456 - nodes in this community are weakly interconnected._
- **Why does `an()` connect `an` to `.buildOrUpdateControllers`, `bt`, `.notifyPlugins`, `.constructor`, `cn`, `tn`, `draw`, `u`, `chart.umd.min.js`, `s`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10826210826210826 - nodes in this community are weakly interconnected._
- **Why does `Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F` connect `Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F` to `README.md`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `run.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07446808510638298 - nodes in this community are weakly interconnected._