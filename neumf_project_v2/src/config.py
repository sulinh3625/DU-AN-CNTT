from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class DatasetConfig:
    name: str
    raw_path: str
    encoding: str = "utf-8"
    k_core: int = 5
    audit_k_values: list[int] = field(default_factory=lambda: [3, 5, 10])
    min_interactions_for_loo: int = 3
    nrows: int | None = None
    start_date: str | None = None
    end_date: str | None = None


@dataclass
class FeedbackConfig:
    mode: str = "binary"  # binary | weighted_confidence
    confidence_alpha: float = 1.0


@dataclass
class ModelConfig:
    embedding_dim: int = 32
    mlp_layers: list[int] = field(default_factory=lambda: [64, 32, 16, 8])
    dropout: float = 0.2
    pretrain_alpha: float = 0.5


@dataclass
class TrainingConfig:
    batch_size: int = 256
    negative_ratio: int = 4
    pretrain_optimizer: str = "adam"
    pretrain_lr: float = 1e-3
    finetune_optimizer: str = "sgd"
    finetune_lr: float = 1e-2
    weight_decay: float = 1e-6
    max_epochs_pretrain: int = 50
    max_epochs_finetune: int = 50
    patience: int = 10
    monitor: str = "NDCG@10"
    device: str = "cpu"
    seed: int = 42
    # EarlyFusionModel dùng cùng optimizer/LR/budget với NeuMF-Scratch
    # (finetune_*) để ablation Early vs Late fusion công bằng.
    train_early_fusion: bool = True


@dataclass
class EvaluationConfig:
    primary: str = "full_ranking"  # full_ranking | sampled
    k_values: list[int] = field(default_factory=lambda: [5, 10])
    sampled_negatives: int = 99
    tie_break_seed: int = 2026
    include_redundant_metrics: bool = False
    head_fraction: float = 0.10
    # Cold-start TƯƠNG ĐỐI: cold_fraction% user ít tương tác nhất trong TRAIN.
    cold_fraction: float = 0.20
    # Cold-start TUYỆT ĐỐI: user bị k-core loại (xem cold_start.build_strict_cold_start).
    strict_cold_start: bool = False
    strict_cold_max_users: int | None = 5000


@dataclass
class BPRConfig:
    embedding_dim: int = 32
    epochs: int = 30
    lr: float = 0.03
    reg: float = 0.005


@dataclass
class BaselineConfig:
    enabled: list[str] = field(default_factory=lambda: ["random", "popularity", "itemknn", "bpr"])
    bpr: BPRConfig = field(default_factory=BPRConfig)


@dataclass
class SideFeaturesConfig:
    """Thông tin phụ trợ (H&M): articles.csv / customers.csv. None = không dùng."""
    articles_path: str | None = None
    customers_path: str | None = None
    # Chỉ cần khi raw_path là cache Parquet (item_raw/user_raw là mã số).
    item_id_map_path: str | None = None
    user_id_map_path: str | None = None


@dataclass
class ContentConfig:
    category_col: str = "product_type_name"
    categorical_cols: list[str] = field(default_factory=lambda: [
        "product_code", "product_type_name", "product_group_name",
        "graphical_appearance_name", "colour_group_name", "perceived_colour_master_name",
        "department_name", "index_name", "section_name", "garment_group_name",
    ])
    text_cols: list[str] = field(default_factory=lambda: ["prod_name", "detail_desc"])
    block_weights: dict[str, float] = field(default_factory=dict)
    text_weight: float = 1.0
    text_max_features: int = 5000
    # Grid recency_decay, chọn theo NDCG@10 trên validation.
    recency_decays: list[float] = field(default_factory=lambda: [1.0, 0.8, 0.5])


@dataclass
class HybridConfig:
    enabled: bool = False
    cf_model: str = "NeuMF-Pretrained"
    alphas: list[float] = field(default_factory=lambda: [round(x * 0.1, 1) for x in range(11)])


@dataclass
class PathsConfig:
    outputs_dir: str = "outputs"


@dataclass
class ProjectConfig:
    dataset: DatasetConfig
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    baselines: BaselineConfig = field(default_factory=BaselineConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    side_features: SideFeaturesConfig = field(default_factory=SideFeaturesConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    hybrid: HybridConfig = field(default_factory=HybridConfig)

    @property
    def output_root(self) -> Path:
        p = Path(self.paths.outputs_dir)
        return p if p.is_absolute() else PROJECT_ROOT / p


def _merge_dataclass(cls, data: dict[str, Any] | None):
    data = data or {}
    if cls is BaselineConfig:
        bpr_data = data.get("bpr", {})
        payload = {k: v for k, v in data.items() if k != "bpr"}
        return BaselineConfig(**payload, bpr=BPRConfig(**bpr_data))
    return cls(**data)


def load_config(path: str | Path) -> ProjectConfig:
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    dataset = DatasetConfig(**raw["dataset"])
    cfg = ProjectConfig(
        dataset=dataset,
        feedback=_merge_dataclass(FeedbackConfig, raw.get("feedback")),
        model=_merge_dataclass(ModelConfig, raw.get("model")),
        training=_merge_dataclass(TrainingConfig, raw.get("training")),
        evaluation=_merge_dataclass(EvaluationConfig, raw.get("evaluation")),
        baselines=_merge_dataclass(BaselineConfig, raw.get("baselines")),
        paths=_merge_dataclass(PathsConfig, raw.get("paths")),
        side_features=_merge_dataclass(SideFeaturesConfig, raw.get("side_features")),
        content=_merge_dataclass(ContentConfig, raw.get("content")),
        hybrid=_merge_dataclass(HybridConfig, raw.get("hybrid")),
    )
    return cfg


def resolve_project_path(value: str | Path) -> Path:
    p = Path(value)
    return p if p.is_absolute() else PROJECT_ROOT / p