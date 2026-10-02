from __future__ import annotations

from pathlib import Path

from src.config import load_config, resolve_project_path
from src.data_pipeline.adapters import HMAdapter

# Mô hình dùng thuộc tính sản phẩm/khách hàng đã bị gỡ khỏi dự án (ngoài phạm vi đề tài MF + DNN), và
# EarlyFusionModel (trùng hệt MLP, không phải hợp nhất MF + DNN). Các run cũ vẫn còn số của chúng trong
# results.json -> ẩn khỏi bảng, biểu đồ (05, 06) và demo.
REPORT_HIDDEN_MODELS = {"AgeGroupPopularity", "CategoryPopularity", "ContentBased", "Hybrid-NeuMF-CBF", "EarlyFusion"}


def build_adapter(config_path: str):
    cfg = load_config(config_path)
    path = resolve_project_path(cfg.dataset.raw_path)
    name = cfg.dataset.name.lower()
    if name == "hm":
        adapter = HMAdapter(
            path,
            encoding=cfg.dataset.encoding,
            nrows=cfg.dataset.nrows,
            start_date=cfg.dataset.start_date,
            end_date=cfg.dataset.end_date,
        )
    else:
        raise ValueError(f"Dataset chưa hỗ trợ: {cfg.dataset.name}")
    return cfg, adapter
