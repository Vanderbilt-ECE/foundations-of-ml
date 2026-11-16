"""Generate the measured numbers the slides plot, into ../data/*.json.

Every curve and statistic on the slides comes from here, not from memory. The training
runs reuse the demo's own code (demos/california_housing_mlp.py), so the slides match
what students get when they run the demo.

Run from this deck's folder, using the demos uv environment:
  uv run --project "../../demos" python scripts/make_data.py
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

HERE = Path(__file__).resolve().parent
DECK = HERE.parent
DEMOS = DECK.parent.parent / "demos"
sys.path.insert(0, str(DEMOS))

import os  # noqa: E402

os.chdir(DEMOS)                       # so the dataset cache in demos/data/ is reused
import california_housing_mlp as ch   # noqa: E402
from sklearn.datasets import fetch_california_housing  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

OUT = DECK / "data"
OUT.mkdir(exist_ok=True)
r4 = lambda v: None if not math.isfinite(v) else round(float(v), 4)  # noqa: E731
# 4 significant figures, for values that span many orders of magnitude (r4 would turn 3e-7 into 0.0)
s4 = lambda v: None if not math.isfinite(v) else float(f"{float(v):.4g}")  # noqa: E731


def dump(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, separators=(",", ":")))
    print(f"wrote data/{name}.json")


# ---------------------------------------------------------------------------
# 1. Feature scales: California Housing, before and after standardizing
# ---------------------------------------------------------------------------
d = fetch_california_housing(data_home="data")
X_train, _, y_train, _ = train_test_split(d.data, d.target, test_size=0.4, random_state=ch.SEED)
mu, sd = X_train.mean(0), X_train.std(0)
Z = (X_train - mu) / sd
dump("features", {
    "names": list(d.feature_names),
    "raw": [{"min": r4(c.min()), "q05": r4(np.quantile(c, 0.05)), "q95": r4(np.quantile(c, 0.95)), "max": r4(c.max()),
             "mean": r4(c.mean()), "std": r4(c.std())} for c in X_train.T],
    "z": [{"min": r4(c.min()), "q05": r4(np.quantile(c, 0.05)), "q95": r4(np.quantile(c, 0.95)), "max": r4(c.max())} for c in Z.T],
    "n_train": int(len(X_train)),
    "target_cap": r4(d.target.max()), "n_at_cap": int((d.target >= 5.0).sum()),
})

# ---------------------------------------------------------------------------
# 2. Demo runs: scaling x optimizer, learning-rate sweep, early stopping
# ---------------------------------------------------------------------------
raw, scaled = ch.load_data(scale=False), ch.load_data(scale=True)
curves = lambda r: [r4(v) for v in r["history"]["val"]]  # noqa: E731
scale_runs = {
    "sgd_raw": ch.train(raw, "sgd", lr=0.01), "sgd_std": ch.train(scaled, "sgd", lr=0.01),
    "adam_raw": ch.train(raw, "adam", lr=1e-3), "adam_std": ch.train(scaled, "adam", lr=1e-3),
}
lr_runs = {str(lr): ch.train(scaled, "adam", lr=lr) for lr in (1e-4, 1e-3, 1e-2, 1e-1)}
es = ch.train(scaled, "adam", lr=1e-3, epochs=300, hidden=256, patience=20)

# dead ReLUs after training at a good and a too-large learning rate
dead = {}
for lr in ("0.001", "0.1"):
    m = lr_runs[lr]["model"]
    with torch.no_grad():
        h2 = torch.relu(m[2](torch.relu(m[0](scaled[0]))))
        dead[lr] = {"layer2_dead": r4((h2.max(0).values == 0).float().mean().item()),
                    "pred_std": r4(m(scaled[0]).std().item()), "pred_mean": r4(m(scaled[0]).mean().item())}

X_te, y_te = scaled[4], scaled[5]
mean_rmse = math.sqrt(((y_te - scaled[1].mean()) ** 2).mean().item())
from sklearn.linear_model import LinearRegression  # noqa: E402
lin = LinearRegression().fit(scaled[0].numpy(), scaled[1].numpy())
lin_rmse = math.sqrt(float(np.mean((lin.predict(X_te.numpy()) - y_te.numpy()) ** 2)))
dump("demo", {
    "scale": {k: curves(r) for k, r in scale_runs.items()},
    "lr": {k: curves(r) for k, r in lr_runs.items()},
    "early": {"train": [r4(v) for v in es["history"]["train"]], "val": curves(es), "best_epoch": es["best_epoch"],
              "best_val": r4(es["best_val"])},
    "dead": dead,
    "test": {"mean": r4(mean_rmse), "linear": r4(lin_rmse), "mlp": r4(ch.rmse(es["model"], X_te, y_te))},
})

# ---------------------------------------------------------------------------
# 3. Learning-rate range test: raise lr exponentially every mini-batch, record the loss
# ---------------------------------------------------------------------------
torch.manual_seed(ch.SEED)
model = ch.make_model()
opt = torch.optim.Adam(model.parameters(), lr=1e-6)
lrs = np.logspace(-6, 0, 300)
gen = torch.Generator().manual_seed(ch.SEED)
losses, smooth = [], None
Xtr, ytr = scaled[0], scaled[1]
for lr in lrs:
    for g in opt.param_groups:
        g["lr"] = lr
    idx = torch.randint(0, len(Xtr), (ch.BATCH_SIZE,), generator=gen)
    loss = nn.functional.mse_loss(model(Xtr[idx]), ytr[idx])
    opt.zero_grad(); loss.backward(); opt.step()
    smooth = loss.item() if smooth is None else 0.9 * smooth + 0.1 * loss.item()
    losses.append(smooth)
    if not math.isfinite(smooth) or smooth > 4 * min(losses):
        break
dump("lr_range", {"lr": [float(f"{v:.4g}") for v in lrs[:len(losses)]], "loss": [r4(v) for v in losses]})  # lr: significant figures, not decimals

# ---------------------------------------------------------------------------
# 4. Initialization: activation std through 10 ReLU layers of width 256
# ---------------------------------------------------------------------------
x0 = torch.randn(1024, 256, generator=torch.Generator().manual_seed(1))
inits = {"small": 0.01, "default": None, "he": math.sqrt(2 / 256), "large": 0.15}
spread = {}
for name, std in inits.items():
    torch.manual_seed(0); h = x0; stds = [s4(h.std().item())]
    for _ in range(10):
        lin_ = nn.Linear(256, 256)
        if std is not None:
            nn.init.normal_(lin_.weight, 0, std); nn.init.zeros_(lin_.bias)
        h = torch.relu(lin_(h)); stds.append(s4(h.std().item()))
    spread[name] = stds
default_std = nn.Linear(256, 256).weight.std().item()
dump("init", {"spread": spread, "default_weight_std": r4(default_std), "he_std": r4(math.sqrt(2 / 256)),
              "inv_sqrt_3n": r4(1 / math.sqrt(3 * 256))})


# ---------------------------------------------------------------------------
# 5. Depth: plain vs. residual MLPs on California Housing (training loss)
# ---------------------------------------------------------------------------
class Block(nn.Module):
    def __init__(self, w, residual):
        super().__init__()
        self.f = nn.Sequential(nn.Linear(w, w), nn.ReLU(), nn.Linear(w, w))
        self.residual = residual

    def forward(self, x):
        return torch.relu(x + self.f(x)) if self.residual else torch.relu(self.f(x))


def deep_net(blocks, residual, w=64):
    return nn.Sequential(nn.Linear(8, w), nn.ReLU(), *[Block(w, residual) for _ in range(blocks)], nn.Linear(w, 1))


def train_depth(blocks, residual, epochs=40):
    torch.manual_seed(ch.SEED)
    m = deep_net(blocks, residual)
    opt = torch.optim.SGD(m.parameters(), lr=0.01, momentum=0.9)
    gen = torch.Generator().manual_seed(ch.SEED)
    hist = []
    for _ in range(epochs):
        m.train()
        order = torch.randperm(len(Xtr), generator=gen)
        for i in range(0, len(order), ch.BATCH_SIZE):
            idx = order[i:i + ch.BATCH_SIZE]
            loss = nn.functional.mse_loss(m(Xtr[idx]), ytr[idx])
            opt.zero_grad(); loss.backward(); opt.step()
        hist.append(r4(ch.rmse(m, Xtr, ytr)))
    # gradient norm of each block's first weight matrix, at initialization, on one batch
    torch.manual_seed(ch.SEED)
    m0 = deep_net(blocks, residual)
    nn.functional.mse_loss(m0(Xtr[:512]), ytr[:512]).backward()
    g = [s4(b.f[0].weight.grad.norm().item()) for b in m0 if isinstance(b, Block)]
    return hist, g


depth = {}
for name, blocks, res in [("plain_2", 1, False), ("plain_20", 10, False), ("res_20", 10, True)]:
    hist, g = train_depth(blocks, res)
    depth[name] = {"train_rmse": hist, "grad": g}
    print(f"  {name:9s} final train RMSE {hist[-1]}  grads first/last block {g[0]} / {g[-1]}")
depth["mean_baseline_train"] = r4(ytr.std(unbiased=False).item())   # RMSE of always predicting the training mean
dump("depth", depth)


# ---------------------------------------------------------------------------
# 6. Sanity checks on MNIST: initial loss vs. ln(10), and overfitting one batch
# ---------------------------------------------------------------------------
from torchvision import datasets, transforms  # noqa: E402

tf = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
Xm, ym = next(iter(torch.utils.data.DataLoader(datasets.MNIST("data", train=True, download=True, transform=tf),
                                               batch_size=4096)))
torch.manual_seed(0)
mnist = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10))
init_loss = nn.functional.cross_entropy(mnist(Xm), ym).item()
xb, yb = Xm[:32], ym[:32]
opt = torch.optim.Adam(mnist.parameters(), lr=1e-3)
one_batch = []
for _ in range(100):
    loss = nn.functional.cross_entropy(mnist(xb), yb)
    opt.zero_grad(); loss.backward(); opt.step()
    one_batch.append(r4(loss.item()))
dump("sanity", {"init_loss": r4(init_loss), "ln10": r4(math.log(10)), "one_batch": one_batch})
