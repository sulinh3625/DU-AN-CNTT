"""Nạp đúng dữ liệu và checkpoint của đánh giá cuối (outputs/v2/final/seed42/, scripts/23_final_v2.py) cho demo.

Dữ liệu dựng lại bằng chính scripts/v2_common.py rồi đối chiếu với data.json của lần chạy; mô hình chỉ dùng ID được bọc
MaskedScorer/MaskedScoreFn như lúc chấm, nên số per-user khớp outputs/v2/final/seed42/per_user.csv.gz. Chỉ dùng khi kết
quả được tạo từ đúng file dữ liệu đã lọc hiện tại (data_md5 khớp outputs/data/manifest.json) — kiểm TRƯỚC khi dựng dữ
liệu, để demo không dựng tập kiểm thử của mẫu kiểm định cho một kết quả cũ. DEMO_V2_DIR=outputs/v2/dry_run để thử với
bản chạy thử (mẫu phát triển, tập xác thực).

Một "sản phẩm" là một product_code (mọi màu của một mẫu gộp lại). Tên, loại và ảnh lấy theo biến thể có article_id nhỏ
nhất — đúng biến thể mà features.group_by_product lấy thuộc tính.

Chỉ import hàm từ src/ và scripts/, không sửa code huấn luyện.
"""
from __future__ import annotations

import json
import os
import sys
from functools import cached_property
from pathlib import Path

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_ROOT = PROJECT_ROOT / "demo"
for p in (PROJECT_ROOT, PROJECT_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import v2_common as V  # noqa: E402
from src.baselines import BPRMFBaseline  # noqa: E402
from src.data_pipeline.features import DAY0  # noqa: E402
from src.models.late_fusion import LateFusion  # noqa: E402

V2_DIR = Path(os.environ.get("DEMO_V2_DIR", str(PROJECT_ROOT / "outputs" / "v2" / "final")))
if not V2_DIR.is_absolute():
    V2_DIR = PROJECT_ROOT / V2_DIR
SEED = 42  # 23_final_v2.py chỉ lưu checkpoint của seed 42
# tên hiển thị -> mã mô hình trong scripts/v2_common.py
V2_NEURAL = {"NeuMF-F": "neumf_f", "GMF-F": "gmf_f", "MLP-F": "mlp_f", "NeuMF": "neumf", "GMF": "gmf", "MLP": "mlp"}
V2_STATIC = {"MostPopular": "popularity", "MostPopular-Recent": "recent_pop", "Content": "content",
             "ItemKNN": "itemknn", "UserKNN": "userknn"}
V2_ORDER = ["NeuMF-F", "LateFusion-F", "GMF-F", "MLP-F", "NeuMF", "GMF", "MLP", "BPR-MF", "UserKNN", "ItemKNN",
            "MostPopular-Recent", "Content", "MostPopular"]
BPR_CHECKPOINT = "bpr.npz"  # mảng P (users x d), Q (items x d)
ARTICLES_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "articles.csv"
CUSTOMERS_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "customers.csv"
# K của demo = K của cấu hình ∪ DEMO_EXTRA_K: chỉ để xem danh sách dài hơn, tính trên cùng thứ hạng nên số @5/@10 vẫn
# khớp file kết quả; không sửa configs/ (cấu hình huấn luyện, đánh giá và mã băm v2).
DEMO_EXTRA_K = (20,)
ARTICLE_COLUMNS = ["article_id", "product_code", "prod_name", "product_type_name", "product_group_name",
                   "index_group_name"]


def v2_data_mismatch(v2_dir: Path = V2_DIR, seed: int = SEED) -> str | None:
    """Lý do kết quả trong v2_dir không dùng được với file dữ liệu đã lọc hiện tại; None = dùng được.

    So data_md5 mà 23_final_v2.py ghi vào data.json với MD5 trong outputs/data/manifest.json của đúng mẫu (bản chạy thử:
    mẫu phát triển; đánh giá cuối: mẫu kiểm định). Gọi TRƯỚC khi dựng dữ liệu: dựng lại mẫu kiểm định kèm tập kiểm thử
    cho một kết quả cũ là mở tập kiểm thử ngoài đánh giá cuối."""
    results = json.loads((v2_dir / f"seed{seed}" / "results.json").read_text(encoding="utf-8"))
    info = json.loads((v2_dir / "data.json").read_text(encoding="utf-8"))
    sample = "dev" if str(results.get("evaluated_on", "")).startswith("dry-run") else "holdout"
    manifest = json.loads(V.MANIFEST.read_text(encoding="utf-8")) if V.MANIFEST.exists() else {}
    want = manifest.get(V.data_name(sample), {}).get("md5")
    if want and info.get("data_md5") == want:
        return None
    return (f"{v2_dir.as_posix()} được tạo từ dữ liệu khác file đã lọc hiện tại của mẫu {sample} (data_md5 "
            f"{info.get('data_md5')} ≠ {want}) — chạy lại đánh giá cuối trước.")


def v2_available(seed: int = SEED) -> bool:
    d = V2_DIR / f"seed{seed}"
    files = [d / "results.json", V2_DIR / "data.json", *(d / f"{k}.pt" for k in V2_NEURAL.values())]
    return all(f.exists() for f in files) and v2_data_mismatch(V2_DIR, seed) is None


def product_table(articles: pd.DataFrame, item_product: np.ndarray) -> pd.DataFrame:
    """Một dòng mỗi sản phẩm (index = chỉ số item, theo item_product): cột của biến thể có article_id nhỏ nhất và số
    màu (số biến thể) của mẫu. Sản phẩm không có trong articles thì ghi "Unknown"."""
    a = articles.sort_values("article_id")
    out = a.drop_duplicates("product_code").set_index("product_code").reindex(item_product)
    out["n_colours"] = a.groupby("product_code").size().reindex(item_product, fill_value=0).to_numpy()
    out = out.reset_index(drop=True).fillna("Unknown")
    out.index.name = "item"
    return out


def user_table(customer_ids: np.ndarray, target_items: dict, train_df: pd.DataFrame, articles: pd.DataFrame,
               user_age: pd.Series) -> pd.DataFrame:
    """Danh sách chọn khách của màn hình Admin: một dòng cho mỗi khách có sản phẩm đích, index = customer_id.

    Cột: số món đã mua (cặp mô hình đã học), số món đích, nhóm giao dịch theo tam phân vị số món đã mua (low / mid /
    high, ngưỡng ở attrs["thresholds"]), khu vực mua nhiều nhất (index_group_name) kèm tỉ lệ, tuổi (customers.csv, có
    thể thiếu), ngày mua đầu tiên / gần nhất (cột date của train_df)."""
    users = np.array(sorted(target_items), dtype=np.int64)
    tr = train_df[train_df["user"].isin(users)]
    by_user = tr.groupby("user")
    area = pd.crosstab(tr["user"].to_numpy(), articles["index_group_name"].to_numpy()[tr["item"].to_numpy()])
    dates = by_user["date"].agg(["min", "max"]).reindex(users)
    df = pd.DataFrame({
        "customer_id": customer_ids[users].astype(str),
        "train_count": by_user.size().reindex(users, fill_value=0).to_numpy(),
        "n_targets": [len(target_items[u]) for u in users],
        "area": area.idxmax(axis=1).reindex(users).to_numpy(),
        "area_share": (area.max(axis=1) / area.sum(axis=1)).reindex(users).round(3).to_numpy(),
        "age": user_age.reindex(users).to_numpy(dtype=float),
        "first_date": dates["min"].dt.strftime("%Y-%m-%d").to_numpy(),
        "last_date": dates["max"].dt.strftime("%Y-%m-%d").to_numpy(),
    })
    t1, t2 = (float(x) for x in np.quantile(df["train_count"], [1 / 3, 2 / 3]))
    n = df["train_count"]
    df["bucket"] = np.where(n <= t1, "low", np.where(n <= t2, "mid", "high"))
    df.index = df["customer_id"].to_numpy()
    df.attrs["thresholds"] = (t1, t2)
    return df


class DataContext:
    def __init__(self, load_customers: bool = True):
        why = v2_data_mismatch(V2_DIR, SEED)
        if why:
            raise ValueError(why)
        seed_dir = V2_DIR / f"seed{SEED}"
        results = json.loads((seed_dir / "results.json").read_text(encoding="utf-8"))
        info = json.loads((V2_DIR / "data.json").read_text(encoding="utf-8"))
        dry = str(results.get("evaluated_on", "")).startswith("dry-run")
        self.run_tag = f"v2_seed{SEED}"
        self.k_values = sorted({*(int(k) for k in V.CFG["evaluation"]["k_values"]), *DEMO_EXTRA_K})
        self.tie_seed = V.CFG["evaluation"]["tie_break_seed"]
        print(f"[demo] checkpoint {seed_dir.relative_to(PROJECT_ROOT).as_posix()} "
              f"({'chạy thử trên mẫu phát triển' if dry else 'mẫu kiểm định'}, commit "
              f"{str(results['provenance'].get('git_commit'))[:7]})")

        D = V.load_data("dev" if dry else "holdout", with_test=not dry)
        ev = D.val if dry else D.test
        stage = info["val" if dry else "test"]
        if (len(ev.records), len(ev.targets)) != (stage["users"], stage["targets"]):
            raise ValueError(f"Dữ liệu tái tạo ({len(ev.records)} user, {len(ev.targets)} cặp đúng) không khớp "
                             f"{V2_DIR.name}/data.json ({stage['users']}, {stage['targets']}).")
        self.evaluated_on = "validation" if dry else "test"
        self.n_users, self.n_items = D.n_users, D.n_items
        self.customer_ids = np.asarray([str(c) for c in D.user_raw], dtype=object)
        self.user2idx = {cid: i for i, cid in enumerate(self.customer_ids)}
        self.item_product = D.item_product
        self.records = {int(r.user): r for r in ev.records}  # đúng tập ứng viên và sản phẩm đích lúc chấm
        self.train_pos = [set(int(i) for i in s) for s in ev.train_pos]
        self.target_items = {u: sorted(int(i) for i in r.positives) for u, r in self.records.items()}
        self.target_users = np.array(sorted(self.target_items), dtype=np.int64)
        # Lịch sử hiển thị = đúng dữ liệu mô hình đã học (mọi cặp trước mốc), ngày = ngày mua đầu.
        tr = ev.train
        self.train_df = tr.assign(date=DAY0 + tr["day"].to_numpy().astype("timedelta64[D]"))
        self.train_item_counts = np.bincount(tr["item"].to_numpy(), minlength=self.n_items)
        self.train_user_counts = np.bincount(tr["user"].to_numpy(), minlength=self.n_users)
        self.run_metadata = {"evaluated_on": self.evaluated_on, "provenance": results["provenance"], "dry_run": dry,
                             "n_test_users": len(ev.records), "n_candidates": int(ev.scoreable.sum()),
                             "targets": len(ev.targets), "train_pairs": len(tr), "n_kept_pairs": len(D.kept),
                             "date_min": str(DAY0 + int(D.kept["day"].min())), "val_start": V.CFG["val_start"],
                             "test_start": V.CFG["test_start"], "k_core": V.CFG["k_core"]}

        self.models: dict[str, torch.nn.Module] = {}
        self.scorers: dict = {}  # mô hình không phải mạng PyTorch: tên -> đối tượng có score_items(user, items)
        self.unavailable: dict[str, str] = {}
        configs = results.get("configs", {})
        for name, key in V2_NEURAL.items():
            path = seed_dir / f"{key}.pt"
            if key not in configs or not path.exists():
                self.unavailable[name] = f"Thiếu cấu hình hoặc checkpoint {path.relative_to(PROJECT_ROOT).as_posix()}"
                continue
            net = V.build_torch(key, configs[key], D, "cpu")
            net.load_state_dict(torch.load(path, map_location="cpu"))
            net.eval()
            self.models[name] = V.torch_scorer(key, net, ev, D, "cpu").eval()
        if "late_f" in configs and {"GMF-F", "MLP-F"} <= set(self.models):
            self.scorers["LateFusion-F"] = LateFusion(self.models["GMF-F"], self.models["MLP-F"], configs["late_f"]["w"])
        for name, key in V2_STATIC.items():
            if key in configs:
                self.scorers[name] = V.score_fn(key, configs[key], D, ev)
        bpr_path = seed_dir / BPR_CHECKPOINT
        if bpr_path.exists():
            self.scorers["BPR-MF"] = V.MaskedScoreFn(BPRMFBaseline.load(bpr_path), ev.scoreable, D.n_id_items)
        else:
            self.unavailable["BPR-MF"] = f"Thiếu {bpr_path.relative_to(PROJECT_ROOT).as_posix()} — demo không tự train lại."
        self.userknn_params = configs.get("userknn")

        self.articles = self._load_articles()
        self.user_age = self._load_ages() if load_customers else pd.Series(dtype=float)

    def _load_articles(self) -> pd.DataFrame:
        if not ARTICLES_PATH.exists():
            raise FileNotFoundError(f"Thiếu {ARTICLES_PATH} — chép articles.csv (và customers.csv) của bộ H&M "
                                    "vào data/raw/hm/ cạnh transactions_train.csv (demo/README.md mục 1).")
        arts = pd.read_csv(ARTICLES_PATH, dtype={"article_id": "string"}, usecols=ARTICLE_COLUMNS)
        arts["article_id"] = arts["article_id"].str.zfill(10)
        return product_table(arts, self.item_product)

    def _load_ages(self) -> pd.Series:
        """Tuổi theo user idx (chỉ user có trong dữ liệu), hiện trong danh sách chọn khách; thiếu file thì trả rỗng."""
        if not CUSTOMERS_PATH.exists():
            return pd.Series(dtype=float)
        with CUSTOMERS_PATH.open(encoding="utf-8") as f:
            first = f.readline()
        # Bản customers.csv trong repo có thêm dòng "Column1;..." phía trên header và phân cách bằng ';'.
        sep = ";" if ";" in first else ","
        skip = 1 if first.startswith("Column1") else 0
        cust = pd.read_csv(CUSTOMERS_PATH, sep=sep, skiprows=skip, usecols=["customer_id", "age"])
        cust = cust.dropna(subset=["age"])
        cust = cust[cust["customer_id"].isin(self.user2idx)]
        return pd.Series(cust["age"].to_numpy(dtype=float), index=cust["customer_id"].map(self.user2idx).to_numpy())

    # ------------------------------------------------------------- accessors
    @property
    def available_models(self) -> list[str]:
        return [m for m in V2_ORDER if m in self.models or m in self.scorers]

    @cached_property
    def users(self) -> pd.DataFrame:
        """Bảng khách cho danh sách chọn khách (user_table), dựng một lần khi cần."""
        return user_table(self.customer_ids, self.target_items, self.train_df, self.articles, self.user_age)

    def resolve_user(self, customer_id: str) -> int:
        idx = self.user2idx.get(customer_id.strip())
        if idx is None:
            raise KeyError(customer_id)
        return idx

    def item_info(self, item: int) -> dict:
        a = self.articles.iloc[int(item)]
        return {
            "item_idx": int(item),
            "product_code": int(self.item_product[int(item)]),
            "article_id": a["article_id"],
            "prod_name": a["prod_name"],
            "product_type_name": a["product_type_name"],
            "product_group_name": a["product_group_name"],
            "index_group_name": a["index_group_name"],
            "n_colours": int(a["n_colours"]),
        }

    def history(self, u: int) -> list[dict]:
        """Sản phẩm mô hình đã học của khách (mọi cặp trước mốc), sắp theo ngày mua đầu."""
        rows = self.train_df[self.train_df["user"] == u].sort_values(["day", "item"])
        return [{**self.item_info(r.item), "t_dat": str(r.date.date())} for r in rows.itertuples(index=False)]

    def neighbors(self, u: int, top: int = 10) -> list[dict] | None:
        """Top-K khách tương đồng nhất theo UserKNN (cosine trên lịch sử mua) — None nếu không có UserKNN."""
        knn = self.scorers.get("UserKNN")
        if knn is None:
            return None
        knn = knn.fn  # MaskedScoreFn bọc UserKNNBaseline
        mine = self.train_pos[u]
        targets = set(self.target_items.get(u, []))
        out = []
        for nb in knn.neighbors(u, top):
            v = nb["user"]
            theirs = self.train_pos[v]
            out.append({
                "customer_id": self.customer_ids[v], "similarity": nb["similarity"], "n_common": nb["n_common"],
                "train_count": int(self.train_user_counts[v]),
                "common_items": [self.item_info(i) for i in sorted(mine & theirs,
                                                                   key=lambda i: -self.train_item_counts[i])[:3]],
                "bought_target": [self.item_info(i) for i in sorted(theirs & targets)],
            })
        return out

    def summary(self) -> dict:
        m = self.run_metadata
        return {
            "dataset": "H&M Personalized Fashion Recommendations", "config": "configs/v2.yaml", "run_tag": self.run_tag,
            "evaluated_on": self.evaluated_on, "dry_run": m["dry_run"], "k_core": m["k_core"],
            "date_min": m["date_min"], "date_max": m["test_start"], "val_start": m["val_start"],
            "test_start": m["test_start"], "n_users": self.n_users, "n_items": self.n_items,
            "n_interactions": m["n_kept_pairs"], "k_values": self.k_values, "models": self.available_models,
            "unavailable_models": self.unavailable, "has_neighbors": "UserKNN" in self.scorers,
            "commit": str(m["provenance"].get("git_commit") or "")[:7], "n_candidates": m["n_candidates"],
            "n_targets": m["targets"],
        }
