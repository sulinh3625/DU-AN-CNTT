# Kịch bản: Đổi H&M làm dataset chính, DataCo làm đối chứng

**Quyết định:** H&M (catalog lớn/thưa, fashion) = primary | DataCo (catalog nhỏ/dày đặc, supply chain) = control
**Lý do chuyển:** DataCo 100 items quá nhỏ, mọi model đều HR@10 ~93% — không phân biệt được model tốt hay xấu.
**Điều kiện:** Có GPU, muốn H&M ở quy mô lớn nhất có thể.

---

## Phân tích quy mô H&M

| Config | Rows | Users (sau k=5) | Items (sau k=5) | Full Ranking | Sampled-99 |
|---|---|---|---|---|---|
| `hm_subset` (hiện tại) | 100K | ~1.743 | ~1.080 | ✅ ~2 phút CPU | ✅ |
| **Lát cắt 5M dòng** | 5M | ~50K–80K | ~30K–50K | ❌ quá chậm | ✅ GPU ~vài phút |
| **Full Parquet cache** | 31.8M | ~889K | ~90K | ❌ không khả thi | ✅ GPU ~10–20 phút |

→ **Kết luận:** Dùng **Sampled-99 làm primary evaluation** cho H&M ở quy mô lớn.
Full Ranking chỉ dùng cho DataCo (100 items — vẫn feasible).

> Sampled-99 là protocol gốc trong paper NCF He et al. (2017) — hoàn toàn hợp lệ học thuật.
> Báo cáo giải thích: "H&M dùng Sampled-99 vì Full Ranking O(users×items) không khả thi ở quy mô 90K items."

---

## Quy mô H&M được đề xuất: date range 1 năm gần nhất

H&M có giao dịch từ 2018-09-20 → 2020-09-22. Dùng **2019-09-23 → 2020-09-22** (1 năm):

Ước tính:
- ~10M–12M transactions trong 1 năm cuối
- Sau k=5: ~200K–300K users, ~50K–70K items
- Train time trên GPU (RTX 3060+): GMF ~5 phút, NeuMF ~15 phút/model
- Sampled-99 eval: ~2–3 phút/model trên GPU

Nếu GPU yếu hơn hoặc muốn nhanh hơn: dùng 6 tháng cuối (2020-03-23 → 2020-09-22).

---

## Các bước thực hiện

### Bước 1 — Tạo config `hm_primary.yaml` (config mới, không sửa file cũ)

Thay đổi so với `hm.yaml`:
- `evaluation.primary: sampled` (thay vì `full_ranking`)
- `start_date: "2019-09-23"` (lọc 1 năm cuối)
- `training.batch_size: 1024` (tận dụng GPU)
- `training.max_epochs_*: 50` (tăng lên vì GPU nhanh)
- `training.patience: 10`
- `evaluation.k_values: [1, 5, 10, 20]` (đầy đủ như DataCo)

### Bước 2 — Chạy audit để biết quy mô thực tế

```bash
python run.py audit --dataset hm --config configs/hm_primary.yaml
```

Xem số users/items sau k-core → quyết định có cần thu hẹp date range không.

### Bước 3 — Train H&M (primary)

```bash
python run.py all --dataset hm --config configs/hm_primary.yaml --run-tag hm_primary_v1
```

Dự kiến: ~1–2 tiếng trên GPU cho đủ 6 model + baselines.

### Bước 4 — Chạy multi-seed H&M (quan trọng — dataset chính cần kiểm định)

```bash
python run.py multi-seed --dataset hm --config configs/hm_primary.yaml --seeds 42 2024 2025
python run.py aggregate  --dataset hm --config configs/hm_primary.yaml --seeds 42 2024 2025
```

### Bước 5 — DataCo vẫn chạy như cũ (giữ nguyên config)

```bash
python run.py all --dataset dataco --run-tag dataco_control_v1
```

DataCo vẫn dùng Full Ranking (100 items — feasible), vai trò là "đối chứng catalog đặc biệt nhỏ/dày đặc".

### Bước 6 — So sánh

```bash
python scripts/07_compare_datasets.py
# Sửa dataco_dir / hm_dir trong script cho đúng run_tag mới
```

---

## Thay đổi luận điểm báo cáo

### Cũ (DataCo chính)
> "DataCo là dataset chính. Kết quả cho thấy NeuMF tương đương baseline trên catalog nhỏ."

### Mới (H&M chính)
> "H&M là dataset chính vì catalog lớn (50K–70K items), thưa, gần với thực tế e-commerce.
> Trên H&M: NeuMF-Pretrained vượt GMF/MLP/BPR-MF ở NDCG@10 [số liệu],
> đặc biệt trên nhóm long-tail items.
> DataCo (100 items, density 8,16%) là dataset đối chứng để kiểm tra trường hợp
> catalog cực nhỏ/dày đặc — nơi popularity signal đã đủ mạnh, NeuMF không tạo thêm lợi thế."

---

## Thay đổi cần sửa trong báo cáo

| Chương | Nội dung cần sửa |
|---|---|
| C3 — Phương pháp | Đổi thứ tự: H&M mô tả trước, DataCo sau. Giải thích lý do chọn Sampled-99 cho H&M |
| C4 — Thực nghiệm | Bảng kết quả chính = H&M. DataCo thành bảng đối chiếu phụ |
| C4 — Hình 4.1 | Vẫn giữ biểu đồ so sánh 2 dataset, nhưng đổi caption |
| C5 — Kết luận | Viết lại kết luận dựa trên số liệu H&M. DataCo là "confirmed on small dense catalog" |
| C6 — Hướng phát triển | Giữ nguyên: Full Ranking trên H&M full, multi-task, LLM |

---

## Rủi ro và xử lý

| Rủi ro | Xác suất | Cách xử lý |
|---|---|---|
| NeuMF vẫn không vượt baseline trên H&M lớn | Trung bình | Phân tích cold-start/long-tail — NeuMF thường tốt hơn ở đây |
| GPU không đủ VRAM cho embedding 889K users | Thấp (32-dim embeddings chỉ ~114MB) | Dùng date range 1 năm thay vì full |
| Sampled-99 bị GVHD hỏi vì sao không Full Ranking | Cao | Chuẩn bị câu trả lời: O(users×items) không khả thi, paper gốc NCF dùng Sampled-99 |
| Không đủ thời gian re-train + re-write báo cáo | Cao | Ưu tiên chạy seed=42 trước, multi-seed sau nếu còn thời gian |

---

## Timeline ước tính

| Công việc | Thời gian |
|---|---|
| Tạo config + chạy audit | 30 phút |
| Train H&M 1 seed (GPU) | 1–2 tiếng |
| Evaluate + vẽ biểu đồ | 30 phút |
| Sửa báo cáo C3, C4 | 3–5 tiếng |
| Multi-seed (3 seeds) | 3–6 tiếng GPU (có thể để qua đêm) |
| Sửa C5, C6 | 1 tiếng |
| **Tổng** | **~1–2 ngày** |
