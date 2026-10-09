from __future__ import annotations

import json
import os
from html import escape
from typing import Literal

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response

from . import inference, metrics_io
from .data_context import DEMO_ROOT, DataContext, resolve_mode, resolve_run_tag

IMAGES_DIR = os.environ.get("DEMO_IMAGES_DIR", str(DEMO_ROOT / "static" / "images"))
BUCKET_LABELS = {"low": "Ít giao dịch", "mid": "Trung bình", "high": "Nhiều giao dịch"}
# Thứ tự danh sách chọn khách: khoá -> (cột, tăng dần?); hoà thì theo customer_id để thứ tự luôn tất định.
SORTS = {
    "train_desc": (["train_count", "customer_id"], [False, True]),
    "train_asc": (["train_count", "customer_id"], [True, True]),
    "targets_desc": (["n_targets", "train_count", "customer_id"], [False, False, True]),
    "id": (["customer_id"], [True]),
}
Bucket = Literal["low", "mid", "high"]
Sort = Literal["train_desc", "train_asc", "targets_desc", "id"]

router = APIRouter(prefix="/api")
_cache: dict[str, DataContext] = {}


def ctx() -> DataContext:
    mode = resolve_mode()
    tag = resolve_run_tag(mode)
    if tag not in _cache:
        _cache[tag] = DataContext(tag, mode=mode)
    return _cache[tag]


def _user(c: DataContext, customer_id: str) -> int:
    try:
        u = c.resolve_user(customer_id)
    except KeyError:
        raise HTTPException(404, f"Không tìm thấy customer_id '{customer_id}' trong dữ liệu sau k-core.")
    if u not in c.target_items:
        raise HTTPException(404, f"User '{customer_id}' không có item {c.evaluated_on} trong split.")
    return u


def filter_users(df: pd.DataFrame, q: str = "", bucket: str | None = None, area: str | None = None,
                 sort: str = "train_desc") -> pd.DataFrame:
    """Lọc và sắp bảng khách (DataContext.users): customer_id chứa q (khớp ở đầu xếp trước), nhóm giao dịch, khu vực
    mua nhiều nhất."""
    q = q.strip().lower()
    if bucket:
        df = df[df["bucket"] == bucket]
    if area:
        df = df[df["area"] == area]
    cols, asc = SORTS[sort]
    if q:
        df = df[df["customer_id"].str.contains(q, regex=False)]
        df = df.assign(_later=~df["customer_id"].str.startswith(q))
        cols, asc = ["_later", *cols], [True, *asc]
    return df.sort_values(cols, ascending=asc).drop(columns="_later", errors="ignore")


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
    return {"status": "ok", "loaded_run_tags": list(_cache)}


@router.get("/context")
def context():
    return ctx().summary()


@router.post("/reload")
def reload():
    old = list(_cache)
    _cache.clear()
    return {"previous_run_tags": old, "current_run_tag": ctx().run_tag}


@router.get("/users/facets")
def user_facets():
    c = ctx()
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
def search_users(q: str = "", bucket: Bucket | None = None, area: str | None = None, sort: Sort = "train_desc",
                 offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=200)):
    df = filter_users(ctx().users, q, bucket, area, sort)
    return {"total": len(df), "offset": offset, "items": user_rows(df.iloc[offset:offset + limit])}


@router.get("/users/random")
def random_user(bucket: Bucket | None = None, area: str | None = None):
    df = filter_users(ctx().users, bucket=bucket, area=area)
    if df.empty:
        raise HTTPException(404, "Không có khách nào khớp bộ lọc.")
    return user_rows(df.sample(1))[0]


@router.get("/users/{customer_id}/position")
def position(customer_id: str, q: str = "", bucket: Bucket | None = None, area: str | None = None,
             sort: Sort = "train_desc"):
    """Vị trí của khách trong danh sách đang lọc (nút ‹ › trên thanh khách)."""
    return user_position(filter_users(ctx().users, q, bucket, area, sort), customer_id)


@router.get("/users/{customer_id}/history")
def history(customer_id: str):
    c = ctx()
    u = _user(c, customer_id)
    return {"customer_id": customer_id, "profile": user_rows(c.users.loc[[c.customer_ids[u]]])[0],
            "items": c.history(u)}


@router.get("/users/{customer_id}/recommend")
def recommend(customer_id: str, model: str = "", k: int = 10):
    c = ctx()
    if k not in c.k_values:
        raise HTTPException(400, f"K phải thuộc {c.k_values} (evaluation.k_values trong config).")
    model = model or c.available_models[0]
    if model not in c.available_models:
        reason = c.unavailable.get(model, "Model không hỗ trợ.")
        raise HTTPException(404, f"Model '{model}' không khả dụng: {reason}")
    u = _user(c, customer_id)
    out = inference.recommend(c, model, u, k)
    out["target_item"] = c.item_info(c.target_item[u])
    # Chế độ explore: chỉ khi chấm test mới hiện thêm item validation (cũng bị loại khỏi candidates); chấm validation
    # thì test giữ kín. Chế độ final: validation đã gộp vào dữ liệu huấn luyện lại nên không có val_item riêng.
    out["val_item"] = c.item_info(c.val_item[u]) if c.evaluated_on == "test" and u in c.val_item else None
    return out


@router.get("/users/{customer_id}/neighbors")
def neighbors(customer_id: str, k: int = 10):
    """Top-K khách tương đồng nhất theo UserKNN (cosine trên lịch sử mua), kèm sản phẩm mua chung."""
    c = ctx()
    u = _user(c, customer_id)
    rows = c.neighbors(u, max(1, min(int(k), 50)))
    if rows is None:
        raise HTTPException(404, "UserKNN không khả dụng ở chế độ này (cần chế độ final và tham số mở rộng).")
    return {"customer_id": customer_id, "k": len(rows), "params": getattr(c, "extension_params", {}).get("UserKNN"),
            "neighbors": rows}


@router.get("/dashboard")
def dashboard():
    c = ctx()
    if c.mode == "v2":
        return metrics_io.v2_dashboard(c)
    return metrics_io.final_dashboard(c) if c.mode == "final" else metrics_io.dashboard(c.run_tag)


@router.get("/image/{article_id}")
def image(article_id: str):
    aid = article_id.zfill(10)
    if not aid.isdigit():
        raise HTTPException(400, "article_id không hợp lệ.")
    path = os.path.join(IMAGES_DIR, aid[:3], f"{aid}.jpg")
    if os.path.exists(path):
        return FileResponse(path, headers={"Cache-Control": "max-age=86400"})
    arts = ctx().articles
    match = arts.loc[arts["article_id"] == aid, "product_type_name"]
    label = escape(match.iloc[0] if len(match) else "H&M")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400">'
        '<rect width="300" height="400" fill="#efeae4"/>'
        '<path d="M110 90l40-20 40 20 40 30-20 40-20-10v160H110V150l-20 10-20-40z" fill="#ddd4ca"/>'
        f'<text x="150" y="360" font-family="sans-serif" font-size="22" fill="#6b625a" text-anchor="middle">{label}</text>'
        "</svg>"
    )
    return Response(svg, media_type="image/svg+xml")
