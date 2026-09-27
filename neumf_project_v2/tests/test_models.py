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


def test_ials_fits_on_train_and_checkpoint_roundtrip(tmp_path):
    import numpy as np
    import pandas as pd

    from src.baselines import IALSBaseline

    train = pd.DataFrame({"user": [0, 0, 1, 1, 2, 2, 3], "item": [0, 1, 1, 2, 2, 3, 0]})
    ials = IALSBaseline(4, 5, factors=4, iterations=5, seed=0).fit(train)
    assert ials.P.shape == (4, 4) and ials.Q.shape == (5, 4)
    cand = np.array([4, 0, 2])
    ials.save(tmp_path / "ials.npz")
    loaded = IALSBaseline.load(tmp_path / "ials.npz")
    for u in range(4):
        assert np.array_equal(loaded.score_items(u, cand), ials.score_items(u, cand))
    # item 4 chưa từng xuất hiện trong train -> điểm thấp hơn item user đã tương tác nhiều
    assert ials.score(0, 0) > ials.score(0, 4)


def test_most_popular_recent_window_counts_only_last_days_of_train():
    import pandas as pd

    from src.baselines import MostPopularBaseline

    t = pd.Timestamp
    train = pd.DataFrame({"user": [0, 1, 2, 3, 4], "item": [0, 0, 0, 1, 1],
                          "last_timestamp": [t("2020-01-01"), t("2020-01-02"), t("2020-01-03"),
                                             t("2020-03-01"), t("2020-03-02")]})
    assert MostPopularBaseline(train, 3).pop_score.tolist() == [3.0, 2.0, 0.0]
    assert MostPopularBaseline(train, 3, window_days=28).pop_score.tolist() == [0.0, 2.0, 0.0]
