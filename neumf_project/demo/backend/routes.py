from __future__ import annotations

import os
import random
from html import escape

import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from . import inference, metrics_io
from .data_context import DEMO_ROOT, DataContext, resolve_mode, resolve_run_tag
from .onboarding import Onboarding, load_onboarding_config

IMAGES_DIR = os.environ.get("DEMO_IMAGES_DIR", str(DEMO_ROOT / "static" / "images"))
BUCKET_LABELS = {"low": "Ít giao dịch", "mid": "Trung bình", "high": "Nhiều giao dịch"}

router = APIRouter(prefix="/api")
_cache: dict[str, DataContext] = {}
_onboarding: dict[str, Onboarding] = {}


def ctx() -> DataContext:
    mode = resolve_mode()
    tag = resolve_run_tag(mode)
    if tag not in _cache:
        _cache[tag] = DataContext(tag, mode=mode)
    return _cache[tag]


def onboarding() -> Onboarding:
    c = ctx()
    if c.run_tag not in _onboarding:
        _onboarding[c.run_tag] = Onboarding(c.train_df, c.articles, c.user_age, load_onboarding_config())
    return _onboarding[c.run_tag]


def _user(c: DataContext, customer_id: str) -> int:
    try:
        u = c.resolve_user(customer_id)
    except KeyError:
        raise HTTPException(404, f"Không tìm thấy customer_id '{customer_id}' trong dữ liệu sau k-core.")
    if u not in c.target_items:
        raise HTTPException(404, f"User '{customer_id}' không có item {c.evaluated_on} trong split.")
    return u


def _thresholds(c: DataContext) -> tuple[float, float]:
    counts = c.train_user_counts[c.target_users]
    return float(np.quantile(counts, 1 / 3)), float(np.quantile(counts, 2 / 3))


def _bucket(n: int, t: tuple[float, float]) -> str:
    return "low" if n <= t[0] else ("mid" if n <= t[1] else "high")


def _user_row(c: DataContext, u: int, t) -> dict:
    n = int(c.train_user_counts[u])
    return {"customer_id": c.customer_ids[u], "train_count": n, "bucket": _bucket(n, t)}


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
    _onboarding.clear()
    return {"previous_run_tags": old, "current_run_tag": ctx().run_tag}


@router.get("/users/buckets")
def user_buckets():
    c = ctx()
    t = _thresholds(c)
    counts = c.train_user_counts[c.target_users]
    sizes = {b: int(sum(_bucket(int(n), t) == b for n in counts)) for b in BUCKET_LABELS}
    return {
        "thresholds": t,
        "buckets": [{"key": b, "label": l, "n_users": sizes[b]} for b, l in BUCKET_LABELS.items()],
        "note": f"Chia theo tam phân vị số tương tác train của các user có item {c.evaluated_on}.",
    }


@router.get("/users/search")
def search_users(q: str = "", bucket: str | None = None, limit: int = 20):
    c, q = ctx(), q.strip().lower()
    t = _thresholds(c)
    out = []
    for u in c.target_users:
        row = _user_row(c, int(u), t)
        if row["customer_id"].startswith(q) and (bucket is None or row["bucket"] == bucket):
            out.append(row)
            if len(out) >= limit:
                break
    return out


@router.get("/users/random")
def random_user(bucket: str | None = None):
    c = ctx()
    t = _thresholds(c)
    pool = [int(u) for u in c.target_users if bucket is None or _bucket(int(c.train_user_counts[u]), t) == bucket]
    if not pool:
        raise HTTPException(404, "Không có user nào trong nhóm này.")
    return _user_row(c, random.choice(pool), t)


@router.get("/users/{customer_id}/history")
def history(customer_id: str):
    c = ctx()
    u = _user(c, customer_id)
    return {"customer_id": customer_id, "items": c.history(u)}


@router.get("/users/{customer_id}/recommend")
def recommend(customer_id: str, model: str = "NeuMF-Pretrained", k: int = 10):
    c = ctx()
    if k not in c.k_values:
        raise HTTPException(400, f"K phải thuộc {c.k_values} (evaluation.k_values trong config).")
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


class OnboardingRequest(BaseModel):
    area: str
    product_groups: list[str] = []
    colours: list[str] = []
    age_group: str | None = None
    k: int = 10


@router.get("/onboarding/options")
def onboarding_options():
    return onboarding().options()


@router.post("/onboarding/recommend")
def onboarding_recommend(req: OnboardingRequest):
    c, ob = ctx(), onboarding()
    if req.k not in c.k_values:
        raise HTTPException(400, f"K phải thuộc {c.k_values}.")
    try:
        res = ob.recommend(req.area, req.product_groups, req.colours, req.age_group, req.k)
    except KeyError:
        raise HTTPException(400, f"Khu vực '{req.area}' không có trong onboarding_config.yaml.")
    for block in ("preferred", "hot_in_area"):
        res[block] = [{**c.item_info(it["item_idx"]), **it} for it in res[block]]
    return res


@router.get("/dashboard")
def dashboard():
    c = ctx()
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
