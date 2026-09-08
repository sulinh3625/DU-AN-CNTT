from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.common import build_adapter
from src.baselines import RandomBaseline, MostPopularBaseline, ItemKNNBaseline, BPRMFBaseline
from src.data.dataset import TrainDataset
from src.data.negative_sampling import build_user_positive_sets
from src.data.preprocessing import build_interactions, apply_feedback_weights
from src.data.splitting import temporal_leave_one_out, assert_disjoint_splits
from src.evaluation.full_ranking import build_full_ranking_records, evaluate_torch_model, evaluate_score_function
from src.evaluation.sampled_ranking import build_sampled_ranking_records
from src.evaluation.long_tail import define_head_items, split_records_head_tail
from src.models.neumf import GMF, MLP, NeuMF
from src.training.trainer import train_one_model, make_optimizer
from src.utils.seed import seed_everything
from src.utils.io import ensure_dir, write_json

METHOD_ORDER = [
    "Random", "MostPopular", "ItemKNN", "BPR-MF",
    "GMF", "MLP", "NeuMF-Scratch", "NeuMF-Pretrained",
]


def build_eval_records(cfg, val_df, test_df, train_df, full_df, n_users, n_items):
    train_pos = build_user_positive_sets(train_df, n_users)
    train_val = pd.concat([train_df, val_df], ignore_index=True)
    train_val_pos = build_user_positive_sets(train_val, n_users)
    all_pos = build_user_positive_sets(full_df, n_users)

    if cfg.evaluation.primary == "full_ranking":
        val_records = build_full_ranking_records(val_df, n_items, train_pos)
        test_records = build_full_ranking_records(test_df, n_items, train_val_pos)
    elif cfg.evaluation.primary == "sampled":
        val_records = build_sampled_ranking_records(
            val_df, n_items, all_pos, cfg.evaluation.sampled_negatives, seed=cfg.training.seed + 1
        )
        test_records = build_sampled_ranking_records(
            test_df, n_items, all_pos, cfg.evaluation.sampled_negatives, seed=cfg.training.seed + 2
        )
    else:
        raise ValueError(f"evaluation.primary không hợp lệ: {cfg.evaluation.primary}")

    sampled_test = build_sampled_ranking_records(
        test_df, n_items, all_pos, cfg.evaluation.sampled_negatives, seed=cfg.training.seed + 2
    )
    return train_pos, val_records, test_records, sampled_test


def run(config_path: str, run_tag: str | None = None):
    cfg, adapter = build_adapter(config_path)
    seed_everything(cfg.training.seed)
    device = torch.device(cfg.training.device)
    run_tag = run_tag or f"{cfg.dataset.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = ensure_dir(cfg.output_root / "experiments" / run_tag)
    ckpt_dir = ensure_dir(cfg.output_root / "checkpoints" / run_tag)

    # 1) Data pipeline
    events = adapter.load_events()
    data = build_interactions(events, cfg.dataset.k_core)
    train_df, val_df, test_df = temporal_leave_one_out(data.df, cfg.dataset.min_interactions_for_loo)
    assert_disjoint_splits(train_df, val_df, test_df)
    train_df, val_df, test_df, feedback_meta = apply_feedback_weights(
        train_df, val_df, test_df, cfg.feedback.mode, cfg.feedback.confidence_alpha
    )

    train_pos, val_records, test_records, sampled_test = build_eval_records(
        cfg, val_df, test_df, train_df, data.df, data.n_users, data.n_items
    )
    train_dataset = TrainDataset(
        train_df, data.n_items, train_pos, cfg.training.negative_ratio, seed=cfg.training.seed
    )

    eval_kwargs = dict(
        k_values=cfg.evaluation.k_values,
        device=device,
        tie_seed=cfg.evaluation.tie_break_seed,
        include_redundant=cfg.evaluation.include_redundant_metrics,
    )

    def eval_torch(model, records):
        return evaluate_torch_model(model, records, **eval_kwargs)

    results_primary = {}
    results_sampled = {}
    train_meta = {}
    models = {}
    score_fns = {}

    # 2) Pretrain GMF
    gmf = GMF(data.n_users, data.n_items, cfg.model.embedding_dim).to(device)
    opt = make_optimizer(cfg.training.pretrain_optimizer, gmf.parameters(), cfg.training.pretrain_lr, cfg.training.weight_decay)
    gmf, hist, meta = train_one_model(
        gmf, train_dataset, val_records, eval_torch, opt, device,
        cfg.training.max_epochs_pretrain, cfg.training.patience, cfg.training.batch_size,
        monitor=cfg.training.monitor, seed=cfg.training.seed + 11, model_name="GMF"
    )
    models["GMF"] = gmf
    train_meta["GMF"] = meta
    pd.DataFrame(hist).to_csv(run_dir / "history_gmf.csv", index=False)
    torch.save(gmf.state_dict(), ckpt_dir / "gmf.pt")

    # 3) Pretrain MLP
    mlp = MLP(data.n_users, data.n_items, cfg.model.embedding_dim, cfg.model.mlp_layers, cfg.model.dropout).to(device)
    opt = make_optimizer(cfg.training.pretrain_optimizer, mlp.parameters(), cfg.training.pretrain_lr, cfg.training.weight_decay)
    mlp, hist, meta = train_one_model(
        mlp, train_dataset, val_records, eval_torch, opt, device,
        cfg.training.max_epochs_pretrain, cfg.training.patience, cfg.training.batch_size,
        monitor=cfg.training.monitor, seed=cfg.training.seed + 22, model_name="MLP"
    )
    models["MLP"] = mlp
    train_meta["MLP"] = meta
    pd.DataFrame(hist).to_csv(run_dir / "history_mlp.csv", index=False)
    torch.save(mlp.state_dict(), ckpt_dir / "mlp.pt")

    # 4) Controlled pretraining ablation: same optimizer/LR/budget for scratch & pretrained.
    scratch = NeuMF(data.n_users, data.n_items, cfg.model.embedding_dim, cfg.model.mlp_layers, cfg.model.dropout).to(device)
    opt = make_optimizer(cfg.training.finetune_optimizer, scratch.parameters(), cfg.training.finetune_lr, cfg.training.weight_decay)
    scratch, hist, meta = train_one_model(
        scratch, train_dataset, val_records, eval_torch, opt, device,
        cfg.training.max_epochs_finetune, cfg.training.patience, cfg.training.batch_size,
        monitor=cfg.training.monitor, seed=cfg.training.seed + 33, model_name="NeuMF-Scratch"
    )
    models["NeuMF-Scratch"] = scratch
    train_meta["NeuMF-Scratch"] = meta
    pd.DataFrame(hist).to_csv(run_dir / "history_neumf_scratch.csv", index=False)
    torch.save(scratch.state_dict(), ckpt_dir / "neumf_scratch.pt")

    pretrained = NeuMF(data.n_users, data.n_items, cfg.model.embedding_dim, cfg.model.mlp_layers, cfg.model.dropout).to(device)
    pretrained.load_pretrained(gmf, mlp, alpha=cfg.model.pretrain_alpha)
    opt = make_optimizer(cfg.training.finetune_optimizer, pretrained.parameters(), cfg.training.finetune_lr, cfg.training.weight_decay)
    pretrained, hist, meta = train_one_model(
        pretrained, train_dataset, val_records, eval_torch, opt, device,
        cfg.training.max_epochs_finetune, cfg.training.patience, cfg.training.batch_size,
        monitor=cfg.training.monitor, seed=cfg.training.seed + 44, model_name="NeuMF-Pretrained"
    )
    models["NeuMF-Pretrained"] = pretrained
    train_meta["NeuMF-Pretrained"] = meta
    pd.DataFrame(hist).to_csv(run_dir / "history_neumf_pretrained.csv", index=False)
    torch.save(pretrained.state_dict(), ckpt_dir / "neumf_pretrained.pt")

    # 5) Classical baselines
    enabled = {x.lower() for x in cfg.baselines.enabled}
    if "random" in enabled:
        random_bl = RandomBaseline(cfg.training.seed)
        score_fns["Random"] = random_bl.score
    if "popularity" in enabled:
        pop_bl = MostPopularBaseline(train_df, data.n_items)
        score_fns["MostPopular"] = pop_bl.score
    if "itemknn" in enabled:
        t0 = time.perf_counter()
        itemknn = ItemKNNBaseline(train_df, data.n_users, data.n_items)
        train_meta["ItemKNN"] = {"train_time_s": time.perf_counter() - t0, "n_parameters": 0}
        score_fns["ItemKNN"] = itemknn.score
    if "bpr" in enabled:
        bpr = BPRMFBaseline(
            data.n_users, data.n_items, cfg.baselines.bpr.embedding_dim, seed=cfg.training.seed
        )
        t0 = time.perf_counter()
        bpr.fit(
            train_df,
            epochs=cfg.baselines.bpr.epochs,
            lr=cfg.baselines.bpr.lr,
            reg=cfg.baselines.bpr.reg,
            seed=cfg.training.seed,
        )
        train_meta["BPR-MF"] = {
            "train_time_s": time.perf_counter() - t0,
            "n_parameters": int(bpr.P.size + bpr.Q.size),
        }
        score_fns["BPR-MF"] = bpr.score

    # 6) Evaluate primary + sampled reproduction protocol
    for name, model in models.items():
        results_primary[name] = eval_torch(model, test_records)
        results_sampled[name] = evaluate_torch_model(model, sampled_test, **eval_kwargs)
    for name, fn in score_fns.items():
        results_primary[name] = evaluate_score_function(
            fn, test_records, cfg.evaluation.k_values,
            tie_seed=cfg.evaluation.tie_break_seed,
            include_redundant=cfg.evaluation.include_redundant_metrics,
        )
        results_sampled[name] = evaluate_score_function(
            fn, sampled_test, cfg.evaluation.k_values,
            tie_seed=cfg.evaluation.tie_break_seed,
            include_redundant=cfg.evaluation.include_redundant_metrics,
        )

    # 7) Long-tail segmentation from TRAIN only
    head_items = define_head_items(train_df, data.n_items, cfg.evaluation.head_fraction)
    head_records, tail_records = split_records_head_tail(test_records, head_items)
    results_tail = {}
    for name, model in models.items():
        results_tail[name] = eval_torch(model, tail_records) if tail_records else {}
    for name, fn in score_fns.items():
        results_tail[name] = evaluate_score_function(
            fn, tail_records, cfg.evaluation.k_values,
            tie_seed=cfg.evaluation.tie_break_seed,
            include_redundant=cfg.evaluation.include_redundant_metrics,
        ) if tail_records else {}

    # Save consistent tables
    order = [m for m in METHOD_ORDER if m in results_primary]
    pd.DataFrame.from_dict(results_primary, orient="index").reindex(order).to_csv(run_dir / "results_primary.csv")
    pd.DataFrame.from_dict(results_sampled, orient="index").reindex(order).to_csv(run_dir / "results_sampled_99.csv")
    pd.DataFrame.from_dict(results_tail, orient="index").reindex(order).to_csv(run_dir / "results_long_tail.csv")

    metadata = {
        "run_tag": run_tag,
        "dataset": cfg.dataset.name,
        "seed": cfg.training.seed,
        "n_users": data.n_users,
        "n_items": data.n_items,
        "n_interactions": len(data.df),
        "train": len(train_df), "validation": len(val_df), "test": len(test_df),
        "k_core": cfg.dataset.k_core,
        "feedback": feedback_meta,
        "evaluation_primary": cfg.evaluation.primary,
        "head_fraction": cfg.evaluation.head_fraction,
        "n_head_items": len(head_items),
        "n_head_test_users": len(head_records),
        "n_long_tail_test_users": len(tail_records),
        "training": train_meta,
    }
    write_json(run_dir / "metadata.json", metadata)
    write_json(run_dir / "results.json", {
        "primary": results_primary,
        "sampled_99": results_sampled,
        "long_tail": results_tail,
        "metadata": metadata,
    })

    print(f"Run complete: {run_dir}")
    print(pd.DataFrame.from_dict(results_primary, orient="index").reindex(order).to_string())
    return run_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/dataco.yaml")
    ap.add_argument("--run-tag", default=None)
    args = ap.parse_args()
    run(args.config, args.run_tag)


if __name__ == "__main__":
    main()
