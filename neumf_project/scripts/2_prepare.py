"""Chuẩn bị dữ liệu đã lọc của giao thức v2 — mọi mô hình đọc cùng file này, kiểm bằng MD5 (scripts/common.py).

python run.py prepare                                (= python scripts/2_prepare.py)
python scripts/2_prepare.py --sample holdout   # chỉ một mẫu
python run.py amazon-data                            # Amazon Beauty (NEUMF_CONFIG=configs/amazon.yaml)"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

import common as V
from src.data_pipeline.adapters import AmazonAdapter, HMAdapter
from src.data_pipeline.features import DAY0, check_product_code, product_code_of, to_day
from src.data_pipeline.protocol_v2 import prepare_pairs, save_pairs
from src.utils.io import write_json

ARTICLES = V.PROJECT_ROOT / "data" / "raw" / "hm" / "articles.csv"


def export(sample_csv, out, test_start: str, k_core: int, dataset: str = "hm", day0=DAY0) -> dict:
    """Ghi file cặp đã lọc của một mẫu; trả về mục manifest (chưa có file, commit) — chỉ số liệu trước test_start."""
    if dataset == "hm":
        events, item_map = HMAdapter(sample_csv).load_events(), product_code_of
    else:
        events, item_map = AmazonAdapter(sample_csv).load_events(), (lambda ids: np.asarray(ids, dtype=np.int64))
    pairs = prepare_pairs(events, test_start, k_core, item_map=item_map, day0=day0)
    md5 = save_pairs(pairs, out)
    pre = events[events["timestamp"] < pd.Timestamp(test_start)]
    core = pairs[pairs["in_kcore"]]
    return dict(
        md5=md5, rows=len(pairs), customers=int(core["user_id"].nunique()), products=int(core["item_id"].nunique()),
        kcore_pairs=len(core), k_core=k_core, test_start=test_start,
        before_test_start=dict(
            articles=int(pre["item_raw"].nunique()), products=len(np.unique(item_map(pre["item_raw"]))),
            article_pairs=len(pre[["user_raw", "item_raw"]].drop_duplicates()),
            product_pairs=int((pairs["first_day"] < to_day(np.datetime64(test_start), day0)).sum())))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", choices=list(V.CFG["samples"]), help="chỉ chuẩn bị một mẫu (mặc định: mọi mẫu)")
    args = ap.parse_args()
    print(f"Dữ liệu: {V.NAME} (configs/{V.CONFIG.name})", flush=True)
    if V.DATASET == "hm" and ARTICLES.exists():
        try:
            check_product_code(ARTICLES)
        except ValueError as e:
            raise SystemExit(str(e)) from None
        print("articles.csv: product_code = article_id // 1000 ở mọi dòng", flush=True)
    V.DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(V.MANIFEST.read_text(encoding="utf-8")) if V.MANIFEST.exists() else {}
    prov = V.provenance()
    done = set()
    for sample in [args.sample] if args.sample else V.CFG["samples"]:
        name = V.data_name(sample)
        if name in done:
            continue
        done.add(name)
        out = V.DATA_DIR / f"{name}.csv.gz"
        entry = dict(file=out.relative_to(V.PROJECT_ROOT).as_posix(),
                     **export(V.PROJECT_ROOT / V.CFG["samples"][sample], out, V.CFG["test_start"], V.CFG["k_core"],
                              V.DATASET, V.CFG.get("day0", DAY0)),
                     git_commit=prov["git_commit"], git_dirty=prov["git_dirty"])
        old = manifest.get(name, {})
        if old.get("git_dirty") is False and {**old, "git_commit": entry["git_commit"],
                                              "git_dirty": entry["git_dirty"]} == entry:
            entry = old
        manifest[name] = entry
        write_json(V.MANIFEST, manifest)
        b = entry["before_test_start"]
        pre = (f"{b['articles']:,} article -> {b['products']:,} sản phẩm (product_code), {b['article_pairs']:,} -> "
               f"{b['product_pairs']:,} cặp" if V.DATASET == "hm" else
               f"{b['products']:,} sản phẩm, {b['product_pairs']:,} cặp")
        print(f"{name} ({sample}): {entry['rows']:,} dòng -> {entry['file']}, MD5 {entry['md5']}\n"
              f"  trước {entry['test_start']}: {pre}\n"
              f"  k-core {entry['k_core']}: {entry['customers']:,} khách, {entry['products']:,} sản phẩm, "
              f"{entry['kcore_pairs']:,} cặp", flush=True)
        if old and old["md5"] != entry["md5"]:
            print(f"  CẢNH BÁO: MD5 khác lần chuẩn bị trước ({old['md5']}) — dữ liệu đã đổi.", flush=True)


if __name__ == "__main__":
    main()
