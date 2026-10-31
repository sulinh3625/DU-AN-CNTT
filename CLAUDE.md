# Đồ án NeuMF-F (khuyến nghị lai MF + DNN có đặc trưng, H&M + Amazon Beauty)

Trả lời bằng tiếng Việt có dấu. Bối cảnh và số liệu: `README.md`, `tong_hop.md`; cách chạy: `neumf_project/README.md`.

## Lệnh (chạy từ `neumf_project/`, Python 3.12, thêm `PYTHONIOENCODING=utf-8` khi gọi thẳng script)
- Test: `python -m pytest -q -p no:cacheprovider` (khoảng 20 giây); demo: `python -m pytest demo/tests -q`
- Đối chiếu câu chữ báo cáo với số liệu: `python run.py check-report`
- Tính lại bảng/hình từ kết quả đã lưu (không mở tập kiểm thử): `python run.py v2-report` / `amazon-report`
- Demo: `python run.py demo` (localhost:8000). Ảnh trong `demo/static/images/` bị gitignore: Amazon tải bằng
  `demo/scripts/download_amazon_images.py`, H&M chép bằng `demo/scripts/copy_images.py` (cần `HM_IMAGES_DIR`)
- Sơ đồ (báo cáo, slide, `pipeline_neumf_5trang.drawio`): `cd image/src && python so_do_bao_cao.py` (cần draw.io desktop)
- Báo cáo: `Report DACNTT/compile.bat` (MiKTeX XeLaTeX + biber)

## Ranh giới
- Không push, không tạo hay đổi nhánh; chỉ commit cục bộ trên `main` khi được yêu cầu.
- Không tự chạy `v2-tune`, `v2-final`, `amazon-final`, `bosung-final` hay `23_final_v2.py`/`25_bosung.py final`: chúng
  mở tập kiểm thử (đã mở đúng một lần, ghi ở `audit/test_access_log.csv`) và chạy hàng giờ. Chỉ đưa lệnh cho người dùng.
- Không sửa `audit/PREREG*.md` đã commit; thay đổi kế hoạch ghi ở mục "lệch kế hoạch".
- Kết quả: LateFusion-F cao nhất trên cả hai bộ; NeuMF-F không vượt GMF-F. Không gọi NeuMF-F là mô hình tốt nhất.

## Quy ước báo cáo (`Report DACNTT/`)
- Mọi số trong báo cáo lấy từ macro do `scripts/24_report_v2.py` sinh ra, không gõ tay; sửa lời văn C1–C5 thì giữ các
  cụm từ mà `scripts/19_check_report.py` kiểm tra.
- Thuật ngữ: tiếng Việt kèm tiếng Anh in nghiêng ở lần đầu; *cold start* giữ tiếng Anh; "lớp" cho mạng nơ-ron, "tầng"
  chỉ cho demo; "hợp nhất sớm/muộn".
- Không ghi chú dưới bảng (giải thích trong đoạn văn); bảng/hình dùng `[H]`, đặt sau đoạn văn nói về nó; không phụ lục.
- Hình mô hình: chỉ NeuMF-F, ghi Top-K (không ghi một K cụ thể), không có đường cắt nhau.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
