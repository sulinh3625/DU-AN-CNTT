"""Demo shop thời trang H&M: inference-only trên checkpoint đã huấn luyện.

Chạy từ thư mục neumf_project_v2/:
    python -m uvicorn demo.backend.main:app --port 8000
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router

app = FastAPI(title="H&M Recommendation Demo API")
app.include_router(router)


@app.middleware("http")
async def no_cache(request, call_next):
    """Tắt cache trình duyệt cho HTML/JS/API (ảnh tự đặt Cache-Control riêng)."""
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-store, max-age=0")
    return response


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
