"""Recognize six smartphone activities with a basic PyTorch MLP.

Run: uv run har_mlp.py
Headless: uv run har_mlp.py --no-show
Reads the supplied UCI HAR zip directly; no download or extraction needed.
"""

import argparse
import copy
from pathlib import Path
from zipfile import ZipFile

import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import ConfusionMatrixDisplay, classification_report
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

# Settings to experiment with: hidden layers, learning rate, batch size, epochs.
SEED = 0
EPOCHS = 30
BATCH_SIZE = 64
LEARNING_RATE = 1e-3
HIDDEN = (128, 64)
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs" / "har_mlp"


def load_data():
    archive = DATA_DIR / "human+activity+recognition+using+smartphones" / "UCI HAR Dataset.zip"
    if not archive.exists():
        raise FileNotFoundError(f"Place the supplied UCI HAR Dataset.zip at {archive}")
    with ZipFile(archive) as z:
        def read(name, dtype=np.float32):
            with z.open(f"UCI HAR Dataset/{name}") as f:
                return np.loadtxt(f, dtype=dtype)

        names = [line.split(maxsplit=1)[1].replace("_", " ").title()
                 for line in z.read("UCI HAR Dataset/activity_labels.txt").decode().splitlines()]
        splits = {}
        for split in ("train", "test"):
            splits[split] = (
                read(f"{split}/X_{split}.txt"),
                read(f"{split}/y_{split}.txt", np.int64) - 1,  # labels 1–6 → 0–5
                read(f"{split}/subject_{split}.txt", np.int64),
            )
        # Total acceleration includes gravity, making posture visible as well as motion.
        signals = np.stack([
            read(f"train/Inertial Signals/total_acc_{axis}_train.txt")
            for axis in "xyz"
        ], axis=-1)
    return splits, signals, names


def plot_inputs(X, y, signals, names):
    examples = [np.flatnonzero(y == i)[0] for i in range(len(names))]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    for ax, i, name in zip(axes.flat, examples, names):
        for axis, label in enumerate("xyz"):
            ax.plot(np.arange(128) / 50, signals[i, :, axis], label=label, linewidth=1)
        ax.set(title=name, xlabel="Time (seconds)", ylabel="Total acceleration (g)")
        ax.grid(alpha=0.2)
    axes.flat[0].legend(title="Phone axis", ncol=3)
    fig.suptitle("Example inputs: 2.56-second smartphone windows sampled at 50 Hz")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "sensor_examples.png", dpi=160)

    fig, ax = plt.subplots(figsize=(13, 4))
    im = ax.imshow(X[examples], aspect="auto", cmap="coolwarm", vmin=-1, vmax=1,
                   interpolation="nearest")
    ax.set(yticks=range(len(names)), yticklabels=names, xlabel="Feature index (561 features)",
           title="What the MLP sees: one engineered feature vector per window")
    fig.colorbar(im, ax=ax, label="Dataset feature value (scaled to [−1, 1])")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "feature_examples.png", dpi=160)


def make_model(n_inputs, n_classes):
    layers = []
    for width in HIDDEN:
        layers.extend([nn.Linear(n_inputs, width), nn.ReLU()])
        n_inputs = width
    layers.append(nn.Linear(n_inputs, n_classes))  # logits; loss applies softmax internally
    return nn.Sequential(*layers)


@torch.no_grad()
def evaluate(model, X, y):
    model.eval()
    logits = model(X)
    return nn.functional.cross_entropy(logits, y).item(), (logits.argmax(1) == y).float().mean().item()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-show", action="store_true", help="Save figures without opening windows")
    args = parser.parse_args()
    torch.manual_seed(SEED)
    torch.set_num_threads(4)  # this small network is fast on a laptop CPU
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    splits, signals, names = load_data()
    X, y, subjects = splits["train"]
    X_test, y_test, test_subjects = splits["test"]
    train_idx, val_idx = next(GroupShuffleSplit(n_splits=1, test_size=0.2,
                                               random_state=SEED).split(X, y, subjects))
    assert set(subjects[train_idx]).isdisjoint(subjects[val_idx])
    assert set(subjects).isdisjoint(test_subjects)
    plot_inputs(X, y, signals, names)

    # Fit preprocessing ONLY on training participants, never validation or test.
    scaler = StandardScaler().fit(X[train_idx])
    X_train, X_val, X_test = [torch.tensor(scaler.transform(a), dtype=torch.float32)
                             for a in (X[train_idx], X[val_idx], X_test)]
    y_train, y_val, y_test = [torch.tensor(a, dtype=torch.long)
                             for a in (y[train_idx], y[val_idx], y_test)]
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
    model = make_model(X.shape[1], len(names))
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    loss_fn = nn.CrossEntropyLoss()
    print(f"Windows: train {len(X_train):,}, validation {len(X_val):,}, test {len(X_test):,}")
    print(f"Participants: train {len(set(subjects[train_idx]))}, "
          f"validation {len(set(subjects[val_idx]))}, test {len(set(test_subjects))}")
    print(model)
    print(f"Trainable parameters: {sum(p.numel() for p in model.parameters()):,}")
    history = []
    best_loss, best_epoch, best_state = float("inf"), 0, None
    for epoch in range(1, EPOCHS + 1):
        model.train()
        for inputs, labels in loader:
            logits = model(inputs)                   # 1. forward
            loss = loss_fn(logits, labels)            # 2. loss
            optimizer.zero_grad()
            loss.backward()                          # 3. backward
            optimizer.step()                         # 4. update
        train_loss, train_acc = evaluate(model, X_train, y_train)
        val_loss, val_acc = evaluate(model, X_val, y_val)
        history.append((train_loss, val_loss, train_acc, val_acc))
        if val_loss < best_loss:
            best_loss, best_epoch = val_loss, epoch
            best_state = copy.deepcopy(model.state_dict())
        print(f"Epoch {epoch:2}/{EPOCHS}: loss {train_loss:.4f}, "
              f"train accuracy {train_acc:.1%}, validation accuracy {val_acc:.1%}")

    # Select weights by validation loss; use the official test set only at the end.
    model.load_state_dict(best_state)
    _, test_acc = evaluate(model, X_test, y_test)
    with torch.no_grad():
        predictions = model(X_test).argmax(1).numpy()
    majority = np.bincount(y[train_idx]).argmax()
    print(f"\nBest validation loss: epoch {best_epoch}")
    print(f"Majority-class test baseline: {(y_test.numpy() == majority).mean():.1%}")
    print(f"MLP test accuracy: {test_acc:.2%}\n")
    print(classification_report(y_test.numpy(), predictions, labels=range(len(names)),
                                target_names=names, digits=3, zero_division=0))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    h = np.array(history)
    epochs = np.arange(1, EPOCHS + 1)
    for col, label in enumerate(("Training", "Validation")):
        axes[0].plot(epochs, h[:, col], label=label)
        axes[1].plot(epochs, 100 * h[:, col + 2], label=label)
    for ax in axes:
        ax.axvline(best_epoch, ls=":", color="gray", label="Selected epoch")
        ax.set_xlabel("Epoch")
        ax.legend()
    axes[0].set(title="Cross-entropy loss", ylabel="Loss")
    axes[1].set(title="Activity classification", ylabel="Accuracy (%)")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "training_curves.png", dpi=160)

    fig, ax = plt.subplots(figsize=(9, 7))
    ConfusionMatrixDisplay.from_predictions(y_test.numpy(), predictions, labels=range(len(names)),
                                            display_labels=names, ax=ax, cmap="Blues",
                                            xticks_rotation=35, colorbar=False)
    ax.set_title(f"Official test set — accuracy {test_acc:.2%}")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=160)
    print(f"Figures saved to {OUTPUT_DIR}")
    if args.no_show:
        plt.close("all")
    else:
        plt.show()


if __name__ == "__main__":
    main()
