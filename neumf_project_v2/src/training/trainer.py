from __future__ import annotations

import copy
import time
import numpy as np
import torch
import torch.nn as nn


def make_optimizer(name: str, params, lr: float, weight_decay: float):
    name = name.lower()
    if name == "adam":
        return torch.optim.Adam(params, lr=lr, weight_decay=weight_decay)
    if name == "sgd":
        return torch.optim.SGD(params, lr=lr, weight_decay=weight_decay)
    raise ValueError(f"Optimizer không hỗ trợ: {name}")


def count_parameters(model) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def train_one_model(
    model,
    train_dataset,
    val_records,
    eval_model_fn,
    optimizer,
    device,
    max_epochs: int,
    patience: int,
    batch_size: int,
    monitor: str = "NDCG@10",
    seed: int = 42,
    model_name: str = "model",
):
    criterion = nn.BCEWithLogitsLoss(reduction="none")
    best_metric = -np.inf
    best_state = copy.deepcopy(model.state_dict())
    best_epoch = 0
    no_improve = 0
    history = []
    rng = np.random.default_rng(seed)
    total_train_time = 0.0

    for epoch in range(1, int(max_epochs) + 1):
        t0 = time.perf_counter()
        train_dataset.resample()
        n = len(train_dataset.users)
        perm = rng.permutation(n)

        model.train()
        total_loss = 0.0
        n_batches = 0
        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            u = torch.from_numpy(train_dataset.users[idx]).long().to(device)
            i = torch.from_numpy(train_dataset.items[idx]).long().to(device)
            y = torch.from_numpy(train_dataset.labels[idx]).float().to(device)
            w = torch.from_numpy(train_dataset.sample_weights[idx]).float().to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(u, i)
            loss = (criterion(logits, y) * w).mean()
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item())
            n_batches += 1

        epoch_time = time.perf_counter() - t0
        total_train_time += epoch_time
        val_metrics = eval_model_fn(model, val_records)
        if monitor not in val_metrics:
            raise KeyError(f"Metric early stopping '{monitor}' không có trong evaluator: {sorted(val_metrics)}")
        metric = float(val_metrics[monitor])
        row = {
            "epoch": epoch,
            "loss": total_loss / max(n_batches, 1),
            monitor: metric,
            "epoch_time_s": epoch_time,
        }
        history.append(row)

        if metric > best_metric + 1e-12:
            best_metric = metric
            best_state = copy.deepcopy(model.state_dict())
            best_epoch = epoch
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                break

    model.load_state_dict(best_state)
    return model, history, {
        "best_metric": float(best_metric),
        "best_epoch": int(best_epoch),
        "train_time_s": float(total_train_time),
        "n_parameters": int(count_parameters(model)),
        "model_name": model_name,
    }
