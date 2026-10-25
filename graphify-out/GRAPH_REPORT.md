# Graph Report - DU-AN-CNTT  (2026-10-25)

## Corpus Check
- 105 files · ~180,807 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 119 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 20)

## Summary
- 2147 nodes · 4941 edges · 121 communities (94 shown, 27 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 239 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7d26f5f1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Trang
- app.js
- numpy
- run.py
- test_data_pipeline.py
- routes.py
- v2_common.py
- code_hash
- test_prepare.py
- DataContext
- mau_kiem_dinh
- test_demo.py
- test_v2.py
- data_context.py
- protocol_v2.py
- test_v2_final.py
- 19_check_report.py
- test_bosung.py
- NeuMFF
- 25_bosung.py
- reviews_Beauty_5
- 23_final_v2.py
- test_evaluation.py
- draw
- test_models.py
- chart.umd.min.js
- test_baselines.py
- MaskedScoreFn
- va
- ns
- d
- test_amazon.py
- ContentProfile
- n
- ki
- bo
- 22_tune_v2.py
- no
- amazon.yaml
- 24_report_v2.py
- Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty
- an
- zt
- MLP
- Demo web — shop thời trang H&M (kèm Amazon Beauty)
- Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F
- README.md
- Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)
- overview.py
- neumf_project — mã nguồn của đề tài
- pandas
- Phần 2. Nắm toàn bộ đề tài
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- Phần 5. Câu hỏi hội đồng hay hỏi
- Macros
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- updateElements
- __main__.py
- 13. Lịch sử phát triển
- 2. Tiến độ (13/10/2026)
- 9. Đánh giá, kiểm định và chống thiên lệch
- CLAUDE.md
- sys
- l
- a
- tn
- BPRMFBaseline
- bn
- .notifyPlugins
- de
- jn
- argparse
- u
- bt
- Cs
- Path
- LateFusion
- update
- ws
- .isHorizontal
- rs
- En
- sn
- build_from_pairs
- Đăng ký trước (pre-registration) — giao thức v2
- ho
- .getDataset
- 02_prepare_data.py
- download_amazon_images.py
- Sơ đồ của đề tài
- product_table
- metrics_io.py
- recommend
- main.py
- demo
- 3. Chạy thực nghiệm
- test_report_tools.py
- .buildOrUpdateControllers
- export_results
- Kế hoạch phân công tiến độ DACNTT_8d8e062d.md
- test_run.py
- time
- claims
- evaluate_torch_model
- pytest
- json
- FeatureTrainDataset
- positive_ranks
- _torch_scores

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
- `3. Mô hình` --references--> `neumf()`  [INFERRED]
  neumf_project/audit/PREREG_v2.md → image/src/so_do_bao_cao.py
- `3. Mô hình` --references--> `neumf()`  [INFERRED]
  neumf_project/audit/PREREG_v2_cu.md → image/src/so_do_bao_cao.py
- `2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026` --references--> `make_stage()`  [INFERRED]
  tong_hop.md → neumf_project/src/data_pipeline/protocol_v2.py
- `13.4 Dọn mã (10/10/2026)` --references--> `evaluate_v2()`  [INFERRED]
  tong_hop.md → neumf_project/src/evaluation/v2.py
- `7. Cấu trúc mã và API` --references--> `k()`  [INFERRED]
  neumf_project/demo/README.md → image/src/so_do_bao_cao.py

## Import Cycles
- None detected.

## Communities (121 total, 27 thin omitted)

### Community 0 - "Trang"
Cohesion: 0.09
Nodes (20): b(), ghi(), Trang, xuat(), danh_gia(), demo(), doc(), doi_chung() (+12 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (94): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+86 more)

### Community 2 - "numpy"
Cohesion: 0.17
Nodes (7): best_ranks(), candidate_scores(), rank_from_scores(), score_items(), deterministic_tie_key(), rank_positives(), test_tie_ranking_is_deterministic()

### Community 3 - "run.py"
Cohesion: 0.14
Nodes (14): _amazon(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report(), cmd_prepare() (+6 more)

### Community 4 - "test_data_pipeline.py"
Cohesion: 0.12
Nodes (9): TrainDataset, iterative_k_core(), available_negatives(), build_user_positive_sets(), sample_train_negatives(), aggregate_unique_user_item(), test_aggregate_before_kcore_counts_unique_edges(), test_negative_sampler_never_returns_positive() (+1 more)

### Community 5 - "routes.py"
Cohesion: 0.08
Nodes (15): ctx(), example(), image(), neighbors(), recommend(), reload(), results(), similar() (+7 more)

### Community 6 - "v2_common.py"
Cohesion: 0.11
Nodes (17): base_key(), build_torch(), configs_for(), data_name(), device(), eval_kw(), evaluate(), fit_torch() (+9 more)

### Community 7 - "code_hash"
Cohesion: 0.12
Nodes (16): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo (+8 more)

### Community 8 - "test_prepare.py"
Cohesion: 0.16
Nodes (10): load_pairs(), evaluate_v2(), _day(), _hm_sample(), test_candidates_and_targets_only_items_with_training_pairs(), test_data_from_file_matches_build_v2(), test_export_twice_gives_same_bytes_and_md5(), test_load_data_rejects_missing_file_and_md5_mismatch() (+2 more)

### Community 9 - "DataContext"
Cohesion: 0.09
Nodes (11): DataContext, best_rank_series(), history(), pick_example(), saved_best_series(), showcase_users(), _user(), user_profile() (+3 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "test_demo.py"
Cohesion: 0.14
Nodes (13): context(), filter_users(), _filtered(), has_images(), health(), position(), random_user(), search_users() (+5 more)

### Community 12 - "test_v2.py"
Cohesion: 0.18
Nodes (15): Catalog, group_by_product(), item_time_features(), build_v2(), _catalog(), _day(), _sales(), test_group_by_product_merges_colour_variants() (+7 more)

### Community 13 - "data_context.py"
Cohesion: 0.09
Nodes (14): unavailable_reason(), v2_available(), v2_data_mismatch(), datasets(), 7. Cấu trúc mã và API, _macros(), _report_tools(), test_dataset_without_final_results_reports_command_not_training() (+6 more)

### Community 14 - "protocol_v2.py"
Cohesion: 0.11
Nodes (11): hybrid_components(), score_fn(), build_user_profile(), category_codes(), _codes(), text_vectors(), user_time_features(), UserProfile (+3 more)

### Community 15 - "test_v2_final.py"
Cohesion: 0.11
Nodes (6): _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_report_runs_end_to_end_on_tiny_results()

### Community 16 - "19_check_report.py"
Cohesion: 0.17
Nodes (13): check_claims(), check_macros_and_tables(), compare_with_committed(), Data, load(), defined_macros(), find_line(), key_numbers() (+5 more)

### Community 17 - "test_bosung.py"
Cohesion: 0.11
Nodes (15): tune(), combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic() (+7 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 19 - "25_bosung.py"
Cohesion: 0.16
Nodes (8): component_check(), file_md5(), final(), lock_errors(), main(), opened_tags(), Precomputed, provenance()

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - "23_final_v2.py"
Cohesion: 0.14
Nodes (12): ablations(), beyond(), cpu_name(), dirty_files(), git(), lock_errors(), machine_info(), opened_seeds() (+4 more)

### Community 22 - "test_evaluation.py"
Cohesion: 0.17
Nodes (14): build_full_ranking_records_multi(), EvalRecord, hr_at_k(), multi_ranking_metrics(), ndcg_at_k(), precision_at_k(), recall_at_k(), test_full_ranking_excludes_seen_and_keeps_positive() (+6 more)

### Community 23 - "draw"
Cohesion: 0.11
Nodes (21): ai(), ao(), dataset(), draw(), Ee(), hi(), index(), ji() (+13 more)

### Community 24 - "test_models.py"
Cohesion: 0.14
Nodes (8): GMF, NeuMF, count_parameters(), _gpu_mem_str(), train_one_model(), test_forward_shapes_and_logits(), test_neumf_uses_four_independent_embeddings(), test_refit_runs_fixed_epochs_without_validation()

### Community 25 - "chart.umd.min.js"
Cohesion: 0.03
Nodes (39): at(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), beforeLayout(), Bi(), da(), destroy() (+31 more)

### Community 26 - "test_baselines.py"
Cohesion: 0.13
Nodes (10): interaction_matrix(), ItemKNNBaseline, topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors() (+2 more)

### Community 27 - "MaskedScoreFn"
Cohesion: 0.16
Nodes (4): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), MaskedScoreFn, MaskedScorer, test_masked_scorer_puts_unscoreable_items_last()

### Community 28 - "va"
Cohesion: 0.06
Nodes (10): Ci(), eo(), Hs, initialize(), Oi(), Si(), start(), va (+2 more)

### Community 31 - "test_amazon.py"
Cohesion: 0.07
Nodes (17): AmazonAdapter, asin_list(), build_features(), category_path(), item_info(), read_meta(), read_reviews(), DatasetAdapter (+9 more)

### Community 32 - "ContentProfile"
Cohesion: 0.23
Nodes (4): ContentProfile, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_recent_popularity_and_content_profile()

### Community 33 - "n"
Cohesion: 0.09
Nodes (22): b(), Do(), e(), ei(), g(), gi(), je(), m() (+14 more)

### Community 34 - "ki"
Cohesion: 0.15
Nodes (10): cn(), generateLabels(), Gn(), hn(), ki(), ln(), rn(), so() (+2 more)

### Community 35 - "bo"
Cohesion: 0.09
Nodes (9): Ae(), bo, et(), getPixelForTick(), getPixelForValue(), getValueForPixel(), H(), mo() (+1 more)

### Community 36 - "22_tune_v2.py"
Cohesion: 0.17
Nodes (9): load_best(), log_row(), logged(), main(), ensure_dir(), log_test_access(), prereg_committed(), test_log_test_access_appends_rows() (+1 more)

### Community 37 - "no"
Cohesion: 0.09
Nodes (10): buildLookupTable(), configure(), Fo(), _generate(), _getTimestampsForTable(), initOffsets(), lt(), no (+2 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - "24_report_v2.py"
Cohesion: 0.14
Nodes (8): bootstrap_ci(), grid(), holm(), hybrid_weights(), num(), params_text(), significance(), verdict()

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 42 - "zt"
Cohesion: 0.11
Nodes (9): Ft(), It(), kt(), mt(), qt(), _t(), wt(), Xt() (+1 more)

### Community 43 - "MLP"
Cohesion: 0.10
Nodes (15): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 8. Lệch kế hoạch (+7 more)

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

### Community 48 - "overview.py"
Cohesion: 0.28
Nodes (4): answers(), results(), _verdict(), test_research_answers_follow_significance()

### Community 49 - "neumf_project — mã nguồn của đề tài"
Cohesion: 0.22
Nodes (7): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, 6. Cấu trúc thư mục, neumf_project — mã nguồn của đề tài

### Community 50 - "pandas"
Cohesion: 0.21
Nodes (10): ablation(), beyond(), by_k(), load(), load_supplement(), main(), phrase(), summarize() (+2 more)

### Community 51 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

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

### Community 57 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 58 - "Macros"
Cohesion: 0.13
Nodes (13): cell(), export_by_k(), export_data(), export_data_amazon(), export_hybrid_tuning(), export_run(), export_supplement(), export_tuning() (+5 more)

### Community 59 - "10. Code, demo, kiểm thử và báo cáo"
Cohesion: 0.33
Nodes (6): 10.1 Quy trình thực nghiệm, 10.2 Demo (`demo/README.md`), 10.3 Kiểm thử, 10.4 Báo cáo LaTeX (`Report DACNTT/`), 10.5 Lưu ý khi làm tiếp, 10. Code, demo, kiểm thử và báo cáo

### Community 60 - "6. Bài toán, câu hỏi nghiên cứu và phạm vi"
Cohesion: 0.33
Nodes (6): 6.1 Bài toán, 6.2 Câu hỏi nghiên cứu, 6.3 Yêu cầu R1–R9, 6.4 Phạm vi, 6.5 Vì sao thiết kế như vậy, 6. Bài toán, câu hỏi nghiên cứu và phạm vi

### Community 61 - "8. Mô hình"
Cohesion: 0.33
Nodes (6): 8.1 NeuMF-F — mô hình đề xuất (`src/models/hybrid_features.py`), 8.2 Hợp nhất sớm và hợp nhất muộn, 8.3 Mô hình đối chứng và cấu hình đã chọn, 8.4 Ablation NeuMF-F, 8.5 Mô hình lai truyền thống Hybrid-CBCF — bổ sung sau đánh giá cuối, 8. Mô hình

### Community 62 - "updateElements"
Cohesion: 0.20
Nodes (9): _calculateBarIndexPixels(), _calculateBarValuePixels(), getLabelAndValue(), _getRuler(), _getStackCount(), _getStackIndex(), _getStacks(), In() (+1 more)

### Community 64 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 65 - "2. Tiến độ (13/10/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (13/10/2026)

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 74 - "sys"
Cohesion: 0.16
Nodes (9): _c(), _hms(), main(), menu(), run_steps(), _show(), test_run_amazon_commands_use_amazon_config(), run() (+1 more)

### Community 75 - "l"
Cohesion: 0.29
Nodes (10): Fn(), getMaxOverflow(), go(), l(), parse(), parseArrayData(), parseObjectData(), parsePrimitiveData() (+2 more)

### Community 76 - "a"
Cohesion: 0.08
Nodes (17): a(), aa(), afterDatasetsUpdate(), buildTicks(), determineDataLimits(), _i(), init(), j() (+9 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.12
Nodes (4): BPRMFBaseline, MostPopularBaseline, RandomBaseline, test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 79 - "bn"
Cohesion: 0.15
Nodes (4): bn, dn(), pn(), un()

### Community 81 - "de"
Cohesion: 0.19
Nodes (5): ce(), de, he(), qs(), te()

### Community 83 - "argparse"
Cohesion: 0.21
Nodes (4): main(), bucket_of(), main(), select_buckets()

### Community 84 - "u"
Cohesion: 0.19
Nodes (3): u(), i(), wn()

### Community 87 - "Path"
Cohesion: 0.26
Nodes (10): ensure(), group(), plot_ablation(), plot_curves(), plot_metrics(), plot_significance(), plot_val_vs_test(), style() (+2 more)

### Community 88 - "LateFusion"
Cohesion: 0.36
Nodes (3): minmax(), model_scores(), test_minmax_constant_is_zero()

### Community 89 - "update"
Cohesion: 0.29
Nodes (3): addElements(), pt(), update()

### Community 90 - "ws"
Cohesion: 0.14
Nodes (11): be(), ct(), ge(), gs(), ms(), pe(), ps(), vs() (+3 more)

### Community 94 - "sn"
Cohesion: 0.23
Nodes (6): ii(), s(), label(), nn(), on(), sn

### Community 95 - "build_from_pairs"
Cohesion: 0.19
Nodes (5): load_data(), DailySales, load_catalog(), load_daily_sales(), build_from_pairs()

### Community 96 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.20
Nodes (9): 0. Vì sao có giao thức v2, 10. Lệch kế hoạch, 1. Dữ liệu, 3. Mô hình, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký (+1 more)

### Community 97 - "ho"
Cohesion: 0.12
Nodes (14): ca(), ha, ho(), inRange(), inXRange(), inYRange(), K(), la() (+6 more)

### Community 99 - "02_prepare_data.py"
Cohesion: 0.19
Nodes (7): export(), main(), check_product_code(), product_code_of(), prepare_pairs(), save_pairs(), write_json()

### Community 100 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.40
Nodes (4): Nguyên tắc vẽ, Sơ đồ của đề tài, Sửa và xuất lại, Tệp

### Community 102 - "product_table"
Cohesion: 0.11
Nodes (7): amazon_table(), product_table(), results_dir(), saved_final_ranks(), user_table(), test_amazon_table_maps_metadata_to_item_columns(), test_product_table_uses_first_variant_and_counts_colours()

### Community 103 - "metrics_io.py"
Cohesion: 0.29
Nodes (6): _block(), _by_k(), dashboard(), _named(), dashboard(), test_dashboard_reads_result_files()

### Community 104 - "recommend"
Cohesion: 0.17
Nodes (6): eval_record(), final_result(), metrics_of(), recommend(), test_best_ranks_match_recommend(), test_late_fusion_minmax_on_candidates()

### Community 106 - "demo"
Cohesion: 0.29
Nodes (6): build, ports, restart, volumes, services, demo

### Community 107 - "3. Chạy thực nghiệm"
Cohesion: 0.29
Nodes (7): 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển, 3.2 Chạy thử (tuỳ chọn), 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần, 3.4 Sau khi chạy, 3.5 Kiểm chứng trên Amazon Beauty (dữ liệu đối chứng), 3.6 Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF, 3. Chạy thực nghiệm

### Community 110 - "export_results"
Cohesion: 0.29
Nodes (8): export_results(), family_summary(), mk(), pct(), phrase_en(), pval(), sig_rows(), vn()

### Community 112 - "test_run.py"
Cohesion: 0.24
Nodes (6): cmd_v2_data(), _menu(), test_all_tunes_then_dry_run_and_opens_test_only_with_final(), test_menu_asks_required_args_and_defaults_to_no_for_test_commands(), test_menu_runs_command_with_extra_options(), test_v2_data_runs_sample_features_then_prepare()

### Community 113 - "time"
Cohesion: 0.47
Nodes (6): build_amazon(), main(), build_catalog(), build_daily_sales(), save_catalog(), save_daily_sales()

### Community 114 - "claims"
Cohesion: 0.28
Nodes (4): claims(), by_k_order(), hyb_fifth(), order()

### Community 115 - "evaluate_torch_model"
Cohesion: 0.28
Nodes (5): _append(), _empty_metric_lists(), evaluate_score_function(), evaluate_torch_model(), _per_user_row()

### Community 116 - "pytest"
Cohesion: 0.31
Nodes (3): _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

### Community 117 - "json"
Cohesion: 0.32
Nodes (4): foreign_results(), main(), dev_info(), describe()

## Knowledge Gaps
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` connect `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` to `13. Lịch sử phát triển`, `2. Tiến độ (13/10/2026)`, `9. Đánh giá, kiểm định và chống thiên lệch`, `README.md`, `3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định`, `4. Kiểm chứng trên Amazon Beauty`, `7. Dữ liệu`, `10. Code, demo, kiểm thử và báo cáo`, `6. Bài toán, câu hỏi nghiên cứu và phạm vi`, `8. Mô hình`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Trang` be split into smaller, more focused modules?**
  _Cohesion score 0.08708272859216255 - nodes in this community are weakly interconnected._
- **Why does `ns()` connect `ns` to `.getDataset`, `a`, `Cs`, `updateElements`, `update`, `chart.umd.min.js`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06674132138857783 - nodes in this community are weakly interconnected._
- **Why does `DataContext` connect `DataContext` to `numpy`, `download_amazon_images.py`, `routes.py`, `product_table`, `MLP`, `test_demo.py`, `data_context.py`, `test_bosung.py`, `argparse`, `test_evaluation.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `run.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14130434782608695 - nodes in this community are weakly interconnected._