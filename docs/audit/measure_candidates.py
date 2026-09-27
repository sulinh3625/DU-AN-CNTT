"""Đo chi phí thật của các ứng viên trên hm500k (chia theo mốc thời gian chung), CHỈ dùng validation."""
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

ROOT = Path(r"D:\KhoaLuanTotNghiep\duan\DU-AN-CNTT\neumf_project_v2")
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from scripts.common import build_adapter
from src.baselines import IALSBaseline
from src.data_pipeline.dataset import TrainDataset
from src.data_pipeline.negative_sampling import build_user_positive_sets
from src.data_pipeline.preprocessing import build_interactions
from src.data_pipeline.splitting import global_temporal_split
from src.evaluation.full_ranking import build_full_ranking_records_multi, evaluate_torch_model
from src.models.neumf import NeuMF

cfg, ad = build_adapter("configs/hm500k_global.yaml")
d = build_interactions(ad.load_events(), cfg.dataset.k_core)
tr, va, te = global_temporal_split(d.df, cfg.dataset.val_start, cfg.dataset.test_start)
tr = tr.assign(sample_weight=1.0)
nu, ni = d.n_users, d.n_items
train_pos = build_user_positive_sets(tr, nu)
val_recs = build_full_ranking_records_multi(va, ni, train_pos, tr["item"].unique())
ds = TrainDataset(tr, ni, train_pos, cfg.training.negative_ratio, seed=0)
dev = torch.device("cuda")
kw = dict(k_values=[10], device=dev, tie_seed=cfg.evaluation.tie_break_seed)
print(f"users {nu} items {ni} train {len(tr)} | mẫu/epoch {len(ds.users):,} | val users {len(val_recs)}")


def one_epoch(model, lr=1e-3, bs=512):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    crit = nn.BCEWithLogitsLoss()
    model.train()
    perm = np.random.default_rng(0).permutation(len(ds.users))
    torch.cuda.synchronize(); t0 = time.time()
    for s in range(0, len(perm), bs):
        idx = perm[s:s + bs]
        u = torch.from_numpy(ds.users[idx]).to(dev); i = torch.from_numpy(ds.items[idx]).to(dev)
        y = torch.from_numpy(ds.labels[idx]).to(dev)
        opt.zero_grad(); crit(model(u, i), y).backward(); opt.step()
    torch.cuda.synchronize()
    return time.time() - t0


def measure(name, model):
    torch.cuda.reset_peak_memory_stats()
    t_ep = one_epoch(model)
    if hasattr(model, "precompute"):
        model.eval(); model.precompute()
    torch.cuda.synchronize(); t0 = time.time()
    r = evaluate_torch_model(model, val_recs, **kw)
    t_ev = time.time() - t0
    print(f"{name:34s} 1 epoch {t_ep:6.1f}s | full ranking val {t_ev:5.1f}s | GPU đỉnh "
          f"{torch.cuda.max_memory_allocated() / 1e9:.2f} GB | val NDCG@10 sau 1 epoch {r['NDCG@10']:.4f}", flush=True)


# ---------------- A. NeuMF (họ hiện có)
for dim in (32, 64):
    measure(f"A. NeuMF d={dim}", NeuMF(nu, ni, dim, [2 * dim, dim, dim // 2, dim // 4], 0.2).to(dev))


# ---------------- C. DeepCF / CFNet (prototype, vector tương tác chỉ từ TRAIN)
class CFNet(nn.Module):
    def __init__(self, R, d_ml=32, rl=(512, 64), ml=(64, 32, 16, 8)):
        super().__init__()
        self.register_buffer("R", R)                   # users x items (0/1 từ train)
        self.register_buffer("RT", R.t().contiguous())  # items x users
        self.u_tower = nn.Sequential(nn.Linear(R.shape[1], rl[0]), nn.ReLU(), nn.Linear(rl[0], rl[1]), nn.ReLU())
        self.i_tower = nn.Sequential(nn.Linear(R.shape[0], rl[0]), nn.ReLU(), nn.Linear(rl[0], rl[1]), nn.ReLU())
        self.ue, self.ie = nn.Embedding(R.shape[0], d_ml), nn.Embedding(R.shape[1], d_ml)
        layers = []
        for a, b in zip((2 * d_ml,) + ml[:-1], ml):
            layers += [nn.Linear(a, b), nn.ReLU()]
        self.mlp = nn.Sequential(*layers)
        self.out = nn.Linear(rl[1] + ml[-1], 1)
        self.cache = None

    def precompute(self):
        with torch.no_grad():
            self.cache = (self.u_tower(self.R), self.i_tower(self.RT))

    def forward(self, u, i):
        if self.cache is not None and not self.training:
            pu, qi = self.cache[0][u], self.cache[1][i]
        else:
            self.cache = None
            pu, qi = self.u_tower(self.R[u]), self.i_tower(self.RT[i])
        ml = self.mlp(torch.cat([self.ue(u), self.ie(i)], -1))
        return self.out(torch.cat([pu * qi, ml], -1)).squeeze(-1)


R = torch.zeros(nu, ni)
R[torch.from_numpy(tr["user"].to_numpy()), torch.from_numpy(tr["item"].to_numpy())] = 1.0
measure("C. CFNet rl[512,64] + ml[64..8]", CFNet(R.to(dev)).to(dev))

# ---------------- B. Late fusion MF + NeuMF: chi phí = MF + NeuMF + trộn điểm (đo MF)
t0 = time.time(); m = IALSBaseline(nu, ni, 64, 0.01, 1.0, 15).fit(tr); print(f"B. thành phần MF (iALS d=64) fit {time.time() - t0:.1f}s; "
                                                                           "trộn điểm = 1 phép cộng có trọng số/candidate")
