# Graph Report - DU-AN-CNTT  (2026-11-06)

## Corpus Check
- 102 files · ~376,889 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 119 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 20)

## Summary
- 2169 nodes · 5240 edges · 102 communities (83 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 226 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0c34e139`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Trang
- app.js
- build_poster.py
- run.py
- numpy
- routes.py
- trainer.py
- Đăng ký trước (pre-registration) — giao thức v2
- protocol_v2.py
- DataContext
- mau_kiem_dinh
- test_demo.py
- FeatureTrainDataset
- test_demo.py
- tune
- test_v2_final.py
- 19_check_report.py
- test_bosung.py
- NeuMFF
- 25_bosung.py
- reviews_Beauty_5
- .run_seed
- inference.py
- draw
- torch
- chart.umd.min.js
- test_baselines.py
- MaskedScoreFn
- va
- ns
- d
- test_amazon.py
- Si
- l
- GMF
- xo
- seed.py
- no
- amazon.yaml
- full_ranking.py
- Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty
- an
- zt
- Đăng ký trước (pre-registration) — thực nghiệm hm500k
- Demo web — shop thời trang H&M (kèm Amazon Beauty)
- Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F
- README.md
- Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)
- overview.py
- test_evaluation.py
- jn
- TrainDataset
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- ItemKNNBaseline
- 24_report_v2.py
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- s
- __main__.py
- .item_info
- 2. Tiến độ (13/10/2026)
- 9. Đánh giá, kiểm định và chống thiên lệch
- Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)
- EvalRecord
- n
- a
- tn
- BPRMFBaseline
- hi
- .notifyPlugins
- de
- fit_torch
- Phần 2. Nắm toàn bộ đề tài
- u
- MLP
- LateFusion
- update
- ws
- ._computeGridLineItems
- rs
- e
- ca
- json
- download_amazon_images.py
- Sơ đồ của đề tài
- data_context.py
- metrics_io.py
- main.py
- test_report_tools.py
- features.py
- pytest

## God Nodes (most connected - your core abstractions)
1. `an()` - 64 edges
2. `ns()` - 57 edges
3. `s()` - 43 edges
4. `n()` - 37 edges
5. `no` - 35 edges
6. `DataContext` - 32 edges
7. `esc()` - 31 edges
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

## Communities (102 total, 19 thin omitted)

### Community 0 - "Trang"
Cohesion: 0.08
Nodes (23): b(), ghi(), Trang, xuat(), danh_gia(), demo(), doc(), doi_chung() (+15 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (94): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+86 more)

### Community 2 - "build_poster.py"
Cohesion: 0.10
Nodes (7): add_par(), bullets(), chu_thich(), ribbon(), set_runs(), style(), textbox()

### Community 3 - "run.py"
Cohesion: 0.07
Nodes (29): _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report() (+21 more)

### Community 4 - "numpy"
Cohesion: 0.08
Nodes (15): hybrid_components(), score_fn(), DatasetAdapter, HMAdapter, iterative_k_core(), available_negatives(), build_user_positive_sets(), sample_train_negatives() (+7 more)

### Community 5 - "routes.py"
Cohesion: 0.08
Nodes (15): ctx(), example(), image(), neighbors(), recommend(), reload(), results(), similar() (+7 more)

### Community 6 - "trainer.py"
Cohesion: 0.29
Nodes (5): device(), count_parameters(), get_device(), _gpu_mem_str(), train_one_model()

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.05
Nodes (36): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo, 7. Kiểm định (+28 more)

### Community 8 - "protocol_v2.py"
Cohesion: 0.07
Nodes (22): configs_for(), data_name(), eval_kw(), evaluate(), load_data(), manifest_path(), read_config(), sample_configs() (+14 more)

### Community 9 - "DataContext"
Cohesion: 0.14
Nodes (9): DataContext, best_rank_series(), history(), pick_example(), saved_best_series(), showcase_users(), _user(), user_profile() (+1 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "test_demo.py"
Cohesion: 0.14
Nodes (13): context(), filter_users(), _filtered(), has_images(), health(), position(), random_user(), search_users() (+5 more)

### Community 13 - "test_demo.py"
Cohesion: 0.10
Nodes (12): unavailable_reason(), v2_available(), v2_data_mismatch(), datasets(), _macros(), _report_tools(), test_dataset_without_final_results_reports_command_not_training(), test_results_from_other_data_are_refused() (+4 more)

### Community 14 - "tune"
Cohesion: 0.20
Nodes (5): combine(), TraditionalHybrid, Table, test_features_are_minmax_on_the_candidate_set(), test_four_fusions()

### Community 15 - "test_v2_final.py"
Cohesion: 0.11
Nodes (8): _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_dirty_files_ignores_outputs_and_test_log(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_opened_seeds_reads_only_tags_of_current_holdout(), test_report_runs_end_to_end_on_tiny_results()

### Community 16 - "19_check_report.py"
Cohesion: 0.12
Nodes (17): check_claims(), check_macros_and_tables(), claims(), by_k_order(), hyb_fifth(), compare_with_committed(), Data, load() (+9 more)

### Community 17 - "test_bosung.py"
Cohesion: 0.19
Nodes (9): crossfit_scores(), fit_weights(), pair_differences(), _args(), _synthetic(), test_bosung_lock_lists_every_violation(), test_bosung_lock_passes_and_overrides_are_explicit(), test_crossfit_scores_use_weights_learned_on_other_users() (+1 more)

### Community 18 - "NeuMFF"
Cohesion: 0.17
Nodes (5): NeuMFF, branch(), id_emb(), test_neumff_branch_flags_and_items_without_id_scored(), _toy_model()

### Community 19 - "25_bosung.py"
Cohesion: 0.07
Nodes (22): 6. Cấu trúc thư mục, bucket_of(), main(), select_buckets(), load_best(), log_row(), logged(), main() (+14 more)

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - ".run_seed"
Cohesion: 0.11
Nodes (16): ablations(), beyond(), cpu_name(), dirty_files(), foreign_results(), git(), lock_errors(), machine_info() (+8 more)

### Community 22 - "inference.py"
Cohesion: 0.14
Nodes (10): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), recommend(), score_items() (+2 more)

### Community 23 - "draw"
Cohesion: 0.11
Nodes (22): ai(), ao(), average(), getCenterPoint(), ho(), Hs, _i(), inRange() (+14 more)

### Community 24 - "torch"
Cohesion: 0.33
Nodes (3): NeuMF, test_forward_shapes_and_logits(), test_neumf_uses_four_independent_embeddings()

### Community 25 - "chart.umd.min.js"
Cohesion: 0.04
Nodes (45): at(), be(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), cn(), da(), destroy() (+37 more)

### Community 26 - "test_baselines.py"
Cohesion: 0.16
Nodes (9): interaction_matrix(), topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors(), _topk_dense() (+1 more)

### Community 27 - "MaskedScoreFn"
Cohesion: 0.07
Nodes (19): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), item_time_features(), user_time_features(), ContentProfile, MaskedScoreFn, MaskedScorer, RecentPopularity, test_content_profile_uses_given_onehot_columns() (+11 more)

### Community 28 - "va"
Cohesion: 0.13
Nodes (7): afterEvent(), Bi(), Ci(), Fi(), f(), va, wi()

### Community 29 - "ns"
Cohesion: 0.06
Nodes (11): As(), bn, labelColor(), labelPointStyle(), ns(), on(), pn(), rt() (+3 more)

### Community 31 - "test_amazon.py"
Cohesion: 0.12
Nodes (11): AmazonAdapter, asin_list(), category_path(), item_info(), read_meta(), read_reviews(), test_adapter_codes_asins_in_sorted_order(), test_amazon_config_uses_hm_configs_without_tuning() (+3 more)

### Community 32 - "Si"
Cohesion: 0.21
Nodes (7): afterUpdate(), ki(), oa(), Oi(), Si(), x(), xa

### Community 33 - "l"
Cohesion: 0.13
Nodes (15): buildTicks(), determineDataLimits(), Fn(), Gn(), go(), ii(), l(), parse() (+7 more)

### Community 37 - "no"
Cohesion: 0.09
Nodes (11): buildLookupTable(), configure(), Fo(), _generate(), _getTimestampsForTable(), initOffsets(), lt(), no (+3 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - "full_ranking.py"
Cohesion: 0.20
Nodes (8): _append(), _empty_metric_lists(), evaluate_score_function(), evaluate_torch_model(), _per_user_row(), deterministic_tie_key(), rank_positives(), test_tie_ranking_is_deterministic()

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 41 - "an"
Cohesion: 0.11
Nodes (4): afterDatasetsUpdate(), an(), Mn(), onClick()

### Community 42 - "zt"
Cohesion: 0.06
Nodes (14): bt, color(), Cs, Ft(), It(), kt(), mt(), os() (+6 more)

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.20
Nodes (9): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 9. Mở rộng sau khi xem test (+1 more)

### Community 44 - "Demo web — shop thời trang H&M (kèm Amazon Beauty)"
Cohesion: 0.20
Nodes (8): popular(), 1. Chuẩn bị, 2. Chạy, 3. Màn hình, 4. Cách chấm — khớp đánh giá cuối, 5. Biến môi trường, 6. Ảnh sản phẩm (tuỳ chọn), Demo web — shop thời trang H&M (kèm Amazon Beauty)

### Community 45 - "Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F"
Cohesion: 0.12
Nodes (17): 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF (+9 more)

### Community 46 - "README.md"
Cohesion: 0.22
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - "overview.py"
Cohesion: 0.28
Nodes (4): answers(), results(), _verdict(), test_research_answers_follow_significance()

### Community 49 - "test_evaluation.py"
Cohesion: 0.28
Nodes (10): build_full_ranking_records_multi(), hr_at_k(), multi_ranking_metrics(), ndcg_at_k(), precision_at_k(), recall_at_k(), test_full_ranking_excludes_seen_and_keeps_positive(), test_multi_metrics_equal_single_item_formulas() (+2 more)

### Community 52 - "Tổng hợp đồ án: phương pháp, kết quả và tiến độ"
Cohesion: 0.15
Nodes (13): 11. Hạn chế đã biết, 12. Đối chiếu 17 góp ý trước của GVHD, 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển, 14.1 File (+5 more)

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

### Community 58 - "24_report_v2.py"
Cohesion: 0.06
Nodes (49): ablation(), beyond(), bootstrap_ci(), by_k(), cell(), ensure(), export_by_k(), export_data() (+41 more)

### Community 59 - "10. Code, demo, kiểm thử và báo cáo"
Cohesion: 0.40
Nodes (5): 10.2 Demo (`demo/README.md`), 10.3 Kiểm thử, 10.4 Báo cáo LaTeX (`Report DACNTT/`), 10.5 Lưu ý khi làm tiếp, 10. Code, demo, kiểm thử và báo cáo

### Community 60 - "6. Bài toán, câu hỏi nghiên cứu và phạm vi"
Cohesion: 0.33
Nodes (6): 6.1 Bài toán, 6.2 Câu hỏi nghiên cứu, 6.3 Yêu cầu R1–R9, 6.4 Phạm vi, 6.5 Vì sao thiết kế như vậy, 6. Bài toán, câu hỏi nghiên cứu và phạm vi

### Community 61 - "8. Mô hình"
Cohesion: 0.33
Nodes (6): 8.1 NeuMF-F — mô hình đề xuất (`src/models/hybrid_features.py`), 8.2 Hợp nhất sớm và hợp nhất muộn, 8.3 Mô hình đối chứng và cấu hình đã chọn, 8.4 Ablation NeuMF-F, 8.5 Mô hình lai truyền thống Hybrid-CBCF — bổ sung sau đánh giá cuối, 8. Mô hình

### Community 62 - "s"
Cohesion: 0.13
Nodes (10): bo, et(), H(), is(), s(), label(), mo(), ne() (+2 more)

### Community 64 - ".item_info"
Cohesion: 0.17
Nodes (3): test_history_is_training_data_before_cutoff(), test_neighbors_are_sorted_and_counted(), test_similar_items_follow_itemknn()

### Community 65 - "2. Tiến độ (13/10/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (29/10/2026)

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 67 - "Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)"
Cohesion: 0.33
Nodes (5): graphify, Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script), Quy ước báo cáo (`Report DACNTT/`), Ranh giới, Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

### Community 74 - "EvalRecord"
Cohesion: 0.20
Nodes (5): EvalRecord, positive_ranks(), test_per_user_rows_match_summary_and_count_candidates(), test_perfect_model_hr_ndcg_one(), test_perfect_scorer_gets_ndcg_one_with_many_positives()

### Community 75 - "n"
Cohesion: 0.12
Nodes (5): Do(), eo(), n(), Oe(), Y()

### Community 76 - "a"
Cohesion: 0.09
Nodes (19): a(), aa(), Di(), g(), j(), ko, m(), g() (+11 more)

### Community 77 - "tn"
Cohesion: 0.10
Nodes (6): addElements(), fe(), ks(), nn(), sn, tn

### Community 78 - "BPRMFBaseline"
Cohesion: 0.12
Nodes (4): BPRMFBaseline, MostPopularBaseline, RandomBaseline, test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 79 - "hi"
Cohesion: 0.31
Nodes (7): dataset(), hi(), index(), ji(), Re(), ve(), Yi()

### Community 80 - ".notifyPlugins"
Cohesion: 0.24
Nodes (3): afterDraw(), ke(), wn()

### Community 81 - "de"
Cohesion: 0.24
Nodes (5): b(), ce(), de, dt(), he()

### Community 82 - "fit_torch"
Cohesion: 0.27
Nodes (7): base_key(), build_torch(), fit_torch(), is_feature(), mlp_layers(), torch_scorer(), make_optimizer()

### Community 83 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 84 - "u"
Cohesion: 0.15
Nodes (8): addBox(), beforeUpdate(), initialize(), removeBox(), reset(), start(), stop(), u()

### Community 85 - "MLP"
Cohesion: 0.38
Nodes (3): 8. Lệch kế hoạch, MLP, test_mlp_dropout_is_configurable()

### Community 88 - "LateFusion"
Cohesion: 0.18
Nodes (6): late_fusion(), LateFusion, minmax(), model_scores(), test_late_fusion_extremes_reproduce_component_ranking(), test_minmax_constant_is_zero()

### Community 89 - "update"
Cohesion: 0.22
Nodes (6): beforeLayout(), generateLabels(), qo(), ss(), ts(), update()

### Community 90 - "ws"
Cohesion: 0.16
Nodes (11): ct(), fs(), ge(), gs(), ms(), ps(), i(), vs() (+3 more)

### Community 93 - "e"
Cohesion: 0.11
Nodes (11): e(), ei(), En, gi(), ia(), init(), je(), mi() (+3 more)

### Community 97 - "ca"
Cohesion: 0.15
Nodes (14): ca(), _calculateBarIndexPixels(), _calculateBarValuePixels(), getBasePixel(), getLabelAndValue(), getLabelForValue(), getPixelForTick(), getPixelForValue() (+6 more)

### Community 99 - "json"
Cohesion: 0.17
Nodes (9): export(), main(), dev_info(), check_product_code(), product_code_of(), prepare_pairs(), save_pairs(), write_json() (+1 more)

### Community 100 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.40
Nodes (4): Nguyên tắc vẽ, Sơ đồ của đề tài, Sửa và xuất lại, Tệp

### Community 102 - "data_context.py"
Cohesion: 0.10
Nodes (8): amazon_table(), product_table(), results_dir(), saved_final_ranks(), user_table(), main(), test_amazon_table_maps_metadata_to_item_columns(), test_product_table_uses_first_variant_and_counts_colours()

### Community 103 - "metrics_io.py"
Cohesion: 0.29
Nodes (6): _block(), _by_k(), dashboard(), _named(), dashboard(), test_dashboard_reads_result_files()

### Community 113 - "features.py"
Cohesion: 0.15
Nodes (17): build_amazon(), main(), build_features(), build_catalog(), build_daily_sales(), build_user_profile(), Catalog, category_codes() (+9 more)

### Community 116 - "pytest"
Cohesion: 0.24
Nodes (4): test_hm_adapter_rejects_excel(), _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

## Knowledge Gaps
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `7. Cấu trúc mã và API` connect `draw` to `Trang`, `a`, `test_demo.py`, `Demo web — shop thời trang H&M (kèm Amazon Beauty)`?**
  _High betweenness centrality (0.392) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Trang` be split into smaller, more focused modules?**
  _Cohesion score 0.08051948051948052 - nodes in this community are weakly interconnected._
- **Why does `test_results_page_matches_report_macros()` connect `test_demo.py` to `overview.py`, `data_context.py`, `draw`?**
  _High betweenness centrality (0.293) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06674132138857783 - nodes in this community are weakly interconnected._
- **Why does `a()` connect `a` to `Si`, `ca`, `l`, `no`, `de`, `u`, `draw`, `chart.umd.min.js`, `ws`, `._computeGridLineItems`, `rs`?**
  _High betweenness centrality (0.240) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09538461538461539 - nodes in this community are weakly interconnected._