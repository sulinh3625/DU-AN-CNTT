# Implementation status — V2 refactor

## Đã triển khai

- Cây thư mục V2 tách data / source / configs / outputs / tests.
- Dataset adapter cho H&M.
- H&M guard: từ chối `transactions_train.xlsx` để tránh dùng file bị cắt bởi giới hạn Excel.
- Aggregate unique User-Item **trước** iterative k-core.
- K-core sensitivity audit.
- Temporal Leave-One-Out trên unique User-Item với deterministic tie-break.
- Assert không có overlap `(user,item)` giữa train/validation/test.
- Binary implicit feedback làm mặc định.
- Weighted confidence transform fit trên **train only**.
- Dynamic negative sampling không trả positive item.
- Training negative pool chỉ dùng train positives.
- Full-ranking evaluator chính + sampled-99 evaluator phụ.
- Tie handling deterministic.
- Early stopping theo configurable metric; default `NDCG@10`.
- MLP dropout lấy từ config.
- NeuMF scratch/pretrained dùng cùng optimizer/LR/budget ở controlled ablation.
- Long-tail định nghĩa theo head fraction từ **train set**.
- BPR-MF negative sampling an toàn, hyperparameter qua config.
- Unit tests bảo vệ methodology.

## Kiểm thử

`pytest -q` -> **15 tests passed**.

## Chưa triển khai trong phase này

- Optuna/fair hyperparameter tuning budget.
- Multi-seed aggregation + Wilcoxon report table tự động.
- Coverage/ARP integration vào bảng kết quả chính (module metric đã có).
- H&M S/M/L subset builder.
- Plot V2 mới.
