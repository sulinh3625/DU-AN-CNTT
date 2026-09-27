from __future__ import annotations

import torch
import torch.nn as nn


class CFNet(nn.Module):
    """DeepCF / CFNet (Deng et al., AAAI 2019) — thuần CF, lai MF + DNN.

    - Nhánh representation (CFNet-rl, kiểu DMF): đầu vào của user là hàng của ma trận tương tác R (0/1),
      của item là cột; mỗi bên qua một tháp MLP rồi nhân element-wise.
    - Nhánh matching (CFNet-ml, kiểu NCF-MLP): embedding ID user/item ghép lại qua MLP.
    - Ghép hai nhánh, lớp tuyến tính cuối ra logit.

    R PHẢI được xây chỉ từ tập train (không chứa tương tác val/test). Khi eval, tháp rl được tính trước
    một lần cho mọi user/item (Full Ranking rẻ như NeuMF).
    """

    def __init__(self, R: torch.Tensor, embedding_dim: int, layers: list[int], rl_layers=(512, 64), dropout: float = 0.0):
        super().__init__()
        n_users, n_items = R.shape
        if not layers or layers[0] != 2 * embedding_dim:
            raise ValueError(f"layers[0] phải bằng 2*embedding_dim = {2 * embedding_dim}")
        self.register_buffer("R", R.float(), persistent=False)
        self.u_tower = self._tower(n_items, rl_layers)
        self.i_tower = self._tower(n_users, rl_layers)
        self.user_emb = nn.Embedding(n_users, embedding_dim)
        self.item_emb = nn.Embedding(n_items, embedding_dim)
        mods = []
        for a, b in zip(layers[:-1], layers[1:]):
            mods += [nn.Linear(a, b), nn.ReLU(), nn.Dropout(dropout)]
        self.mlp_layers = nn.Sequential(*mods)
        self.output_layer = nn.Linear(rl_layers[-1] + layers[-1], 1, bias=False)
        nn.init.normal_(self.user_emb.weight, std=0.01)
        nn.init.normal_(self.item_emb.weight, std=0.01)
        self._cache = None

    @staticmethod
    def _tower(in_dim, sizes):
        mods, prev = [], in_dim
        for size in sizes:
            mods += [nn.Linear(prev, size), nn.ReLU()]
            prev = size
        return nn.Sequential(*mods)

    def train(self, mode: bool = True):
        self._cache = None  # trọng số sắp đổi -> bỏ cache tháp rl
        return super().train(mode)

    @torch.no_grad()
    def _precompute(self):
        self._cache = (self.u_tower(self.R), self.i_tower(self.R.t()))

    def forward(self, users, items):
        if self.training:
            pu, qi = self.u_tower(self.R[users]), self.i_tower(self.R[:, items].t())
        else:
            if self._cache is None:
                self._precompute()
            pu, qi = self._cache[0][users], self._cache[1][items]
        ml = self.mlp_layers(torch.cat([self.user_emb(users), self.item_emb(items)], dim=-1))
        return self.output_layer(torch.cat([pu * qi, ml], dim=-1)).squeeze(-1)


def interaction_matrix(train_df, n_users: int, n_items: int) -> torch.Tensor:
    """Ma trận 0/1 users x items CHỈ từ train_df."""
    R = torch.zeros(n_users, n_items)
    R[torch.as_tensor(train_df["user"].to_numpy()), torch.as_tensor(train_df["item"].to_numpy())] = 1.0
    return R
