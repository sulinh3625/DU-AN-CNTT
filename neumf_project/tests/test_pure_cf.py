"""R2 (thuần CF) + R4 (thống kê chỉ từ train) cho pipeline của giao thức v1 (lịch sử phát triển).

Giao thức v2 dùng đặc trưng sản phẩm/khách hàng có chủ đích (audit/PREREG_v2.md) — các module của v2 được liệt kê riêng
trong V2_FEATURE_FILES và kiểm tra không rò rỉ thời gian ở tests/test_v2.py; pipeline v1 vẫn phải thuần CF."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.common import build_adapter
from src.data_pipeline.preprocessing import apply_feedback_weights

ROOT = Path(__file__).resolve().parents[1]
MAIN_CONFIGS = ["configs/hm500k.yaml", "configs/hm500k_global.yaml"]
# Module chỉ dùng cho giao thức v2 (mô hình có đặc trưng) — được phép đọc articles.csv, customers.csv.
V2_FEATURE_FILES = {ROOT / "src" / "data_pipeline" / f for f in ("features.py", "protocol_v2.py", "feature_dataset.py")} | {
    ROOT / "src" / "models" / "hybrid_features.py", ROOT / "src" / "evaluation" / "v2.py"}
PIPELINE_FILES = sorted({*ROOT.joinpath("src").rglob("*.py"), *ROOT.joinpath("scripts").glob("0[1-6]_*.py"),
                         ROOT / "scripts" / "common.py", ROOT / "scripts" / "run_all.py"} - V2_FEATURE_FILES)
METADATA = re.compile(r"articles\.csv|customers\.csv|side_features|detail_desc|prod_name")
CF_BASELINES = {"random", "popularity", "bpr", "itemknn"}


@pytest.mark.parametrize("path", MAIN_CONFIGS)
def test_main_configs_are_pure_cf(path):
    raw = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    assert not {"side_features", "content", "hybrid"} & set(raw)
    assert set(raw["baselines"]["enabled"]) <= CF_BASELINES
    assert "transactions" in raw["dataset"]["raw_path"]


def test_training_and_evaluation_code_never_mentions_metadata_files():
    hits = [f"{p.relative_to(ROOT)}:{i}" for p in PIPELINE_FILES
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if METADATA.search(line)]
    assert hits == []


def test_v1_pipeline_does_not_import_v2_feature_modules():
    """Pipeline v1 (thuần CF) không import module đặc trưng của v2; các module v2 có tồn tại thật."""
    assert all(p.exists() for p in V2_FEATURE_FILES)
    names = re.compile(r"\b(features|protocol_v2|feature_dataset|hybrid_features)\b")
    hits = [f"{p.relative_to(ROOT)}:{i}" for p in PIPELINE_FILES
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if line.lstrip().startswith(("from ", "import ")) and names.search(line)]
    assert hits == []


@pytest.mark.parametrize("path", MAIN_CONFIGS)
def test_adapter_reads_only_transactions(path, monkeypatch):
    cfg, adapter = build_adapter(path)
    if not adapter.path.exists():
        pytest.skip(f"Chưa có {adapter.path} — chạy python run.py sample-hm")
    opened = []
    real = pd.read_csv
    monkeypatch.setattr(pd, "read_csv", lambda f, *a, **k: opened.append(str(f)) or real(f, *a, **k))
    events = adapter.load_events()
    assert opened and all("transactions" in f for f in opened)
    assert set(events.columns) == {"user_raw", "item_raw", "timestamp", "value_raw", "source_order"}


def test_confidence_weight_scale_fitted_on_train_only():
    train = pd.DataFrame({"value_sum": [1.0, 3.0]})
    val = pd.DataFrame({"value_sum": [2.0]})
    test_a = pd.DataFrame({"value_sum": [5.0]})
    test_b = pd.DataFrame({"value_sum": [5000.0]})
    tr_a, _, _, meta_a = apply_feedback_weights(train, val, test_a, "weighted_confidence")
    tr_b, _, _, meta_b = apply_feedback_weights(train, val, test_b, "weighted_confidence")
    assert meta_a["train_log_scale"] == meta_b["train_log_scale"] == pytest.approx(np.log1p(3.0))
    assert tr_a["sample_weight"].tolist() == tr_b["sample_weight"].tolist()


def test_popularity_statistics_in_03_use_train_df():
    src = (ROOT / "scripts" / "03_run_experiment.py").read_text(encoding="utf-8")
    for call in ("MostPopularBaseline(train_df", "define_head_items(train_df", "define_cold_users(train_df",
                 'item_popularity = train_df["item"]', "TrainDataset(\n        train_df"):
        assert call in src, call
