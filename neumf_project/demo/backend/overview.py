"""Dữ liệu cho trang "Kết quả đánh giá": đọc file kết quả của scripts/24_report_v2.py (cùng nguồn với bảng và macro số
liệu của báo cáo), không tính lại, không có số gõ tay. Câu trả lời cho ba câu hỏi nghiên cứu suy ra từ kết luận kiểm định
đã lưu, nên đổi theo dữ liệu."""
from __future__ import annotations

import json

import pandas as pd

from .data_context import PROJECT_ROOT

# Biến thể bóc tách -> nhãn hiển thị. Amazon không có thuộc tính khách: "bỏ thông tin khách" là bỏ đặc trưng thời gian
# của khách (audit/PREREG_amazon.md).
ABL_LABEL = {"neumf_f-time": "Bỏ đặc trưng thời gian", "neumf_f-user": "Bỏ thông tin khách hàng",
             "neumf_f-attr": "Bỏ thuộc tính sản phẩm", "neumf_f-text": "Bỏ mô tả văn bản",
             "neumf_f-iddrop": "Không bỏ ID ngẫu nhiên"}
ABL_LABEL_DATASET = {"amazon": {"neumf_f-user": "Bỏ đặc trưng thời gian của khách"}}
VERDICT = {"A tốt hơn": "A", "B tốt hơn": "B"}  # mọi kết luận khác: "=" (không khác biệt có ý nghĩa)


def _verdict(v: str) -> str:
    return VERDICT.get(str(v), "=")


def answers(pairs: list[dict]) -> list[dict]:
    """Ba câu hỏi nghiên cứu -> "yes" / "part" / "no", suy ra từ kết luận kiểm định NeuMF-F với từng mô hình."""
    v = {p["b"]: p["verdict"] for p in pairs if p["a"] == "neumf_f"}
    branches = [v.get("mlp_f"), v.get("gmf_f")]
    n_better = sum(x == "A" for x in branches)
    return [
        {"id": "features", "pairs": ["neumf"], "answer": "yes" if v.get("neumf") == "A" else "no"},
        {"id": "branches", "pairs": ["mlp_f", "gmf_f"],
         "answer": "yes" if n_better == 2 else "part" if n_better == 1 else "no"},
        {"id": "fusion", "pairs": ["late_f"], "answer": "yes" if v.get("late_f") == "A" else "no"},
    ]


def results(ctx) -> dict:
    d = ctx.results_dir
    bs = "bosung/" if (d / "bosung" / "summary.csv").exists() else ""
    summary = pd.read_csv(d / f"{bs}summary.csv")
    sig = pd.read_csv(d / "significance.csv")
    abl = pd.read_csv(d / "ablation.csv")
    info = json.loads((d / "data.json").read_text(encoding="utf-8"))
    test = info.get("test", info["val"])
    name = dict(zip(summary["model"], summary["name"]))

    models = [{"key": r["model"], "name": r["name"], "ndcg10": float(r["NDCG@10_mean"]), "hr10": float(r["HR@10_mean"]),
               "supplementary": bool(r.get("supplementary", False))}
              for _, r in summary.sort_values("NDCG@10_mean", ascending=False).iterrows()]
    pairs = [{"id": int(r["id"]), "a": r["A"], "b": r["B"], "a_name": name.get(r["A"], r["A"]),
              "b_name": name.get(r["B"], r["B"]), "rel": float(r["rel_diff"]), "p_holm": float(r["p_holm"]),
              "verdict": _verdict(r["verdict"])} for _, r in sig.iterrows()]
    labels = {**ABL_LABEL, **ABL_LABEL_DATASET.get(ctx.dataset, {})}
    ablation = [{"key": r["variant"], "label": labels.get(r["variant"], r["variant"]), "rel": float(r["rel"]),
                 "ci_low": float(r["ci_low"]), "ci_high": float(r["ci_high"]),
                 "unsure": bool(r["ci_low"] < 0 < r["ci_high"])}
                for _, r in abl[abl["variant"] != "neumf_f"].sort_values("rel").iterrows()]
    return {
        "dataset": ctx.dataset, "users": int(test["users"]), "targets": int(test["targets"]),
        "candidates": int(round(test["candidates_mean"])), "n_items": int(info["n_items"]),
        "seeds": int(summary["n_seeds"].max()), "test_start": ctx.run_metadata["test_start"],
        "models": models, "pairs": pairs, "answers": answers(pairs), "ablation": ablation,
        "ablation_seed": int(abl["seed"].iloc[0]),
        "source": [(d / f).relative_to(PROJECT_ROOT).as_posix()
                   for f in (f"{bs}summary.csv", "significance.csv", "ablation.csv", "data.json")],
    }
