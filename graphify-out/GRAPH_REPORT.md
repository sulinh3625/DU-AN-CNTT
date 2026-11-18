# Graph Report - DU-AN-CNTT  (2026-11-18)

## Corpus Check
- 113 files · ~210,252 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 116 file(s) not represented in the graph (top: .tex 37, .csv 31, .gz 20)

## Summary
- 2313 nodes · 5259 edges · 113 communities (89 shown, 24 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 237 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad9eef8d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- torch
- app.js
- build_poster.py
- run.py
- d
- routes.py
- Đăng ký trước (pre-registration) — giao thức v2, bản cuối
- draw
- DataContext
- mau_kiem_dinh
- En
- test_prepare.py
- ko
- download_hm_images.py
- sys
- 19_check_report.py
- test_v2_final.py
- NeuMFF
- bn
- reviews_Beauty_5
- 23_final_v2.py
- full_ranking.py
- test_evaluation.py
- Trang
- chart.umd.min.js
- hinh_bao_cao.py
- features.py
- va
- ns
- .__init__
- pathlib
- i
- hop
- jn
- pytest
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
- Đăng ký trước (pre-registration) — giao thức v2
- test_v2.py
- numpy
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- json
- 24_report_v2.py
- 10. Code, demo, kiểm thử và báo cáo
- 6. Bài toán, câu hỏi nghiên cứu và phạm vi
- 8. Mô hình
- s
- __main__.py
- build_slides.py
- user_rows
- 9. Đánh giá, kiểm định và chống thiên lệch
- Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)
- test_demo.py
- subprocess
- o
- tn
- BPRMFBaseline
- Phần 5. Câu hỏi hội đồng hay hỏi
- data_context.py
- .get
- trainer.py
- user_filter
- 2. Tiến độ (12/11/2026)
- 13. Lịch sử phát triển
- hybrid_features.py
- LateFusion
- Cs
- test_baselines.py
- .item_info
- metrics_io.py
- pathlib
- .update
- Đăng ký trước (pre-registration) — giao thức v2, bản cuối
- EvalRecord
- .getLabels
- slide
- n
- bam
- Sơ đồ của đề tài
- claims
- neumf_project — mã nguồn của đề tài
- _torch_scores
- Kế hoạch phân công tiến độ DACNTT_8d8e062d.md
- ket_qua
- Phần 2. Nắm toàn bộ đề tài
- rs
- main.py
- download_amazon_images.py
- ItemKNNBaseline
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
- `10.3 Kiểm thử` --references--> `saved_final_ranks()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/data_context.py
- `10.1 Quy trình thực nghiệm` --references--> `tune()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/25_bosung.py

## Import Cycles
- None detected.

## Communities (113 total, 24 thin omitted)

### Community 0 - "torch"
Cohesion: 0.14
Nodes (10): best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), recommend(), score_items() (+2 more)

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
Cohesion: 0.08
Nodes (4): d(), wn(), Xs(), Y()

### Community 5 - "routes.py"
Cohesion: 0.10
Nodes (21): context(), ctx(), example(), _filtered(), has_images(), health(), image(), neighbors() (+13 more)

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2, bản cuối"
Cohesion: 0.12
Nodes (14): 10. Lệch kế hoạch, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu A (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu B (`scripts/23_final_v2.py`), 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển, 3.2 Chạy thử (tuỳ chọn), 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần (+6 more)

### Community 8 - "draw"
Cohesion: 0.14
Nodes (15): ao(), draw(), Ee(), kn(), la(), Le(), lo(), qn() (+7 more)

### Community 9 - "DataContext"
Cohesion: 0.13
Nodes (9): DataContext, best_rank_series(), history(), pick_example(), saved_best_series(), showcase_users(), _user(), user_profile() (+1 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 12 - "test_prepare.py"
Cohesion: 0.11
Nodes (16): load_data(), DailySales, group_by_product(), build_from_pairs(), build_v2(), DataV2, load_pairs(), make_stage() (+8 more)

### Community 13 - "ko"
Cohesion: 0.09
Nodes (8): Ae(), configure(), getValueForPixel(), j(), ko, vo(), wo(), xo

### Community 14 - "download_hm_images.py"
Cohesion: 0.12
Nodes (6): fetch(), get_range(), main(), member_bytes(), RangeFile, zip_url()

### Community 15 - "sys"
Cohesion: 0.15
Nodes (6): cpu_name(), main(), cpu_name(), machine_info(), seed_everything(), cat_anh()

### Community 16 - "19_check_report.py"
Cohesion: 0.13
Nodes (15): _net(), o(), check_claims(), check_macros_and_tables(), compare_with_committed(), Data, load(), defined_macros() (+7 more)

### Community 17 - "test_v2_final.py"
Cohesion: 0.05
Nodes (22): combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic(), Table (+14 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - "23_final_v2.py"
Cohesion: 0.13
Nodes (13): ablations(), beyond(), dirty_files(), foreign_results(), git(), lock_errors(), main(), opened_seeds() (+5 more)

### Community 22 - "full_ranking.py"
Cohesion: 0.18
Nodes (8): _append(), _empty_metric_lists(), evaluate_score_function(), evaluate_torch_model(), _per_user_row(), deterministic_tie_key(), rank_positives(), positive_ranks()

### Community 23 - "test_evaluation.py"
Cohesion: 0.25
Nodes (11): build_full_ranking_records_multi(), hr_at_k(), multi_ranking_metrics(), ndcg_at_k(), precision_at_k(), recall_at_k(), test_full_ranking_excludes_seen_and_keeps_positive(), test_multi_metrics_equal_single_item_formulas() (+3 more)

### Community 24 - "Trang"
Cohesion: 0.12
Nodes (9): cac_buoc(), chia_thoi_gian(), demo_ngang(), duong_ong(), tinh_chinh_danh_gia(), Trang, vien_(), xu_ly_du_lieu() (+1 more)

### Community 25 - "chart.umd.min.js"
Cohesion: 0.03
Nodes (43): addElements(), at(), be(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), beforeLayout(), Bi() (+35 more)

### Community 26 - "hinh_bao_cao.py"
Cohesion: 0.16
Nodes (13): du_lieu_amazon_ngang(), du_lieu_hm_ngang(), _du_lieu_ngang(), hop_nhat(), kien_truc_neumf(), kien_truc_neumf_f(), _neumf(), neumf_f_ngang() (+5 more)

### Community 27 - "features.py"
Cohesion: 0.11
Nodes (22): build_amazon(), main(), build_features(), build_catalog(), build_daily_sales(), build_user_profile(), Catalog, category_codes() (+14 more)

### Community 28 - "va"
Cohesion: 0.06
Nodes (8): Ci(), eo(), Hs, Oi(), Si(), start(), va, xa

### Community 29 - "ns"
Cohesion: 0.07
Nodes (5): As(), initialize(), ns(), rt(), zs()

### Community 30 - ".__init__"
Cohesion: 0.15
Nodes (6): amazon_table(), product_table(), user_table(), test_amazon_table_maps_metadata_to_item_columns(), test_product_table_uses_first_variant_and_counts_colours(), test_bpr_checkpoint_roundtrip_and_demo_scoring_match()

### Community 31 - "pathlib"
Cohesion: 0.10
Nodes (8): AmazonAdapter, asin_list(), category_path(), item_info(), read_meta(), read_reviews(), DatasetAdapter, HMAdapter

### Community 32 - "i"
Cohesion: 0.17
Nodes (9): ct(), ge(), gs(), ms(), ps(), vs(), we(), ws (+1 more)

### Community 33 - "hop"
Cohesion: 0.11
Nodes (12): bong(), chan_trang(), chu_thich(), chuoi_buoc(), hop(), khung_cam(), khung_tren_hinh(), mui_ten() (+4 more)

### Community 37 - "no"
Cohesion: 0.09
Nodes (11): buildLookupTable(), ca(), Fo(), _generate(), _getTimestampsForTable(), ha, initOffsets(), no (+3 more)

### Community 38 - "amazon.yaml"
Cohesion: 0.06
Nodes (32): audit_dir, best_configs, content_onehot, data_dir, dataset, day0, evaluation, k_values (+24 more)

### Community 39 - ".constructor"
Cohesion: 0.20
Nodes (5): dt(), fe(), ks(), nn(), sn

### Community 40 - "Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty"
Cohesion: 0.18
Nodes (11): 0. Mục đích, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức, 3. Mô hình — giống H&M, trừ phần đặc trưng, 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M, 5. Đánh giá cuối, 6–7. Độ đo và kiểm định (+3 more)

### Community 41 - "an"
Cohesion: 0.09
Nodes (3): an(), f(), Mn()

### Community 42 - "zt"
Cohesion: 0.12
Nodes (7): Ft(), It(), kt(), qt(), wt(), Xt(), zt()

### Community 43 - "Đăng ký trước (pre-registration) — thực nghiệm hm500k"
Cohesion: 0.20
Nodes (9): 1. Dữ liệu & protocol, 2. Độ đo, 3. Mô hình, 4. Ngân sách tuning (như nhau cho mọi mô hình có siêu tham số), 5. Đánh giá cuối (test), 6. Kiểm định, 7. Chọn "mô hình lai tốt nhất", 9. Mở rộng sau khi xem test (+1 more)

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
Cohesion: 0.12
Nodes (10): 8. Lệch kế hoạch, build_torch(), mlp_layers(), GMF, MLP, NeuMF, test_forward_shapes_and_logits(), test_mlp_dropout_is_configurable() (+2 more)

### Community 49 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.20
Nodes (9): 0. Vì sao có giao thức v2, 10. Lệch kế hoạch, 1. Dữ liệu, 3. Mô hình, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký (+1 more)

### Community 50 - "test_v2.py"
Cohesion: 0.12
Nodes (15): FeatureTrainDataset, item_time_features(), user_time_features(), _catalog(), _day(), _sales(), test_feature_dataset_negatives_launched_and_not_positive(), test_group_by_product_merges_colour_variants() (+7 more)

### Community 51 - "numpy"
Cohesion: 0.11
Nodes (10): TrainDataset, iterative_k_core(), available_negatives(), build_user_positive_sets(), sample_train_negatives(), aggregate_unique_user_item(), prepare_pairs(), test_aggregate_before_kcore_counts_unique_edges() (+2 more)

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

### Community 57 - "json"
Cohesion: 0.07
Nodes (27): 6. Cấu trúc thư mục, export(), main(), load_best(), log_row(), logged(), main(), component_check() (+19 more)

### Community 58 - "24_report_v2.py"
Cohesion: 0.06
Nodes (49): ablation(), beyond(), bootstrap_ci(), by_k(), cell(), dev_info(), ensure(), export_by_k() (+41 more)

### Community 59 - "10. Code, demo, kiểm thử và báo cáo"
Cohesion: 0.50
Nodes (4): 10.2 Demo (`demo/README.md`), 10.4 Báo cáo LaTeX (`Report DACNTT/`), 10.5 Lưu ý khi làm tiếp, 10. Code, demo, kiểm thử và báo cáo

### Community 60 - "6. Bài toán, câu hỏi nghiên cứu và phạm vi"
Cohesion: 0.33
Nodes (6): 6.1 Bài toán, 6.2 Câu hỏi nghiên cứu, 6.3 Yêu cầu R1–R9, 6.4 Phạm vi, 6.5 Vì sao thiết kế như vậy, 6. Bài toán, câu hỏi nghiên cứu và phạm vi

### Community 61 - "8. Mô hình"
Cohesion: 0.33
Nodes (6): 8.1 NeuMF-F — mô hình đề xuất (`src/models/hybrid_features.py`), 8.2 Hợp nhất sớm và hợp nhất muộn, 8.3 Mô hình đối chứng và cấu hình đã chọn, 8.4 Ablation NeuMF-F, 8.5 Mô hình lai truyền thống Hybrid-CBCF — bổ sung sau đánh giá cuối, 8. Mô hình

### Community 62 - "s"
Cohesion: 0.07
Nodes (29): ai(), bo, dataset(), et(), H(), hi(), ho(), ii() (+21 more)

### Community 64 - "build_slides.py"
Cohesion: 0.10
Nodes (11): bieu_do(), ghi_hieu_ung(), _hien(), _hieu_ung(), macros(), morph(), so_voi_truyen_thong(), summary() (+3 more)

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
Cohesion: 0.06
Nodes (42): a(), aa(), afterDatasetsUpdate(), b(), cn(), determineDataLimits(), Di(), dn() (+34 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.14
Nodes (3): BPRMFBaseline, MostPopularBaseline, RandomBaseline

### Community 79 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 80 - "data_context.py"
Cohesion: 0.16
Nodes (5): results_dir(), saved_final_ranks(), v2_data_mismatch(), test_results_from_other_data_are_refused(), 10.3 Kiểm thử

### Community 81 - ".get"
Cohesion: 0.19
Nodes (5): ce(), de, he(), qs(), te()

### Community 82 - "trainer.py"
Cohesion: 0.25
Nodes (5): device(), count_parameters(), get_device(), _gpu_mem_str(), train_one_model()

### Community 84 - "2. Tiến độ (12/11/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (18/11/2026)

### Community 85 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 86 - "hybrid_features.py"
Cohesion: 0.06
Nodes (23): 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), base_key(), configs_for(), data_name(), eval_kw(), evaluate(), fit_torch(), hybrid_components() (+15 more)

### Community 87 - "LateFusion"
Cohesion: 0.21
Nodes (6): late_fusion(), LateFusion, minmax(), model_scores(), test_late_fusion_extremes_reproduce_component_ranking(), test_minmax_constant_is_zero()

### Community 89 - "test_baselines.py"
Cohesion: 0.16
Nodes (9): interaction_matrix(), topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors(), _topk_dense() (+1 more)

### Community 90 - ".item_info"
Cohesion: 0.17
Nodes (3): test_history_is_training_data_before_cutoff(), test_neighbors_are_sorted_and_counted(), test_similar_items_follow_itemknn()

### Community 91 - "metrics_io.py"
Cohesion: 0.29
Nodes (6): _block(), _by_k(), dashboard(), _named(), dashboard(), test_dashboard_reads_result_files()

### Community 93 - "pathlib"
Cohesion: 0.12
Nodes (7): bucket_of(), main(), select_buckets(), test_hm_adapter_rejects_excel(), _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

### Community 95 - "Đăng ký trước (pre-registration) — giao thức v2, bản cuối"
Cohesion: 0.22
Nodes (9): 0. Vì sao có bản này, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 6. Độ đo, 7. Kiểm định, 8. Kết luận được phép, 9. Hạn chế đã biết lúc đăng ký (+1 more)

### Community 96 - "EvalRecord"
Cohesion: 0.22
Nodes (4): EvalRecord, test_per_user_rows_match_summary_and_count_candidates(), test_perfect_model_hr_ndcg_one(), test_perfect_scorer_gets_ndcg_one_with_many_positives()

### Community 97 - ".getLabels"
Cohesion: 0.22
Nodes (7): buildTicks(), getPixelForTick(), getPixelForValue(), go(), init(), parse(), po()

### Community 98 - "slide"
Cohesion: 0.21
Nodes (8): anh(), anh_vua(), hinh(), logo(), nen(), nhan_chuong(), ra_sau(), slide()

### Community 99 - "n"
Cohesion: 0.11
Nodes (20): _calculateBarIndexPixels(), _calculateBarValuePixels(), Do(), Fn(), getLabelAndValue(), getMaxOverflow(), _getRuler(), _getStackCount() (+12 more)

### Community 100 - "bam"
Cohesion: 0.33
Nodes (3): bam(), pha(), phang()

### Community 101 - "Sơ đồ của đề tài"
Cohesion: 0.50
Nodes (3): Lối vẽ, Sơ đồ của đề tài, Sửa và xuất lại

### Community 102 - "claims"
Cohesion: 0.28
Nodes (4): claims(), by_k_order(), hyb_fifth(), order()

### Community 103 - "neumf_project — mã nguồn của đề tài"
Cohesion: 0.25
Nodes (6): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, neumf_project — mã nguồn của đề tài

### Community 108 - "ket_qua"
Cohesion: 0.24
Nodes (7): du_lieu(), ket_qua(), n_better(), nhan_xet(), text(), the(), the_so()

### Community 109 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 116 - "download_amazon_images.py"
Cohesion: 0.31
Nodes (3): amazon_image_path(), fetch(), main()

## Knowledge Gaps
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` connect `Tổng hợp đồ án: phương pháp, kết quả và tiến độ` to `9. Đánh giá, kiểm định và chống thiên lệch`, `README.md`, `2. Tiến độ (12/11/2026)`, `3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định`, `13. Lịch sử phát triển`, `4. Kiểm chứng trên Amazon Beauty`, `7. Dữ liệu`, `10. Code, demo, kiểm thử và báo cáo`, `6. Bài toán, câu hỏi nghiên cứu và phạm vi`, `8. Mô hình`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `torch` be split into smaller, more focused modules?**
  _Cohesion score 0.13768115942028986 - nodes in this community are weakly interconnected._
- **Why does `an()` connect `an` to `bt`, `.constructor`, `o`, `tn`, `bn`, `chart.umd.min.js`, `.update`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06600877192982456 - nodes in this community are weakly interconnected._
- **Why does `Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F` connect `Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F` to `Phần 2. Nắm toàn bộ đề tài`, `README.md`, `Phần 5. Câu hỏi hội đồng hay hỏi`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09538461538461539 - nodes in this community are weakly interconnected._