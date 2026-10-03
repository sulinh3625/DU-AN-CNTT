from __future__ import annotations

import torch
import torch.nn as nn


class EarlyFusionModel(nn.Module):
    """Lớp cũ, KHÔNG dùng trong tuning/đánh giá cuối: kiến trúc trùng hệt MLP của src/models/neumf.py.

    Lớp này được viết theo cách hiểu ban đầu "early fusion = nối embedding user–item ngay ở đầu vào". Đối chiếu cho thấy
    nó chính là MLP đứng riêng (cùng 2 embedding → nối → tháp MLP → lớp output; test
    tests/test_tuning.py::test_early_fusion_is_architecturally_identical_to_mlp), nên bị loại (PREREG mục 8).

    Thuật ngữ đã chốt theo luận án của GVHD (Hồ Thị Linh, 2023) và báo cáo mục 2.3.4:
      - Early Fusion = nối biểu diễn của các view rồi MỘT mô hình dự đoán -> NeuMF (nối vector GMF với vector cuối MLP);
      - Late Fusion = trộn điểm của các mô hình huấn luyện riêng -> src/models/late_fusion.py (GMF + MLP);
      - MLP đứng riêng = mô hình DNN thuần, không phải phép hợp nhất MF + DNN.
    Tên lớp giữ nguyên vì run khám phá cũ và test còn dùng.
    """

    def __init__(self, n_users: int, n_items: int, embedding_dim: int, layers: list[int], dropout: float = 0.2):
        super().__init__()
        input_size = 2 * embedding_dim
        if not layers or layers[0] != input_size:
            raise ValueError(f"mlp_layers[0] phải bằng 2*embedding_dim = {input_size}")

        self.user_emb = nn.Embedding(n_users, embedding_dim)
        self.item_emb = nn.Embedding(n_items, embedding_dim)

        modules = []
        for in_size, out_size in zip(layers[:-1], layers[1:]):
            modules.extend([nn.Linear(in_size, out_size), nn.ReLU(), nn.Dropout(dropout)])
        self.mlp_layers = nn.Sequential(*modules)
        self.output_layer = nn.Linear(layers[-1], 1, bias=False)
        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.user_emb.weight, std=0.01)
        nn.init.normal_(self.item_emb.weight, std=0.01)
        for layer in self.mlp_layers:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)
        nn.init.xavier_uniform_(self.output_layer.weight)

    def vector(self, users, items):
        # Nối embedding user–item ở đầu vào — đúng như MLP.vector() trước tháp MLP (đây là DNN thuần, không phải
        # hợp nhất MF + DNN).
        return torch.cat([self.user_emb(users), self.item_emb(items)], dim=-1)

    def forward(self, users, items):
        x = self.mlp_layers(self.vector(users, items))
        return self.output_layer(x).squeeze(-1)