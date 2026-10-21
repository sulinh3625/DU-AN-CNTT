# Graph Report - DU-AN-CNTT  (2026-10-21)

## Corpus Check
- 97 files · ~218,602 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 115 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 21)

## Summary
- 1285 nodes · 2950 edges · 74 communities (62 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 128 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `19f14620`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 24_report_v2.py
- app.js
- numpy
- run.py
- test_data_pipeline.py
- routes.py
- v2_common.py
- Đăng ký trước (pre-registration) — giao thức v2
- protocol_v2.py
- DataContext
- mau_kiem_dinh
- test_demo.py
- test_v2.py
- data_context.py
- features.py
- test_v2_final.py
- 19_check_report.py
- test_bosung.py
- NeuMFF
- 25_bosung.py
- reviews_Beauty_5
- .run_seed
- HMAdapter
- argparse
- test_models.py
- test_prepare.py
- test_baselines.py
- MaskedScoreFn
- user_rows
- 23_final_v2.py
- UserKNNBaseline
- test_amazon.py
- ContentProfile
- DailySales
- TraditionalHybrid
- build_features
- io.py
- amazon.py
- 22_tune_v2.py
- test_report_tools.py
- Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty
- pathlib
- interaction_matrix
- Đăng ký trước (pre-registration) — thực nghiệm hm500k
- Demo web — shop thời trang H&M (kèm Amazon Beauty)
- Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F
- README.md
- Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)
- overview.py
- neumf_project — mã nguồn của đề tài
- claims
- Phần 2. Nắm toàn bộ đề tài
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- MLP
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- Phần 5. Câu hỏi hội đồng hay hỏi
- ItemKNNBaseline
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- user_filter
- __main__.py
- 13. Lịch sử phát triển
- 2. Tiến độ (13/10/2026)
- 9. Đánh giá, kiểm định và chống thiên lệch
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `esc()` - 31 edges
2. `DataContext` - 30 edges
3. `main()` - 30 edges
4. `initAdmin()` - 24 edges
5. `final()` - 21 edges
6. `build_from_pairs()` - 21 edges
7. `NeuMFF` - 21 edges
8. `ctx()` - 19 edges
9. `build_features()` - 18 edges
10. `Catalog` - 17 edges

## Surprising Connections (you probably didn't know these)
- `2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026` --references--> `make_stage()`  [INFERRED]
  tong_hop.md → neumf_project/src/data_pipeline/protocol_v2.py
- `13.4 Dọn mã (10/10/2026)` --references--> `evaluate_v2()`  [INFERRED]
  tong_hop.md → neumf_project/src/evaluation/v2.py
- `10.3 Kiểm thử` --references--> `saved_final_ranks()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/data_context.py
- `10.3 Kiểm thử` --references--> `final_result()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/inference.py
- `10.1 Quy trình thực nghiệm` --references--> `tune()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/25_bosung.py

## Import Cycles
- None detected.

## Communities (74 total, 12 thin omitted)

### Community 0 - "24_report_v2.py"
Cohesion: 0.05
Nodes (54): _block(), _by_k(), dashboard(), _named(), ablation(), beyond(), bootstrap_ci(), by_k() (+46 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (95): ad, ANSWER, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT (+87 more)

### Community 2 - "numpy"
Cohesion: 0.06
Nodes (35): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), recommend(), score_items() (+27 more)

### Community 3 - "run.py"
Cohesion: 0.06
Nodes (30): no_cache(), _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune() (+22 more)

### Community 4 - "test_data_pipeline.py"
Cohesion: 0.06
Nodes (13): BPRMFBaseline, MostPopularBaseline, RandomBaseline, TrainDataset, iterative_k_core(), available_negatives(), build_user_positive_sets(), sample_train_negatives() (+5 more)

### Community 5 - "routes.py"
Cohesion: 0.10
Nodes (20): context(), ctx(), dashboard(), example(), has_images(), health(), history(), image() (+12 more)

### Community 6 - "v2_common.py"
Cohesion: 0.09
Nodes (19): base_key(), configs_for(), device(), eval_kw(), evaluate(), fit_torch(), hybrid_components(), is_feature() (+11 more)

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.06
Nodes (32): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo (+24 more)

### Community 8 - "protocol_v2.py"
Cohesion: 0.12
Nodes (14): export(), main(), check_product_code(), group_by_product(), product_code_of(), to_day(), aggregate_unique_user_item(), build_from_pairs() (+6 more)

### Community 9 - "DataContext"
Cohesion: 0.09
Nodes (10): DataContext, best_rank_series(), pick_example(), saved_best_series(), showcase_users(), user_profile(), test_history_is_training_data_before_cutoff(), test_neighbors_are_sorted_and_counted() (+2 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "test_demo.py"
Cohesion: 0.10
Nodes (14): amazon_table(), product_table(), user_table(), 7. Cấu trúc mã và API, _macros(), _report_tools(), test_amazon_table_maps_metadata_to_item_columns(), test_dashboard_reads_result_files() (+6 more)

### Community 12 - "test_v2.py"
Cohesion: 0.12
Nodes (15): FeatureTrainDataset, item_time_features(), user_time_features(), _catalog(), _day(), _sales(), test_feature_dataset_negatives_launched_and_not_positive(), test_group_by_product_merges_colour_variants() (+7 more)

### Community 13 - "data_context.py"
Cohesion: 0.10
Nodes (9): results_dir(), saved_final_ranks(), unavailable_reason(), v2_available(), v2_data_mismatch(), datasets(), test_dataset_without_final_results_reports_command_not_training(), test_results_from_other_data_are_refused() (+1 more)

### Community 14 - "features.py"
Cohesion: 0.20
Nodes (11): build_amazon(), main(), build_catalog(), build_daily_sales(), build_user_profile(), Catalog, _codes(), load_catalog() (+3 more)

### Community 15 - "test_v2_final.py"
Cohesion: 0.10
Nodes (8): _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_dirty_files_ignores_outputs_and_test_log(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_opened_seeds_reads_only_tags_of_current_holdout(), test_report_runs_end_to_end_on_tiny_results()

### Community 16 - "19_check_report.py"
Cohesion: 0.17
Nodes (13): check_claims(), check_macros_and_tables(), compare_with_committed(), Data, load(), defined_macros(), find_line(), key_numbers() (+5 more)

### Community 17 - "test_bosung.py"
Cohesion: 0.18
Nodes (10): combine(), crossfit_scores(), fit_weights(), pair_differences(), _args(), _synthetic(), test_bosung_lock_lists_every_violation(), test_bosung_lock_passes_and_overrides_are_explicit() (+2 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 19 - "25_bosung.py"
Cohesion: 0.18
Nodes (8): component_check(), file_md5(), final(), lock_errors(), opened_tags(), Precomputed, provenance(), tune()

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - ".run_seed"
Cohesion: 0.17
Nodes (7): ablations(), beyond(), foreign_results(), main(), Runner, record(), score()

### Community 22 - "HMAdapter"
Cohesion: 0.17
Nodes (3): AmazonAdapter, DatasetAdapter, HMAdapter

### Community 23 - "argparse"
Cohesion: 0.17
Nodes (5): main(), bucket_of(), main(), select_buckets(), main()

### Community 24 - "test_models.py"
Cohesion: 0.20
Nodes (6): build_torch(), mlp_layers(), GMF, NeuMF, test_forward_shapes_and_logits(), test_neumf_uses_four_independent_embeddings()

### Community 25 - "test_prepare.py"
Cohesion: 0.20
Nodes (9): load_pairs(), _day(), _hm_sample(), test_candidates_and_targets_only_items_with_training_pairs(), test_data_from_file_matches_build_v2(), test_export_twice_gives_same_bytes_and_md5(), test_load_data_rejects_missing_file_and_md5_mismatch(), test_prepare_again_keeps_manifest_when_only_commit_differs() (+1 more)

### Community 26 - "test_baselines.py"
Cohesion: 0.21
Nodes (6): late_fusion(), LateFusion, minmax(), model_scores(), test_late_fusion_extremes_reproduce_component_ranking(), test_minmax_constant_is_zero()

### Community 27 - "MaskedScoreFn"
Cohesion: 0.18
Nodes (4): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), MaskedScoreFn, MaskedScorer, test_masked_scorer_puts_unscoreable_items_last()

### Community 28 - "user_rows"
Cohesion: 0.22
Nodes (8): filter_users(), _filtered(), position(), random_user(), search_users(), user_position(), at(), user_rows()

### Community 29 - "23_final_v2.py"
Cohesion: 0.26
Nodes (7): cpu_name(), dirty_files(), git(), lock_errors(), machine_info(), opened_seeds(), tuning_code_hashes()

### Community 30 - "UserKNNBaseline"
Cohesion: 0.23
Nodes (7): UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors(), _topk_dense(), _toy()

### Community 31 - "test_amazon.py"
Cohesion: 0.22
Nodes (7): category_path(), test_adapter_codes_asins_in_sorted_order(), test_amazon_config_uses_hm_configs_without_tuning(), test_features_catalog_and_daily_reviews(), test_load_data_amazon_config_without_customers(), _ts(), _write()

### Community 32 - "ContentProfile"
Cohesion: 0.23
Nodes (4): ContentProfile, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_recent_popularity_and_content_profile()

### Community 33 - "DailySales"
Cohesion: 0.18
Nodes (5): data_name(), load_data(), manifest_path(), DailySales, load_daily_sales()

### Community 34 - "TraditionalHybrid"
Cohesion: 0.23
Nodes (4): TraditionalHybrid, Table, test_features_are_minmax_on_the_candidate_set(), test_four_fusions()

### Community 35 - "build_features"
Cohesion: 0.29
Nodes (4): asin_list(), build_features(), item_info(), read_reviews()

### Community 36 - "io.py"
Cohesion: 0.27
Nodes (5): log_test_access(), prereg_committed(), write_json(), test_log_test_access_appends_rows(), test_prereg_missing_means_not_committed()

### Community 37 - "amazon.py"
Cohesion: 0.24
Nodes (3): read_meta(), category_codes(), text_vectors()

### Community 38 - "22_tune_v2.py"
Cohesion: 0.31
Nodes (5): load_best(), log_row(), logged(), main(), ensure_dir()

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 41 - "pathlib"
Cohesion: 0.24
Nodes (4): test_hm_adapter_rejects_excel(), _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.20
Nodes (9): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 9. Mở rộng sau khi xem test (+1 more)

### Community 44 - "Demo web — shop thời trang H&M (kèm Amazon Beauty)"
Cohesion: 0.20
Nodes (8): popular(), 1. Chuẩn bị, 2. Chạy, 3. Màn hình, 4. Cách chấm — khớp đánh giá cuối, 5. Biến môi trường, 6. Ảnh sản phẩm (tuỳ chọn), Demo web — shop thời trang H&M (kèm Amazon Beauty)

### Community 45 - "Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F"
Cohesion: 0.20
Nodes (10): 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F, Phần 1. Thông điệp chính, Phần 3. Số liệu cần nhớ, Phần 4. Nội dung nào nói trong báo cáo, nội dung nào chỉ nói khi được hỏi, Phần 6. Câu không được nói (+2 more)

### Community 46 - "README.md"
Cohesion: 0.22
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - "overview.py"
Cohesion: 0.28
Nodes (4): answers(), results(), _verdict(), test_research_answers_follow_significance()

### Community 49 - "neumf_project — mã nguồn của đề tài"
Cohesion: 0.22
Nodes (7): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, 6. Cấu trúc thư mục, neumf_project — mã nguồn của đề tài

### Community 50 - "claims"
Cohesion: 0.28
Nodes (4): claims(), by_k_order(), hyb_fifth(), order()

### Community 51 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.2), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.3), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 52 - "Tổng hợp đồ án: phương pháp, kết quả và tiến độ"
Cohesion: 0.25
Nodes (8): 11. Hạn chế đã biết, 12. Đối chiếu 17 góp ý trước của GVHD, 14.1 File, 14.2 Tài liệu tham khảo chính, 14. Danh sách file và tài liệu tham khảo, 1. Đồ án làm gì — nói ngắn, 5. Những điều phải nói thẳng khi bảo vệ, Tổng hợp đồ án: phương pháp, kết quả và tiến độ

### Community 53 - "3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định"
Cohesion: 0.25
Nodes (8): 3.1 Lần chạy, 3.2 NDCG@10 của 14 mô hình (trung bình ± độ lệch chuẩn qua 5 seed), 3.3 Theo K = 5, 10, 15, 20 (báo cáo mục 4.4.2, Bảng 4.5–4.6), 3.4 Họ 10 so sánh đăng ký trước, 3.5 Phân tích phụ (chỉ mô tả, không kiểm định), 3.6 Trả lời câu hỏi nghiên cứu, 3.7 Phân tích bổ sung: mô hình lai truyền thống Hybrid-CBCF (báo cáo mục 4.4.4, Bảng 4.8), 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định

### Community 54 - "MLP"
Cohesion: 0.38
Nodes (3): 8. Lệch kế hoạch, MLP, test_mlp_dropout_is_configurable()

### Community 55 - "4. Kiểm chứng trên Amazon Beauty"
Cohesion: 0.29
Nodes (7): 4.1 Lần chạy, 4.2 Kết quả trên tập kiểm thử Amazon (5 seed; báo cáo Bảng 4.11, Hình 4.6), 4.3 Họ 10 so sánh, đặt cạnh kết luận của H&M (báo cáo Bảng 4.15–4.16), 4.4 Ba kết luận của H&M có còn đúng không (báo cáo mục 4.5.2), 4.5 Ablation và độ phủ (seed 42; báo cáo Bảng 4.17), 4.6 Hybrid-CBCF trên Amazon (phân tích bổ sung; báo cáo mục 4.5.1, Bảng 4.14), 4. Kiểm chứng trên Amazon Beauty

### Community 56 - "7. Dữ liệu"
Cohesion: 0.29
Nodes (7): 7.1 Nguồn H&M và lý do lấy mẫu, 7.2 Hai mẫu khách hàng, 7.3 Tiền xử lý (`scripts/02_prepare_data.py`; báo cáo Thuật toán 3.1), 7.4 Giai đoạn đánh giá và tập ứng viên, 7.5 Đặc trưng theo thời điểm (H&M), 7.6 Amazon Beauty (`audit/PREREG_amazon.md`), 7. Dữ liệu

### Community 57 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 59 - "10. Code, demo, kiểm thử và báo cáo"
Cohesion: 0.33
Nodes (6): 10.1 Quy trình thực nghiệm, 10.2 Demo (`demo/README.md`), 10.3 Kiểm thử, 10.4 Báo cáo LaTeX (`Report DACNTT/`), 10.5 Lưu ý khi làm tiếp, 10. Code, demo, kiểm thử và báo cáo

### Community 60 - "6. Bài toán, câu hỏi nghiên cứu và phạm vi"
Cohesion: 0.33
Nodes (6): 6.1 Bài toán, 6.2 Câu hỏi nghiên cứu, 6.3 Yêu cầu R1–R9, 6.4 Phạm vi, 6.5 Vì sao thiết kế như vậy, 6. Bài toán, câu hỏi nghiên cứu và phạm vi

### Community 61 - "8. Mô hình"
Cohesion: 0.33
Nodes (6): 8.1 NeuMF-F — mô hình đề xuất (`src/models/hybrid_features.py`), 8.2 Hợp nhất sớm và hợp nhất muộn, 8.3 Mô hình đối chứng và cấu hình đã chọn, 8.4 Ablation NeuMF-F, 8.5 Mô hình lai truyền thống Hybrid-CBCF — bổ sung sau đánh giá cuối, 8. Mô hình

### Community 64 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 65 - "2. Tiến độ (13/10/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (13/10/2026)

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

## Knowledge Gaps
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` connect `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` to `13. Lịch sử phát triển`, `2. Tiến độ (13/10/2026)`, `9. Đánh giá, kiểm định và chống thiên lệch`, `README.md`, `3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định`, `4. Kiểm chứng trên Amazon Beauty`, `7. Dữ liệu`, `10. Code, demo, kiểm thử và báo cáo`, `6. Bài toán, câu hỏi nghiên cứu và phạm vi`, `8. Mô hình`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `DataContext` (e.g. with `TraditionalHybrid` and `EvalRecord`) actually correct?**
  _`DataContext` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `24_report_v2.py` be split into smaller, more focused modules?**
  _Cohesion score 0.054215625644197074 - nodes in this community are weakly interconnected._
- **Why does `10. Code, demo, kiểm thử và báo cáo` connect `10. Code, demo, kiểm thử và báo cáo` to `Tổng hợp đồ án: phương pháp, kết quả và tiến độ`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06513157894736842 - nodes in this community are weakly interconnected._
- **Why does `evaluate_v2()` connect `numpy` to `13. Lịch sử phát triển`, `v2_common.py`, `25_bosung.py`, `.run_seed`, `test_prepare.py`, `23_final_v2.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Should `numpy` be split into smaller, more focused modules?**
  _Cohesion score 0.05727848101265823 - nodes in this community are weakly interconnected._