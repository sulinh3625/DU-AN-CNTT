from __future__ import annotations

import os
import random
import numpy as np
import torch


def seed_everything(seed: int):
    # GPU mặc định không tất định (cuBLAS, cộng dồn gradient Embedding) -> 2 lần chạy
    # cùng seed ra số khác nhau. CUBLAS_WORKSPACE_CONFIG phải có trước lần gọi cuBLAS đầu tiên.
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
