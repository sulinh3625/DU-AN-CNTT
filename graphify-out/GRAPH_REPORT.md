# Graph Report - DU-AN-CNTT  (2026-11-07)

## Corpus Check
- 103 files · ~423,447 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 119 file(s) not represented in the graph (top: .tex 36, .csv 31, .gz 20)

## Summary
- 2193 nodes · 5287 edges · 99 communities (84 shown, 15 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 226 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `427dd422`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Trang
- app.js
- build_poster.py
- run.py
- protocol_v2.py
- routes.py
- torch
- Đăng ký trước (pre-registration) — giao thức v2, bản cuối
- protocol_v2.py
- DataContext
- mau_kiem_dinh
- o
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
- da
- test_amazon.py
- recommend
- l
- 3. Chạy thực nghiệm
- user_table
- sn
- no
- amazon.yaml
- argparse
- Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty
- an
- zt
- Đăng ký trước (pre-registration) — thực nghiệm hm500k
- Demo web — shop thời trang H&M (kèm Amazon Beauty)
- Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F
- README.md
- Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)
- .getDatasetMeta
- Đăng ký trước (pre-registration) — giao thức v2
- jn
- numpy
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
- ._stop
- 2. Tiến độ (13/10/2026)
- 9. Đánh giá, kiểm định và chống thiên lệch
- Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)
- .buildOrUpdateControllers
- n
- a
- tn
- BPRMFBaseline
- Phần 5. Câu hỏi hội đồng hay hỏi
- .notifyPlugins
- de
- v2_common.py
- Phần 2. Nắm toàn bộ đề tài
- u
- 13. Lịch sử phát triển
- LateFusion
- ws
- e
- ca
- io.py
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
6. `DataContext` - 34 edges
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

## Communities (99 total, 15 thin omitted)

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

### Community 4 - "protocol_v2.py"
Cohesion: 0.11
Nodes (10): export(), main(), HMAdapter, check_product_code(), to_day(), iterative_k_core(), make_stage(), prepare_pairs() (+2 more)

### Community 5 - "routes.py"
Cohesion: 0.08
Nodes (21): context(), ctx(), datasets(), example(), _filtered(), has_images(), health(), image() (+13 more)

### Community 6 - "torch"
Cohesion: 0.17
Nodes (9): load_best(), log_row(), logged(), main(), device(), count_parameters(), get_device(), _gpu_mem_str() (+1 more)

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2, bản cuối"
Cohesion: 0.12
Nodes (15): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo, 7. Kiểm định (+7 more)

### Community 8 - "protocol_v2.py"
Cohesion: 0.12
Nodes (14): DailySales, group_by_product(), product_code_of(), build_from_pairs(), build_v2(), load_pairs(), _day(), _hm_sample() (+6 more)

### Community 9 - "DataContext"
Cohesion: 0.09
Nodes (11): DataContext, best_rank_series(), history(), pick_example(), saved_best_series(), showcase_users(), _user(), user_profile() (+3 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "o"
Cohesion: 0.10
Nodes (22): at(), cn(), dn(), e(), ei(), g(), gi(), Gn() (+14 more)

### Community 12 - "test_v2.py"
Cohesion: 0.10
Nodes (15): FeatureTrainDataset, item_time_features(), user_time_features(), _catalog(), _day(), _sales(), test_feature_dataset_negatives_launched_and_not_positive(), test_group_by_product_merges_colour_variants() (+7 more)

### Community 13 - "test_demo.py"
Cohesion: 0.09
Nodes (15): answers(), results(), _verdict(), filter_users(), user_position(), at(), user_rows(), _macros() (+7 more)

### Community 14 - "download_hm_images.py"
Cohesion: 0.12
Nodes (6): fetch(), get_range(), main(), member_bytes(), RangeFile, zip_url()

### Community 15 - "test_v2_final.py"
Cohesion: 0.11
Nodes (9): final(), _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_dirty_files_ignores_outputs_and_test_log(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit(), test_lock_skips_tuning_hash_when_configs_come_from_other_dataset(), test_opened_seeds_reads_only_tags_of_current_holdout() (+1 more)

### Community 16 - "19_check_report.py"
Cohesion: 0.12
Nodes (17): check_claims(), check_macros_and_tables(), claims(), by_k_order(), hyb_fifth(), compare_with_committed(), Data, load() (+9 more)

### Community 17 - "test_bosung.py"
Cohesion: 0.12
Nodes (15): tune(), combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic() (+7 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 19 - "25_bosung.py"
Cohesion: 0.14
Nodes (7): component_check(), file_md5(), lock_errors(), main(), opened_tags(), Precomputed, provenance()

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - ".run_seed"
Cohesion: 0.12
Nodes (15): ablations(), beyond(), cpu_name(), dirty_files(), foreign_results(), git(), lock_errors(), machine_info() (+7 more)

### Community 22 - "test_evaluation.py"
Cohesion: 0.06
Nodes (34): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), score_items(), test_late_fusion_minmax_on_candidates() (+26 more)

### Community 23 - "draw"
Cohesion: 0.07
Nodes (36): ai(), ao(), average(), beforeDraw(), dataset(), draw(), getCenterPoint(), getMaxOverflow() (+28 more)

### Community 24 - "test_models.py"
Cohesion: 0.13
Nodes (10): 8. Lệch kế hoạch, build_torch(), mlp_layers(), GMF, MLP, NeuMF, test_late_fusion_extremes_reproduce_component_ranking(), test_forward_shapes_and_logits() (+2 more)

### Community 25 - "chart.umd.min.js"
Cohesion: 0.04
Nodes (20): Ae(), be(), beforeLayout(), d(), destroy(), es(), Gt(), Jo() (+12 more)

### Community 26 - "test_baselines.py"
Cohesion: 0.16
Nodes (9): interaction_matrix(), topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors(), _topk_dense() (+1 more)

### Community 27 - "MaskedScoreFn"
Cohesion: 0.10
Nodes (8): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), ContentProfile, MaskedScoreFn, MaskedScorer, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_masked_scorer_puts_unscoreable_items_last(), test_recent_popularity_and_content_profile()

### Community 28 - "va"
Cohesion: 0.06
Nodes (19): afterDraw(), afterEvent(), afterUpdate(), Bi(), Ci(), Ee(), Fi(), ki() (+11 more)

### Community 29 - "ns"
Cohesion: 0.06
Nodes (11): As(), bn, labelColor(), labelPointStyle(), ns(), on(), pn(), rt() (+3 more)

### Community 30 - "da"
Cohesion: 0.12
Nodes (16): beforeDatasetDraw(), beforeDatasetsDraw(), da(), ea(), fa(), ga(), ha, Ie() (+8 more)

### Community 31 - "test_amazon.py"
Cohesion: 0.09
Nodes (13): AmazonAdapter, asin_list(), build_features(), category_path(), item_info(), read_meta(), read_reviews(), DatasetAdapter (+5 more)

### Community 32 - "recommend"
Cohesion: 0.13
Nodes (8): recommend(), recommend(), test_best_ranks_match_recommend(), test_customer_without_targets_gets_model_recommendations(), test_metrics_match_per_user_file(), test_new_customer_gets_popular_list_instead_of_error(), test_showcase_users_hit_for_a_and_miss_for_b(), 4. Kiểm thử

### Community 33 - "l"
Cohesion: 0.17
Nodes (10): buildTicks(), Fn(), go(), ii(), parse(), parseArrayData(), parseObjectData(), parsePrimitiveData() (+2 more)

### Community 34 - "3. Chạy thực nghiệm"
Cohesion: 0.15
Nodes (12): 1. Cài đặt, 2. Dữ liệu, 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển, 3.2 Chạy thử (tuỳ chọn), 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần, 3.4 Sau khi chạy, 3.5 Kiểm chứng trên Amazon Beauty (dữ liệu đối chứng), 3.6 Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF (+4 more)

### Community 35 - "user_table"
Cohesion: 0.23
Nodes (5): amazon_table(), product_table(), user_table(), test_amazon_table_maps_metadata_to_item_columns(), test_product_table_uses_first_variant_and_counts_colours()

### Community 36 - "sn"
Cohesion: 0.26
Nodes (4): fe(), ks(), nn(), sn

### Community 37 - "no"
Cohesion: 0.09
Nodes (10): buildLookupTable(), Fo(), _generate(), _getTimestampsForTable(), initOffsets(), lt(), no, nt() (+2 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - "argparse"
Cohesion: 0.25
Nodes (3): bucket_of(), main(), select_buckets()

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 41 - "an"
Cohesion: 0.12
Nodes (4): an(), f(), generateLabels(), ts()

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
Cohesion: 0.18
Nodes (10): 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F, Phần 1. Thông điệp chính, Phần 3. Số liệu cần nhớ, Phần 4. Nội dung nào nói trong báo cáo, nội dung nào chỉ nói khi được hỏi, Phần 6. Câu không được nói (+2 more)

### Community 46 - "README.md"
Cohesion: 0.25
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - ".getDatasetMeta"
Cohesion: 0.27
Nodes (3): aa(), afterDatasetsUpdate(), onClick()

### Community 49 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.22
Nodes (8): 0. Vì sao có giao thức v2, 10. Lệch kế hoạch, 1. Dữ liệu, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký, Đăng ký trước (pre-registration) — giao thức v2

### Community 51 - "numpy"
Cohesion: 0.13
Nodes (9): TrainDataset, available_negatives(), build_user_positive_sets(), sample_train_negatives(), aggregate_unique_user_item(), test_aggregate_before_kcore_counts_unique_edges(), test_negative_sampler_never_returns_positive(), test_train_dataset_never_labels_positive_as_negative() (+1 more)

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

### Community 58 - "24_report_v2.py"
Cohesion: 0.06
Nodes (50): ablation(), beyond(), bootstrap_ci(), by_k(), cell(), dev_info(), ensure(), export_by_k() (+42 more)

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
Nodes (9): bo, et(), H(), s(), label(), mo(), n(), ne() (+1 more)

### Community 65 - "2. Tiến độ (13/10/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (06/11/2026)

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 67 - "Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)"
Cohesion: 0.33
Nodes (5): graphify, Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script), Quy ước báo cáo (`Report DACNTT/`), Ranh giới, Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

### Community 75 - "n"
Cohesion: 0.14
Nodes (5): ca(), Do(), eo(), getBasePixel(), Oe()

### Community 76 - "a"
Cohesion: 0.10
Nodes (13): a(), determineDataLimits(), Di(), getValueForPixel(), j(), ko, pi(), r() (+5 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.13
Nodes (4): BPRMFBaseline, MostPopularBaseline, RandomBaseline, test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 79 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 81 - "de"
Cohesion: 0.17
Nodes (6): b(), ce(), de, dt(), he(), qs()

### Community 82 - "v2_common.py"
Cohesion: 0.10
Nodes (18): base_key(), configs_for(), data_name(), eval_kw(), evaluate(), fit_torch(), hybrid_components(), is_feature() (+10 more)

### Community 83 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 84 - "u"
Cohesion: 0.17
Nodes (8): addBox(), beforeUpdate(), configure(), initialize(), reset(), start(), u(), vn()

### Community 85 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 88 - "LateFusion"
Cohesion: 0.36
Nodes (3): minmax(), model_scores(), test_minmax_constant_is_zero()

### Community 90 - "ws"
Cohesion: 0.16
Nodes (12): ct(), fs(), ge(), gs(), ms(), ps(), qe(), i() (+4 more)

### Community 93 - "e"
Cohesion: 0.18
Nodes (3): En, ia(), init()

### Community 97 - "ca"
Cohesion: 0.12
Nodes (17): _calculateBarIndexPixels(), _calculateBarValuePixels(), getLabelAndValue(), getLabelForValue(), getPixelForTick(), getPixelForValue(), _getRuler(), _getStackCount() (+9 more)

### Community 99 - "io.py"
Cohesion: 0.27
Nodes (5): log_test_access(), prereg_committed(), write_json(), test_log_test_access_appends_rows(), test_prereg_missing_means_not_committed()

### Community 100 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.40
Nodes (4): Nguyên tắc vẽ, Sơ đồ của đề tài, Sửa và xuất lại, Tệp

### Community 102 - "data_context.py"
Cohesion: 0.10
Nodes (10): results_dir(), saved_final_ranks(), unavailable_reason(), v2_available(), v2_data_mismatch(), test_dataset_without_final_results_reports_command_not_training(), test_results_from_other_data_are_refused(), vctx() (+2 more)

### Community 103 - "metrics_io.py"
Cohesion: 0.29
Nodes (6): _block(), _by_k(), dashboard(), _named(), dashboard(), test_dashboard_reads_result_files()

### Community 113 - "features.py"
Cohesion: 0.17
Nodes (15): build_amazon(), main(), build_catalog(), build_daily_sales(), build_user_profile(), Catalog, category_codes(), _codes() (+7 more)

### Community 116 - "pytest"
Cohesion: 0.24
Nodes (4): test_hm_adapter_rejects_excel(), _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

## Knowledge Gaps
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `7. Cấu trúc mã và API` connect `draw` to `Trang`, `a`, `test_demo.py`, `Demo web — shop thời trang H&M (kèm Amazon Beauty)`?**
  _High betweenness centrality (0.392) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Trang` be split into smaller, more focused modules?**
  _Cohesion score 0.08051948051948052 - nodes in this community are weakly interconnected._
- **Why does `test_results_page_matches_report_macros()` connect `test_demo.py` to `data_context.py`, `draw`?**
  _High betweenness centrality (0.285) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06674132138857783 - nodes in this community are weakly interconnected._
- **Why does `a()` connect `a` to `l`, `no`, `n`, `o`, `.getDatasetMeta`, `de`, `u`, `draw`, `chart.umd.min.js`, `ws`, `va`?**
  _High betweenness centrality (0.240) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09538461538461539 - nodes in this community are weakly interconnected._