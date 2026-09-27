"""P4a: lấy cấu hình tuning, NeuMF hai nhánh khác chiều, EarlyFusion trùng MLP."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pandas as pd
import pytest
import torch

from scripts.common import build_adapter
from src.models.early_fusion import EarlyFusionModel
from src.models.neumf import GMF, MLP, NeuMF

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tune", ROOT / "scripts" / "10_tune.py")
tune = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tune)


@pytest.mark.parametrize("model", [m for m in tune.ORDER])
def test_sample_configs_default_first_deterministic_in_grid(model):
    cfg, _ = build_adapter("configs/hm500k_global.yaml")
    default = tune.default_config(model, cfg)
    a = tune.sample_configs(tune.GRIDS[model], default, 6)
    assert a == tune.sample_configs(tune.GRIDS[model], default, 6)
    assert a[0] == default
    assert len(a) == min(6, math.prod(len(v) for v in tune.GRIDS[model].values()))
    assert len({str(sorted(c.items())) for c in a}) == len(a)


def test_neumf_separate_gmf_dim_loads_pretrained_exactly():
    torch.manual_seed(0)
    gmf, mlp = GMF(5, 7, 4), MLP(5, 7, 8, [16, 8, 4], dropout=0.0)
    net = NeuMF(5, 7, 8, [16, 8, 4], dropout=0.0, gmf_dim=4)
    net.load_pretrained(gmf, mlp, alpha=0.3)
    u, i = torch.tensor([0, 1, 4]), torch.tensor([6, 2, 3])
    for m in (gmf, mlp, net):
        m.eval()
    assert torch.allclose(net(u, i), 0.3 * gmf(u, i) + 0.7 * mlp(u, i), atol=1e-6)



def test_early_fusion_is_architecturally_identical_to_mlp():
    """Lý do bỏ EarlyFusion khỏi tuning (PREREG mục 8): cùng seed -> cùng tham số -> cùng đầu ra."""
    torch.manual_seed(1)
    mlp = MLP(5, 7, 8, [16, 8, 4], dropout=0.0)
    torch.manual_seed(1)
    ef = EarlyFusionModel(5, 7, 8, [16, 8, 4], dropout=0.0)
    assert [(k, v.shape) for k, v in mlp.state_dict().items()] == [(k, v.shape) for k, v in ef.state_dict().items()]
    u, i = torch.tensor([0, 3, 4]), torch.tensor([1, 6, 2])
    assert torch.equal(mlp(u, i), ef(u, i))
