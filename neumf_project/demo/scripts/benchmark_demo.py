"""Đo hiệu năng hệ thống demo (Mục "Lựa chọn mô hình triển khai và yêu cầu phi chức năng" của báo cáo).

Chỉ gọi API của demo trên checkpoint đã lưu: không huấn luyện, không chạy lại đánh giá cuối. Đo thời gian nạp mỗi bộ dữ
liệu, độ trễ khuyến nghị Top-K của NeuMF-F trên khách được đánh giá, độ trễ các chức năng phụ, và số sản phẩm có ảnh thật
lưu trên máy. Kết quả ghi ra outputs/demo/benchmark.json.

Chạy từ thư mục neumf_project:  python demo/scripts/benchmark_demo.py
"""
from __future__ import annotations

import json
import os
import platform
import random
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from fastapi.testclient import TestClient  # noqa: E402

from demo.backend import routes  # noqa: E402
from demo.backend.main import app  # noqa: E402

N_USERS, N_SIDE, N_NEW, SEED = 300, 100, 50, 2026
OUT = ROOT / "outputs" / "demo" / "benchmark.json"


def cpu_name() -> str:
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    return platform.processor()


def main() -> None:
    client = TestClient(app)

    def timed(url: str) -> float:
        t = time.perf_counter()
        r = client.get(url)
        dt = (time.perf_counter() - t) * 1000
        if r.status_code != 200:
            raise SystemExit(f"{url} -> {r.status_code}: {r.text[:200]}")
        return dt

    def p95(xs: list[float]) -> float:
        xs = sorted(xs)
        return xs[min(len(xs) - 1, round(0.95 * (len(xs) - 1)))]

    rng = random.Random(SEED)
    result = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "cpu": cpu_name(), "python": platform.python_version(),
              "n_users": N_USERS, "seed": SEED, "note": "TestClient của FastAPI, đo cả xử lý API và đóng gói JSON"}
    for ds in ("hm", "amazon"):
        t = time.perf_counter()
        timed(f"/api/context?dataset={ds}")
        load_s = time.perf_counter() - t
        c = routes.ctx(ds)
        users = [str(c.customer_ids[u]) for u in c.target_users]
        sample = rng.sample(users, N_USERS)
        for u in sample[:5]:  # làm nóng
            timed(f"/api/users/{u}/recommend?model=NeuMF-F&k=10&dataset={ds}")
        rec = [timed(f"/api/users/{u}/recommend?model=NeuMF-F&k=10&dataset={ds}") for u in sample]
        neigh = [timed(f"/api/users/{u}/neighbors?k=6&dataset={ds}") for u in sample[:N_SIDE]]
        sim = [timed(f"/api/items/{i}/similar?k=6&dataset={ds}") for i in rng.sample(range(c.n_items), N_SIDE)]
        new = [timed(f"/api/users/KHACH_MOI_{i}/recommend?model=NeuMF-F&k=10&dataset={ds}") for i in range(N_NEW)]
        with_image = 0
        for i in range(c.n_items):
            aid = str(c.item_info(i)["article_id"])
            path = (os.path.join(routes.IMAGES_DIR, aid.zfill(10)[:3], f"{aid.zfill(10)}.jpg") if ds == "hm"
                    else routes.amazon_image_path(aid))
            with_image += os.path.exists(path)
        result[ds] = {
            "load_s": round(load_s, 1), "n_items": int(c.n_items), "n_eval_users": len(users),
            "models": list(c.available_models),
            "recommend_top10_ms": {"median": round(statistics.median(rec), 1), "p95": round(p95(rec), 1)},
            "similar_items_ms_median": round(statistics.median(sim), 1),
            "neighbors_ms_median": round(statistics.median(neigh), 1),
            "new_customer_ms_median": round(statistics.median(new), 1),
            "items_with_image": with_image,
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
