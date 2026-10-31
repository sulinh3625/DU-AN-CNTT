# Graph Report - DU-AN-CNTT  (2026-10-31)

## Corpus Check
- 104 files · ~180,827 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 117 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 20)

## Summary
- 2140 nodes · 4935 edges · 111 communities (82 shown, 29 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 239 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9914d055`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Trang
- app.js
- 23_final_v2.py
- run.py
- numpy
- routes.py
- v2_common.py
- code_hash
- protocol_v2.py
- DataContext
- mau_kiem_dinh
- test_demo.py
- test_v2.py
- data_context.py
- tune
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
- d
- test_amazon.py
- o
- l
- GMF
- bo
- torch
- no
- amazon.yaml
- 24_report_v2.py
- Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty
- an
- zt
- Đăng ký trước (pre-registration) — thực nghiệm hm500k
- Demo web — shop thời trang H&M (kèm Amazon Beauty)
- Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F
- README.md
- Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)
- test_demo.py
- neumf_project — mã nguồn của đề tài
- export_data_amazon
- TrainDataset
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- ItemKNNBaseline
- Macros
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- s
- __main__.py
- 13. Lịch sử phát triển
- 2. Tiến độ (13/10/2026)
- 9. Đánh giá, kiểm định và chống thiên lệch
- CLAUDE.md
- io.py
- n
- a
- tn
- BPRMFBaseline
- bn
- .notifyPlugins
- de
- user_filter
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
- Precomputed
- Đăng ký trước (pre-registration) — giao thức v2
- ki
- provenance
- pathlib
- download_amazon_images.py
- Sơ đồ của đề tài
- product_table
- metrics_io.py
- main.py
- 3. Chạy thực nghiệm
- test_report_tools.py
- .buildOrUpdateControllers
- Kế hoạch phân công tiến độ DACNTT_8d8e062d.md
- time
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

## Communities (111 total, 29 thin omitted)

### Community 0 - "Trang"
Cohesion: 0.09
Nodes (20): b(), ghi(), Trang, xuat(), danh_gia(), demo(), doc(), doi_chung() (+12 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (94): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+86 more)

### Community 2 - "23_final_v2.py"
Cohesion: 0.20
Nodes (8): has_images(), cpu_name(), dirty_files(), git(), lock_errors(), machine_info(), opened_seeds(), tuning_code_hashes()

### Community 3 - "run.py"
Cohesion: 0.07
Nodes (29): _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report() (+21 more)

### Community 4 - "numpy"
Cohesion: 0.12
Nodes (13): bucket_of(), main(), select_buckets(), beyond(), by_k(), summarize(), available_negatives(), build_user_positive_sets() (+5 more)

### Community 5 - "routes.py"
Cohesion: 0.11
Nodes (19): context(), ctx(), dashboard(), example(), health(), history(), image(), neighbors() (+11 more)

### Community 6 - "v2_common.py"
Cohesion: 0.08
Nodes (23): base_key(), configs_for(), data_name(), device(), eval_kw(), evaluate(), fit_torch(), hybrid_components() (+15 more)

### Community 7 - "code_hash"
Cohesion: 0.14
Nodes (15): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo (+7 more)

### Community 8 - "protocol_v2.py"
Cohesion: 0.09
Nodes (19): DailySales, group_by_product(), product_code_of(), iterative_k_core(), build_from_pairs(), build_v2(), DataV2, load_pairs() (+11 more)

### Community 9 - "DataContext"
Cohesion: 0.09
Nodes (10): DataContext, best_rank_series(), pick_example(), saved_best_series(), showcase_users(), user_profile(), test_history_is_training_data_before_cutoff(), test_neighbors_are_sorted_and_counted() (+2 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "test_demo.py"
Cohesion: 0.16
Nodes (11): filter_users(), _filtered(), position(), random_user(), search_users(), user_position(), at(), user_rows() (+3 more)

### Community 12 - "test_v2.py"
Cohesion: 0.11
Nodes (14): FeatureTrainDataset, Catalog, item_time_features(), user_time_features(), _catalog(), _day(), _sales(), test_feature_dataset_negatives_launched_and_not_positive() (+6 more)

### Community 13 - "data_context.py"
Cohesion: 0.11
Nodes (10): results_dir(), saved_final_ranks(), unavailable_reason(), v2_available(), v2_data_mismatch(), datasets(), test_dataset_without_final_results_reports_command_not_training(), vctx() (+2 more)

### Community 14 - "tune"
Cohesion: 0.20
Nodes (6): tune(), combine(), TraditionalHybrid, Table, test_features_are_minmax_on_the_candidate_set(), test_four_fusions()

### Community 15 - "test_v2_final.py"
Cohesion: 0.10
Nodes (6): _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_report_runs_end_to_end_on_tiny_results()

### Community 16 - "19_check_report.py"
Cohesion: 0.12
Nodes (17): check_claims(), check_macros_and_tables(), claims(), by_k_order(), hyb_fifth(), compare_with_committed(), Data, load() (+9 more)

### Community 17 - "test_bosung.py"
Cohesion: 0.20
Nodes (9): crossfit_scores(), fit_weights(), pair_differences(), _args(), _synthetic(), test_bosung_lock_lists_every_violation(), test_bosung_lock_passes_and_overrides_are_explicit(), test_crossfit_scores_use_weights_learned_on_other_users() (+1 more)

### Community 18 - "NeuMFF"
Cohesion: 0.17
Nodes (5): NeuMFF, branch(), id_emb(), test_neumff_branch_flags_and_items_without_id_scored(), _toy_model()

### Community 19 - "25_bosung.py"
Cohesion: 0.15
Nodes (9): component_check(), file_md5(), final(), lock_errors(), opened_tags(), provenance(), evaluate_v2(), positive_ranks() (+1 more)

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - ".run_seed"
Cohesion: 0.16
Nodes (8): ablations(), beyond(), foreign_results(), main(), Runner, record(), score(), ensure_dir()

### Community 22 - "test_evaluation.py"
Cohesion: 0.06
Nodes (32): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), recommend(), score_items() (+24 more)

### Community 23 - "draw"
Cohesion: 0.11
Nodes (24): ai(), ao(), dataset(), hi(), ho(), index(), inRange(), inXRange() (+16 more)

### Community 24 - "test_models.py"
Cohesion: 0.16
Nodes (8): 8. Lệch kế hoạch, build_torch(), mlp_layers(), MLP, NeuMF, test_forward_shapes_and_logits(), test_mlp_dropout_is_configurable(), test_neumf_uses_four_independent_embeddings()

### Community 25 - "chart.umd.min.js"
Cohesion: 0.03
Nodes (35): at(), be(), beforeLayout(), Bi(), cn(), destroy(), draw(), dt() (+27 more)

### Community 26 - "test_baselines.py"
Cohesion: 0.16
Nodes (9): interaction_matrix(), topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors(), _topk_dense() (+1 more)

### Community 27 - "MaskedScoreFn"
Cohesion: 0.10
Nodes (8): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), ContentProfile, MaskedScoreFn, MaskedScorer, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_masked_scorer_puts_unscoreable_items_last(), test_recent_popularity_and_content_profile()

### Community 28 - "va"
Cohesion: 0.05
Nodes (13): Ci(), configure(), eo(), f(), Hs, initialize(), Oi(), p() (+5 more)

### Community 29 - "ns"
Cohesion: 0.06
Nodes (7): As(), _calculateBarValuePixels(), jn, ns(), rt(), updateElements(), zs()

### Community 31 - "test_amazon.py"
Cohesion: 0.09
Nodes (15): asin_list(), build_features(), category_path(), item_info(), read_meta(), read_reviews(), category_codes(), text_vectors() (+7 more)

### Community 32 - "o"
Cohesion: 0.26
Nodes (6): b(), g(), m(), g(), o(), i()

### Community 33 - "l"
Cohesion: 0.13
Nodes (16): dn(), e(), ei(), gi(), Gn(), je(), mi(), l() (+8 more)

### Community 34 - "GMF"
Cohesion: 0.28
Nodes (3): GMF, test_late_fusion_extremes_reproduce_component_ranking(), test_refit_runs_fixed_epochs_without_validation()

### Community 35 - "bo"
Cohesion: 0.10
Nodes (11): Ae(), buildTicks(), determineDataLimits(), getPixelForTick(), getPixelForValue(), getValueForPixel(), go(), init() (+3 more)

### Community 36 - "torch"
Cohesion: 0.24
Nodes (5): load_best(), log_row(), logged(), main(), seed_everything()

### Community 37 - "no"
Cohesion: 0.11
Nodes (8): buildLookupTable(), Fo(), _generate(), _getTimestampsForTable(), initOffsets(), no, nt(), zo()

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - "24_report_v2.py"
Cohesion: 0.09
Nodes (14): ablation(), bootstrap_ci(), dev_info(), grid(), group(), holm(), hybrid_weights(), num() (+6 more)

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 42 - "zt"
Cohesion: 0.11
Nodes (9): Ft(), It(), kt(), mt(), qt(), _t(), wt(), Xt() (+1 more)

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.20
Nodes (9): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 9. Mở rộng sau khi xem test (+1 more)

### Community 44 - "Demo web — shop thời trang H&M (kèm Amazon Beauty)"
Cohesion: 0.20
Nodes (8): popular(), 1. Chuẩn bị, 2. Chạy, 3. Màn hình, 4. Cách chấm — khớp đánh giá cuối, 5. Biến môi trường, 6. Ảnh sản phẩm (tuỳ chọn), Demo web — shop thời trang H&M (kèm Amazon Beauty)

### Community 45 - "Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F"
Cohesion: 0.07
Nodes (26): 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5) (+18 more)

### Community 46 - "README.md"
Cohesion: 0.25
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - "test_demo.py"
Cohesion: 0.12
Nodes (10): answers(), results(), _verdict(), 7. Cấu trúc mã và API, _macros(), _report_tools(), test_overview_example_matches_saved_ranks(), test_research_answers_follow_significance() (+2 more)

### Community 49 - "neumf_project — mã nguồn của đề tài"
Cohesion: 0.22
Nodes (7): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, 6. Cấu trúc thư mục, neumf_project — mã nguồn của đề tài

### Community 50 - "export_data_amazon"
Cohesion: 0.20
Nodes (7): cell(), export_data(), export_data_amazon(), phrase(), text_report(), thousands(), vn_date()

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

### Community 58 - "Macros"
Cohesion: 0.15
Nodes (15): export_by_k(), export_hybrid_tuning(), export_results(), export_run(), export_supplement(), export_tuning(), family_summary(), Macros (+7 more)

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
Cohesion: 0.10
Nodes (18): bo, _calculateBarIndexPixels(), et(), fa(), ga(), _getStackCount(), _getStackIndex(), _getStacks() (+10 more)

### Community 64 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 65 - "2. Tiến độ (13/10/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (13/10/2026)

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 74 - "io.py"
Cohesion: 0.29
Nodes (4): log_test_access(), prereg_committed(), test_log_test_access_appends_rows(), test_prereg_missing_means_not_committed()

### Community 75 - "n"
Cohesion: 0.13
Nodes (14): Do(), Fn(), getLabelAndValue(), getMaxOverflow(), _getRuler(), In(), lt(), n() (+6 more)

### Community 76 - "a"
Cohesion: 0.10
Nodes (14): a(), aa(), afterDatasetsUpdate(), Di(), _i(), j(), ko, oa() (+6 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.13
Nodes (3): BPRMFBaseline, MostPopularBaseline, RandomBaseline

### Community 81 - "de"
Cohesion: 0.19
Nodes (5): ce(), de, he(), qs(), te()

### Community 87 - "Path"
Cohesion: 0.23
Nodes (12): ensure(), load(), load_supplement(), main(), plot_ablation(), plot_curves(), plot_metrics(), plot_significance() (+4 more)

### Community 88 - "LateFusion"
Cohesion: 0.23
Nodes (5): late_fusion(), LateFusion, minmax(), model_scores(), test_minmax_constant_is_zero()

### Community 89 - "update"
Cohesion: 0.29
Nodes (8): addElements(), es(), is(), pt(), Qi(), ss(), ts(), update()

### Community 90 - "ws"
Cohesion: 0.17
Nodes (9): ct(), ge(), gs(), ms(), ps(), vs(), we(), ws (+1 more)

### Community 94 - "sn"
Cohesion: 0.33
Nodes (3): nn(), on(), sn

### Community 96 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.20
Nodes (9): 0. Vì sao có giao thức v2, 10. Lệch kế hoạch, 1. Dữ liệu, 3. Mô hình, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký (+1 more)

### Community 97 - "ki"
Cohesion: 0.12
Nodes (15): beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), ca(), da(), ea(), generateLabels(), ha (+7 more)

### Community 99 - "pathlib"
Cohesion: 0.12
Nodes (8): export(), main(), AmazonAdapter, DatasetAdapter, HMAdapter, check_product_code(), write_json(), test_hm_adapter_rejects_excel()

### Community 100 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.40
Nodes (4): Nguyên tắc vẽ, Sơ đồ của đề tài, Sửa và xuất lại, Tệp

### Community 102 - "product_table"
Cohesion: 0.19
Nodes (5): amazon_table(), product_table(), user_table(), test_amazon_table_maps_metadata_to_item_columns(), test_product_table_uses_first_variant_and_counts_colours()

### Community 103 - "metrics_io.py"
Cohesion: 0.33
Nodes (5): _block(), _by_k(), dashboard(), _named(), test_dashboard_reads_result_files()

### Community 107 - "3. Chạy thực nghiệm"
Cohesion: 0.29
Nodes (7): 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển, 3.2 Chạy thử (tuỳ chọn), 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần, 3.4 Sau khi chạy, 3.5 Kiểm chứng trên Amazon Beauty (dữ liệu đối chứng), 3.6 Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF, 3. Chạy thực nghiệm

### Community 113 - "time"
Cohesion: 0.28
Nodes (9): build_amazon(), main(), build_catalog(), build_daily_sales(), build_user_profile(), _codes(), save_catalog(), save_daily_sales() (+1 more)

### Community 116 - "pytest"
Cohesion: 0.31
Nodes (3): _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

## Knowledge Gaps
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` connect `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` to `13. Lịch sử phát triển`, `2. Tiến độ (13/10/2026)`, `9. Đánh giá, kiểm định và chống thiên lệch`, `README.md`, `3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định`, `4. Kiểm chứng trên Amazon Beauty`, `7. Dữ liệu`, `10. Code, demo, kiểm thử và báo cáo`, `6. Bài toán, câu hỏi nghiên cứu và phạm vi`, `8. Mô hình`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Trang` be split into smaller, more focused modules?**
  _Cohesion score 0.08708272859216255 - nodes in this community are weakly interconnected._
- **Why does `NeuMF` connect `test_models.py` to `v2_common.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06674132138857783 - nodes in this community are weakly interconnected._
- **Why does `ns()` connect `ns` to `chart.umd.min.js`, `n`, `a`, `Cs`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `run.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07397959183673469 - nodes in this community are weakly interconnected._