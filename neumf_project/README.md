# neumf_project — mã nguồn của đề tài

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Kết quả chính (kế hoạch đăng ký trước: `audit/PREREG_v2.md`):

- **Mô hình đề xuất NeuMF-F:** hai nhánh GMF-F và MLP-F hợp nhất sớm như NeuMF. Vector của khách và sản phẩm =
  embedding ID + phép chiếu của đặc trưng (thuộc tính và mô tả văn bản của sản phẩm, thông tin khách, doanh số và thời
  gian — tính theo thời điểm, không dùng thông tin tương lai).
- **Dữ liệu:** hai mẫu khách hàng không giao nhau của H&M — **mẫu phát triển** chỉ để tinh chỉnh (trên tập xác thực),
  **mẫu kiểm định** chỉ để đánh giá cuối (mở tập kiểm thử đúng một lần). Một sản phẩm là một mẫu (`product_code`, mọi màu
  gộp lại); tập ứng viên là các sản phẩm có dữ liệu huấn luyện trước mốc.
- **So sánh:** 14 mô hình, 5 seed, họ 10 so sánh có hiệu chỉnh Holm; bốn độ đo ở K = 5, 10, 15, 20. Kết quả:
  `outputs/v2/final/ket_qua.txt`.
- **Kiểm chứng trên Amazon Beauty 2014** (`audit/PREREG_amazon.md`): cùng mã, cùng 14 mô hình và họ 10 so sánh, dùng
  cấu hình đã chọn trên H&M (không tinh chỉnh lại). Kết quả: `outputs/amazon/final/ket_qua.txt`.

Phương pháp, kết quả và tiến độ: `../tong_hop.md`. Mọi lệnh dưới đây chạy từ thư mục `neumf_project/`.

| Mục | Nội dung |
|---|---|
| 1 | Cài đặt |
| 2 | Dữ liệu |
| 3 | Chạy thực nghiệm (H&M; Amazon Beauty ở mục 3.5) |
| 4 | Kiểm thử |
| 5 | Demo |
| 6 | Cấu trúc thư mục |

---

## 1. Cài đặt

Python 3.11 trở lên (đã chạy với 3.12 và 3.13), RAM 16 GB. GPU NVIDIA không bắt buộc nhưng nhanh hơn nhiều.

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Có GPU: cài PyTorch bản CUDA **trước** `requirements.txt`, ví dụ
`pip install torch --index-url https://download.pytorch.org/whl/cu124`, rồi kiểm tra
`python -c "import torch; print(torch.cuda.is_available())"`. Cấu hình để `device: auto` nên tự dùng GPU nếu có.

## 2. Dữ liệu

Tải 3 file của cuộc thi Kaggle
[H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)
(phải bấm *I Understand and Accept* ở trang Rules) vào `data/raw/hm/`:

| File | Dùng cho |
|---|---|
| `transactions_train.csv` (3,5 GB) | Lịch sử mua; doanh số theo ngày của toàn H&M (đặc trưng) |
| `articles.csv` | Thuộc tính và mô tả văn bản của sản phẩm (đặc trưng); tên, loại sản phẩm trên demo |
| `customers.csv` | Thuộc tính khách (đặc trưng); tuổi trong danh sách chọn khách của demo |

Không dùng bản `.xlsx`: Excel cắt ở 1.048.576 dòng. `customers.csv` đúng có 1.371.980 khách; bản chỉ có 1.048.575 dòng
là bản đã bị Excel cắt, cần tải lại (code báo lỗi nếu thiếu dòng).

Tải bằng Kaggle CLI (cần `~/.kaggle/kaggle.json`):

```bash
pip install kaggle
kaggle competitions download -c h-and-m-personalized-fashion-recommendations -f transactions_train.csv -p data/raw/hm
```

(làm tương tự với `articles.csv`, `customers.csv`). Sau đó tạo hai mẫu, đặc trưng và dữ liệu đã lọc — chạy một lần:

```bash
python run.py sample-hm     # mẫu phát triển (khối 0) → data/processed/hm/mau_phat_trien.csv
python run.py v2-data       # mẫu kiểm định (khối 2) → mau_kiem_dinh.csv; đặc trưng → catalog_v2.npz, daily_sales_v2.npz;
                            # dữ liệu đã lọc → outputs/data/<mẫu>.csv.gz + manifest.json (MD5)
```

Mẫu lấy theo băm `customer_id` với khoá cố định nên chạy lại luôn ra đúng cùng file (MD5 ghi trong
`audit/PREREG_v2.md` mục 1). Khối 1 đã bị mở trong lúc phát triển nên không dùng. Thư mục `data/` không được commit.

Dữ liệu Amazon Beauty (chỉ cần để chạy lại phần kiểm chứng, mục 3.5): `reviews_Beauty_5.json.gz` và
`meta_Beauty.json.gz` vào `data/raw/amazon/`.

## 3. Chạy thực nghiệm

| Bước | Lệnh | Việc | Thời gian |
|---|---|---|---|
| 1 | `python run.py v2-tune --resume` | Tinh chỉnh trên tập xác thực của mẫu phát triển | khoảng 7 giờ (CPU 4 nhân) |
| 2 | `python run.py v2-dry-run` | Tuỳ chọn: chạy thử trọn đường ống, không mở tập kiểm thử | khoảng 1 giờ |
| 3 | `python run.py v2-final --reason "..."` | Đánh giá cuối trên tập kiểm thử của mẫu kiểm định + xuất bảng, hình cho báo cáo | khoảng 7,5 giờ (RTX 3050 Laptop) |
| 4 | `python run.py check-report` | Đối chiếu câu chữ báo cáo với số liệu | dưới 1 phút |

Chạy qua đêm một lệnh: `python run.py all` = `prepare` → bước 1 (`--resume`) → bước 2; thêm `--final --reason "..."`
để chạy luôn bước 3 ở cuối (khoá kiểm thử của bước 3 vẫn áp dụng). Bị ngắt thì chạy lại đúng lệnh đó: tinh chỉnh đi
tiếp từ cấu hình còn thiếu.

### 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển

- Mỗi mô hình có học thử 6 cấu hình (seed 42); mô hình một tham số thử đủ lưới. Lưới: `audit/PREREG_v2.md` mục 4.
- Mỗi cấu hình ghi một dòng `audit/v2/tuning_log.csv` kèm commit và **mã băm mã nguồn** (`code_hash`, tính trên
  `src/`, `scripts/v2_common.py`, `scripts/22_tune_v2.py`, `scripts/02_prepare_data.py`, `configs/v2.yaml`). Cấu hình
  tốt nhất ghi vào `audit/v2/best_configs.json`.
- Bị ngắt thì chạy lại đúng lệnh trên: cấu hình đã có được bỏ qua.
- Xong thì đưa bảng tinh chỉnh vào báo cáo: `python scripts/24_report_v2.py --tuning-only`.

### 3.2 Chạy thử (tuỳ chọn)

`python run.py v2-dry-run` chạy trọn đường ống đánh giá cuối nhưng trên tập xác thực của mẫu phát triển, mỗi mạng nơ-ron
1 epoch — không mở tập kiểm thử nào. Kết quả ở `outputs/v2/dry_run/` (không commit).

### 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần

**Đã chạy ngày 10/10/2026** (commit `e4e4f25`, `code_hash` `0f1ea1eec5a86c31`; seed 42 chạy lại theo
`audit/PREREG_v2.md` mục 10). Kết quả: `outputs/v2/final/` — đọc nhanh ở `ket_qua.txt`.

```bash
git status       # mọi thay đổi (kể cả audit/PREREG_v2.md, audit/v2/) phải đã commit
python run.py v2-final --reason "Đánh giá cuối theo PREREG_v2"
```

Lệnh chạy hai script:

1. `scripts/23_final_v2.py` — 5 seed (42, 2024, 2025, 2026, 3407). Mỗi seed: mạng nơ-ron chọn số epoch trên tập xác thực
   của mẫu kiểm định, huấn luyện lại từ đầu trên mọi cặp trước 29/07/2020, rồi chấm tập kiểm thử và lưu hạng của từng
   sản phẩm đúng (`seed*/per_user.csv.gz`). Seed 42 thêm ablation của NeuMF-F (bỏ biến thể trùng NeuMF-F), top-20 và
   checkpoint cho demo. Ra: `outputs/v2/final/seed*/`; thư mục này còn kết quả của dữ liệu khác thì script dừng.
2. `scripts/24_report_v2.py` — trung bình ± độ lệch chuẩn, bốn độ đo ở K = 5, 10, 15, 20 (`by_k.csv`), kiểm định
   (Wilcoxon + bootstrap + Holm, 10 so sánh), ablation, độ phủ. Ra: `outputs/v2/final/*.csv`, `ket_qua.txt`, hình, bảng
   `.tex` và macro số liệu trong `../Report DACNTT/`.

**Khoá kiểm thử.** `23_final_v2.py` từ chối chạy nếu:

- `audit/PREREG_v2.md` chưa commit, hoặc thiếu `--reason`;
- có file đã theo dõi bị sửa mà chưa commit (trừ `outputs/` và `audit/test_access_log.csv`), hoặc có file mã nguồn chưa
  theo dõi trong `src/`, `scripts/`, `configs/`;
- tinh chỉnh chưa đủ mô hình, hoặc mã băm mã nguồn khác lúc tinh chỉnh;
- seed đã từng mở tập kiểm thử.

Mỗi seed ghi một dòng `audit/test_access_log.csv` **trước** khi chấm. Bị ngắt giữa chừng: chạy tiếp các seed còn thiếu
bằng `--seeds ...`. Seed đang chạy dở đã mở tập kiểm thử, nên chạy lại seed đó cần `--allow-rerun` và phải ghi vào
`audit/PREREG_v2.md` mục 10 (lệch kế hoạch).

Sau đánh giá cuối, mã của giai đoạn phát triển ban đầu (chỉ dùng ID) đã được xoá khỏi `src/` và mã được mở rộng để chạy
Amazon Beauty, nên mã băm hiện tại khác `0f1ea1eec5a86c31`; với H&M, mặc định vẫn cho đúng hành vi cũ (các test cũ đều
qua). Chạy lại `23_final_v2.py` vì vậy cần `--allow-code-change` (và ghi vào mục 10).

### 3.4 Sau khi chạy

1. `python run.py check-report`: báo câu nhận xét bằng chữ trong báo cáo không còn đúng với số liệu (H&M và Amazon),
   dòng tài liệu còn ghi số cũ, macro/bảng/hình còn thiếu.
2. Số liệu trong báo cáo đọc qua macro nên tự cập nhật; phần thảo luận Chương 4–5 viết theo
   `outputs/v2/final/significance.csv` và `summary.csv` — sửa lại nếu kết luận đổi.
3. Chụp ảnh demo (mục 5), biên dịch báo cáo (`../Report DACNTT/compile.bat`), commit.

Cần tính lại bảng/hình mà không mở lại tập kiểm thử: `python run.py v2-report`. Bảng theo K đọc cột hạng `ranks` đã lưu
trong `seed*/per_user.csv.gz`: K = 15 tính từ đó, và số @5/@10/@20 tính lại phải trùng `summary.csv` (lệch thì script
dừng).

### 3.5 Kiểm chứng trên Amazon Beauty (dữ liệu đối chứng)

Chạy lại cùng giao thức trên Amazon Beauty 2014 5-core: cùng mã, cùng 14 mô hình, cùng họ 10 so sánh. **Không tinh
chỉnh lại:** mọi mô hình dùng cấu hình đã chọn trên H&M (`audit/v2/best_configs.json`); chỉ số epoch được chọn trên tập
xác thực Amazon, ngay trong lần đánh giá cuối. Đặc trưng khác H&M: Amazon không có thông tin khách; đặc trưng sản phẩm
gồm thương hiệu, danh mục, nhóm giá và văn bản. Kế hoạch đăng ký trước: `audit/PREREG_amazon.md`; cấu hình:
`configs/amazon.yaml`.

**Đã chạy ngày 10–11/10/2026** (commit `f866337`, 5 seed, GPU RTX 3050 Laptop, tổng khoảng 3 giờ). Kết quả:
`outputs/amazon/final/` — đọc nhanh ở `ket_qua.txt`.

Mọi script đọc bộ dữ liệu từ biến môi trường `NEUMF_CONFIG`, mặc định `configs/v2.yaml` (H&M). Các lệnh `amazon-*`
tự đặt biến này cho script con, nên không cần đặt tay.

```bash
python run.py amazon-data                     # đặc trưng + dữ liệu đã lọc + MD5 (cần data/raw/amazon/, ~1 phút)
python run.py amazon-dry-run                  # thử trọn đường ống trên tập xác thực, 1 epoch (không mở tập kiểm thử)
python run.py amazon-final --reason "..."     # đánh giá cuối: mở tập kiểm thử Amazon đúng một lần
python run.py amazon-report                   # chỉ tính lại kiểm định, bảng theo K, hình, macro LaTeX, ket_qua.txt
```

- **Dữ liệu thô:** `data/raw/amazon/reviews_Beauty_5.json.gz` và `meta_Beauty.json.gz`, tải từ
  `http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/`.
- **Nơi ghi:** `outputs/amazon/final/`, gồm `ket_qua.txt`, các CSV (kể cả `by_k.csv`), hình và checkpoint seed 42 cho
  demo.
- **Khoá kiểm thử:** như H&M — `PREREG_amazon.md` phải được commit trước, tree sạch, nhật ký ghi
  `amazon_kiemdinh_seed<N>`. Không so mã băm với nhật ký tinh chỉnh vì không tinh chỉnh trên Amazon.
- **Báo cáo LaTeX:** `24_report_v2.py` với Amazon ghi bảng và macro (`\ARes`, `\ASig`, ...) vào
  `content/tables/amazon/`, hình vào `media/figures/amazon/` — không đụng bảng của H&M. `--tuning-only` bị từ chối vì
  Amazon không có bước tinh chỉnh.
- **Gọi thẳng script (Git Bash):** thêm `NEUMF_CONFIG=configs/amazon.yaml` trước lệnh, ví dụ
  `NEUMF_CONFIG=configs/amazon.yaml python scripts/23_final_v2.py --dry-run --max-epochs 1`.

### 3.6 Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF

Theo góp ý của GVHD (baseline ba nhóm), nhóm học máy truyền thống có thêm một mô hình lai truyền thống: kết hợp
Content, UserKNN, ItemKNN (cấu hình đã chọn, giữ nguyên) theo mô hình lai trong chương 3 luận án của cô. Điểm từng thành
phần chuẩn hoá min–max trên tập ứng viên; thử 4 cách kết hợp — trung bình, max, min, tổng có trọng số học bằng hồi quy
logistic theo cặp — trên tập xác thực của mẫu phát triển. Kế hoạch đăng ký bổ sung: `audit/PREREG_bosung.md`; mã:
`src/baselines/hybrid.py`, `scripts/25_bosung.py`. Mô hình tất định, không cần GPU, chạy vài phút trên CPU.

```bash
python run.py bosung-tune                     # chọn cách kết hợp trên tập xác thực (H&M) -> audit/v2/bosung_*
python run.py bosung-dry-run                  # thử đường ống trên tập xác thực (không mở tập kiểm thử)
python run.py bosung-final --reason "..."     # chấm tập kiểm thử H&M một lần, rồi xuất lại bảng (24)
python run.py amazon-bosung-final --reason "..."   # như trên cho Amazon (cách kết hợp chọn trên H&M)
```

- **Khoá kiểm thử:** `PREREG_bosung.md` và hai tệp `audit/v2/bosung_*` phải được commit; tree sạch; mã băm mã nguồn trùng
  lúc chạy `bosung-tune` (H&M); nhật ký ghi `bosung_hybrid_hm` / `bosung_hybrid_amazon`, mỗi bộ dữ liệu một lần. Vì
  vậy sau khi commit, chạy `bosung-final` **trước** khi sửa file nào khác.
- **Nơi ghi:** `outputs/v2/final/bosung/`, `outputs/amazon/final/bosung/`. Các tệp của 14 mô hình đăng ký trước
  (`summary.csv`, `significance.csv`, `by_k.csv`, ...) không đổi; `24_report_v2.py` thêm Hybrid-CBCF (dấu †) vào bảng
  kết quả xếp theo ba nhóm, bảng theo K, bảng độ phủ, và ghi bảng kiểm định họ bổ sung `tab_*_sigbs.tex`.
- **Đối chiếu thành phần:** lần chấm bổ sung chấm lại Content, UserKNN, ItemKNN và so hạng của từng khách với lần
  đánh giá cuối. Tệp đặc trưng văn bản (`data/processed/hm/catalog_v2.npz`) không nằm trong git, mỗi máy tự dựng, nên
  Content có thể lệch nhẹ; UserKNN, ItemKNN phải trùng khớp.

## 4. Kiểm thử

```bash
pytest -q              # tests/ (108 test) — không cần dữ liệu thật
pytest demo/tests -q   # demo (14 test) — test nạp checkpoint bỏ qua khi chưa có dữ liệu và outputs/v2/final/seed42/
```

Ngày 14/10/2026, trên máy chỉ có CPU: `tests/` 108/108 qua; `demo/tests` 14/14 qua.

**Tái lập trên máy khác.** Mô hình không dùng vector văn bản (NeuMF, GMF, MLP, BPR-MF, UserKNN, ItemKNN, hai mô hình
phổ biến) cho đúng từng hạng đã lưu khi chấm lại, kể cả checkpoint tạo trên GPU chấm lại trên CPU. Vector văn bản thì
nằm trong tệp đặc trưng `data/processed/hm/catalog_v2.npz` (Amazon: `data/processed/amazon/catalog.npz`). Tệp này
không nằm trong git; mỗi máy tự dựng bằng TF-IDF và TruncatedSVD của scikit-learn, và phiên bản thư viện khác cho vector
khác. Vì vậy bốn mô hình có đặc trưng, Content và Hybrid-CBCF chỉ cho đúng hạng đã lưu khi dùng đúng tệp đặc trưng của
máy đã tạo kết quả. Muốn khớp tuyệt đối với đánh giá cuối, chép tệp này từ máy đã chạy đánh giá cuối. Demo đối chiếu
từng kết quả với hạng đã lưu và báo khi lệch (mục 5); test `test_metrics_match_per_user_file` kiểm tra điều đó.

## 5. Demo

```bash
python run.py demo     # http://localhost:8000
```

Dùng đúng các mô hình của đánh giá cuối, chỉ nạp checkpoint, không huấn luyện lại:
- H&M: `outputs/v2/final/seed42/`;
- Amazon Beauty: `outputs/amazon/final/seed42/`.

Chọn bộ dữ liệu trên thanh đầu trang. **Luôn có gợi ý:** khách chưa có trong dữ liệu đã học nhận 10 sản phẩm phổ biến
nhất (Most Popular, nhãn "Gợi ý phổ biến") thay cho lỗi; khách có lịch sử nhưng không có sản phẩm đích vẫn nhận gợi ý
của mô hình. K chọn được 5, 10, 15, 20. Chi tiết: `demo/README.md`.

## 6. Cấu trúc thư mục

```text
neumf_project/
├── configs/      v2.yaml (H&M), amazon.yaml (Amazon Beauty)
├── data/         raw/hm/ (3 file Kaggle), raw/amazon/, processed/ (mẫu, đặc trưng) — không commit
├── src/
│   ├── data_pipeline/   adapters/ (hm.py, amazon.py: đọc dữ liệu), gộp cặp, k-core, mẫu âm; features.py (đặc
│   │                    trưng, gộp theo product_code), protocol_v2.py (giai đoạn xác thực / kiểm thử),
│   │                    feature_dataset.py
│   ├── models/          neumf.py (GMF, MLP, NeuMF), late_fusion.py,
│   │                    hybrid_features.py (NeuMF-F, GMF-F, MLP-F, MostPopular-Recent, Content)
│   ├── baselines/       Random, Most Popular, BPR-MF, ItemKNN, UserKNN; hybrid.py (Hybrid-CBCF, bổ sung)
│   ├── training/        vòng lặp huấn luyện, dừng sớm
│   └── evaluation/      xếp hạng toàn bộ, độ đo; v2.py (chấm theo kế hoạch đánh giá)
├── scripts/      xem bảng dưới
├── audit/        bằng chứng thực nghiệm đã commit (bảng dưới)
├── outputs/      data/ (manifest dữ liệu đã lọc), v2/tuning/ (checkpoint tinh chỉnh), v2/final/ (kết quả H&M),
│                 amazon/ (dữ liệu đã lọc và kết quả Amazon)
├── demo/         web demo
├── tests/
└── run.py        lệnh tắt — python run.py -h
```

| Script | Việc |
|---|---|
| `00_sample_hm.py` | Lấy mẫu khách theo khối: `--block 0` mẫu phát triển, `--block 2` mẫu kiểm định |
| `21_build_features.py` | Danh mục sản phẩm (thuộc tính + vector văn bản), doanh số theo ngày (H&M) hoặc số đánh giá theo ngày (Amazon) |
| `02_prepare_data.py` | Gộp màu theo `product_code` (H&M), k-core trước mốc kiểm thử → file dữ liệu đã lọc + MD5 |
| `22_tune_v2.py` | Tinh chỉnh trên tập xác thực của mẫu phát triển → `audit/v2/` (chỉ H&M) |
| `23_final_v2.py` | Đánh giá cuối trên tập kiểm thử (có khoá kiểm thử); `--dry-run`: chạy thử |
| `24_report_v2.py` | Kiểm định, bảng theo K (`by_k.csv`), bảng, hình, macro LaTeX, `ket_qua.txt`; `--tuning-only`: chỉ bảng tinh chỉnh |
| `25_bosung.py` | Mô hình lai truyền thống bổ sung: `tune` (tập xác thực), `final` (tập kiểm thử, có khoá kiểm thử riêng) |
| `v2_common.py` | Nạp dữ liệu, dựng, huấn luyện, chấm mô hình — dùng chung cho 22, 23 và demo |
| `19_check_report.py` | Đối chiếu câu chữ báo cáo và tài liệu với số liệu của H&M và Amazon |

`audit/` gồm: `PREREG_v2.md` (kế hoạch H&M, bản cuối), `PREREG_amazon.md` (kế hoạch kiểm chứng Amazon),
`PREREG_bosung.md` (kế hoạch bổ sung: mô hình lai truyền thống), `v2/tuning_log.csv`, `v2/best_configs.json`,
`v2/data_dev.json` (tinh chỉnh), `v2/bosung_tuning_log.csv`, `v2/bosung_best_configs.json` (tinh chỉnh bổ sung),
`test_access_log.csv` (mọi lần mở tập
kiểm thử, kể cả của giai đoạn phát triển). Lịch sử: `PREREG.md` (giai đoạn phát triển ban đầu, mô hình chỉ dùng ID —
trong mã gọi là "v1"; báo cáo mục 4.6) và `PREREG_v2_cu.md` (bản đầu của kế hoạch đánh giá, đánh giá trên khối 1). Mã
nguồn và kết quả của hai giai đoạn này nằm trong lịch sử git: commit `9799f1a` (tag cục bộ `truoc-don-dep`). Code
đọc/ghi trực tiếp các file trong `audit/` — không sửa tay.
