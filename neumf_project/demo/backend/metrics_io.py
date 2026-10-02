"""Đọc file kết quả đã chạy cho dashboard. Không tính lại, không có số mặc định:
thiếu file thì trả status "missing" kèm lệnh cần chạy."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .data_context import CONFIG_PATH, DEMO_ROOT, EXPERIMENTS_DIR, PROJECT_ROOT
from scripts.common import REPORT_HIDDEN_MODELS  # noqa: E402  (data_context đã thêm PROJECT_ROOT vào sys.path)

TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FINAL_DIR = PROJECT_ROOT / "outputs" / "final"
ARTIFACTS_DIR = DEMO_ROOT / "artifacts"
RANK_BIN_EDGES = [1, 2, 3, 5, 11, 21, 51, 101, 201, 501, 1001, 2001, 5001, 10001, 20001]
OFFLINE_CMD = "python demo/scripts/build_offline_artifacts.py"
TRAIN_CMD = "python run.py train"
CONFIG_NAME = Path(CONFIG_PATH).stem


def _rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _ok(path: Path, run_tag: str | None, data) -> dict:
    return {"status": "ok", "source": _rel(path), "run_tag": run_tag, "data": data}


def _missing(message: str, run_tag: str | None = None) -> dict:
    return {"status": "missing", "run_tag": run_tag, "message": f"Chưa có dữ liệu — cần chạy {message}"}


def _first_existing(*paths: Path) -> Path | None:
    return next((p for p in paths if p.exists()), None)


def _records(df: pd.DataFrame) -> list[dict]:
    if "model" in df.columns:
        df = df[~df["model"].isin(REPORT_HIDDEN_MODELS)]
    return json.loads(df.to_json(orient="records"))


def per_user_path(run_tag: str) -> Path | None:
    return _first_existing(TABLES_DIR / run_tag / "results_per_user.csv",
                           ARTIFACTS_DIR / run_tag / "results_per_user.csv")


def primary_results(run_tag: str) -> dict:
    path = _first_existing(TABLES_DIR / run_tag / "primary_results.csv",
                           EXPERIMENTS_DIR / run_tag / "results_primary.csv")
    if path is None:
        return _missing(TRAIN_CMD, run_tag)
    df = pd.read_csv(path, index_col=0).rename_axis("model").reset_index()
    return _ok(path, run_tag, _records(df))


def multi_seed_summary() -> dict:
    out_dir = TABLES_DIR / f"{CONFIG_NAME}_multiseed"
    path, meta_path = out_dir / "multi_seed_summary_primary.csv", out_dir / "multi_seed_meta_primary.json"
    cmd = "python run.py multi-seed rồi python run.py aggregate"
    if not path.exists() or not meta_path.exists():
        return _missing(cmd)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("config_name") != CONFIG_NAME:
        return _missing(f"{cmd} (file hiện có là của '{meta.get('config_name')}')")
    df = pd.read_csv(path).rename(columns={"method": "model"})
    return _ok(path, None, {"seeds": meta.get("seeds", []), "rows": _records(df)})


def beyond_accuracy(run_tag: str) -> dict:
    table = TABLES_DIR / run_tag / "beyond_accuracy.csv"
    if table.exists():
        df = pd.read_csv(table).rename(columns={
            "Model": "model", "Coverage@K": "coverage", "Novelty": "novelty",
            "Head Rec Rate": "head_rec_rate", "Avg Rec Popularity": "avg_rec_popularity",
        })
        return _ok(table, run_tag, _records(df[["model", "coverage", "novelty", "head_rec_rate", "avg_rec_popularity"]]))
    results = EXPERIMENTS_DIR / run_tag / "results.json"
    if results.exists():
        payload = json.loads(results.read_text(encoding="utf-8")).get("beyond_accuracy")
        if payload:
            rows = [{"model": m, "coverage": v["catalog_coverage"], "novelty": v["novelty"],
                     "head_rec_rate": v["head_rec_rate"], "avg_rec_popularity": v["avg_rec_popularity"]}
                    for m, v in payload.items() if m not in REPORT_HIDDEN_MODELS]
            return _ok(results, run_tag, rows)
    return _missing(TRAIN_CMD, run_tag)


def rank_distribution(run_tag: str) -> dict:
    path = per_user_path(run_tag)
    if path is None:
        return _missing(OFFLINE_CMD, run_tag)
    df = pd.read_csv(path, usecols=["model", "rank"])
    edges = [e for e in RANK_BIN_EDGES if e < df["rank"].max() + 1]
    edges.append(int(df["rank"].max()) + 1)
    labels = [str(a) if b - a == 1 else f"{a}–{b - 1}" for a, b in zip(edges[:-1], edges[1:])]
    series = {}
    for model, g in df[~df["model"].isin(REPORT_HIDDEN_MODELS)].groupby("model", sort=False):
        counts, _ = np.histogram(g["rank"], bins=edges)
        series[model] = {"counts": counts.tolist(), "median_rank": float(g["rank"].median()), "n_users": int(len(g))}
    return _ok(path, run_tag, {"bins": labels, "series": series})


def popularity_bias(run_tag: str) -> dict:
    path = ARTIFACTS_DIR / run_tag / "popularity_bias.csv"
    if not path.exists():
        return _missing(OFFLINE_CMD, run_tag)
    return _ok(path, run_tag, _records(pd.read_csv(path, dtype={"article_id": str})))


def data_stats(run_tag: str) -> dict:
    path = EXPERIMENTS_DIR / run_tag / "metadata.json"
    if not path.exists():
        return _missing(TRAIN_CMD, run_tag)
    meta = json.loads(path.read_text(encoding="utf-8"))
    keys = ["n_users", "n_items", "n_interactions", "train", "validation", "test", "k_core",
            "n_head_items", "n_head_test_users", "n_long_tail_test_users"]
    data = {k: meta.get(k) for k in keys}
    data["density"] = meta["n_interactions"] / (meta["n_users"] * meta["n_items"])
    return _ok(path, run_tag, data)


FINAL_RUN_CMD = 'python run.py final --reason "..."'


def _final_csv(name: str) -> tuple[Path, pd.DataFrame | None]:
    path = FINAL_DIR / name
    return path, (pd.read_csv(path) if path.exists() else None)


def final_dashboard(ctx) -> dict:
    """Dashboard chế độ final: đọc đúng các file kết quả của Chương 4 (outputs/final/), không tính lại."""
    out = {"mode": "final", "run_tag": ctx.run_tag}
    path, main = _final_csv("summary.csv")
    ext_path, ext = _final_csv("extension/summary.csv")
    if main is None:
        out["summary"] = _missing(FINAL_RUN_CMD)
    else:
        main = main.rename(columns={main.columns[0]: "model"}).assign(extension=False)
        if ext is not None:
            ext = ext.rename(columns={ext.columns[0]: "model"}).assign(extension=True)
            main = pd.concat([main, ext], ignore_index=True)
        out["summary"] = _ok(path, None, json.loads(main.sort_values("NDCG@10_mean", ascending=False)
                                                     .to_json(orient="records")))
    for key, name in (("significance", "significance.csv"), ("ext_significance", "extension/significance.csv")):
        p, df = _final_csv(name)
        out[key] = _missing(FINAL_RUN_CMD) if df is None else _ok(p, None, json.loads(df.to_json(orient="records")))
    p, st = _final_csv("stratified.csv")
    out["stratified"] = _missing(FINAL_RUN_CMD) if st is None else _ok(p, None, json.loads(
        st.groupby(["model", "subset"])["NDCG@10"].mean().unstack("subset").reset_index().to_json(orient="records")))
    for key, name in (("beyond", "beyond_accuracy.csv"), ("sampled", "sampled99.csv")):
        p, df = _final_csv(name)
        out[key] = _missing(FINAL_RUN_CMD) if df is None else _ok(p, None, json.loads(
            df.drop(columns=[c for c in ("seed", "n_cases") if c in df.columns]).groupby("model").mean()
            .reset_index().to_json(orient="records")))
    p, lat = _final_csv("latency.csv")
    out["latency"] = _missing(FINAL_RUN_CMD) if lat is None else _ok(p, None, json.loads(
        lat[["model", "p50_ms", "p95_ms", "mean_ms", "n_candidates_mean"]].to_json(orient="records")))
    m = ctx.run_metadata
    out["stats"] = {"status": "ok", "source": f"outputs/final/{ctx.run_tag.replace('final_', '')}/results.json",
                    "run_tag": ctx.run_tag, "data": {
                        "n_users": ctx.n_users, "n_items": ctx.n_items, "n_interactions": int(len(ctx.data_df)),
                        "density": len(ctx.data_df) / (ctx.n_users * ctx.n_items), "k_core": ctx.cfg.dataset.k_core,
                        "train": m["train"], "validation": m["validation"], "test": m["test"],
                        "train_val": m["train_val"], "n_test_users": m["n_test_users"],
                        "n_candidates": m["n_candidate_items"], "commit": str(m["provenance"].get("git_commit"))[:7]}}
    return out


def dashboard(run_tag: str) -> dict:
    return {
        "run_tag": run_tag,
        "primary": primary_results(run_tag),
        "multi_seed": multi_seed_summary(),
        "beyond": beyond_accuracy(run_tag),
        "rank_distribution": rank_distribution(run_tag),
        "popularity_bias": popularity_bias(run_tag),
        "stats": data_stats(run_tag),
    }
