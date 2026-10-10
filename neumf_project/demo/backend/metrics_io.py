"""Đọc file kết quả của scripts/24_report_v2.py (outputs/v2/final/) cho dashboard. Không tính lại, không có số mặc định:
thiếu file thì trả status "missing" kèm lệnh cần chạy."""
from __future__ import annotations

import json

import pandas as pd

from .data_context import PROJECT_ROOT, V2_DIR, V

RUN_CMD = 'python run.py v2-final --reason "..." (hoặc python run.py v2-report)'
BY_K_COLS = [f"{m}@{k}_mean" for m in ("NDCG", "Recall", "HR", "Precision") for k in (5, 10, 20)]


def _block(name: str, transform) -> dict:
    path = V2_DIR / name
    try:
        df = pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = None
    if df is None or df.empty:
        return {"status": "missing", "message": f"Chưa có dữ liệu — cần chạy {RUN_CMD}"}
    return {"status": "ok", "source": path.relative_to(PROJECT_ROOT).as_posix(),
            "data": json.loads(transform(df).to_json(orient="records"))}


def _named(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(model=df["model"].map(V.DISPLAY).fillna(df["model"]))


def _by_k(df: pd.DataFrame) -> pd.DataFrame:
    """Bảng "đánh giá theo K": các cột trung bình @5 / @10 / @20 có trong file, sắp theo NDCG@10."""
    return df[["model", *[c for c in BY_K_COLS if c in df.columns]]].sort_values("NDCG@10_mean", ascending=False)


def dashboard(ctx) -> dict:
    m = ctx.run_metadata
    return {
        "run_tag": ctx.run_tag, "dry_run": m["dry_run"],
        "summary": _block("summary.csv", _named),
        "by_k": _block("summary.csv", lambda df: _by_k(_named(df))),
        "significance": _block("significance.csv", lambda df: df.assign(A=df["A"].map(V.DISPLAY),
                                                                        B=df["B"].map(V.DISPLAY))),
        "beyond": _block("beyond.csv", _named),
        "ablation": _block("ablation.csv", lambda df: df),
        "stats": {"status": "ok", "source": (V2_DIR / "data.json").relative_to(PROJECT_ROOT).as_posix(), "data": {
            "n_users": ctx.n_users, "n_items": ctx.n_items, "n_interactions": m["n_kept_pairs"],
            "train_pairs": m["train_pairs"], "n_test_users": m["n_test_users"], "targets": m["targets"],
            "n_candidates": m["n_candidates"], "k_core": m["k_core"],
            "commit": str(m["provenance"].get("git_commit"))[:7]}},
    }
