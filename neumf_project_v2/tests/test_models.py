from __future__ import annotations

import torch
import pytest

from src.models.neumf import GMF, MLP, NeuMF


def test_forward_shapes_and_logits():
    gmf = GMF(10, 20, 8)
    mlp = MLP(10, 20, 8, [16, 8, 4], dropout=0.1)
    neumf = NeuMF(10, 20, 8, [16, 8, 4], dropout=0.1)
    u = torch.tensor([0, 1, 2])
    i = torch.tensor([3, 4, 5])
    assert gmf(u, i).shape == (3,)
    assert mlp(u, i).shape == (3,)
    assert neumf(u, i).shape == (3,)


def test_neumf_uses_four_independent_embeddings():
    m = NeuMF(10, 20, 8, [16, 8, 4])
    assert m.gmf_user_emb is not m.mlp_user_emb
    assert m.gmf_item_emb is not m.mlp_item_emb


def test_pretrained_copy():
    gmf = GMF(10, 20, 8)
    mlp = MLP(10, 20, 8, [16, 8, 4])
    n = NeuMF(10, 20, 8, [16, 8, 4])
    n.load_pretrained(gmf, mlp, alpha=0.5)
    assert torch.allclose(n.gmf_user_emb.weight, gmf.user_emb.weight)
    assert torch.allclose(n.mlp_user_emb.weight, mlp.user_emb.weight)


def test_mlp_dropout_is_configurable():
    m = MLP(10, 20, 8, [16, 8, 4], dropout=0.35)
    drops = [x for x in m.mlp_layers if isinstance(x, torch.nn.Dropout)]
    assert drops and all(d.p == pytest.approx(0.35) for d in drops)


def test_bpr_checkpoint_roundtrip_and_demo_scoring_match(tmp_path):
    import numpy as np
    import pandas as pd

    from src.baselines import BPRMFBaseline

    train = pd.DataFrame({"user": [0, 0, 1, 2, 2], "item": [0, 1, 2, 3, 1]})
    bpr = BPRMFBaseline(3, 6, 4, seed=0).fit(train, epochs=3)
    bpr.save(tmp_path / "bpr.npz")
    loaded = BPRMFBaseline.load(tmp_path / "bpr.npz")
    cand = np.array([5, 0, 3, 2])
    for u in range(3):
        assert np.array_equal(loaded.score_items(u, cand), bpr.score_items(u, cand))
        # demo/backend/inference.py chấm mọi item bằng Q @ P[u] rồi lấy theo candidates
        assert np.array_equal((loaded.Q @ loaded.P[u])[cand], bpr.score_items(u, cand))



def test_refit_runs_fixed_epochs_without_validation():
    """val_records=None (train lại trên train ∪ val): chạy đúng max_epochs, không gọi eval, giữ trọng số cuối."""
    import pandas as pd
    from src.data_pipeline.dataset import TrainDataset
    from src.data_pipeline.negative_sampling import build_user_positive_sets
    from src.training.trainer import train_one_model

    df = pd.DataFrame({"user": [0, 0, 1, 2], "item": [1, 2, 3, 4], "sample_weight": 1.0})
    ds = TrainDataset(df, 6, build_user_positive_sets(df, 3), neg_ratio=2, seed=0)
    net = GMF(3, 6, 4)

    def no_eval(*_):
        raise AssertionError("refit không được chấm val")

    opt = torch.optim.Adam(net.parameters(), lr=0.1)
    _, hist, meta = train_one_model(net, ds, None, no_eval, opt, "cpu", 3, 3, 2, seed=0)
    assert len(hist) == 3 and meta["best_epoch"] == 3 and meta["best_metric"] is None
