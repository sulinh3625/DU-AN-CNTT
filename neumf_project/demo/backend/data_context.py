"""Nạp đúng dữ liệu và checkpoint của đánh giá cuối (outputs/v2/final/seed42/, scripts/23_final_v2.py) cho demo.

Dữ liệu dựng lại bằng chính scripts/v2_common.py rồi đối chiếu với data.json của lần chạy; mô hình chỉ dùng ID được bọc
MaskedScorer/MaskedScoreFn như lúc chấm, nên số per-user khớp outputs/v2/final/seed42/per_user.csv.gz. Chỉ dùng khi kết
quả được tạo từ đúng file dữ liệu đã lọc hiện tại (data_md5 khớp outputs/data/manifest.json) — kiểm TRƯỚC khi dựng dữ
liệu, để demo không dựng tập kiểm thử của mẫu kiểm định cho một kết quả cũ. DEMO_V2_DIR=outputs/v2/dry_run để thử với
bản chạy thử (mẫu phát triển, tập xác thực).

Một "sản phẩm" là một product_code (mọi màu của một mẫu gộp lại). Tên, loại và ảnh lấy theo biến thể có article_id nhỏ
nhất — đúng biến thể mà features.group_by_product lấy thuộc tính.

Hai bộ dữ liệu (DATASETS), chọn trên thanh đầu trang: H&M (configs/v2.yaml, outputs/v2/final/) và Amazon Beauty
(configs/amazon.yaml, outputs/amazon/final/ — dữ liệu đối chứng, audit/PREREG_amazon.md). Cả hai chỉ nạp checkpoint
seed 42 của đánh giá cuối, không huấn luyện lại; chưa có kết quả thì demo báo lệnh cần chạy. Amazon: một sản phẩm là
một asin; tên, thương hiệu, danh mục, giá, ảnh lấy từ data/processed/amazon/items.csv.gz (scripts/21_build_features.py).

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
from src.baselines.hybrid import COMPONENTS as HYBRID_COMPONENTS, TraditionalHybrid  # noqa: E402
from src.evaluation.full_ranking import EvalRecord  # noqa: E402
from src.evaluation.ranking_utils import deterministic_tie_key  # noqa: E402
from src.models.late_fusion import LateFusion  # noqa: E402

V2_DIR = Path(os.environ.get("DEMO_V2_DIR", str(PROJECT_ROOT / "outputs" / "v2" / "final")))
if not V2_DIR.is_absolute():
    V2_DIR = PROJECT_ROOT / V2_DIR
# Bộ dữ liệu của demo: cấu hình, thư mục kết quả đánh giá cuối, chữ hiển thị.
DATASETS = {
    "hm": dict(config="configs/v2.yaml", label="H&M", tagline="gợi ý thời trang", final_cmd="v2-final",
               history_note="Dataset H&M chỉ có lịch sử mua, không có lịch sử xem.",
               item_note="Một sản phẩm = một mẫu (<code>product_code</code>), mọi màu gộp lại; ảnh và tên lấy theo màu "
                         "đầu tiên của mẫu."),
    "amazon": dict(config="configs/amazon.yaml", label="Amazon Beauty", tagline="gợi ý mỹ phẩm (dữ liệu đối chứng)",
                   final_cmd="amazon-final",
                   history_note="Amazon chỉ có đánh giá sản phẩm: mỗi đánh giá coi là một lần mua (phản hồi ẩn).",
                   item_note="Một sản phẩm = một <code>asin</code>; tên, thương hiệu, danh mục, giá và ảnh lấy từ "
                             "metadata Amazon 2014."),
}
CONFIGS = {k: V.read_config(PROJECT_ROOT / d["config"]) for k, d in DATASETS.items()}


def results_dir(dataset: str) -> Path:
    """Thư mục kết quả đánh giá cuối của bộ dữ liệu (H&M: V2_DIR, đổi được bằng DEMO_V2_DIR)."""
    return V2_DIR if dataset == "hm" else PROJECT_ROOT / CONFIGS[dataset]["out_dir"] / "final"
SEED = 42  # 23_final_v2.py chỉ lưu checkpoint của seed 42
# tên hiển thị -> mã mô hình trong scripts/v2_common.py
V2_NEURAL = {"NeuMF-F": "neumf_f", "GMF-F": "gmf_f", "MLP-F": "mlp_f", "NeuMF": "neumf", "GMF": "gmf", "MLP": "mlp"}
V2_STATIC = {"MostPopular": "popularity", "MostPopular-Recent": "recent_pop", "Content": "content",
             "ItemKNN": "itemknn", "UserKNN": "userknn"}
V2_ORDER = ["NeuMF-F", "LateFusion-F", "GMF-F", "MLP-F", "NeuMF", "GMF", "MLP", "BPR-MF", "Hybrid-CBCF", "UserKNN",
            "ItemKNN", "MostPopular-Recent", "Content", "MostPopular"]
# Mô hình lai truyền thống (bổ sung sau đánh giá cuối, scripts/25_bosung.py): chỉ dựng khi <kết quả>/bosung/results.json
# đã có — tức tập kiểm thử đã được chấm cho mô hình này theo audit/PREREG_bosung.md; demo không chấm trước kế hoạch.
HYBRID = "Hybrid-CBCF"
BPR_CHECKPOINT = "bpr.npz"  # mảng P (users x d), Q (items x d)
ARTICLES_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "articles.csv"
CUSTOMERS_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "customers.csv"
# K của demo = K của cấu hình ∪ DEMO_EXTRA_K (báo cáo dùng K = 5, 10, 15, 20): tính trên cùng thứ hạng nên số @5/@10/@20
# vẫn khớp file kết quả; không sửa configs/ (cấu hình huấn luyện, đánh giá và mã băm v2).
DEMO_EXTRA_K = (15, 20)
ARTICLE_COLUMNS = ["article_id", "product_code", "prod_name", "product_type_name", "product_group_name",
                   "index_group_name"]


def v2_data_mismatch(v2_dir: Path = V2_DIR, seed: int = SEED, cfg: dict | None = None) -> str | None:
    """Lý do kết quả trong v2_dir không dùng được với file dữ liệu đã lọc hiện tại; None = dùng được.

    So data_md5 mà 23_final_v2.py ghi vào data.json với MD5 trong outputs/data/manifest.json của đúng mẫu (bản chạy thử:
    mẫu phát triển; đánh giá cuối: mẫu kiểm định). Gọi TRƯỚC khi dựng dữ liệu: dựng lại mẫu kiểm định kèm tập kiểm thử
    cho một kết quả cũ là mở tập kiểm thử ngoài đánh giá cuối. cfg: cấu hình của bộ dữ liệu (mặc định của tiến trình)."""
    results = json.loads((v2_dir / f"seed{seed}" / "results.json").read_text(encoding="utf-8"))
    info = json.loads((v2_dir / "data.json").read_text(encoding="utf-8"))
    sample = "dev" if str(results.get("evaluated_on", "")).startswith("dry-run") else "holdout"
    path = V.MANIFEST if cfg is None else V.manifest_path(cfg)
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    want = manifest.get(V.data_name(sample, cfg), {}).get("md5")
    if want and info.get("data_md5") == want:
        return None
    return (f"{v2_dir.as_posix()} được tạo từ dữ liệu khác file đã lọc hiện tại của mẫu {sample} (data_md5 "
            f"{info.get('data_md5')} ≠ {want}) — chạy lại đánh giá cuối trước.")


def unavailable_reason(dataset: str = "hm", seed: int = SEED) -> str | None:
    """Vì sao demo chưa nạp được bộ dữ liệu (thiếu kết quả / checkpoint, hoặc kết quả của dữ liệu khác); None = nạp được.
    Demo không huấn luyện gì: thiếu thì chỉ báo lệnh cần chạy."""
    root = results_dir(dataset)
    d = root / f"seed{seed}"
    files = [d / "results.json", root / "data.json", *(d / f"{k}.pt" for k in V2_NEURAL.values())]
    # thư mục kết quả có thể nằm ngoài dự án (DEMO_V2_DIR, out_dir tuyệt đối): khi đó in đường dẫn đầy đủ
    missing = [(f.relative_to(PROJECT_ROOT) if f.is_relative_to(PROJECT_ROOT) else f).as_posix()
               for f in files if not f.exists()]
    if missing:
        return (f"Chưa có kết quả đánh giá cuối {DATASETS[dataset]['label']} ({missing[0]}"
                f"{f' và {len(missing) - 1} file khác' if len(missing) > 1 else ''}) — chạy "
                f"`python run.py {DATASETS[dataset]['final_cmd']} --reason \"...\"` trước; demo không tự huấn luyện.")
    return v2_data_mismatch(root, seed, CONFIGS[dataset])


def v2_available(seed: int = SEED, dataset: str = "hm") -> bool:
    return unavailable_reason(dataset, seed) is None


def product_table(articles: pd.DataFrame, item_product: np.ndarray) -> pd.DataFrame:
    """Một dòng mỗi sản phẩm (index = chỉ số item, theo item_product): cột của biến thể có article_id nhỏ nhất và số
    màu (số biến thể) của mẫu. Sản phẩm không có trong articles thì ghi "Unknown"."""
    a = articles.sort_values("article_id")
    out = a.drop_duplicates("product_code").set_index("product_code").reindex(item_product)
    out["n_colours"] = a.groupby("product_code").size().reindex(item_product, fill_value=0).to_numpy()
    out = out.reset_index(drop=True).fillna("Unknown")
    out.index.name = "item"
    return out


def amazon_table(items: pd.DataFrame, item_product: np.ndarray) -> pd.DataFrame:
    """Như product_table cho Amazon (items.csv.gz của 21_build_features.py, index = mã asin): article_id = asin, tên =
    title, loại = danh mục sâu nhất, nhóm = danh mục cấp 2, khu vực (index_group_name) = danh mục cấp 1; thêm subtitle
    (thương hiệu · loại · giá) và image_url (imUrl của Amazon)."""
    it = items.reindex(item_product)
    cat = it[["category_1", "category_2", "category_3"]].fillna("").astype(str)
    leaf = (cat["category_3"].where(cat["category_3"] != "", cat["category_2"]).where(lambda s: s != "", cat["category_1"])
            .replace("", "Beauty"))
    asin = it["asin"].fillna("").astype(str)
    title = it["title"].fillna("").astype(str)
    price = it["price"].map(lambda p: f"${p:.2f}" if pd.notna(p) else "")
    brand = it["brand"].fillna("").astype(str)
    out = pd.DataFrame({
        "article_id": asin.to_numpy(), "prod_name": title.where(title != "", asin).to_numpy(),
        "product_type_name": leaf.to_numpy(), "product_group_name": cat["category_2"].to_numpy(),
        "index_group_name": cat["category_1"].replace("", "Khác").to_numpy(), "n_colours": 1,
        "subtitle": [" · ".join(x for x in row if x) for row in zip(brand, leaf, price)],
        "image_url": it["imUrl"].fillna("").astype(str).to_numpy()})
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
    def __init__(self, load_customers: bool = True, dataset: str = "hm"):
        why = unavailable_reason(dataset, SEED)
        if why:
            raise ValueError(why)
        self.dataset, cfg = dataset, CONFIGS[dataset]
        self.results_dir = root = results_dir(dataset)
        seed_dir = root / f"seed{SEED}"
        results = json.loads((seed_dir / "results.json").read_text(encoding="utf-8"))
        info = json.loads((root / "data.json").read_text(encoding="utf-8"))
        dry = str(results.get("evaluated_on", "")).startswith("dry-run")
        self.run_tag = f"{'v2' if dataset == 'hm' else dataset}_seed{SEED}"
        self.k_values = sorted({*(int(k) for k in cfg["evaluation"]["k_values"]), *DEMO_EXTRA_K})
        self.tie_seed = cfg["evaluation"]["tie_break_seed"]
        print(f"[demo] checkpoint {seed_dir.relative_to(PROJECT_ROOT).as_posix()} "
              f"({'chạy thử trên mẫu phát triển' if dry else 'mẫu kiểm định'}, commit "
              f"{str(results['provenance'].get('git_commit'))[:7]})")

        D = V.load_data("dev" if dry else "holdout", with_test=not dry, cfg=cfg)
        ev = D.val if dry else D.test
        stage = info["val" if dry else "test"]
        if (len(ev.records), len(ev.targets)) != (stage["users"], stage["targets"]):
            raise ValueError(f"Dữ liệu tái tạo ({len(ev.records)} user, {len(ev.targets)} cặp đúng) không khớp "
                             f"{root.name}/data.json ({stage['users']}, {stage['targets']}).")
        day0 = np.datetime64(D.meta["day0"], "D")
        self.evaluated_on = "validation" if dry else "test"
        self.n_users, self.n_items = D.n_users, D.n_items
        self.customer_ids = np.asarray([str(c) for c in D.user_raw], dtype=object)
        self.user2idx = {cid: i for i, cid in enumerate(self.customer_ids)}
        self.item_product = D.item_product
        self.records = {int(r.user): r for r in ev.records}  # đúng tập ứng viên và sản phẩm đích lúc chấm
        self.scoreable_items = np.flatnonzero(ev.scoreable)  # sản phẩm có dữ liệu huấn luyện trước mốc
        self.train_pos = [set(int(i) for i in s) for s in ev.train_pos]
        self.target_items = {u: sorted(int(i) for i in r.positives) for u, r in self.records.items()}
        self.target_users = np.array(sorted(self.target_items), dtype=np.int64)
        # Lịch sử hiển thị = đúng dữ liệu mô hình đã học (mọi cặp trước mốc), ngày = ngày mua đầu.
        tr = ev.train
        self.train_df = tr.assign(date=day0 + tr["day"].to_numpy().astype("timedelta64[D]"))
        self.train_item_counts = np.bincount(tr["item"].to_numpy(), minlength=self.n_items)
        self.train_user_counts = np.bincount(tr["user"].to_numpy(), minlength=self.n_users)
        self.run_metadata = {"evaluated_on": self.evaluated_on, "provenance": results["provenance"], "dry_run": dry,
                             "n_test_users": len(ev.records), "n_candidates": int(ev.scoreable.sum()),
                             "targets": len(ev.targets), "train_pairs": len(tr), "n_kept_pairs": len(D.kept),
                             "date_min": str(day0 + int(D.kept["day"].min())), "val_start": cfg["val_start"],
                             "test_start": cfg["test_start"], "k_core": cfg["k_core"]}

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
        bosung = root / "bosung" / "results.json"
        parts = [V.DISPLAY[k] for k in HYBRID_COMPONENTS]
        if bosung.exists() and set(parts) <= set(self.scorers):
            p = json.loads(bosung.read_text(encoding="utf-8"))["config"]["params"]
            self.scorers[HYBRID] = TraditionalHybrid([self.scorers[n] for n in parts], p["fusion"], p.get("weights"))
        else:
            self.unavailable[HYBRID] = ("Chưa chấm tập kiểm thử cho mô hình bổ sung — chạy `python run.py "
                                        f"{'' if dataset == 'hm' else 'amazon-'}bosung-final --reason \"...\"`.")
        bpr_path = seed_dir / BPR_CHECKPOINT
        if bpr_path.exists():
            self.scorers["BPR-MF"] = V.MaskedScoreFn(BPRMFBaseline.load(bpr_path), ev.scoreable, D.n_id_items)
        else:
            self.unavailable["BPR-MF"] = f"Thiếu {bpr_path.relative_to(PROJECT_ROOT).as_posix()} — demo không tự train lại."
        self.userknn_params = configs.get("userknn")

        self.articles = self._load_articles()
        self.user_age = self._load_ages() if load_customers and dataset == "hm" else pd.Series(dtype=float)

    def _load_articles(self) -> pd.DataFrame:
        if self.dataset != "hm":
            path = PROJECT_ROOT / CONFIGS[self.dataset]["features"]["items"]
            if not path.exists():
                raise FileNotFoundError(f"Thiếu {path.relative_to(PROJECT_ROOT).as_posix()} — chạy `python run.py "
                                        "amazon-data`.")
            return amazon_table(pd.read_csv(path, index_col="item", dtype={"asin": str}), self.item_product)
        if not ARTICLES_PATH.exists():
            raise FileNotFoundError(f"Thiếu {ARTICLES_PATH} — chép articles.csv (và customers.csv) của bộ H&M "
                                    "vào data/raw/hm/ cạnh transactions_train.csv (demo/README.md mục 1).")
        arts = pd.read_csv(ARTICLES_PATH, dtype={"article_id": "string"}, usecols=ARTICLE_COLUMNS)
        arts["article_id"] = arts["article_id"].str.zfill(10)
        out = product_table(arts, self.item_product)
        out["subtitle"] = out["product_type_name"].astype(str) + " · " + out["n_colours"].astype(str) + " màu"
        out["image_url"] = "/api/image/" + out["article_id"].astype(str)
        return out

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

    def record(self, u: int) -> EvalRecord:
        """Ứng viên và sản phẩm đích của khách u: đúng record lúc chấm nếu khách có sản phẩm đích; khách có lịch sử nhưng
        không mua món mới nào trong giai đoạn đánh giá thì ứng viên = sản phẩm có dữ liệu huấn luyện trừ món đã mua,
        không có sản phẩm đích (vẫn gợi ý được bằng mô hình, chỉ không có gì để chấm)."""
        rec = self.records.get(int(u))
        if rec is not None:
            return rec
        bought = np.fromiter(self.train_pos[int(u)], dtype=np.int64, count=len(self.train_pos[int(u)]))
        cand = np.setdiff1d(self.scoreable_items, bought)
        return EvalRecord(int(u), -1, cand, np.empty(0, dtype=np.int64))

    def popular_items(self, k: int) -> tuple[list[int], list[int]]:
        """K sản phẩm phổ biến nhất cho khách mới (Most Popular): sản phẩm có dữ liệu huấn luyện xếp theo số khách đã mua
        trước mốc, bằng nhau thì theo khoá tất định. Trả về (sản phẩm, số khách đã mua)."""
        items = self.scoreable_items
        counts = self.train_item_counts[items]
        order = np.lexsort((deterministic_tie_key(-1, items, self.tie_seed), -counts))[:k]
        return items[order].tolist(), counts[order].tolist()

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
            "subtitle": a["subtitle"],
            # Amazon thiếu imUrl -> ô thay thế của máy chủ
            "image_url": a["image_url"] or f"/api/image/{a['article_id']}?dataset={self.dataset}",
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
        d = DATASETS[self.dataset]
        return {
            "dataset": self.dataset, "dataset_label": d["label"], "tagline": d["tagline"],
            "history_note": d["history_note"], "item_note": d["item_note"], "seed": SEED,
            "config": d["config"], "run_tag": self.run_tag,
            "evaluated_on": self.evaluated_on, "dry_run": m["dry_run"], "k_core": m["k_core"],
            "date_min": m["date_min"], "date_max": m["test_start"], "val_start": m["val_start"],
            "test_start": m["test_start"], "n_users": self.n_users, "n_items": self.n_items,
            "n_interactions": m["n_kept_pairs"], "k_values": self.k_values, "models": self.available_models,
            "unavailable_models": self.unavailable, "has_neighbors": "UserKNN" in self.scorers,
            "commit": str(m["provenance"].get("git_commit") or "")[:7], "n_candidates": m["n_candidates"],
            "n_targets": m["targets"],
        }
