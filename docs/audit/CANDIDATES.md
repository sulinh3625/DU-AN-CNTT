# Ứng viên mô hình (Pha 3b, loop 10 — 27/09/2026)

Số đo thật bằng `docs/audit/measure_candidates.py` trên hm500k, chia theo mốc thời gian chung
(7.519 users × 10.345 items; train 201.801 cặp → 1.009.005 mẫu/epoch với 4 negative; 2.275 user validation),
GPU RTX 3050 Laptop 4 GB, batch 512, Adam 1e-3. **Chỉ dùng validation**, không chạm test.
Val NDCG@10 sau 1 epoch chỉ để chắc mô hình học được, không dùng để chọn.

| | Ứng viên | R2 thuần CF | R3 MF + DNN | 1 epoch | Full ranking val | GPU đỉnh | Rủi ro leakage | Quyết định |
|---|---|---|---|---|---|---|---|---|
| A | NeuMF tune đúng cách (d, negative_ratio, lr, weight_decay, dropout, pretrain α; BCE vs BPR loss) | Có (chỉ ID) | Đúng NCF | d=32: 6,3 s · d=64: 7,6 s | 3,4–3,9 s | 0,04–0,06 GB | Thấp: negative chỉ từ train positives (`TrainDataset`) | **Làm** — mô hình chính |
| B | Late fusion điểm MF đã tune + NeuMF, trọng số chọn trên val | Có (cả hai CF) | Lai MF + DNN ở mức điểm | = MF (iALS fit 0,6 s) + NeuMF | ≈ tổng hai thành phần | ≈ NeuMF | Trung bình: val vừa chọn siêu tham số thành phần vừa chọn trọng số → nêu rõ, không chạm test | **Làm** — rẻ nhất |
| C | DeepCF/CFNet: nhánh representation (tháp DMF, đầu vào = hàng/cột ma trận tương tác 0/1 từ train) + nhánh matching (MLP) | Có (vector tương tác xây chỉ từ train) | Lai MF + DNN (Deng et al. 2019) | 18,7 s (≈ 3× NeuMF) | 3,7 s (tính trước 2 tháp một lần) | 0,84 GB (ma trận R + Rᵀ trên GPU) | Trung bình: ma trận R PHẢI chỉ từ train; khi --final vẫn dùng R của train (mô hình không thấy val/test) | **Làm** — kiến trúc mới thứ nhất (≤ 2 cho phép) |
| — | ConvNCF | Có | Có | không đo | không đo | — | — | **Không làm**: tích ngoài d×d + CNN cho từng cặp → Full Ranking ~23 triệu cặp/lượt val quá đắt; nêu lý do trong báo cáo |

## Hệ quả cho ngân sách (Q4: 8 giờ GPU, 3 seed)
- Huấn luyện thuần rất rẻ (NeuMF 20 epoch ≈ 2–3 phút kể cả val mỗi epoch). Phần đắt trong `03_run_experiment.py` là
  overhead (resample negative bằng vòng lặp Python, đánh giá mọi baseline, long-tail, cold-start): smoke 1 epoch vẫn
  mất 18,5 phút (loop 6). → Tuning nên chạy bằng script nhẹ (1 mô hình + val), chỉ dùng 03 đầy đủ cho --final.
- Baseline cùng ngân sách: iALS (fit < 1 s), MostPopular (0 s), BPR-MF (vòng lặp numpy, vài phút/lần).
- Nhánh representation của C tăng ~0,8 GB GPU; vẫn dư trong 4 GB.

## Lưu ý đo
- Thời gian 1 epoch đo riêng vòng lặp tối ưu (không gồm resample negative và val mỗi epoch).
- Prototype CFNet ở `docs/audit/measure_candidates.py` (tháp rl [512, 64] như README DeepCF, nhánh ml [64,32,16,8]);
  bản đưa vào `src/models/` sẽ viết lại + test ở Pha 4 nếu PREREG giữ ứng viên C.
