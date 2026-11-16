"""Training an MLP on real tabular data: California Housing, in PyTorch.

Predict a district's median house value (in $100,000s) from 8 numeric features
such as median income, house age, population, and location.

Run it with:  uv run california_housing_mlp.py

It runs three experiments, prints what happened, and opens one figure:
  1. Scaling: the same network trained on raw vs. standardized inputs,
     with plain SGD and with Adam.
  2. Learning rate: Adam with four learning rates, from 1e-4 to 1e-1.
  3. Early stopping: a bigger network trained until the validation loss
     stops improving; we keep the best weights, not the last ones.
Takes about 15 seconds on a laptop CPU. The dataset (~1 MB) downloads into data/.
"""

import copy
import math

import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn

SEED = 0
BATCH_SIZE = 128
torch.set_num_threads(4)


# ---------------------------------------------------------------------------
# Data: split FIRST, then fit the scaler on the training set only.
# ---------------------------------------------------------------------------
def load_data(scale=True):
    """Return (X_train, y_train, X_val, y_val, X_test, y_test) as float32 tensors."""
    data = fetch_california_housing(data_home="data")
    X, y = data.data, data.target
    # 60% train, 20% validation, 20% test
    X_train, X_rest, y_train, y_rest = train_test_split(X, y, test_size=0.4, random_state=SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_rest, y_rest, test_size=0.5, random_state=SEED)

    if scale:
        scaler = StandardScaler().fit(X_train)   # mean and std of the TRAINING rows only
        X_train, X_val, X_test = (scaler.transform(a) for a in (X_train, X_val, X_test))

    def t(a):
        return torch.tensor(a, dtype=torch.float32)

    return (t(X_train), t(y_train).unsqueeze(1), t(X_val), t(y_val).unsqueeze(1),
            t(X_test), t(y_test).unsqueeze(1))


def make_model(hidden=64):
    return nn.Sequential(
        nn.Linear(8, hidden), nn.ReLU(),
        nn.Linear(hidden, hidden), nn.ReLU(),
        nn.Linear(hidden, 1),            # regression: one number, no activation
    )


def rmse(model, X, y):
    model.eval()
    with torch.no_grad():
        return math.sqrt(nn.functional.mse_loss(model(X), y).item())


# ---------------------------------------------------------------------------
# Training loop with optional early stopping.
# ---------------------------------------------------------------------------
def train(data, optimizer="adam", lr=1e-3, epochs=100, hidden=64, patience=None):
    """Train one model. Returns a dict with per-epoch train/val RMSE and the best model."""
    X_train, y_train, X_val, y_val, _, _ = data
    torch.manual_seed(SEED)
    model = make_model(hidden)
    if optimizer == "adam":
        opt = torch.optim.Adam(model.parameters(), lr=lr)
    else:
        opt = torch.optim.SGD(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    history = {"train": [], "val": []}
    best = {"val": float("inf"), "epoch": 0, "state": None}
    gen = torch.Generator().manual_seed(SEED)
    for epoch in range(1, epochs + 1):
        model.train()
        order = torch.randperm(len(X_train), generator=gen)       # shuffle every epoch
        for i in range(0, len(order), BATCH_SIZE):
            idx = order[i:i + BATCH_SIZE]
            loss = loss_fn(model(X_train[idx]), y_train[idx])     # forward + loss
            opt.zero_grad()
            loss.backward()                                       # backward
            opt.step()                                            # update

        tr, va = rmse(model, X_train, y_train), rmse(model, X_val, y_val)
        history["train"].append(tr)
        history["val"].append(va)
        if not math.isfinite(tr):                                 # the loss blew up
            break
        if va < best["val"]:                                      # checkpoint the best model
            best = {"val": va, "epoch": epoch, "state": copy.deepcopy(model.state_dict())}
        elif patience and epoch - best["epoch"] >= patience:      # early stopping
            break

    if best["state"] is not None:
        model.load_state_dict(best["state"])
    return {"history": history, "best_epoch": best["epoch"], "best_val": best["val"], "model": model}


def show(name, run):
    h = run["history"]
    last = h["val"][-1]
    status = "diverged (NaN)" if not math.isfinite(last) else f"final val RMSE {last:.3f}"
    print(f"  {name:28s} {status:28s} best {run['best_val']:.3f} at epoch {run['best_epoch']}")


def main():
    raw, scaled = load_data(scale=False), load_data(scale=True)
    X_test, y_test = scaled[4], scaled[5]
    print("Target: median house value in $100,000s. RMSE 0.5 means typically off by about $50,000.\n")

    # 1. Scaling ------------------------------------------------------------
    print("1. Raw vs. standardized inputs (100 epochs)")
    runs_scale = {
        "SGD, raw inputs": train(raw, "sgd", lr=0.01),
        "SGD, standardized": train(scaled, "sgd", lr=0.01),
        "Adam, raw inputs": train(raw, "adam", lr=1e-3),
        "Adam, standardized": train(scaled, "adam", lr=1e-3),
    }
    for k, r in runs_scale.items():
        show(k, r)

    # 2. Learning rate --------------------------------------------------------
    print("\n2. Learning rate (Adam, standardized, 100 epochs)")
    runs_lr = {lr: train(scaled, "adam", lr=lr) for lr in (1e-4, 1e-3, 1e-2, 1e-1)}
    for lr, r in runs_lr.items():
        show(f"lr = {lr:g}", r)

    # 3. Early stopping -------------------------------------------------------
    print("\n3. Early stopping (256-unit layers, up to 300 epochs, patience 20)")
    es = train(scaled, "adam", lr=1e-3, epochs=300, hidden=256, patience=20)
    show("Adam, 256 units", es)
    print(f"  stopped after epoch {len(es['history']['val'])}; kept the weights from epoch {es['best_epoch']}")

    # Final test score, against two baselines -------------------------------------
    X_train, y_train = scaled[0], scaled[1]
    mean_rmse = math.sqrt(((y_test - y_train.mean()) ** 2).mean().item())
    lin = LinearRegression().fit(X_train.numpy(), y_train.numpy())
    lin_rmse = math.sqrt(np.mean((lin.predict(X_test.numpy()) - y_test.numpy()) ** 2))
    mlp_rmse = rmse(es["model"], X_test, y_test)
    print("\nTest RMSE (data never used for training or choosing):")
    print(f"  always predict the mean   {mean_rmse:.3f}  (≈ ${mean_rmse * 1e5:,.0f})")
    print(f"  linear regression         {lin_rmse:.3f}  (≈ ${lin_rmse * 1e5:,.0f})")
    print(f"  MLP, early stopping       {mlp_rmse:.3f}  (≈ ${mlp_rmse * 1e5:,.0f})")

    # Figure ----------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    ax = axes[0]
    for k, r in runs_scale.items():
        v = [x if math.isfinite(x) else np.nan for x in r["history"]["val"]]
        ax.plot(range(1, len(v) + 1), v, label=k, ls="--" if "raw" in k else "-")
    ax.text(50, 1.5, "SGD on raw inputs: the loss blew up\nto NaN in the first epoch (not drawn)",
            ha="center", fontsize=8, color="tab:blue")
    ax.set(title="1. Scaling the inputs", xlabel="epoch", ylabel="validation RMSE", ylim=(0.4, 1.7))
    ax.legend(fontsize=8)

    ax = axes[1]
    for lr, r in runs_lr.items():
        v = r["history"]["val"]
        ax.plot(range(1, len(v) + 1), v, label=f"lr = {lr:g}")
    ax.set(title="2. Learning rate (Adam)", xlabel="epoch", ylabel="validation RMSE", ylim=(0.45, 1.2))
    ax.legend(fontsize=8)

    ax = axes[2]
    h = es["history"]
    ax.plot(range(1, len(h["train"]) + 1), h["train"], label="training")
    ax.plot(range(1, len(h["val"]) + 1), h["val"], label="validation")
    ax.axvline(es["best_epoch"], color="gray", ls=":", label=f"best epoch ({es['best_epoch']})")
    ax.set(title="3. Early stopping", xlabel="epoch", ylabel="RMSE")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    return runs_scale, runs_lr, es


if __name__ == "__main__":
    main()
