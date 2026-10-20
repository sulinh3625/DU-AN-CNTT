from __future__ import annotations

import json
import os
from html import escape
from threading import Lock, Thread
from typing import Literal

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response

from . import inference, metrics_io, overview
from .data_context import DATASETS, DEMO_ROOT, DataContext, unavailable_reason

IMAGES_DIR = os.environ.get("DEMO_IMAGES_DIR", str(DEMO_ROOT / "static" / "images"))
BUCKET_LABELS = {"low": "Ít giao dịch", "mid": "Trung bình", "high": "Nhiều giao dịch"}
# Thứ tự danh sách chọn khách: khoá -> (cột, tăng dần?); hoà thì theo customer_id để thứ tự luôn tất định.
SORTS = {
    "train_desc": (["train_count", "customer_id"], [False, True]),
    "train_asc": (["train_count", "customer_id"], [True, True]),
    "targets_desc": (["n_targets", "train_count", "customer_id"], [False, False, True]),
    "id": (["customer_id"], [True]),
    "rank": (["best_rank", "train_count", "customer_id"], [True, False, True]),  # hạng món đích tốt nhất của mô hình
}
Bucket = Literal["low", "mid", "high"]
Sort = Literal["train_desc", "train_asc", "targets_desc", "id", "rank"]
Hit = Literal["hit", "miss"]
Dataset = Literal["hm", "amazon"]  # mọi API nhận ?dataset=, mặc định H&M

router = APIRouter(prefix="/api")
_cache: dict[str, DataContext] = {}  # bộ dữ liệu -> dữ liệu và mô hình đã nạp (nạp lần đầu khi cần)
_ranks: dict[tuple[str, str], pd.Series] = {}  # (bộ dữ liệu, mô hình) -> hạng tốt nhất theo customer_id
_ctx_lock = Lock()
_ranks_lock = Lock()  # ponytail: một khoá chung, hai mô hình không chấm song song — đủ cho demo một người xem


def ctx(dataset: str = "hm") -> DataContext:
    with _ctx_lock:  # các request đầu đến cùng lúc: chỉ nạp một lần
        if dataset not in _cache:
            why = unavailable_reason(dataset)
            if why:  # chưa có kết quả đánh giá cuối: báo lệnh cần chạy, không huấn luyện gì
                raise HTTPException(503, why)
            c = DataContext(dataset=dataset)
            # Dựng bảng khách trước khi có luồng nền: cached_property không có khoá, hai luồng cùng dựng thì pandas
            # đôi khi báo "cannot reindex on an axis with duplicate labels" (500 ở lần mở trang đầu).
            c.users
            _cache[dataset] = c
            warm_example(dataset)
    return _cache[dataset]


def _user(c: DataContext, customer_id: str) -> int | None:
    """Mã nội bộ của khách; None = khách chưa có trong dữ liệu đã học (khách mới, hoặc quá ít lần mua để qua lọc k-core)
    — demo gợi ý sản phẩm phổ biến cho khách này thay vì báo lỗi (báo cáo, Thuật toán suy diễn Top-K)."""
    try:
        return c.resolve_user(customer_id)
    except KeyError:
        return None


NEW_CUSTOMER_NOTE = ("Khách chưa có trong dữ liệu đã học (khách mới, hoặc chưa đủ lần mua để qua lọc k-core): chưa có "
                     "lịch sử để cá nhân hoá, hệ thống gợi ý sản phẩm phổ biến.")


def user_profile(c: DataContext, u: int | None, customer_id: str) -> dict:
    """Hồ sơ khách cho thanh khách của màn hình Admin: dòng của bảng khách có sản phẩm đích; khách có lịch sử nhưng không
    có sản phẩm đích thì dựng các cột tương tự từ lịch sử; khách mới thì chỉ có mã và cờ is_new."""
    empty = dict(customer_id=customer_id.strip(), train_count=0, n_targets=0, area=None, area_share=None, age=None,
                 first_date=None, last_date=None, bucket=None)
    if u is None:
        return {**empty, "is_new": True}
    cid = str(c.customer_ids[u])
    if cid in c.users.index:
        return {**user_rows(c.users.loc[[cid]])[0], "is_new": False}
    rows = c.train_df[c.train_df["user"] == u]
    areas = pd.Series(c.articles["index_group_name"].to_numpy()[rows["item"].to_numpy()]).value_counts()
    age = c.user_age.get(u) if len(c.user_age) else None
    return {**empty, "customer_id": cid, "is_new": False, "train_count": int(len(rows)),
            "area": str(areas.index[0]) if len(areas) else None,
            "area_share": round(float(areas.iloc[0] / areas.sum()), 3) if len(areas) else None,
            "age": None if age is None or pd.isna(age) else float(age),
            "first_date": str(rows["date"].min().date()) if len(rows) else None,
            "last_date": str(rows["date"].max().date()) if len(rows) else None}


def filter_users(df: pd.DataFrame, q: str = "", bucket: str | None = None, area: str | None = None,
                 sort: str = "train_desc", best_rank: pd.Series | None = None, hit: str | None = None,
                 k: int = 10) -> pd.DataFrame:
    """Lọc và sắp bảng khách (DataContext.users): customer_id chứa q (không phân biệt hoa thường, khớp ở đầu xếp
    trước), nhóm giao dịch, khu vực mua nhiều nhất; có best_rank (hạng món đích tốt nhất của một mô hình, index
    customer_id) thì thêm cột best_rank và lọc hit = có món đích trong top-k / miss = không có."""
    q = q.strip().lower()
    if bucket:
        df = df[df["bucket"] == bucket]
    if area:
        df = df[df["area"] == area]
    if best_rank is not None:
        df = df.assign(best_rank=best_rank.reindex(df.index).to_numpy())
        if hit:
            df = df[(df["best_rank"] <= k) == (hit == "hit")]
    cols, asc = SORTS[sort if sort != "rank" or "best_rank" in df else "train_desc"]
    if q:
        df = df[df["customer_id"].str.lower().str.contains(q, regex=False)]
        df = df.assign(_later=~df["customer_id"].str.lower().str.startswith(q))
        cols, asc = ["_later", *cols], [True, *asc]
    return df.sort_values(cols, ascending=asc).drop(columns="_later", errors="ignore")


def best_rank_series(c: DataContext, model: str) -> pd.Series:
    """Hạng món đích tốt nhất của mô hình cho mọi khách (index customer_id) — chấm một lần (vài giây) rồi giữ lại."""
    key = (c.dataset, model)
    with _ranks_lock:
        if key not in _ranks:
            r = inference.best_ranks(c, model)
            _ranks[key] = pd.Series(list(r.values()), index=c.customer_ids[list(r)].astype(str))
    return _ranks[key]


def user_filter(q: str = "", bucket: Bucket | None = None, area: str | None = None, sort: Sort = "train_desc",
                model: str | None = None, hit: Hit | None = None, k: int = 10, dataset: Dataset = "hm") -> dict:
    """Tham số lọc chung của danh sách chọn khách; model + k chỉ dùng khi lọc hit / sắp theo hạng (sort=rank)."""
    return dict(q=q, bucket=bucket, area=area, sort=sort, model=model, hit=hit, k=k, dataset=dataset)


def _filtered(f: dict) -> pd.DataFrame:
    c = ctx(f["dataset"])
    ranks = None
    if f["hit"] or f["sort"] == "rank":
        model = f["model"] or c.available_models[0]
        if model not in c.available_models:
            raise HTTPException(404, f"Model '{model}' không khả dụng.")
        if f["k"] not in c.k_values:
            raise HTTPException(400, f"K phải thuộc {c.k_values}.")
        ranks = best_rank_series(c, model)
    return filter_users(c.users, f["q"], f["bucket"], f["area"], f["sort"], ranks, f["hit"], f["k"])


def user_rows(df: pd.DataFrame) -> list[dict]:
    """Dòng của bảng khách dạng JSON (tuổi thiếu -> null)."""
    return json.loads(df.to_json(orient="records"))


def user_position(df: pd.DataFrame, customer_id: str) -> dict:
    """Vị trí (từ 0) của khách trong danh sách đã lọc, kèm khách liền trước / liền sau; khách ngoài danh sách thì
    "liền sau" là khách đầu danh sách."""
    hit = np.flatnonzero(df["customer_id"].to_numpy() == customer_id.strip())
    i = int(hit[0]) if len(hit) else None

    def at(j: int) -> dict | None:
        return user_rows(df.iloc[[j]])[0] if 0 <= j < len(df) else None

    if i is None:
        return {"index": None, "total": len(df), "prev": None, "next": at(0)}
    return {"index": i, "total": len(df), "prev": at(i - 1), "next": at(i + 1)}


@router.get("/health")
def health():
    return {"status": "ok", "loaded": bool(_cache)}


@router.get("/datasets")
def datasets():
    """Bộ dữ liệu của demo và đã nạp được chưa (chỉ kiểm file kết quả, không dựng dữ liệu)."""
    return [{"key": k, "label": d["label"], "reason": unavailable_reason(k)} for k, d in DATASETS.items()]


def has_images(dataset: str) -> bool:
    """Có ảnh sản phẩm thật không: Amazon lấy ảnh theo imUrl gốc; H&M cần thư mục ảnh đã chép (copy_images.py)."""
    return dataset == "amazon" or (os.path.isdir(IMAGES_DIR) and any(os.scandir(IMAGES_DIR)))


@router.get("/context")
def context(dataset: Dataset = "hm"):
    return {**ctx(dataset).summary(), "has_images": has_images(dataset)}


@router.post("/reload")
def reload(dataset: Dataset = "hm"):
    _cache.clear()
    _ranks.clear()
    _examples.clear()
    return {"run_tag": ctx(dataset).run_tag}


@router.get("/results")
def results(dataset: Dataset = "hm"):
    """Trang "Kết quả đánh giá": mô hình, kiểm định, bóc tách và câu trả lời cho ba câu hỏi, đọc từ file kết quả."""
    try:
        return overview.results(ctx(dataset))
    except FileNotFoundError as e:
        cmd = DATASETS[dataset]["final_cmd"].replace("final", "report")
        raise HTTPException(503, f"Thiếu file kết quả ({e.filename}) — chạy python run.py {cmd}.") from e


_examples: dict[str, dict] = {}  # bộ dữ liệu -> khách ví dụ của trang Tổng quan (chọn một lần)


def pick_example(c: DataContext, a: str = "NeuMF-F", b: str = "NeuMF", k: int = 10) -> dict | None:
    """Khách ví dụ cho trang Tổng quan, chọn theo dữ liệu chứ không gõ tay: trong các khách mà a gợi ý trúng còn b trượt
    (theo hạng đã lưu, xếp theo chênh hạng), lấy khách có nhiều món đích nhất trong top-k của a, lịch sử 6–40 món, mọi
    sản phẩm có loại rõ, và hạng tính lại của cả hai mô hình trùng hạng đã lưu ở đánh giá cuối."""
    # Ứng viên lấy từ hạng đã lưu (per_user.csv.gz) thay vì chấm lại mọi khách: a trúng, b trượt, chênh hạng lớn trước.
    # Từng ứng viên vẫn được tính lại thật và chỉ nhận khi hạng tính lại trùng hạng đã lưu (điều kiện match bên dưới).
    df = c.users.assign(best_rank=saved_best_series(c, a).reindex(c.users.index).to_numpy(),
                        rank_b=saved_best_series(c, b).reindex(c.users.index).to_numpy())
    df = df[(df["best_rank"] <= k) & (df["rank_b"] > k) & df["train_count"].between(6, 40)]
    df = df.assign(_gap=df["rank_b"] - df["best_rank"]).sort_values(["_gap", "customer_id"], ascending=[False, True])
    best = None
    for row in user_rows(df.drop(columns="_gap").head(200)):
        u = c.resolve_user(row["customer_id"])
        ra, rb = inference.recommend(c, a, u, k), inference.recommend(c, b, u, k)
        if not all(r["evaluation"] and r["evaluation"]["final"] and r["evaluation"]["final"]["match"] for r in (ra, rb)):
            continue
        if any(str(it["product_type_name"]).lower() == "unknown" for it in ra["items"] + rb["items"]):
            continue
        hits = sum(it["is_target"] for it in ra["items"])
        if best is None or hits > best[0]:
            best = (hits, row, ra, rb)
        if hits >= 2 and hits == len(ra["targets"]):  # mọi món khách mua sau đó đều lọt top-k: không cần tìm tiếp
            break
    if best is None:
        return None
    _, row, ra, rb = best
    hist = history(row["customer_id"], dataset=c.dataset)
    return {"customer_id": row["customer_id"], "profile": hist["profile"], "history": hist["items"], "k": k,
            "model_a": a, "model_b": b, "a": ra, "b": rb}


_example_lock = Lock()


@router.get("/example")
def example(dataset: Dataset = "hm"):
    """Khách ví dụ của trang Tổng quan. Lần đầu phải chấm mọi khách với hai mô hình (vài chục giây trên CPU) nên được
    tìm sẵn ở luồng nền ngay khi nạp dữ liệu (warm_example); sau đó giữ lại."""
    c = ctx(dataset)
    with _example_lock:
        if dataset not in _examples:
            ex = pick_example(c)
            if ex is None:
                raise HTTPException(404, "Không tìm được khách ví dụ khớp số đã lưu.")
            _examples[dataset] = ex
    return _examples[dataset]


def warm_example(dataset: str) -> None:
    """Tìm sẵn khách ví dụ ở luồng nền để trang Tổng quan không phải chờ (lỗi thì để lần gọi thật báo)."""
    def run():
        try:
            example(dataset)
        except Exception:  # noqa: BLE001 — chỉ làm nóng bộ nhớ đệm
            pass
    Thread(target=run, daemon=True).start()


@router.get("/users/facets")
def user_facets(dataset: Dataset = "hm"):
    c = ctx(dataset)
    df = c.users
    return {
        "total": len(df),
        "thresholds": df.attrs["thresholds"],
        "buckets": [{"key": b, "label": label, "n_users": int((df["bucket"] == b).sum())}
                    for b, label in BUCKET_LABELS.items()],
        "areas": [{"key": a, "n_users": int(n)} for a, n in df["area"].value_counts().items()],
        "has_age": bool(df["age"].notna().any()),
        "note": f"Nhóm giao dịch chia theo tam phân vị số món đã mua của các khách có item {c.evaluated_on}.",
    }


@router.get("/users/search")
def search_users(f: dict = Depends(user_filter), offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=200)):
    df = _filtered(f)
    return {"total": len(df), "offset": offset, "items": user_rows(df.iloc[offset:offset + limit])}


@router.get("/users/random")
def random_user(f: dict = Depends(user_filter)):
    df = _filtered({**f, "q": ""})  # ngẫu nhiên trong bộ lọc, bỏ qua chữ đang gõ trong ô tìm
    if df.empty:
        raise HTTPException(404, "Không có khách nào khớp bộ lọc.")
    return user_rows(df.sample(1))[0]


def saved_best_series(c: DataContext, model: str) -> pd.Series:
    """Hạng món đích tốt nhất đã lưu ở đánh giá cuối (index customer_id); khách không có số đã lưu bị bỏ."""
    saved = {int(u): min(r) for u in c.target_users if (r := c.saved_ranks.get((model, int(u))))}
    return pd.Series(list(saved.values()), index=c.customer_ids[list(saved)].astype(str), dtype="float64")


def showcase_users(c: DataContext, a: str, b: str, k: int, limit: int) -> pd.DataFrame:
    """Ví dụ để đặt hai mô hình cạnh nhau: khách mà mô hình a có món đích trong top-k còn mô hình b thì không, xếp theo
    mức chênh hạng giảm dần. Chỉ lấy khách có hạng tính lại trên máy này trùng hạng đã lưu ở đánh giá cuối (với cả hai
    mô hình), để ví dụ luôn khớp số của báo cáo. Thêm cột best_rank (hạng của a) và rank_b."""
    for m in (a, b):
        if m not in c.available_models:
            raise HTTPException(404, f"Model '{m}' không khả dụng.")
    if k not in c.k_values:
        raise HTTPException(400, f"K phải thuộc {c.k_values}.")
    idx = c.users.index
    live_a, live_b = (best_rank_series(c, m).reindex(idx).to_numpy() for m in (a, b))
    saved_a, saved_b = (saved_best_series(c, m).reindex(idx).to_numpy() for m in (a, b))
    df = c.users.assign(best_rank=live_a, rank_b=live_b)
    df = df[(live_a == saved_a) & (live_b == saved_b) & (live_a <= k) & (live_b > k)]
    return df.assign(_gap=df["rank_b"] - df["best_rank"]).sort_values(["_gap", "customer_id"], ascending=[False, True]) \
        .head(limit).drop(columns="_gap")


@router.get("/users/showcase")
def showcase(a: str, b: str, k: int = 10, dataset: Dataset = "hm", limit: int = Query(20, ge=1, le=100)):
    """Khách mà mô hình a gợi ý đúng còn b gợi ý sai (nút "Xem ví dụ" của màn hình demo)."""
    df = showcase_users(ctx(dataset), a, b, k, limit)
    return {"a": a, "b": b, "k": k, "items": user_rows(df)}


@router.get("/users/{customer_id}/position")
def position(customer_id: str, f: dict = Depends(user_filter)):
    """Vị trí của khách trong danh sách đang lọc (nút ‹ › trên thanh khách)."""
    return user_position(_filtered(f), customer_id)


@router.get("/users/{customer_id}/history")
def history(customer_id: str, dataset: Dataset = "hm"):
    """Lịch sử mua mà mô hình đã học; khách mới: lịch sử rỗng, is_new = true."""
    c = ctx(dataset)
    u = _user(c, customer_id)
    if u is None:
        return {"customer_id": customer_id, "is_new": True, "profile": user_profile(c, None, customer_id), "items": [],
                "note": NEW_CUSTOMER_NOTE}
    return {"customer_id": customer_id, "is_new": False, "profile": user_profile(c, u, customer_id),
            "items": c.history(u)}


@router.get("/users/{customer_id}/recommend")
def recommend(customer_id: str, model: str = "", k: int = 10, dataset: Dataset = "hm"):
    """Top-K của mô hình; khách mới (không có trong dữ liệu đã học) nhận danh sách Most Popular kèm nhãn "gợi ý phổ
    biến" — không bao giờ để trống."""
    c = ctx(dataset)
    if k not in c.k_values:
        raise HTTPException(400, f"K phải thuộc {c.k_values} (evaluation.k_values trong config + DEMO_EXTRA_K).")
    model = model or c.available_models[0]
    if model not in c.available_models:
        reason = c.unavailable.get(model, "Model không hỗ trợ.")
        raise HTTPException(404, f"Model '{model}' không khả dụng: {reason}")
    u = _user(c, customer_id)
    return inference.popular(c, k) if u is None else inference.recommend(c, model, u, k)


@router.get("/users/{customer_id}/neighbors")
def neighbors(customer_id: str, k: int = 10, dataset: Dataset = "hm"):
    """Top-K khách tương đồng nhất theo UserKNN (cosine trên lịch sử mua), kèm sản phẩm mua chung."""
    c = ctx(dataset)
    u = _user(c, customer_id)
    if u is None:
        return {"customer_id": customer_id, "k": 0, "params": c.userknn_params, "neighbors": [],
                "note": "Khách mới: chưa có lịch sử mua để tìm khách tương đồng."}
    rows = c.neighbors(u, max(1, min(int(k), 50)))
    if rows is None:
        raise HTTPException(404, "UserKNN không khả dụng (thiếu cấu hình userknn trong results.json).")
    return {"customer_id": customer_id, "k": len(rows), "params": c.userknn_params, "neighbors": rows}


@router.get("/items/{item_idx}/similar")
def similar(item_idx: int, k: int = Query(6, ge=1, le=20), dataset: Dataset = "hm"):
    """Thẻ chi tiết sản phẩm: thông tin sản phẩm và các sản phẩm tương tự theo ItemKNN."""
    c = ctx(dataset)
    if not 0 <= item_idx < c.n_items:
        raise HTTPException(404, "Không có sản phẩm này.")
    rows = c.similar_items(item_idx, k)
    if rows is None:
        raise HTTPException(404, "ItemKNN không khả dụng (thiếu cấu hình itemknn trong results.json).")
    return {"item": c.item_info(item_idx), "similar": rows, "buyers": int(c.train_item_counts[item_idx])}


@router.get("/dashboard")
def dashboard(dataset: Dataset = "hm"):
    return metrics_io.dashboard(ctx(dataset))


@router.get("/image/{article_id}")
def image(article_id: str, dataset: Dataset = "hm"):
    """Ảnh H&M trong DEMO_IMAGES_DIR; không có ảnh (hoặc Amazon thiếu imUrl / ảnh lỗi) thì vẽ ô thay thế ghi loại sản
    phẩm."""
    aid = article_id.zfill(10) if dataset == "hm" else article_id
    if not aid.isalnum():
        raise HTTPException(400, "article_id không hợp lệ.")
    path = os.path.join(IMAGES_DIR, aid[:3], f"{aid}.jpg")
    if dataset == "hm" and os.path.exists(path):
        return FileResponse(path, headers={"Cache-Control": "max-age=86400"})
    arts = ctx(dataset).articles
    match = arts.loc[arts["article_id"] == aid, "product_type_name"]
    label = escape(match.iloc[0] if len(match) else DATASETS[dataset]["label"])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400">'
        '<rect width="300" height="400" fill="#efeae4"/>'
        '<path d="M110 90l40-20 40 20 40 30-20 40-20-10v160H110V150l-20 10-20-40z" fill="#ddd4ca"/>'
        f'<text x="150" y="360" font-family="sans-serif" font-size="22" fill="#6b625a" text-anchor="middle">{label}</text>'
        "</svg>"
    )
    return Response(svg, media_type="image/svg+xml")
