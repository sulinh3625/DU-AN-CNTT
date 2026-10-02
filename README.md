# DU-AN-CNTT — NeuMF trên dữ liệu H&M

```text
DU-AN-CNTT/
├── neumf_project/      # Code, dữ liệu, kết quả, demo, notebook Colab
├── Report DACNTT/      # Báo cáo LaTeX (main.tex; biên dịch: compile.bat)
└── tai_lieu/           # Tài liệu tham khảo (PDF luận án của GVHD)
```

- Hướng dẫn chạy (máy local và Google Colab): [`neumf_project/README.md`](neumf_project/README.md)
- Chạy lại toàn bộ số liệu báo cáo: `cd neumf_project`, `python run.py preflight`, rồi
  `python run.py final --reason "..."` (README dự án, mục 5.2–5.3)
- Lý thuyết, phạm vi, phương pháp, kết quả: [`neumf_project/pham_vi_du_an.md`](neumf_project/pham_vi_du_an.md)
- Bằng chứng thực nghiệm (PREREG, tuning log, nhật ký truy cập test): [`neumf_project/audit/`](neumf_project/audit/)
- Demo (mô hình của đánh giá cuối, khách tương đồng UserKNN): [`neumf_project/demo/README.md`](neumf_project/demo/README.md)
- Chuẩn bị vấn đáp (trả lời 17 góp ý của giảng viên): [`van_dap.md`](van_dap.md)
