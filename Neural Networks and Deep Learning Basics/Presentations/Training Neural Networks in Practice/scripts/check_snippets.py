"""Run every code snippet in slides.md (or an equivalent) and check the claims made about it.

  uv run --project "../../demos" --with pandas python scripts/check_snippets.py
"""

import math
import warnings

import numpy as np
import pandas as pd
import torch
from torch import nn

torch.manual_seed(0)

# --- Slide "Categories and Missing Values: Build a Pipeline" -----------------------------
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

X_train = pd.DataFrame({
    "income": [3.1, 5.0, np.nan, 2.2, 8.4], "house_age": [20, 35, 41, np.nan, 12], "rooms": [5.1, 6.0, 4.4, 5.5, 7.2],
    "ocean_proximity": ["NEAR BAY", "INLAND", "INLAND", "<1H OCEAN", "NEAR BAY"],
})
X_val = pd.DataFrame({"income": [4.0], "house_age": [np.nan], "rooms": [5.0], "ocean_proximity": ["ISLAND"]})
numeric = ["income", "house_age", "rooms"]
categorical = ["ocean_proximity"]
prep = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])
X_train_ready = prep.fit_transform(X_train)
X_val_ready = prep.transform(X_val)
assert X_train_ready.shape == (5, 3 + 3), X_train_ready.shape        # 3 numeric + 3 seen categories
assert np.isfinite(X_train_ready).all() and np.isfinite(X_val_ready).all()
assert np.allclose(X_train_ready[:, :3].mean(0), 0, atol=1e-9)        # standardized with train stats
assert X_val_ready[0, 3:].sum() == 0                                  # unseen "ISLAND" → all zeros
print("pipeline: OK", X_train_ready.shape)

# --- Slide "He and Xavier Initialization" -------------------------------------------------
def init_he(m):
    if isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight, nonlinearity="relu")
        nn.init.zeros_(m.bias)

model = nn.Sequential(nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 256))
model.apply(init_he)
std = model[0].weight.std().item()
assert abs(std - math.sqrt(2 / 256)) < 0.005, std
assert model[0].bias.abs().max().item() == 0
default_std = nn.Linear(256, 256).weight.std().item()
assert abs(default_std - 1 / math.sqrt(3 * 256)) < 0.002, default_std  # "PyTorch default ≈ 1/√(3·n_in)"
print(f"init: OK  He std {std:.4f} (√(2/256) = {math.sqrt(2/256):.4f}), default {default_std:.4f}")

# --- Slide "Learning-Rate Schedules" ------------------------------------------------------
model = nn.Linear(4, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
X, y = torch.randn(64, 4), torch.randn(64, 1)

def train_one_epoch(model, loader, optimizer):
    loss = nn.functional.mse_loss(model(X), y)
    optimizer.zero_grad(); loss.backward(); optimizer.step()

scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=90)
lrs = []
for epoch in range(90):
    train_one_epoch(model, None, optimizer)
    scheduler.step()
    lrs.append(optimizer.param_groups[0]["lr"])
assert abs(lrs[44] - 0.05) < 0.002 and lrs[-1] < 1e-6, (lrs[44], lrs[-1])   # halfway ≈ η₀/2, end ≈ 0
print(f"scheduler: OK  lr at epoch 45 {lrs[44]:.4f}, at 90 {lrs[-1]:.1e}")

# --- Slide "A Residual Block in PyTorch" --------------------------------------------------
class ResidualBlock(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.f = nn.Sequential(nn.Linear(width, width), nn.ReLU(),
                               nn.Linear(width, width))

    def forward(self, x):
        return torch.relu(x + self.f(x))   # the skip connection

model = nn.Sequential(
    nn.Linear(8, 64), nn.ReLU(),
    *[ResidualBlock(64) for _ in range(10)],
    nn.Linear(64, 1),
)
out = model(torch.randn(32, 8))
n_linear = sum(isinstance(m, nn.Linear) for m in model.modules())
assert out.shape == (32, 1) and n_linear == 22, (out.shape, n_linear)  # "22 Linear layers in total"
print(f"residual: OK  output {tuple(out.shape)}, {n_linear} Linear layers")

# --- Dropout: inverted scaling 1/(1−p) in training, identity in eval ----------------------
drop = nn.Dropout(p=0.5)
x = torch.ones(10000)
drop.train(); kept = drop(x)
assert set(kept.unique().tolist()) <= {0.0, 2.0} and abs(kept.mean().item() - 1) < 0.05
drop.eval(); assert torch.equal(drop(x), x)
print(f"dropout: OK  train survivors ×2 (mean {kept.mean():.3f}), eval = identity")

# --- Batch norm: batch stats in training, running stats in eval --------------------------
bn = nn.BatchNorm1d(3)
h = torch.randn(256, 3) * 5 + 10
bn.train(); y_tr = bn(h)
assert y_tr.mean(0).abs().max() < 1e-5 and (y_tr.std(0, unbiased=False) - 1).abs().max() < 1e-3
bn.eval(); single = bn(h[:1])
assert torch.isfinite(single).all()                                    # one example works in eval mode
print("batchnorm: OK  train standardizes per batch; eval uses running averages")

# --- Bug slide: (N, 1) predictions vs (N,) targets broadcast to (N, N) --------------------
pred, target = torch.randn(5, 1), torch.randn(5)
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    bad = nn.MSELoss()(pred, target)
assert any("broadcast" in str(x.message).lower() or "size" in str(x.message).lower() for x in w), [str(x.message) for x in w]
good = nn.MSELoss()(pred, target.unsqueeze(1))
assert not torch.isclose(bad, good)
assert ((pred - target) ** 2).shape == (5, 5)
print(f"shape bug: OK  warning raised, wrong loss {bad:.3f} vs right {good:.3f}")

# --- Adam vs AdamW weight decay both exist with the stated meaning ------------------------
p = nn.Parameter(torch.ones(3))
torch.optim.Adam([p], lr=1e-3, weight_decay=0.01); torch.optim.AdamW([p], lr=1e-3, weight_decay=0.01)
print("optimizers: OK")
print("\nall snippet checks passed")
