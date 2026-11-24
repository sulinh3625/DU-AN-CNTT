# Graph Report - DU-AN-CNTT  (2026-11-24)

## Corpus Check
- 110 files · ~624,702 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 116 file(s) not represented in the graph (top: .tex 37, .csv 31, .gz 20)

## Summary
- 2313 nodes · 5533 edges · 108 communities (87 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 226 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4d3d02f9`
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
- Đăng ký trước (pre-registration) — giao thức v2
- .getProps
- DataContext
- mau_kiem_dinh
- En
- test_prepare.py
- v2_common.py
- download_hm_images.py
- benchmark_demo.py
- 19_check_report.py
- test_v2_final.py
- NeuMFF
- bn
- reviews_Beauty_5
- 23_final_v2.py
- n
- test_v2_final.py
- Trang
- chart.umd.min.js
- hinh_bao_cao.py
- features.py
- va
- ns
- 02_prepare_data.py
- pathlib
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
- numpy
- Tổng hợp đồ án: phương pháp, kết quả và tiến độ
- 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định
- v2.yaml
- 4. Kiểm chứng trên Amazon Beauty
- 7. Dữ liệu
- 22_tune_v2.py
- 24_report_v2.py
- 25_bosung.py
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
- unavailable_reason
- .get
- trainer.py
- user_filter
- 2. Tiến độ (12/11/2026)
- 13. Lịch sử phát triển
- hybrid_features.py
- LateFusion
- .getDataset
- test_baselines.py
- ._resolveElementOptions
- updateElements
- pathlib
- .update
- summary
- .getLabels
- slide
- .getParsed
- bam
- Sơ đồ của đề tài
- claims
- neumf_project — mã nguồn của đề tài
- ket_qua
- Phần 2. Nắm toàn bộ đề tài
- main.py
- argparse
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
- `2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026` --references--> `make_stage()`  [INFERRED]
  tong_hop.md → neumf_project/src/data_pipeline/protocol_v2.py
- `13.4 Dọn mã (10/10/2026)` --references--> `evaluate_v2()`  [INFERRED]
  tong_hop.md → neumf_project/src/evaluation/v2.py
- `10.1 Quy trình thực nghiệm` --references--> `final()`  [INFERRED]
  tong_hop.md → neumf_project/scripts/25_bosung.py
- `10.3 Kiểm thử` --references--> `saved_final_ranks()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/data_context.py
- `10.3 Kiểm thử` --references--> `final_result()`  [INFERRED]
  tong_hop.md → neumf_project/demo/backend/inference.py

## Import Cycles
- None detected.

## Communities (108 total, 21 thin omitted)

### Community 0 - "data_context.py"
Cohesion: 0.05
Nodes (37): saved_final_ranks(), best_ranks(), candidate_scores(), eval_record(), final_result(), metrics_of(), rank_from_scores(), recommend() (+29 more)

### Community 1 - "app.js"
Cohesion: 0.07
Nodes (95): ad, api(), AREA_VI, areaLabel(), avatar(), body(), BUCKET_SHORT, BY_K (+87 more)

### Community 2 - "build_poster.py"
Cohesion: 0.09
Nodes (7): add_par(), bullets(), chu_thich(), ribbon(), set_runs(), style(), textbox()

### Community 3 - "run.py"
Cohesion: 0.07
Nodes (29): _amazon(), _c(), cmd_all(), cmd_amazon_data(), cmd_bosung_dry_run(), cmd_bosung_final(), cmd_bosung_tune(), cmd_check_report() (+21 more)

### Community 4 - "d"
Cohesion: 0.09
Nodes (4): d(), Di(), Xs(), Y()

### Community 5 - "routes.py"
Cohesion: 0.11
Nodes (20): context(), ctx(), dashboard(), example(), has_images(), health(), history(), image() (+12 more)

### Community 7 - "Đăng ký trước (pre-registration) — giao thức v2"
Cohesion: 0.06
Nodes (33): 0. Vì sao có bản này, 10. Lệch kế hoạch, 1. Dữ liệu, 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`), 3. Mô hình, 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`), 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`), 6. Độ đo (+25 more)

### Community 8 - ".getProps"
Cohesion: 0.11
Nodes (22): ai(), ao(), average(), getCenterPoint(), ho(), Hs, _i(), inRange() (+14 more)

### Community 9 - "DataContext"
Cohesion: 0.10
Nodes (9): DataContext, best_rank_series(), pick_example(), saved_best_series(), showcase_users(), user_profile(), test_history_is_training_data_before_cutoff(), test_neighbors_are_sorted_and_counted() (+1 more)

### Community 10 - "mau_kiem_dinh"
Cohesion: 0.08
Nodes (28): article_pairs, articles, product_pairs, products, mau_kiem_dinh, before_test_start, customers, file (+20 more)

### Community 11 - "En"
Cohesion: 0.13
Nodes (7): ei(), En, init(), je(), qe(), ti(), ze()

### Community 12 - "test_prepare.py"
Cohesion: 0.10
Nodes (17): data_name(), load_data(), manifest_path(), DailySales, group_by_product(), build_from_pairs(), build_v2(), load_pairs() (+9 more)

### Community 13 - "v2_common.py"
Cohesion: 0.08
Nodes (20): base_key(), configs_for(), device(), eval_kw(), evaluate(), fit_torch(), hybrid_components(), is_feature() (+12 more)

### Community 14 - "download_hm_images.py"
Cohesion: 0.12
Nodes (6): fetch(), get_range(), main(), member_bytes(), RangeFile, zip_url()

### Community 16 - "19_check_report.py"
Cohesion: 0.13
Nodes (15): _net(), o(), check_claims(), check_macros_and_tables(), compare_with_committed(), Data, load(), defined_macros() (+7 more)

### Community 17 - "test_v2_final.py"
Cohesion: 0.11
Nodes (14): combine(), crossfit_scores(), fit_weights(), pair_differences(), TraditionalHybrid, _args(), _synthetic(), Table (+6 more)

### Community 18 - "NeuMFF"
Cohesion: 0.18
Nodes (3): NeuMFF, branch(), id_emb()

### Community 19 - "bn"
Cohesion: 0.17
Nodes (5): bn, on(), pn(), xn(), Ye()

### Community 20 - "reviews_Beauty_5"
Cohesion: 0.12
Nodes (16): article_pairs, articles, product_pairs, products, reviews_Beauty_5, before_test_start, customers, file (+8 more)

### Community 21 - "23_final_v2.py"
Cohesion: 0.12
Nodes (14): ablations(), beyond(), cpu_name(), dirty_files(), foreign_results(), git(), lock_errors(), machine_info() (+6 more)

### Community 22 - "n"
Cohesion: 0.11
Nodes (5): ca(), Do(), eo(), n(), Oe()

### Community 23 - "test_v2_final.py"
Cohesion: 0.09
Nodes (13): final(), lock_errors(), opened_tags(), _args(), test_by_k_recomputes_metrics_from_saved_ranks(), test_dirty_files_ignores_outputs_and_test_log(), test_lock_lists_every_violation(), test_lock_passes_and_overrides_are_explicit() (+5 more)

### Community 24 - "Trang"
Cohesion: 0.12
Nodes (9): cac_buoc(), chia_thoi_gian(), demo_ngang(), duong_ong(), tinh_chinh_danh_gia(), Trang, vien_(), xu_ly_du_lieu() (+1 more)

### Community 25 - "chart.umd.min.js"
Cohesion: 0.04
Nodes (47): at(), be(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), beforeLayout(), cn(), da() (+39 more)

### Community 26 - "hinh_bao_cao.py"
Cohesion: 0.16
Nodes (13): du_lieu_amazon_ngang(), du_lieu_hm_ngang(), _du_lieu_ngang(), hop_nhat(), kien_truc_neumf(), kien_truc_neumf_f(), _neumf(), neumf_f_ngang() (+5 more)

### Community 27 - "features.py"
Cohesion: 0.17
Nodes (14): build_amazon(), main(), build_catalog(), build_daily_sales(), build_user_profile(), Catalog, category_codes(), _codes() (+6 more)

### Community 28 - "va"
Cohesion: 0.06
Nodes (22): afterDraw(), afterEvent(), afterUpdate(), Bi(), Ci(), configure(), Ee(), Fi() (+14 more)

### Community 30 - "02_prepare_data.py"
Cohesion: 0.12
Nodes (9): export(), main(), AmazonAdapter, DatasetAdapter, HMAdapter, check_product_code(), product_code_of(), save_pairs() (+1 more)

### Community 31 - "pathlib"
Cohesion: 0.11
Nodes (13): asin_list(), build_features(), category_path(), item_info(), read_meta(), read_reviews(), to_day(), test_adapter_codes_asins_in_sorted_order() (+5 more)

### Community 32 - "i"
Cohesion: 0.17
Nodes (11): ct(), fs(), ge(), gs(), ms(), ps(), i(), vs() (+3 more)

### Community 33 - "hop"
Cohesion: 0.11
Nodes (14): bong(), chan_trang(), chu_thich(), chuoi_buoc(), hop(), khung_cam(), khung_tren_hinh(), mui_ten() (+6 more)

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

### Community 49 - "hi"
Cohesion: 0.22
Nodes (8): dataset(), generateLabels(), hi(), index(), ji(), Re(), ve(), Yi()

### Community 50 - "test_v2.py"
Cohesion: 0.12
Nodes (15): FeatureTrainDataset, item_time_features(), user_time_features(), _catalog(), _day(), _sales(), test_feature_dataset_negatives_launched_and_not_positive(), test_group_by_product_merges_colour_variants() (+7 more)

### Community 51 - "numpy"
Cohesion: 0.15
Nodes (8): TrainDataset, available_negatives(), build_user_positive_sets(), sample_train_negatives(), aggregate_unique_user_item(), test_aggregate_before_kcore_counts_unique_edges(), test_negative_sampler_never_returns_positive(), test_train_dataset_never_labels_positive_as_negative()

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
Cohesion: 0.18
Nodes (9): load_best(), log_row(), logged(), main(), ensure_dir(), log_test_access(), prereg_committed(), test_log_test_access_appends_rows() (+1 more)

### Community 58 - "24_report_v2.py"
Cohesion: 0.05
Nodes (55): _block(), _by_k(), dashboard(), _named(), test_dashboard_reads_result_files(), ablation(), beyond(), bootstrap_ci() (+47 more)

### Community 59 - "25_bosung.py"
Cohesion: 0.13
Nodes (10): component_check(), file_md5(), Precomputed, provenance(), tune(), 10.1 Quy trình thực nghiệm, 10.2 Demo (`demo/README.md`), 10.4 Báo cáo LaTeX (`Report DACNTT/`) (+2 more)

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
Cohesion: 0.11
Nodes (10): bieu_do(), cat_anh(), ghi_hieu_ung(), _hien(), _hieu_ung(), macros(), morph(), so_voi_truyen_thong() (+2 more)

### Community 65 - "user_rows"
Cohesion: 0.15
Nodes (12): filter_users(), _filtered(), position(), random_user(), search_users(), user_position(), at(), user_rows() (+4 more)

### Community 66 - "9. Đánh giá, kiểm định và chống thiên lệch"
Cohesion: 0.40
Nodes (5): 9.1 Full Ranking và độ đo, 9.2 Tinh chỉnh và đánh giá cuối, 9.3 Kiểm định, 9.4 Quy trình chống thiên lệch, 9. Đánh giá, kiểm định và chống thiên lệch

### Community 67 - "Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)"
Cohesion: 0.33
Nodes (5): graphify, Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script), Quy ước báo cáo (`Report DACNTT/`), Ranh giới, Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

### Community 74 - "test_demo.py"
Cohesion: 0.09
Nodes (14): amazon_table(), product_table(), user_table(), answers(), results(), _verdict(), _macros(), _report_tools() (+6 more)

### Community 75 - "subprocess"
Cohesion: 0.22
Nodes (6): _ghi(), _edge(), _html(), _khung(), xuat(), main()

### Community 76 - "o"
Cohesion: 0.08
Nodes (25): a(), aa(), b(), dn(), e(), g(), gi(), Gn() (+17 more)

### Community 78 - "BPRMFBaseline"
Cohesion: 0.14
Nodes (3): BPRMFBaseline, MostPopularBaseline, RandomBaseline

### Community 79 - "Phần 5. Câu hỏi hội đồng hay hỏi"
Cohesion: 0.29
Nodes (7): 5.1 Đề tài và đóng góp, 5.2 Mô hình, 5.3 Dữ liệu, đánh giá và thống kê, 5.4 Kết quả, 5.5 Amazon Beauty và Hybrid-CBCF, 5.6 Quá trình làm (chỉ nói khi được hỏi), Phần 5. Câu hỏi hội đồng hay hỏi

### Community 80 - "unavailable_reason"
Cohesion: 0.10
Nodes (9): results_dir(), unavailable_reason(), v2_available(), v2_data_mismatch(), datasets(), test_dataset_without_final_results_reports_command_not_training(), test_results_from_other_data_are_refused(), vctx() (+1 more)

### Community 81 - ".get"
Cohesion: 0.19
Nodes (5): ce(), de, dt(), he(), ia()

### Community 82 - "trainer.py"
Cohesion: 0.39
Nodes (3): count_parameters(), _gpu_mem_str(), train_one_model()

### Community 84 - "2. Tiến độ (12/11/2026)"
Cohesion: 0.40
Nodes (5): 2.1 Tình hình, 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026, 2.3 Việc còn lại, 2.4 Mức độ hoàn thành theo hạng mục, 2. Tiến độ (18/11/2026)

### Community 85 - "13. Lịch sử phát triển"
Cohesion: 0.40
Nodes (5): 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID, 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối, 13.3 Bản cuối so với giai đoạn phát triển ban đầu, 13.4 Dọn mã (10/10/2026), 13. Lịch sử phát triển

### Community 86 - "hybrid_features.py"
Cohesion: 0.10
Nodes (7): ContentProfile, MaskedScoreFn, MaskedScorer, RecentPopularity, test_content_profile_uses_given_onehot_columns(), test_masked_scorer_puts_unscoreable_items_last(), test_recent_popularity_and_content_profile()

### Community 87 - "LateFusion"
Cohesion: 0.18
Nodes (6): late_fusion(), LateFusion, minmax(), model_scores(), test_late_fusion_extremes_reproduce_component_ranking(), test_minmax_constant_is_zero()

### Community 89 - "test_baselines.py"
Cohesion: 0.13
Nodes (10): interaction_matrix(), ItemKNNBaseline, topk_cosine(), UserKNNBaseline, _dense_cosine(), test_itemknn_scores_follow_definition(), test_topk_cosine_matches_dense_bruteforce(), test_userknn_scores_and_neighbors() (+2 more)

### Community 93 - "pathlib"
Cohesion: 0.11
Nodes (6): test_hm_adapter_rejects_excel(), data(), test_report_claims_detect_changed_results(), _old_select_buckets(), test_blocks_0_and_1_match_old_holdout_logic(), test_last_block_may_hit_end_then_runs_out()

### Community 94 - ".update"
Cohesion: 0.16
Nodes (6): addBox(), beforeUpdate(), initialize(), reset(), start(), u()

### Community 97 - ".getLabels"
Cohesion: 0.15
Nodes (12): buildTicks(), determineDataLimits(), Fn(), go(), ii(), parse(), parseArrayData(), parseObjectData() (+4 more)

### Community 98 - "slide"
Cohesion: 0.27
Nodes (7): anh(), anh_vua(), logo(), nen(), nhan_chuong(), ra_sau(), slide()

### Community 99 - ".getParsed"
Cohesion: 0.10
Nodes (15): Ae(), _calculateBarIndexPixels(), _calculateBarValuePixels(), getLabelAndValue(), getLabelForValue(), getPixelForTick(), getPixelForValue(), _getRuler() (+7 more)

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
Cohesion: 0.22
Nodes (7): test_metrics_match_per_user_file(), 1. Cài đặt, 2. Dữ liệu, 4. Kiểm thử, 5. Demo, 6. Cấu trúc thư mục, neumf_project — mã nguồn của đề tài

### Community 108 - "ket_qua"
Cohesion: 0.22
Nodes (6): du_lieu(), hinh(), ket_qua(), n_better(), the(), the_so()

### Community 109 - "Phần 2. Nắm toàn bộ đề tài"
Cohesion: 0.22
Nodes (9): 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1), 2.2 Cơ sở lý thuyết (Chương 2), 2.3 Dữ liệu và tiền xử lý (mục 3.2), 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4), 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5), 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5), 2.7 Kết quả (Chương 4), 2.8 Demo (mục 3.9) (+1 more)

### Community 116 - "argparse"
Cohesion: 0.12
Nodes (8): amazon_image_path(), main(), fetch(), main(), bucket_of(), main(), select_buckets(), main()

## Knowledge Gaps
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `7. Cấu trúc mã và API` connect `.getProps` to `test_demo.py`, `o`, `Demo web — shop thời trang H&M (kèm Amazon Beauty)`?**
  _High betweenness centrality (0.386) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `s()` (e.g. with `ho()` and `ii()`) actually correct?**
  _`s()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `data_context.py` be split into smaller, more focused modules?**
  _Cohesion score 0.051131354687040845 - nodes in this community are weakly interconnected._
- **Why does `test_results_page_matches_report_macros()` connect `test_demo.py` to `.getProps`, `unavailable_reason`?**
  _High betweenness centrality (0.356) - this node is a cross-community bridge._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06600877192982456 - nodes in this community are weakly interconnected._
- **Why does `a()` connect `o` to `i`, `.getLabels`, `.getParsed`, `d`, `no`, `.getContext`, `.getProps`, `.get`, `n`, `chart.umd.min.js`, `va`, `.update`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Should `build_poster.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09116809116809117 - nodes in this community are weakly interconnected._