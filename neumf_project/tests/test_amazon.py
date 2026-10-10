"""Dữ liệu đối chứng Amazon Beauty (configs/amazon.yaml, audit/PREREG_amazon.md): adapter, đặc trưng, ngày tính từ
day0 của cấu hình, dữ liệu không có thông tin khách, lệnh amazon-* của run.py — trên file giả nhỏ."""
from __future__ import annotations

import gzip
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run  # noqa: E402
import v2_common as V  # noqa: E402
from src.data_pipeline.adapters.amazon import AmazonAdapter, build_features, category_path  # noqa: E402
from src.data_pipeline.features import save_catalog, save_daily_sales, to_day  # noqa: E402
from src.models.hybrid_features import ContentProfile, NeuMFF  # noqa: E402

spec = importlib.util.spec_from_file_location("prep", ROOT / "scripts" / "02_prepare_data.py")
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)

DAY0 = "2010-01-01"
VAL, TEST = "2010-03-01", "2010-04-01"


def _ts(day: str) -> int:
    return int(pd.Timestamp(day).timestamp())


def _write(tmp_path: Path) -> tuple[Path, Path]:
    """6 khách × 4 sản phẩm trước VAL, mỗi khách thêm 1 sản phẩm trong giai đoạn xác thực và 1 trong kiểm thử."""
    asins = ["B0D", "B0A", "B0C", "B0B"]
    rows = []
    for u in range(6):
        for k, a in enumerate(asins):
            rows.append(dict(reviewerID=f"U{u}", asin=a, overall=5.0, unixReviewTime=_ts(f"2010-01-{10 + u + k:02d}")))
    rows += [dict(reviewerID=f"U{u}", asin="B0E", overall=4.0, unixReviewTime=_ts("2010-03-05")) for u in range(3)]
    rows += [dict(reviewerID=f"U{u}", asin="B0E", overall=4.0, unixReviewTime=_ts("2010-04-05")) for u in range(3, 6)]
    reviews, meta = tmp_path / "reviews.json.gz", tmp_path / "meta.json.gz"
    with gzip.open(reviews, "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    metas = [{"asin": "B0A", "title": "Matte lipstick red", "description": "beauty product care",
              "categories": [["Beauty", "Makeup", "Lips", "Lipstick"]], "brand": "Acme", "price": 7.5,
              "imUrl": "http://x/a.jpg"},
             {"asin": "B0B", "title": "Face cream beauty product care", "categories": [["Other"], ["Beauty", "Skin Care", "Face"]],
              "price": 120.0},
             {"asin": "B0C", "title": "Shampoo beauty product care", "categories": [["Beauty", "Hair Care"]], "brand": "Acme"},
             {"asin": "B0E", "title": "Lipstick pink beauty product care", "categories": [["Beauty", "Makeup", "Lips", "Lipstick"]]}]
    with gzip.open(meta, "wt", encoding="utf-8") as f:  # dict Python (nháy đơn) như file gốc; B0D không có metadata
        f.writelines(repr(m) + "\n" for m in metas)
    return reviews, meta


def test_adapter_codes_asins_in_sorted_order(tmp_path):
    reviews, _ = _write(tmp_path)
    ev = AmazonAdapter(reviews).load_events()
    assert list(ev.columns) == ["user_raw", "item_raw", "timestamp", "value_raw", "source_order"]
    first = ev.iloc[0]  # U0 – B0D: asin thứ 4 theo thứ tự từ điển (A, B, C, D, E)
    assert (first["user_raw"], first["item_raw"], str(first["timestamp"].date())) == ("U0", 3, "2010-01-10")
    assert sorted(ev["item_raw"].unique()) == [0, 1, 2, 3, 4]


def test_features_catalog_and_daily_reviews(tmp_path):
    reviews, meta = _write(tmp_path)
    cat, ds, info = build_features(reviews, meta, DAY0, text_dim=2)
    assert info["asin"].tolist() == ["B0A", "B0B", "B0C", "B0D", "B0E"] and cat.article_ids.tolist() == [0, 1, 2, 3, 4]
    assert info.loc[1, ["category_1", "category_2"]].tolist() == ["Skin Care", "Face"]  # đường danh mục bắt đầu bằng Beauty
    assert info.loc[3, "title"] == "" and cat.cats[3].tolist() == [0, 0, 0, 0, 0]  # không có metadata -> không biết
    assert cat.cats[:, 4].tolist() == [2, 8, 0, 0, 0]  # giá 7,5 -> nhóm 5–10; 120 -> >= 100; thiếu -> 0
    assert cat.cats[0, 0] == cat.cats[2, 0] > 0 and cat.cats[1, 0] == 0  # cùng thương hiệu Acme; B0B thiếu
    assert cat.text.shape == (5, 2)
    assert ds.counts.sum() == 30 and ds.n_days == int(to_day(np.datetime64("2010-04-05"), DAY0)) + 1
    assert ds.counts[4, int(to_day(np.datetime64("2010-03-05"), DAY0))] == 3
    assert ds.first_day[0] == int(to_day(np.datetime64("2010-01-11"), DAY0))  # B0A: U0 đánh giá ngày 11/01
    with pytest.raises(ValueError, match="day0"):
        build_features(reviews, meta, "2010-02-01", text_dim=2)
    assert category_path({}) == ["", "", ""]


def test_load_data_amazon_config_without_customers(tmp_path):
    reviews, meta = _write(tmp_path)
    cat, ds, _ = build_features(reviews, meta, DAY0, text_dim=2)
    save_catalog(cat, tmp_path / "cat.npz")
    save_daily_sales(ds, tmp_path / "ds.npz")
    entry = prep.export(reviews, tmp_path / "reviews.csv.gz", TEST, 2, dataset="amazon", day0=DAY0)
    (tmp_path / "manifest.json").write_text(json.dumps({"reviews": entry}), encoding="utf-8")
    cfg = {**V.read_config(ROOT / "configs" / "amazon.yaml"), "data_dir": str(tmp_path), "day0": DAY0,
           "val_start": VAL, "test_start": TEST, "k_core": 2,
           "samples": {"dev": str(reviews), "holdout": str(reviews)},
           "features": {"catalog": str(tmp_path / "cat.npz"), "sales": str(tmp_path / "ds.npz"), "customers": None}}
    D = V.load_data("holdout", with_test=True, cfg=cfg)
    assert entry["before_test_start"]["products"] == 5 and entry["customers"] == 6
    assert (D.n_users, D.user_cats.shape, D.user_cards) == (6, (6, 0), [])
    assert D.meta["day0"] == DAY0 and D.meta["dataset"] == "amazon" and D.meta["content_onehot"] == [1, 2]
    assert D.val.cutoff == int(to_day(np.datetime64(VAL), DAY0))
    assert len(D.val.targets) == 0  # B0E chưa có cặp nào trước VAL: không là ứng viên, không là đáp án
    assert len(D.test.targets) == 3 and set(D.test.targets["user"]) == {3, 4, 5}
    # NeuMF-F không có thuộc tính khách: nhánh user chỉ còn đặc trưng thời gian; tắt thời gian thì không còn gì
    for flags in ({}, {"use_time": False}, {"use_user": False}):
        net = NeuMFF(D.n_users, D.n_id_items, D.item_cards, D.user_cards, D.item_text.shape[1], 8, 8,
                     **flags).attach(D.item_cats, D.item_text, D.item_cum, D.item_first_day, D.user_cats)
        out = net(torch.tensor([0, 1]), torch.tensor([0, 1]), torch.tensor([60, 61]), torch.zeros(2, 2))
        assert out.shape == (2,) and torch.isfinite(out).all()
    cp = V.score_fn("content", {"half_life": None}, D, D.test)
    assert cp.X.shape == (D.n_items, 2 + D.item_cards[1] + D.item_cards[2])  # one-hot danh mục cấp 1, cấp 2


def test_content_profile_uses_given_onehot_columns():
    text = np.eye(3, dtype=np.float32)
    cats = np.array([[1, 2], [1, 1], [2, 2]])
    train = pd.DataFrame({"user": [0], "item": [0], "day": [1]})
    cp = ContentProfile(text, cats, [3, 3], train, n_users=1, cutoff=2, onehot_cols=[1])
    assert cp.X.shape == (3, 6)
    s = cp.score_items(0, [1, 2])
    assert s[1] > s[0]  # sản phẩm 2 cùng giá trị cột 1 với sản phẩm đã mua


def test_run_amazon_commands_use_amazon_config(monkeypatch):
    ns = run.argparse.Namespace
    steps = run.cmd_all(ns(final=True, reason="đêm", command="amazon-all"))
    assert steps[:3] == [["scripts/21_build_features.py"], ["scripts/02_prepare_data.py"],
                         ["scripts/22_tune_v2.py", "--model", "all", "--resume"]]
    assert ["scripts/24_report_v2.py", "--final-dir", "outputs/amazon/dry_run", "--report-dir", ""] in steps
    assert steps[-2:] == [["scripts/23_final_v2.py", "--reason", "đêm"], ["scripts/24_report_v2.py"]]
    got = {}
    monkeypatch.setattr(run, "run_steps", lambda name, steps, config=None: got.setdefault(name, config) and 0)
    for cmd, cfg in (("amazon-report", "configs/amazon.yaml"), ("v2-report", "configs/v2.yaml")):
        monkeypatch.setattr(sys, "argv", ["run.py", cmd])
        with pytest.raises(SystemExit):
            run.main()
        assert got[cmd] == cfg
    assert run._show(["scripts/x.py"], "configs/amazon.yaml") == "NEUMF_CONFIG=configs/amazon.yaml python scripts/x.py"
