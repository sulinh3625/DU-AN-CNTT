# Graph Report - DU-AN-CNTT  (2026-11-10)

## Corpus Check
- 104 files · ~436,612 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 120 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 20)

## Summary
- 2224 nodes · 5356 edges · 105 communities (89 shown, 16 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 228 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2fc4c6aa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Trang
- app.js
- build_poster.py
- run.py
- da
- routes.py
- torch
- Đăng ký trước (pre-registration) — giao thức v2, bản cuối
- protocol_v2.py
- DataContext
- mau_kiem_dinh
- n
- test_v2.py
- test_demo.py
- download_hm_images.py
- test_v2_final.py
- 19_check_report.py
- test_bosung.py
- NeuMFF
- 25_bosung.py
- reviews_Beauty_5
- .run_seed
- test_evaluation.py
- draw
- test_models.py
- chart.umd.min.js
- test_baselines.py
- MaskedScoreFn
- va
- ns
- xa
- test_amazon.py
- neumf_project — mã nguồn của đề tài
- build_from_pairs
- 3. Chạy thực nghiệm
- data_context.py
- sn
- no
- amazon.yaml
- json
- Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty
- an
- zt
- Đăng ký trước (pre-registration) — thực nghiệm hm500k
- Demo web — shop thời trang H&M (kèm Amazon Beauty)
- Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F
- README.md
- Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)
- TrainDataset
- Đăng ký trước (pre-registration) — giao thức v2
- jn
- pandas
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- user_rows
- 24_report_v2.py
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- s
- __main__.py
- .bindResponsiveEvents
- 2. Tiến độ (13/10/2026)
- 9. Đánh giá, kiểm định và chống thiên lệch
- Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)
- ket_qua
- eo
- a
- tn
- BPRMFBaseline
- Phần 5. Câu hỏi hội đồng hay hỏi
- .notifyPlugins
- .get
- v2_common.py
- Phần 2. Nắm toàn bộ đề tài
- u
- 13. Lịch sử phát triển
- Cs
- ContentProfile
- rs
- LateFusion
- bt
- download_amazon_images.py
- update
- claims
- add_par
- wt
- DatasetAdapter
- ca
- Precomputed
- 23_final_v2.py
- Sơ đồ của đề tài
- metrics_io.py
- sys
- features.py
- pytest

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
10. `o()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026` --references--> `make_stage()`  [INFERRED]
  tong_hop.md → neumf_project/src/data_pipeline/protocol_v2.py
- `13.4 Dọn mã (10/10/2026)` --references--> `evaluate_v2()`  [INFERRED]
  tong_hop.md → neumf_project/src/evaluation/v2.py
- `7. Cấu trúc mã và API` --references--> `k()`  [INFERRED]
  neumf_project/demo/README.md → image/src/so_do_bao_cao.py
- `3. Mô hình` --references--> `neumf()`  [INFERRED]
  neumf_project/audit/PREREG_v2.md → image/src/so_do_bao_cao.py
- `3. Mô hình` --references--> `neumf()`  [INFERRED]
  neumf_project/audit/PREREG_v2_cu.md → image/src/so_do_bao_cao.py

## Import Cycles
- None detected.

## Communities (105 total, 16 thin omitted)

### Community 0 - "Trang"
Cohesion: 0.09
Nodes (21): b(), ghi(), Trang, xuat(), danh_gia(), demo(), doc(), doi_chung() (+13 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (95): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+87 more)

### Community 2 - "build_poster.py"
Cohesion: 0.10
Nodes (7): set_runs(), bar_chart(), fit(), image(), macros(), picture_fit(), vn4()

### Community 3 - "run.py"
Cohesion: 0.07
Nodes (29): _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report() (+21 more)

### Community 4 - "da"
Cohesion: 0.16
Nodes (12): beforeDatasetDraw(), beforeDatasetsDraw(), da(), ea(), fa(), ga(), ha, na() (+4 more)

### Community 5 - "routes.py"
Cohesion: 0.11
Nodes (20): context(), ctx(), example(), _filtered(), has_images(), health(), image(), neighbors() (+12 more)

### Community 6 - "torch"
Cohesion: 0.24
Nodes (5): device(), count_parameters(), get_device(), _gpu_mem_str(), train_one_model()

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2, bản cuối"
Cohesion: 0.12
Nodes (15): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo, 7. Kiểm định (+7 more)

### Community 8 - "protocol_v2.py"
Cohesion: 0.16
Nodes (10): load_pairs(), evaluate_v2(), _day(), _hm_sample(), test_candidates_and_targets_only_items_with_training_pairs(), test_data_from_file_matches_build_v2(), test_export_twice_gives_same_bytes_and_md5(), test_load_data_rejects_missing_file_and_md5_mismatch() (+2 more)

### Community 9 - "DataContext"
Cohesion: 0.09
Nodes (11): DataContext, best_rank_series(), history(), pick_example(), saved_best_series(), showcase_users(), _user(), user_profile() (+3 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "n"
Cohesion: 0.06
Nodes (37): b(), be(), ct(), dn(), e(), ei(), fs(), g() (+29 more)

### Community 12 - "test_v2.py"
Cohesion: 0.12
Nodes (15): FeatureTrainDataset, Catalog, group_by_product(), item_time_features(), user_time_features(), build_v2(), _catalog(), _day() (+7 more)

### Community 13 - "test_demo.py"
Cohesion: 0.08
Nodes (15): amazon_table(), product_table(), user_table(), answers(), results(), _verdict(), _macros(), _report_tools() (+7 more)

### Community 14 - "download_hm_images.py"
Cohesion: 0.12
Nodes (6): fetch(), get_range(), main(), member_bytes(), RangeFile, zip_url()

### Community 15 - "test_v2_final.py"
Cohesion: 0.11
Nodes (7): _args(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_report_beyond_late_fusion_time_is_sum_of_branches(), test_report_metric_bars_share_one_color(), test_report_runs_end_to_end_on_tiny_results()

### Community 16 - "19_check_report.py"
Cohesion: 0.17
Nodes (13): check_claims(), check_macros_and_tables(), compare_with_committed(), Data, load(), defined_macros(), find_line(), key_numbers() (+5 more)

### Community 17 - "test_bosung.py"
Cohesion: 0.11
Nodes (15): tune(), combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic() (+7 more)

### Community 18 - "NeuMFF"
Cohesion: 0.16
Nodes (6): NeuMFF, branch(), id_emb(), test_neumff_branch_flags_and_items_without_id_scored(), test_neumff_eval_matches_training_path_and_time_features(), _toy_model()

### Community 19 - "25_bosung.py"
Cohesion: 0.17
Nodes (9): component_check(), file_md5(), final(), lock_errors(), main(), opened_tags(), provenance(), test_dirty_files_ignores_outputs_and_test_log() (+1 more)

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - ".run_seed"
Cohesion: 0.23
Nodes (5): ablations(), beyond(), Runner, record(), score()

### Community 22 - "test_evaluation.py"
Cohesion: 0.05
Nodes (38): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), recommend(), score_items() (+30 more)

### Community 23 - "draw"
Cohesion: 0.07
Nodes (40): ai(), ao(), average(), beforeDraw(), dataset(), draw(), getCenterPoint(), getMaxOverflow() (+32 more)

### Community 24 - "test_models.py"
Cohesion: 0.14
Nodes (8): build_torch(), GMF, MLP, NeuMF, test_forward_shapes_and_logits(), test_mlp_dropout_is_configurable(), test_neumf_uses_four_independent_embeddings(), test_refit_runs_fixed_epochs_without_validation()

### Community 25 - "chart.umd.min.js"
Cohesion: 0.04
Nodes (20): at(), cn(), d(), destroy(), Gt(), hn(), Ie(), Jo() (+12 more)

### Community 26 - "test_baselines.py"
Cohesion: 0.13
Nodes (10): interaction_matrix(), ItemKNNBaseline, topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors() (+2 more)

### Community 27 - "MaskedScoreFn"
Cohesion: 0.18
Nodes (4): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), MaskedScoreFn, MaskedScorer, test_masked_scorer_puts_unscoreable_items_last()

### Community 28 - "va"
Cohesion: 0.12
Nodes (6): afterDraw(), afterEvent(), f(), Oi(), va, x()

### Community 29 - "ns"
Cohesion: 0.06
Nodes (8): As(), bn, labelColor(), labelPointStyle(), ns(), pn(), rt(), zs()

### Community 31 - "test_amazon.py"
Cohesion: 0.11
Nodes (15): AmazonAdapter, asin_list(), build_features(), category_path(), item_info(), read_meta(), read_reviews(), category_codes() (+7 more)

### Community 32 - "neumf_project — mã nguồn của đề tài"
Cohesion: 0.22
Nodes (7): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, 6. Cấu trúc thư mục, neumf_project — mã nguồn của đề tài

### Community 33 - "build_from_pairs"
Cohesion: 0.17
Nodes (4): DailySales, build_from_pairs(), make_stage(), save_pairs()

### Community 34 - "3. Chạy thực nghiệm"
Cohesion: 0.29
Nodes (7): 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển, 3.2 Chạy thử (tuỳ chọn), 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần, 3.4 Sau khi chạy, 3.5 Kiểm chứng trên Amazon Beauty (dữ liệu đối chứng), 3.6 Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF, 3. Chạy thực nghiệm

### Community 35 - "data_context.py"
Cohesion: 0.12
Nodes (9): results_dir(), saved_final_ranks(), unavailable_reason(), v2_available(), v2_data_mismatch(), datasets(), test_dataset_without_final_results_reports_command_not_training(), test_results_from_other_data_are_refused() (+1 more)

### Community 36 - "sn"
Cohesion: 0.29
Nodes (4): fe(), ks(), nn(), sn

### Community 37 - "no"
Cohesion: 0.06
Nodes (15): buildLookupTable(), configure(), En, Fo(), _generate(), _getTimestampsForTable(), ia(), init() (+7 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - "json"
Cohesion: 0.11
Nodes (14): bucket_of(), main(), select_buckets(), main(), load_best(), log_row(), logged(), main() (+6 more)

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 41 - "an"
Cohesion: 0.10
Nodes (4): an(), generateLabels(), Mn(), onClick()

### Community 42 - "zt"
Cohesion: 0.14
Nodes (5): color(), jt(), te(), Xt(), zt()

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.18
Nodes (10): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 8. Lệch kế hoạch (+2 more)

### Community 44 - "Demo web — shop thời trang H&M (kèm Amazon Beauty)"
Cohesion: 0.20
Nodes (8): popular(), 1. Chuẩn bị, 2. Chạy, 3. Màn hình, 4. Cách chấm — khớp đánh giá cuối, 5. Biến môi trường, 6. Ảnh sản phẩm (tuỳ chọn), Demo web — shop thời trang H&M (kèm Amazon Beauty)

### Community 45 - "Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F"
Cohesion: 0.18
Nodes (10): 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F, Phần 1. Thông điệp chính, Phần 3. Số liệu cần nhớ, Phần 4. Nội dung nào nói trong báo cáo, nội dung nào chỉ nói khi được hỏi, Phần 6. Câu không được nói (+2 more)

### Community 46 - "README.md"
Cohesion: 0.25
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - "TrainDataset"
Cohesion: 0.18
Nodes (4): TrainDataset, available_negatives(), sample_train_negatives(), test_negative_sampler_never_returns_positive()

### Community 49 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.22
Nodes (8): 0. Vì sao có giao thức v2, 10. Lệch kế hoạch, 1. Dữ liệu, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký, Đăng ký trước (pre-registration) — giao thức v2

### Community 51 - "pandas"
Cohesion: 0.12
Nodes (11): export(), HMAdapter, check_product_code(), product_code_of(), iterative_k_core(), build_user_positive_sets(), aggregate_unique_user_item(), prepare_pairs() (+3 more)

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
Nodes (7): 4.1 Lần chạy, 4.2 Kết quả trên tập kiểm thử Amazon (5 seed; báo cáo Bảng 4.13, Hình 4.6), 4.3 Họ 10 so sánh, đặt cạnh kết luận của H&M (báo cáo Bảng 4.17–4.18), 4.4 Ba kết luận của H&M có còn đúng không (báo cáo mục 4.5.2), 4.5 Ablation và độ phủ (seed 42; báo cáo Bảng 4.19), 4.6 Hybrid-CBCF trên Amazon (phân tích bổ sung; báo cáo mục 4.4.2, Bảng 4.16), 4. Kiểm chứng trên Amazon Beauty

### Community 56 - "7. Dữ liệu"
Cohesion: 0.29
Nodes (7): 7.1 Nguồn H&M và lý do lấy mẫu, 7.2 Hai mẫu khách hàng, 7.3 Tiền xử lý (`scripts/02_prepare_data.py`; báo cáo Thuật toán 3.1), 7.4 Giai đoạn đánh giá và tập ứng viên, 7.5 Đặc trưng theo thời điểm (H&M), 7.6 Amazon Beauty (`audit/PREREG_amazon.md`), 7. Dữ liệu

### Community 57 - "user_rows"
Cohesion: 0.18
Nodes (8): filter_users(), user_position(), at(), user_rows(), test_filter_users_search_sort_and_position(), test_short_code_finds_customer(), test_user_table_counts_area_age_and_buckets(), _users()

### Community 58 - "24_report_v2.py"
Cohesion: 0.06
Nodes (49): ablation(), beyond(), bootstrap_ci(), by_k(), cell(), ensure(), export_by_k(), export_data() (+41 more)

### Community 59 - "10. Code, demo, kiểm thử và báo cáo"
Cohesion: 0.33
Nodes (6): 10.1 Quy trình thực nghiệm, 10.2 Demo (`demo/README.md`), 10.3 Kiểm thử, 10.4 Báo cáo LaTeX (`Report DACNTT/`), 10.5 Lưu ý khi làm tiếp, 10. Code, demo, kiểm thử và báo cáo

### Community 60 - "6. Bài toán, câu hỏi nghiên cứu và phạm vi"
Cohesion: 0.33
Nodes (6): 6.1 Bài toán, 6.2 Câu hỏi nghiên cứu, 6.3 Yêu cầu R1–R9, 6.4 Phạm vi, 6.5 Vì sao thiết kế như vậy, 6. Bài toán, câu hỏi nghiên cứu và phạm vi

### Community 61 - "8. Mô hình"
Cohesion: 0.33
Nodes (6): 8.1 NeuMF-F — mô hình đề xuất (`src/models/hybrid_features.py`), 8.2 Hợp nhất sớm và hợp nhất muộn, 8.3 Mô hình đối chứng và cấu hình đã chọn, 8.4 Ablation NeuMF-F, 8.5 Mô hình lai truyền thống Hybrid-CBCF — bổ sung sau đánh giá cuối, 8. Mô hình

### Community 62 - "s"
Cohesion: 0.13
Nodes (9): bo, et(), H(), s(), j(), label(), mo(), ne() (+1 more)

### Community 64 - ".bindResponsiveEvents"
Cohesion: 0.19
Nodes (3): ke(), removeBox(), stop()

### Community 65 - "2. Tiến độ (13/10/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (06/11/2026)

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 67 - "Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)"
Cohesion: 0.33
Nodes (5): graphify, Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script), Quy ước báo cáo (`Report DACNTT/`), Ranh giới, Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

### Community 74 - "ket_qua"
Cohesion: 0.19
Nodes (10): 3. Mô hình, 3. Mô hình, card(), content(), ket_qua(), n_better(), paras(), stat() (+2 more)

### Community 75 - "eo"
Cohesion: 0.10
Nodes (14): Bi(), ca(), Ci(), Do(), Ee(), eo(), Fi(), Ft() (+6 more)

### Community 76 - "a"
Cohesion: 0.07
Nodes (17): a(), aa(), afterDatasetsUpdate(), determineDataLimits(), Di(), dt(), getValueForPixel(), is() (+9 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.12
Nodes (4): BPRMFBaseline, MostPopularBaseline, RandomBaseline, test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 79 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 80 - ".notifyPlugins"
Cohesion: 0.17
Nodes (5): beforeUpdate(), initialize(), reset(), start(), wn()

### Community 81 - ".get"
Cohesion: 0.21
Nodes (4): ce(), de, he(), qs()

### Community 82 - "v2_common.py"
Cohesion: 0.12
Nodes (14): base_key(), configs_for(), data_name(), eval_kw(), evaluate(), fit_torch(), is_feature(), manifest_path() (+6 more)

### Community 83 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 84 - "u"
Cohesion: 0.32
Nodes (3): addBox(), u(), vn()

### Community 85 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 87 - "ContentProfile"
Cohesion: 0.13
Nodes (8): hybrid_components(), score_fn(), DataV2, Stage, ContentProfile, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_recent_popularity_and_content_profile()

### Community 89 - "LateFusion"
Cohesion: 0.21
Nodes (6): late_fusion(), LateFusion, minmax(), model_scores(), test_late_fusion_extremes_reproduce_component_ranking(), test_minmax_constant_is_zero()

### Community 91 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

### Community 92 - "update"
Cohesion: 0.25
Nodes (8): addElements(), beforeLayout(), es(), Qi(), qo(), ss(), ts(), update()

### Community 93 - "claims"
Cohesion: 0.28
Nodes (4): claims(), by_k_order(), hyb_fifth(), order()

### Community 94 - "add_par"
Cohesion: 0.25
Nodes (6): add_par(), bullets(), chu_thich(), ribbon(), style(), textbox()

### Community 95 - "wt"
Cohesion: 0.33
Nodes (3): kt(), qt(), wt()

### Community 97 - "ca"
Cohesion: 0.10
Nodes (25): Ae(), buildTicks(), _calculateBarIndexPixels(), _calculateBarValuePixels(), Fn(), getBasePixel(), getLabelAndValue(), getLabelForValue() (+17 more)

### Community 99 - "23_final_v2.py"
Cohesion: 0.15
Nodes (11): cpu_name(), dirty_files(), git(), lock_errors(), machine_info(), opened_seeds(), tuning_code_hashes(), log_test_access() (+3 more)

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.40
Nodes (4): Nguyên tắc vẽ, Sơ đồ của đề tài, Sửa và xuất lại, Tệp

### Community 103 - "metrics_io.py"
Cohesion: 0.29
Nodes (6): _block(), _by_k(), dashboard(), _named(), dashboard(), test_dashboard_reads_result_files()

### Community 105 - "sys"
Cohesion: 0.12
Nodes (3): no_cache(), user_filter(), main()

### Community 113 - "features.py"
Cohesion: 0.17
Nodes (13): build_amazon(), main(), load_data(), build_catalog(), build_daily_sales(), build_user_profile(), _codes(), load_catalog() (+5 more)

## Knowledge Gaps
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `7. Cấu trúc mã và API` connect `draw` to `Trang`, `a`, `test_demo.py`, `Demo web — shop thời trang H&M (kèm Amazon Beauty)`?**
  _High betweenness centrality (0.407) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Trang` be split into smaller, more focused modules?**
  _Cohesion score 0.08525506638714186 - nodes in this community are weakly interconnected._
- **Why does `test_results_page_matches_report_macros()` connect `test_demo.py` to `data_context.py`, `draw`?**
  _High betweenness centrality (0.286) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06600877192982456 - nodes in this community are weakly interconnected._
- **Why does `a()` connect `a` to `.bindResponsiveEvents`, `no`, `eo`, `n`, `u`, `draw`, `chart.umd.min.js`, `ns`?**
  _High betweenness centrality (0.257) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10052910052910052 - nodes in this community are weakly interconnected._