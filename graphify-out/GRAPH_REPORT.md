# Graph Report - DU-AN-CNTT  (2026-11-27)

## Corpus Check
- 110 files · ~634,366 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 116 file(s) not represented in the graph (top: .tex 37, .csv 31, .gz 20)

## Summary
- 2312 nodes · 5532 edges · 114 communities (93 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 226 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `af03c10a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- data_context.py
- app.js
- build_poster.py
- run.py
- d
- routes.py
- .getContext
- code_hash
- .getProps
- DataContext
- mau_kiem_dinh
- En
- numpy
- .run_seed
- download_hm_images.py
- benchmark_demo.py
- 8_check_report.py
- test_v2_final.py
- NeuMFF
- bn
- reviews_Beauty_5
- pathlib
- n
- test_v2_final.py
- hinh_bao_cao.py
- chart.umd.min.js
- pandas
- features.py
- va
- ns
- 6_bosung.py
- test_amazon.py
- i
- hop
- jn
- .getDatasetMeta
- ._stop
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
- hi
- test_v2.py
- TrainDataset
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- json
- 7_report.py
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- s
- __main__.py
- build_slides.py
- user_rows
- 9. Đánh giá, kiểm định và chống thiên lệch
- Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)
- user_table
- BPRMFBaseline
- o
- tn
- common.py
- Phần 5. Câu hỏi hội đồng hay hỏi
- unavailable_reason
- .get
- Đăng ký trước (pre-registration) — giao thức v2
- user_filter
- 2. Tiến độ (12/11/2026)
- 13. Lịch sử phát triển
- MaskedScoreFn
- LateFusion
- .getDataset
- test_baselines.py
- ._resolveElementOptions
- updateElements
- pytest
- .update
- Đăng ký trước (pre-registration) — giao thức v2, bản cuối
- test_demo.py
- .getLabels
- slide
- .getParsed
- bam
- Sơ đồ của đề tài
- test_prepare.py
- neumf_project — mã nguồn của đề tài
- torch
- ContentProfile
- history
- metrics_io.py
- ket_qua
- Phần 2. Nắm toàn bộ đề tài
- sys
- summary
- main.py
- download_amazon_images.py

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
- `2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026` --references--> `make_stage()`  [INFERRED]
  tong_hop.md → neumf_project/src/data_pipeline/protocol_v2.py
- `13.4 Dọn mã (10/10/2026)` --references--> `evaluate_v2()`  [INFERRED]
  tong_hop.md → neumf_project/src/evaluation/v2.py
- `10.3 Kiểm thử` --references--> `saved_final_ranks()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/data_context.py
- `10.3 Kiểm thử` --references--> `final_result()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/inference.py
- `10.1 Quy trình thực nghiệm` --references--> `tune()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/6_bosung.py

## Import Cycles
- None detected.

## Communities (114 total, 21 thin omitted)

### Community 0 - "data_context.py"
Cohesion: 0.05
Nodes (35): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), recommend(), score_items() (+27 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (95): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+87 more)

### Community 2 - "build_poster.py"
Cohesion: 0.10
Nodes (7): add_par(), bullets(), chu_thich(), ribbon(), set_runs(), style(), textbox()

### Community 3 - "run.py"
Cohesion: 0.07
Nodes (29): _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report() (+21 more)

### Community 4 - "d"
Cohesion: 0.09
Nodes (4): d(), Di(), Xs(), Y()

### Community 5 - "routes.py"
Cohesion: 0.10
Nodes (20): context(), ctx(), datasets(), example(), _filtered(), has_images(), health(), image() (+12 more)

### Community 7 - "code_hash"
Cohesion: 0.12
Nodes (14): 10. Lệch kế hoạch, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu A (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu B (`scripts/23_final_v2.py`), 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển, 3.2 Chạy thử (tuỳ chọn), 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần (+6 more)

### Community 8 - ".getProps"
Cohesion: 0.11
Nodes (22): ai(), ao(), average(), getCenterPoint(), ho(), Hs, _i(), inRange() (+14 more)

### Community 9 - "DataContext"
Cohesion: 0.10
Nodes (10): DataContext, best_rank_series(), pick_example(), saved_best_series(), showcase_users(), user_profile(), main(), test_history_is_training_data_before_cutoff() (+2 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "En"
Cohesion: 0.13
Nodes (7): ei(), En, init(), je(), qe(), ti(), ze()

### Community 12 - "numpy"
Cohesion: 0.13
Nodes (14): export(), load_data(), DailySales, group_by_product(), load_daily_sales(), product_code_of(), to_day(), build_from_pairs() (+6 more)

### Community 13 - ".run_seed"
Cohesion: 0.11
Nodes (15): ablations(), beyond(), cpu_name(), dirty_files(), foreign_results(), git(), lock_errors(), machine_info() (+7 more)

### Community 14 - "download_hm_images.py"
Cohesion: 0.12
Nodes (6): fetch(), get_range(), main(), member_bytes(), RangeFile, zip_url()

### Community 16 - "8_check_report.py"
Cohesion: 0.09
Nodes (19): _net(), o(), check_claims(), check_macros_and_tables(), claims(), by_k_order(), hyb_fifth(), compare_with_committed() (+11 more)

### Community 17 - "test_v2_final.py"
Cohesion: 0.12
Nodes (15): tune(), combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic() (+7 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 19 - "bn"
Cohesion: 0.17
Nodes (5): bn, on(), pn(), xn(), Ye()

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - "pathlib"
Cohesion: 0.24
Nodes (3): bucket_of(), main(), select_buckets()

### Community 22 - "n"
Cohesion: 0.11
Nodes (5): ca(), Do(), eo(), n(), Oe()

### Community 23 - "test_v2_final.py"
Cohesion: 0.07
Nodes (16): 6. Cấu trúc thư mục, component_check(), final(), lock_errors(), opened_tags(), _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_dirty_files_ignores_outputs_and_test_log() (+8 more)

### Community 24 - "hinh_bao_cao.py"
Cohesion: 0.06
Nodes (29): cac_buoc(), chia_thoi_gian(), demo_ngang(), du_lieu_amazon_ngang(), du_lieu_hm_ngang(), _du_lieu_ngang(), duong_ong(), _ghi() (+21 more)

### Community 25 - "chart.umd.min.js"
Cohesion: 0.04
Nodes (47): at(), be(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), beforeLayout(), cn(), da() (+39 more)

### Community 26 - "pandas"
Cohesion: 0.12
Nodes (7): DatasetAdapter, HMAdapter, iterative_k_core(), build_user_positive_sets(), aggregate_unique_user_item(), test_aggregate_before_kcore_counts_unique_edges(), test_train_dataset_never_labels_positive_as_negative()

### Community 27 - "features.py"
Cohesion: 0.14
Nodes (16): build_amazon(), main(), build_features(), build_catalog(), build_daily_sales(), build_user_profile(), Catalog, category_codes() (+8 more)

### Community 28 - "va"
Cohesion: 0.06
Nodes (22): afterDraw(), afterEvent(), afterUpdate(), Bi(), Ci(), configure(), Ee(), Fi() (+14 more)

### Community 30 - "6_bosung.py"
Cohesion: 0.15
Nodes (8): load_best(), log_row(), logged(), main(), file_md5(), main(), Precomputed, provenance()

### Community 31 - "test_amazon.py"
Cohesion: 0.11
Nodes (11): AmazonAdapter, asin_list(), category_path(), item_info(), read_meta(), read_reviews(), test_adapter_codes_asins_in_sorted_order(), test_amazon_config_uses_hm_configs_without_tuning() (+3 more)

### Community 32 - "i"
Cohesion: 0.17
Nodes (11): ct(), fs(), ge(), gs(), ms(), ps(), i(), vs() (+3 more)

### Community 33 - "hop"
Cohesion: 0.15
Nodes (8): chan_trang(), chuoi_buoc(), khung_cam(), khung_tren_hinh(), mui_ten(), so_tron(), the_bt(), vong()

### Community 35 - ".getDatasetMeta"
Cohesion: 0.22
Nodes (3): afterDatasetsUpdate(), Mn(), onClick()

### Community 37 - "no"
Cohesion: 0.11
Nodes (9): buildLookupTable(), Fo(), _generate(), _getTimestampsForTable(), initOffsets(), no, nt(), zi() (+1 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - ".constructor"
Cohesion: 0.29
Nodes (4): fe(), ks(), nn(), sn

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 41 - "an"
Cohesion: 0.13
Nodes (3): an(), ke(), wn()

### Community 42 - "zt"
Cohesion: 0.06
Nodes (14): bt, color(), Cs, Ft(), It(), kt(), mt(), os() (+6 more)

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.18
Nodes (10): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 8. Lệch kế hoạch (+2 more)

### Community 44 - "Demo web — shop thời trang H&M (kèm Amazon Beauty)"
Cohesion: 0.20
Nodes (8): popular(), 1. Chuẩn bị, 2. Chạy, 3. Màn hình, 4. Cách chấm — khớp đánh giá cuối, 5. Biến môi trường, 6. Ảnh sản phẩm (tuỳ chọn), Demo web — shop thời trang H&M (kèm Amazon Beauty)

### Community 45 - "Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F"
Cohesion: 0.17
Nodes (12): 0.1 Bốn điểm yếu hội đồng có thể xoáy sâu (đánh giá 18/11/2026), 1.1 Ba câu phải nói được ngay, 1.2 Bốn đóng góp (dùng cho slide kết luận), 1.3 Lời mở đầu gợi ý (khoảng 3 phút), Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F, Phần 0. 10 câu dễ bị hỏi nhất (sàng lọc 18/11/2026), Phần 1. Thông điệp chính, Phần 3. Số liệu cần nhớ (+4 more)

### Community 46 - "README.md"
Cohesion: 0.22
Nodes (3): Thư mục, Đọc gì, ở đâu, Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

### Community 47 - "Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)"
Cohesion: 0.22
Nodes (9): 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`), 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`), 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`), 4. Độ đo và kiểm định, 5. Trình bày theo ba nhóm baseline, 6. Kết luận được phép, 7. Hạn chế đã biết lúc đăng ký, 8. Lệch kế hoạch (+1 more)

### Community 48 - "test_models.py"
Cohesion: 0.14
Nodes (8): build_torch(), GMF, MLP, NeuMF, test_forward_shapes_and_logits(), test_mlp_dropout_is_configurable(), test_neumf_uses_four_independent_embeddings(), test_refit_runs_fixed_epochs_without_validation()

### Community 49 - "hi"
Cohesion: 0.22
Nodes (8): dataset(), generateLabels(), hi(), index(), ji(), Re(), ve(), Yi()

### Community 50 - "test_v2.py"
Cohesion: 0.12
Nodes (15): FeatureTrainDataset, item_time_features(), user_time_features(), _catalog(), _day(), _sales(), test_feature_dataset_negatives_launched_and_not_positive(), test_group_by_product_merges_colour_variants() (+7 more)

### Community 51 - "TrainDataset"
Cohesion: 0.16
Nodes (4): TrainDataset, available_negatives(), sample_train_negatives(), test_negative_sampler_never_returns_positive()

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

### Community 57 - "json"
Cohesion: 0.26
Nodes (6): main(), log_test_access(), prereg_committed(), write_json(), test_log_test_access_appends_rows(), test_prereg_missing_means_not_committed()

### Community 58 - "7_report.py"
Cohesion: 0.06
Nodes (50): ablation(), beyond(), bootstrap_ci(), by_k(), cell(), dev_info(), ensure(), export_by_k() (+42 more)

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
Cohesion: 0.11
Nodes (9): bo, et(), H(), s(), label(), mo(), ne(), numeric() (+1 more)

### Community 64 - "build_slides.py"
Cohesion: 0.12
Nodes (9): bieu_do(), ghi_hieu_ung(), _hien(), _hieu_ung(), macros(), morph(), so_voi_truyen_thong(), trang_thai() (+1 more)

### Community 65 - "user_rows"
Cohesion: 0.18
Nodes (8): filter_users(), user_position(), at(), user_rows(), test_filter_users_search_sort_and_position(), test_short_code_finds_customer(), test_user_table_counts_area_age_and_buckets(), _users()

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 67 - "Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)"
Cohesion: 0.33
Nodes (5): graphify, Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script), Quy ước báo cáo (`Report DACNTT/`), Ranh giới, Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

### Community 74 - "user_table"
Cohesion: 0.19
Nodes (5): amazon_table(), product_table(), user_table(), test_amazon_table_maps_metadata_to_item_columns(), test_product_table_uses_first_variant_and_counts_colours()

### Community 75 - "BPRMFBaseline"
Cohesion: 0.12
Nodes (5): score_fn(), BPRMFBaseline, MostPopularBaseline, RandomBaseline, test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 76 - "o"
Cohesion: 0.08
Nodes (25): a(), aa(), b(), dn(), e(), g(), gi(), Gn() (+17 more)

### Community 78 - "common.py"
Cohesion: 0.10
Nodes (16): base_key(), configs_for(), data_name(), eval_kw(), evaluate(), fit_torch(), hybrid_components(), is_feature() (+8 more)

### Community 79 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 80 - "unavailable_reason"
Cohesion: 0.21
Nodes (5): results_dir(), saved_final_ranks(), unavailable_reason(), v2_data_mismatch(), test_results_from_other_data_are_refused()

### Community 81 - ".get"
Cohesion: 0.19
Nodes (5): ce(), de, dt(), he(), ia()

### Community 82 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.20
Nodes (9): 0. Vì sao có giao thức v2, 10. Lệch kế hoạch, 1. Dữ liệu, 3. Mô hình, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký (+1 more)

### Community 84 - "2. Tiến độ (12/11/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (18/11/2026)

### Community 85 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 86 - "MaskedScoreFn"
Cohesion: 0.18
Nodes (4): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), MaskedScoreFn, MaskedScorer, test_masked_scorer_puts_unscoreable_items_last()

### Community 87 - "LateFusion"
Cohesion: 0.21
Nodes (6): late_fusion(), LateFusion, minmax(), model_scores(), test_late_fusion_extremes_reproduce_component_ranking(), test_minmax_constant_is_zero()

### Community 89 - "test_baselines.py"
Cohesion: 0.13
Nodes (10): interaction_matrix(), ItemKNNBaseline, topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors() (+2 more)

### Community 93 - "pytest"
Cohesion: 0.11
Nodes (6): test_hm_adapter_rejects_excel(), data(), test_report_claims_detect_changed_results(), _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

### Community 94 - ".update"
Cohesion: 0.16
Nodes (6): addBox(), beforeUpdate(), initialize(), reset(), start(), u()

### Community 95 - "Đăng ký trước (pre-registration) — giao thức v2, bản cuối"
Cohesion: 0.22
Nodes (9): 0. Vì sao có bản này, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký (+1 more)

### Community 96 - "test_demo.py"
Cohesion: 0.12
Nodes (10): v2_available(), answers(), results(), _verdict(), _macros(), _report_tools(), test_dataset_without_final_results_reports_command_not_training(), test_research_answers_follow_significance() (+2 more)

### Community 97 - ".getLabels"
Cohesion: 0.15
Nodes (12): buildTicks(), determineDataLimits(), Fn(), go(), ii(), parse(), parseArrayData(), parseObjectData() (+4 more)

### Community 98 - "slide"
Cohesion: 0.17
Nodes (10): anh(), anh_vua(), bong(), hop(), logo(), nen(), nhan_chuong(), paras() (+2 more)

### Community 99 - ".getParsed"
Cohesion: 0.10
Nodes (15): Ae(), _calculateBarIndexPixels(), _calculateBarValuePixels(), getLabelAndValue(), getLabelForValue(), getPixelForTick(), getPixelForValue(), _getRuler() (+7 more)

### Community 100 - "bam"
Cohesion: 0.33
Nodes (3): bam(), pha(), phang()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.50
Nodes (3): Lối vẽ, Sơ đồ của đề tài, Sửa và xuất lại

### Community 102 - "test_prepare.py"
Cohesion: 0.18
Nodes (9): load_pairs(), _day(), _hm_sample(), test_candidates_and_targets_only_items_with_training_pairs(), test_data_from_file_matches_build_v2(), test_export_twice_gives_same_bytes_and_md5(), test_load_data_rejects_missing_file_and_md5_mismatch(), test_prepare_again_keeps_manifest_when_only_commit_differs() (+1 more)

### Community 103 - "neumf_project — mã nguồn của đề tài"
Cohesion: 0.25
Nodes (6): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, neumf_project — mã nguồn của đề tài

### Community 104 - "torch"
Cohesion: 0.24
Nodes (5): device(), count_parameters(), get_device(), _gpu_mem_str(), train_one_model()

### Community 105 - "ContentProfile"
Cohesion: 0.23
Nodes (4): ContentProfile, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_recent_popularity_and_content_profile()

### Community 106 - "history"
Cohesion: 0.21
Nodes (6): history(), neighbors(), recommend(), _user(), test_customer_without_targets_gets_model_recommendations(), test_new_customer_gets_popular_list_instead_of_error()

### Community 107 - "metrics_io.py"
Cohesion: 0.29
Nodes (6): _block(), _by_k(), dashboard(), _named(), dashboard(), test_dashboard_reads_result_files()

### Community 108 - "ket_qua"
Cohesion: 0.17
Nodes (9): chu_thich(), du_lieu(), hinh(), ket_qua(), n_better(), nhan_xet(), text(), the() (+1 more)

### Community 109 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 116 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

## Knowledge Gaps
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `7. Cấu trúc mã và API` connect `.getProps` to `test_demo.py`, `o`, `Demo web — shop thời trang H&M (kèm Amazon Beauty)`?**
  _High betweenness centrality (0.389) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `data_context.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05322947095098994 - nodes in this community are weakly interconnected._
- **Why does `test_results_page_matches_report_macros()` connect `test_demo.py` to `.getProps`, `unavailable_reason`?**
  _High betweenness centrality (0.361) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06600877192982456 - nodes in this community are weakly interconnected._
- **Why does `a()` connect `o` to `i`, `.getLabels`, `.getParsed`, `d`, `no`, `.getContext`, `.getProps`, `.get`, `n`, `chart.umd.min.js`, `va`, `.update`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09538461538461539 - nodes in this community are weakly interconnected._