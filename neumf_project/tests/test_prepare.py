"""Dữ liệu đã lọc của giao thức v2 (protocol_v2.prepare_pairs / build_from_pairs, scripts/02_prepare_data.py): gộp màu
theo product_code, ứng viên và đáp án chỉ gồm sản phẩm có cặp huấn luyện, xuất file tất định, đọc lại có kiểm MD5, dựng
từ file khớp với build_v2 dựng trực tiếp. Chỉ dùng dữ liệu tổng hợp nhỏ, mã sản phẩm dạng thật của H&M."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from scipy import sparse

from src.data_pipeline.features import Catalog, DailySales, group_by_product, product_code_of
from src.data_pipeline.protocol_v2 import build_from_pairs, build_v2, load_pairs, prepare_pairs
from src.evaluation.v2 import evaluate_v2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("prepare_data", ROOT / "scripts" / "02_prepare_data.py")
prep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prep)
V = prep.V

VAL, TEST, K = "2018-11-19", "2018-12-09", 2  # ngày 60 và 80 kể từ 2018-09-20


def _day(d: int) -> str:
    return str(np.datetime64("2018-09-20") + np.timedelta64(d, "D"))


def _hm_sample(path: Path, seed: int = 0) -> tuple[Catalog, DailySales]:
    """Ghi mẫu H&M giả (như transactions_train.csv): 40 khách, 26 mẫu × 2 màu, 100 ngày; mẫu cuối (109700) chỉ bán từ
    ngày 61 (trong cửa sổ xác thực); khách "zz" chỉ mua trong cửa sổ kiểm thử. Trả về catalog và doanh số theo
    article_id."""
    rng = np.random.default_rng(seed)
    articles = np.array([(108775 + 37 * p) * 1000 + c for p in range(26) for c in (15, 44)], dtype=np.int64)
    buys = [(int(rng.integers(0, 100)), f"u{u:02d}", int(rng.choice(articles[:-2])))
            for u in range(40) for _ in range(int(rng.integers(4, 16)))]
    buys += [(61 + u, f"u{u:02d}", int(articles[-1])) for u in range(6)] + [(95, "zz", int(articles[0]))] * 3
    pd.DataFrame([(_day(d), u, a, 0.01, 1) for d, u, a in buys],
                 columns=["t_dat", "customer_id", "article_id", "price", "sales_channel_id"]).to_csv(path, index=False)
    days = np.array([d for d, _, _ in buys])
    rows = np.searchsorted(articles, [a for _, _, a in buys])
    counts = sparse.csr_matrix((np.ones(len(buys), np.int32), (rows, days)), shape=(len(articles), 100))
    first = np.full(len(articles), 100, dtype=np.int64)
    np.minimum.at(first, rows, days)
    cats = rng.integers(1, 3, size=(len(articles), 11)).astype(np.int32)
    text = rng.random((len(articles), 4)).astype(np.float32)
    return Catalog(articles, cats, [3] * 11, text), DailySales(counts, first)


# ------------------------------------------------------------------ dựng dữ liệu
def test_prepare_pairs_merges_two_colours_into_one_pair():
    # khách u mua màu 044 ngày 9 (dòng đầu của file) rồi màu 015 ngày 3 -> một cặp (u, 108775), ngày mua đầu = 3
    ev = pd.DataFrame({"user_raw": ["u", "u", "v"], "item_raw": ["0108775044", "0108775015", "0108775015"],
                       "timestamp": pd.to_datetime([_day(9), _day(3), _day(5)]), "value_raw": 0.01,
                       "source_order": [0, 1, 2]})
    pairs = prepare_pairs(ev, TEST, 1, item_map=product_code_of)
    assert pairs.columns.tolist() == ["user_id", "item_id", "first_day", "in_kcore"]
    assert pairs[["user_id", "item_id", "first_day"]].values.tolist() == [["u", 108775, 3], ["v", 108775, 5]]
    assert len(prepare_pairs(ev, TEST, 1)) == 3  # không có item_map: mỗi màu là một sản phẩm


def test_candidates_and_targets_only_items_with_training_pairs(tmp_path):
    cat, sales = _hm_sample(tmp_path / "s.csv")
    data = build_v2(tmp_path / "s.csv", VAL, TEST, K, cat, sales, with_test=True)
    assert "zz" not in set(data.user_raw)  # khách chỉ mua trong cửa sổ kiểm thử không có trong dữ liệu
    assert data.n_items == data.n_id_items
    late = data.item_product == 109700  # có trong k-core nhưng chưa có cặp nào trước mốc xác thực
    assert late.sum() == 1 and not data.val.scoreable[late].any() and data.test.scoreable[late].all()
    for st in (data.val, data.test):
        has_train = np.zeros(data.n_items, dtype=bool)
        has_train[st.train["item"].to_numpy()] = True  # có ít nhất 1 cặp huấn luyện trước mốc cắt
        assert (st.train["day"] < st.cutoff).all() and np.array_equal(st.scoreable, has_train)
        assert not st.new.any() and np.array_equal(st.pool, np.flatnonzero(st.scoreable))
        assert st.records and st.scoreable[st.targets["item"].to_numpy()].all()
        for r in st.records:
            assert st.scoreable[r.candidates].all() and st.scoreable[r.positives].all()

    class ByIndex:
        def score_items(self, user, items):
            return np.asarray(items, dtype=float)

    res = evaluate_v2(ByIndex(), data.test.records, data.test.new)  # không có sản phẩm mới: _new là NaN, không lỗi
    assert np.isfinite(res["NDCG@10"]) and np.isnan(res["NDCG@10_new"]) and res["users_new"] == 0


# ------------------------------------------------------------- file dữ liệu
def test_export_twice_gives_same_bytes_and_md5(tmp_path):
    _hm_sample(tmp_path / "s.csv")
    out = [tmp_path / d / "mau.csv.gz" for d in ("a", "b")]
    entries = []
    for p in out:
        p.parent.mkdir()
        entries.append(prep.export(tmp_path / "s.csv", p, TEST, K))
    assert out[0].read_bytes() == out[1].read_bytes() and entries[0] == entries[1]
    b = entries[0]["before_test_start"]
    assert entries[0]["kcore_pairs"] > 0 and b["products"] < b["articles"] and b["product_pairs"] < b["article_pairs"]


def test_load_data_rejects_missing_file_and_md5_mismatch(tmp_path, monkeypatch):
    _hm_sample(tmp_path / "s.csv")
    monkeypatch.setattr(V, "DATA_DIR", tmp_path)
    monkeypatch.setattr(V, "MANIFEST", tmp_path / "manifest.json")
    with pytest.raises(SystemExit, match="run.py prepare"):  # chưa chạy prepare
        V.load_data("dev")
    name = V.data_name("dev")
    entry = {**prep.export(tmp_path / "s.csv", tmp_path / f"{name}.csv.gz", TEST, K),
             "k_core": V.CFG["k_core"], "test_start": V.CFG["test_start"]}
    with pytest.raises(ValueError, match="MD5"):
        load_pairs(tmp_path / f"{name}.csv.gz", "0" * 32)
    for bad in ({"md5": "0" * 32}, {"k_core": V.CFG["k_core"] + 1}):  # file bị sửa / manifest lọc với tham số khác
        (tmp_path / "manifest.json").write_text(json.dumps({name: {**entry, **bad}}), encoding="utf-8")
        with pytest.raises(SystemExit, match="run.py prepare"):
            V.load_data("dev")


def test_prepare_again_keeps_manifest_when_only_commit_differs(tmp_path, monkeypatch):
    _hm_sample(tmp_path / "s.csv")
    for attr, value in (("PROJECT_ROOT", tmp_path), ("DATA_DIR", tmp_path / "out"), ("MANIFEST", tmp_path / "m.json"),
                        ("CFG", {**V.CFG, "samples": {"dev": "s.csv"}, "test_start": TEST, "k_core": K})):
        monkeypatch.setattr(V, attr, value)
    monkeypatch.setattr(prep, "ARTICLES", tmp_path / "khong_co.csv")
    monkeypatch.setattr(sys, "argv", ["02_prepare_data.py"])

    def run(commit, dirty):
        monkeypatch.setattr(V, "provenance", lambda: {"git_commit": commit, "git_dirty": dirty})
        prep.main()
        return json.loads(V.MANIFEST.read_text(encoding="utf-8"))["s"]

    first, second = run("a", True), run("b", False)
    assert second == {**first, "git_commit": "b", "git_dirty": False}  # mục cũ từ mã chưa commit -> ghi lại
    assert run("c", True) == second  # chỉ khác commit -> giữ mục cũ: chạy lại không làm đổi manifest


def test_tune_refuses_log_from_other_data(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("tune_v2", ROOT / "scripts" / "22_tune_v2.py")
    tune = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tune)
    (tmp_path / "tuning_log.csv").write_text("model,params,code_hash\npopularity,{},abc\n",  # trước khi có data_md5
                                             encoding="utf-8")
    monkeypatch.setattr(tune, "CKPT", tmp_path / "ckpt")
    monkeypatch.setattr(V, "load_data", lambda *a, **k: SimpleNamespace(meta={"data_md5": "x"}))
    monkeypatch.setattr(sys, "argv", ["22_tune_v2.py", "--resume", "--log-dir", str(tmp_path)])
    with pytest.raises(SystemExit, match="1 dòng tinh chỉnh trên dữ liệu khác"):  # dừng trước khi bỏ qua / huấn luyện
        tune.main()


def test_data_from_file_matches_build_v2(tmp_path):
    cat, sales = _hm_sample(tmp_path / "s.csv")
    direct = build_v2(tmp_path / "s.csv", VAL, TEST, K, cat, sales, with_test=True)
    entry = prep.export(tmp_path / "s.csv", tmp_path / "mau.csv.gz", TEST, K)
    via = build_from_pairs(load_pairs(tmp_path / "mau.csv.gz", entry["md5"]), VAL, TEST, *group_by_product(cat, sales),
                           with_test=True)
    assert direct.user_raw.tolist() == via.user_raw.tolist()
    assert direct.item_product.tolist() == via.item_product.tolist()
    for a, b in ((direct.val, via.val), (direct.test, via.test)):
        pd.testing.assert_frame_equal(a.targets, b.targets)
        assert np.array_equal(a.scoreable, b.scoreable)
    assert (entry["customers"], entry["products"], entry["kcore_pairs"]) == (direct.n_users, direct.n_items,
                                                                           len(direct.kept))
