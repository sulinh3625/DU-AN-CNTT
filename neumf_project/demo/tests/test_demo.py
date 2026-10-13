"""Chạy từ neumf_project/:  python -m pytest demo/tests -q

Test có fixture vctx nạp checkpoint seed 42 của đánh giá cuối (outputs/v2/final/) và dữ liệu thật; tự bỏ qua nếu chưa có.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from demo.backend import data_context, inference, metrics_io
from demo.backend.data_context import (SEED, V2_DIR, DataContext, product_table, user_table, v2_available,
                                      v2_data_mismatch)
from demo.backend.routes import filter_users, user_position, user_rows

TOL = 1e-6
# Mô hình không đọc tệp đặc trưng văn bản (data/processed/, mỗi máy tự dựng, không nằm trong git): hạng tính lại phải trùng
# hạng đã lưu ở mọi máy, kể cả checkpoint tạo trên GPU chấm lại trên CPU. Mô hình đọc tệp này (bốn mô hình có đặc trưng,
# Content, Hybrid-CBCF qua Content) chỉ trùng khi tệp giống máy đã chạy; tệp dựng bằng phiên bản thư viện khác cho vector
# văn bản khác, khi đó demo phải báo lệch và trả đúng số đã lưu.
TEXT_FREE = {"NeuMF", "GMF", "MLP", "BPR-MF", "UserKNN", "ItemKNN", "MostPopular", "MostPopular-Recent"}
V2_KEY = {"NeuMF-F": "neumf_f", "GMF-F": "gmf_f", "MLP-F": "mlp_f", "NeuMF": "neumf", "GMF": "gmf", "MLP": "mlp",
          "LateFusion-F": "late_f", "BPR-MF": "bpr", "UserKNN": "userknn", "ItemKNN": "itemknn",
          "MostPopular-Recent": "recent_pop", "Content": "content", "MostPopular": "popularity",
          "Hybrid-CBCF": "hybrid"}


@pytest.fixture(scope="module")
def vctx():
    """Checkpoint seed 42 của đánh giá cuối (outputs/v2/final/seed42)."""
    if not v2_available():
        pytest.skip("Chưa có outputs/v2/final/seed42 kèm checkpoint tạo từ file dữ liệu đã lọc hiện tại — chạy "
                    "scripts/23_final_v2.py")
    return DataContext(load_customers=False)


# ------------------------------------------------------------- khớp đánh giá cuối
def test_metrics_match_per_user_file(vctx):
    """Demo đối chiếu với outputs/v2/final/seed42/per_user.csv.gz (số của Chương 4) và, khi đã chấm bổ sung,
    bosung/per_user.csv.gz của mô hình lai truyền thống: số đã lưu trả kèm luôn đúng; hạng tính lại trùng số đã lưu (mô
    hình trong TEXT_FREE thì bắt buộc), hoặc demo báo lệch kèm lý do."""
    per = pd.read_csv(V2_DIR / f"seed{SEED}" / "per_user.csv.gz")
    bs = V2_DIR / "bosung" / "per_user.csv.gz"
    if bs.exists():  # scripts/25_bosung.py: mô hình tất định, một bản cho mỗi seed
        b = pd.read_csv(bs)
        per = pd.concat([per, b[b["seed"] == SEED]], ignore_index=True)
    per = per.set_index(["model", "user"])
    rng = np.random.default_rng(2)
    users = rng.choice(vctx.target_users, size=min(40, len(vctx.target_users)), replace=False)
    assert {"NeuMF-F", "NeuMF", "GMF-F", "MLP-F", "LateFusion-F", "BPR-MF"} <= set(vctx.available_models)
    for m in vctx.available_models:
        for u in users:
            res = inference.recommend(vctx, m, int(u), 10)
            out, fin = res["evaluation"], res["evaluation"]["final"]
            row = per.loc[(V2_KEY[m], int(u))]
            want = [int(x) for x in str(row["ranks"]).split(";")]
            assert out["n_candidates"] == row["n_candidates"]
            assert fin["ranks"] == want and abs(fin["metrics"]["NDCG@10"] - row["NDCG@10"]) <= TOL, (m, u)
            assert fin["match"] or m not in TEXT_FREE, (m, u, out["ranks"], want)
            if fin["match"]:
                assert out["ranks"] == want and abs(out["metrics"]["NDCG@10"] - row["NDCG@10"]) <= TOL, (m, u)
                assert res["note"] is None
            else:
                assert res["note"] == inference.MISMATCH_NOTE, (m, u)


def test_new_customer_gets_popular_list_instead_of_error(vctx, monkeypatch):
    """Khách không có trong dữ liệu đã học: luôn có gợi ý — danh sách Most Popular kèm nhãn, không báo lỗi 404."""
    from demo.backend import routes

    monkeypatch.setattr(routes, "_cache", {"hm": vctx})
    cid = "khach-moi-chua-co-trong-du-lieu"
    out = routes.recommend(cid, model="NeuMF-F", k=10, dataset="hm")
    assert out["fallback"] == "popular" and out["evaluation"] is None and len(out["items"]) == 10
    counts = [it["score"] for it in out["items"]]
    assert counts == sorted(counts, reverse=True)
    assert counts[0] == vctx.train_item_counts[vctx.scoreable_items].max()
    hist = routes.history(cid, dataset="hm")
    assert hist["is_new"] and hist["items"] == [] and hist["profile"]["customer_id"] == cid
    assert routes.neighbors(cid, dataset="hm")["neighbors"] == []
    assert 15 in vctx.k_values  # báo cáo dùng K = 5, 10, 15, 20


def test_customer_without_targets_gets_model_recommendations(vctx, monkeypatch):
    """Khách có lịch sử nhưng không mua món mới nào sau mốc: vẫn nhận gợi ý của mô hình, không có chỉ số để chấm."""
    from demo.backend import routes

    monkeypatch.setattr(routes, "_cache", {"hm": vctx})
    u = next(u for u in range(vctx.n_users) if u not in vctx.target_items)
    cid = str(vctx.customer_ids[u])
    out = routes.recommend(cid, model="NeuMF-F", k=10, dataset="hm")
    assert "fallback" not in out and out["evaluation"] is None and len(out["items"]) == 10
    shown = {it["item_idx"] for it in out["items"]}
    assert not shown & vctx.train_pos[u] and shown <= set(vctx.scoreable_items.tolist())
    prof = routes.history(cid, dataset="hm")["profile"]
    assert prof["train_count"] == len(vctx.train_pos[u]) and prof["n_targets"] == 0 and not prof["is_new"]


def test_history_is_training_data_before_cutoff(vctx):
    test_start = str(data_context.V.CFG["test_start"])
    for u in vctx.target_users[:300]:
        u = int(u)
        assert not set(vctx.target_items[u]) & vctx.train_pos[u]
        hist = vctx.history(u)
        assert {h["item_idx"] for h in hist} == vctx.train_pos[u]
        dates = [h["t_dat"] for h in hist]
        assert dates == sorted(dates) and all(d < test_start for d in dates)


def test_late_fusion_minmax_on_candidates(vctx):
    """Late fusion chuẩn hoá min-max trên tập ứng viên của khách, không phải trên toàn catalog."""
    u = int(vctx.target_users[0])
    rec = inference.eval_record(vctx, u)
    scores = inference.candidate_scores(vctx, "LateFusion-F", u, rec)
    assert len(scores) == len(rec.candidates) and scores.min() >= 0 and scores.max() <= 1


def test_neighbors_are_sorted_and_counted(vctx):
    u = int(vctx.target_users[5])
    nb = vctx.neighbors(u, 10)
    assert 0 < len(nb) <= 10
    sims = [n["similarity"] for n in nb]
    assert sims == sorted(sims, reverse=True)
    for n in nb:
        v = vctx.user2idx[n["customer_id"]]
        assert n["n_common"] == len(vctx.train_pos[u] & vctx.train_pos[v]) > 0
        assert {t["item_idx"] for t in n["bought_target"]} <= set(vctx.target_items[u])


def test_best_ranks_match_recommend(vctx):
    """Hạng dùng để lọc khách gợi ý trúng = đúng hạng mà màn Kiểm thử mô hình hiển thị cho từng khách."""
    users = vctx.target_users[:12]
    for m in ("GMF", "MostPopular", "LateFusion-F"):
        got = inference.best_ranks(vctx, m, users, chunk=5)
        assert got == {int(u): inference.recommend(vctx, m, int(u), 10)["evaluation"]["rank"] for u in users}, m


def test_dashboard_reads_result_files(vctx):
    d = metrics_io.dashboard(vctx)
    assert d["summary"]["status"] == "ok" and d["significance"]["status"] == "ok"
    assert {"NeuMF-F", "NeuMF", "UserKNN"} <= {r["model"] for r in d["summary"]["data"]}
    assert len(d["significance"]["data"]) == 10  # họ đăng ký trước, không trộn họ bổ sung
    assert d["stats"]["data"]["n_test_users"] == len(vctx.target_users)
    # Mô hình lai truyền thống chỉ hiện khi tập kiểm thử đã được chấm cho nó theo kế hoạch bổ sung (25_bosung.py)
    scored = (V2_DIR / "bosung" / "results.json").exists()
    assert ("Hybrid-CBCF" in vctx.available_models) == scored
    assert (d["significance_bs"] is not None) == (V2_DIR / "bosung" / "summary.csv").exists()
    if d["significance_bs"] is not None:
        assert len(d["significance_bs"]["data"]) == 2


def test_results_from_other_data_are_refused(tmp_path, monkeypatch):
    """Kết quả tạo từ dữ liệu khác file đã lọc hiện tại (thiếu / lệch data_md5) không được nạp: demo không dựng tập
    kiểm thử của mẫu kiểm định cho một kết quả cũ."""
    V = data_context.V
    (tmp_path / "seed42").mkdir()
    (tmp_path / "seed42" / "results.json").write_text(json.dumps({"evaluated_on": "test"}), encoding="utf-8")
    (tmp_path / "manifest.json").write_text(json.dumps({V.data_name("holdout"): {"md5": "abc"}}), encoding="utf-8")
    monkeypatch.setattr(V, "MANIFEST", tmp_path / "manifest.json")
    for data_md5, usable in ((None, False), ("xyz", False), ("abc", True)):
        (tmp_path / "data.json").write_text(json.dumps({"data_md5": data_md5}), encoding="utf-8")
        assert (v2_data_mismatch(tmp_path, 42) is None) == usable, data_md5


# ------------------------------------------------------------- sản phẩm theo product_code
def test_product_table_uses_first_variant_and_counts_colours():
    arts = pd.DataFrame({"article_id": ["0108775051", "0108775015", "0110065001"],
                         "product_code": [108775, 108775, 110065],
                         "prod_name": ["Strap top (2)", "Strap top", "OP T-shirt"],
                         "product_type_name": ["Vest top", "Vest top", "Bra"]})
    df = product_table(arts, np.array([110065, 108775, 999999]))
    assert df["article_id"].tolist() == ["0110065001", "0108775015", "Unknown"]  # biến thể có article_id nhỏ nhất
    assert df["prod_name"].tolist() == ["OP T-shirt", "Strap top", "Unknown"]
    assert df["n_colours"].tolist() == [1, 2, 0]


# ------------------------------------------------------------- danh sách chọn khách (Admin)
def _users() -> pd.DataFrame:
    """5 khách, khách gh05 không có sản phẩm đích; mua nhiều nhất: ab01 đồ nữ 2/3, bf04 đồ nữ 2/4."""
    days = (1, 5, 3, 2, 2, 9, 1, 2, 3, 4, 1)
    train = pd.DataFrame({"user": [0, 0, 0, 1, 1, 2, 3, 3, 3, 3, 4], "item": [0, 1, 2, 0, 3, 3, 0, 1, 2, 3, 0],
                          "date": pd.to_datetime([f"2020-01-0{d}" for d in days])})
    articles = pd.DataFrame({"index_group_name": ["Ladieswear", "Ladieswear", "Menswear", "Divided"]})
    ids = np.array(["ab01", "ab02", "cd03", "bf04", "gh05"], dtype=object)
    return user_table(ids, {0: [3], 1: [1, 2], 2: [0], 3: [5, 6, 7]}, train, articles, pd.Series({0: 31.0, 3: 22.0}))


def test_user_table_counts_area_age_and_buckets():
    df = _users()
    assert df.index.tolist() == ["ab01", "ab02", "cd03", "bf04"]
    assert df["train_count"].tolist() == [3, 2, 1, 4] and df["n_targets"].tolist() == [1, 2, 1, 3]
    assert (df.loc["ab01", "area"], df.loc["ab01", "area_share"]) == ("Ladieswear", round(2 / 3, 3))
    assert (df.loc["ab01", "first_date"], df.loc["ab01", "last_date"]) == ("2020-01-01", "2020-01-05")
    assert df.attrs["thresholds"] == (2.0, 3.0) and df["bucket"].tolist() == ["mid", "low", "low", "high"]
    assert user_rows(df.loc[["ab01", "ab02"]])[0]["age"] == 31 and user_rows(df.loc[["ab02"]])[0]["age"] is None


def test_filter_users_search_sort_and_position():
    df = _users()
    assert filter_users(df, " B")["customer_id"].tolist() == ["bf04", "ab01", "ab02"]  # khớp ở đầu xếp trước
    assert filter_users(df, sort="train_asc")["customer_id"].tolist() == ["cd03", "ab02", "ab01", "bf04"]
    assert filter_users(df, bucket="low", sort="id")["customer_id"].tolist() == ["ab02", "cd03"]
    assert filter_users(df, area="Ladieswear")["customer_id"].tolist() == ["bf04", "ab01"]
    full = filter_users(df)  # mua nhiều nhất trước: bf04, ab01, ab02, cd03
    pos = user_position(full, "ab01")
    assert (pos["index"], pos["total"]) == (1, 4)
    assert (pos["prev"]["customer_id"], pos["next"]["customer_id"]) == ("bf04", "ab02")
    assert user_position(full, "bf04")["prev"] is None and user_position(full, "cd03")["next"] is None
    out = user_position(filter_users(df, bucket="high"), "ab01")  # ngoài bộ lọc: "sau" = khách đầu danh sách
    assert out["index"] is None and out["prev"] is None and out["next"]["customer_id"] == "bf04"
    ranks = pd.Series({"ab01": 3, "ab02": 25, "cd03": 10, "bf04": 11})  # hạng món đích tốt nhất của một mô hình
    assert filter_users(df, best_rank=ranks, hit="hit", k=10, sort="rank")["customer_id"].tolist() == ["ab01", "cd03"]
    assert filter_users(df, best_rank=ranks, hit="miss", k=20)["customer_id"].tolist() == ["ab02"]
    assert filter_users(df, best_rank=ranks)["best_rank"].tolist() == [11, 3, 25, 10]  # không lọc: chỉ thêm cột


# ------------------------------------------------------------- Amazon Beauty (dữ liệu đối chứng)
def test_amazon_table_maps_metadata_to_item_columns():
    items = pd.DataFrame({"asin": ["B01", "B02", "B03"], "title": ["Lip balm", None, "Serum"],
                          "brand": ["Acme", None, ""], "category_1": ["Makeup", "Skin Care", None],
                          "category_2": ["Lips", "Face", None], "category_3": ["Lip Balm", None, None],
                          "price": [3.5, None, 20.0], "imUrl": ["http://x/1.jpg", None, ""]},
                         index=pd.Index([0, 1, 2], name="item"))
    df = data_context.amazon_table(items, np.array([2, 0, 1]))
    assert df["article_id"].tolist() == ["B03", "B01", "B02"]
    assert df["prod_name"].tolist() == ["Serum", "Lip balm", "B02"]  # thiếu tên -> asin
    assert df["product_type_name"].tolist() == ["Beauty", "Lip Balm", "Face"]  # danh mục sâu nhất có giá trị
    assert df["index_group_name"].tolist() == ["Khác", "Makeup", "Skin Care"]  # khu vực = danh mục cấp 1
    assert df["subtitle"].tolist() == ["Beauty · $20.00", "Acme · Lip Balm · $3.50", "Face"]
    assert df["image_url"].tolist() == ["", "http://x/1.jpg", ""]


def test_dataset_without_final_results_reports_command_not_training(tmp_path, monkeypatch):
    """Chưa có kết quả đánh giá cuối Amazon: demo báo lệnh cần chạy (HTTP 503), không dựng dữ liệu, không huấn luyện."""
    from fastapi import HTTPException

    from demo.backend import routes

    monkeypatch.setitem(data_context.CONFIGS["amazon"], "out_dir", str(tmp_path))
    monkeypatch.setattr(routes, "_cache", {})
    why = data_context.unavailable_reason("amazon")
    assert "amazon-final" in why and not data_context.v2_available(dataset="amazon")
    with pytest.raises(HTTPException) as e:
        routes.ctx("amazon")
    assert e.value.status_code == 503 and "amazon-final" in e.value.detail
    listed = {d["key"]: d for d in routes.datasets()}
    assert listed["amazon"]["label"] == "Amazon Beauty" and listed["amazon"]["reason"] == why
