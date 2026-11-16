"""A multilayer perceptron that reads handwritten digits (MNIST), in PyTorch.

Each 28×28 image is flattened into 784 numbers and passed through two hidden
layers of ReLU units. The output layer gives 10 scores, one per digit.

Run it with:  uv run mnist_mlp.py

The first run downloads MNIST (about 12 MB) into data/. Training takes about a
minute on a laptop CPU. At the end, two windows open: the training curves, and a
grid of test digits with the network's guesses (including some it got wrong).
"""

import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# ---------------------------------------------------------------------------
# Settings: try changing these.
# ---------------------------------------------------------------------------
EPOCHS = 5            # passes through all 60,000 training images
BATCH_SIZE = 64       # images per gradient step (a mini-batch)
LEARNING_RATE = 1e-3  # step size for the optimizer
HIDDEN = (128, 64)    # units in each hidden layer

torch.manual_seed(0)  # same random start every run, so results are repeatable

# Use a GPU if there is one (NVIDIA "cuda" or Apple-silicon "mps"); otherwise the CPU.
# A network this small trains fine on the CPU.
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"


# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
# ToTensor turns each image into numbers between 0 and 1. Normalize then shifts
# and scales them to mean 0, standard deviation 1 (0.1307 and 0.3081 are the
# mean and std of the MNIST training pixels), which helps gradient descent.
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,)),
])

train_data = datasets.MNIST("data", train=True, download=True, transform=transform)
test_data = datasets.MNIST("data", train=False, download=True, transform=transform)

# A DataLoader hands out the data in shuffled mini-batches.
train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_data, batch_size=1000)

print(f"Training images: {len(train_data):,}   Test images: {len(test_data):,}   Device: {device}")


# ---------------------------------------------------------------------------
# 2. Model: a multilayer perceptron
# ---------------------------------------------------------------------------
# Flatten: 28×28 image → 784 inputs.
# Each Linear layer is a set of neurons: a weighted sum plus a bias.
# ReLU is the activation; without it the layers would collapse into one linear layer.
# The last layer outputs 10 raw scores ("logits"). There is no softmax here:
# CrossEntropyLoss applies it internally (see the "Three Demos, Three Heads" slide).
model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(28 * 28, HIDDEN[0]), nn.ReLU(),
    nn.Linear(HIDDEN[0], HIDDEN[1]), nn.ReLU(),
    nn.Linear(HIDDEN[1], 10),
).to(device)

n_params = sum(p.numel() for p in model.parameters())
print(model)
print(f"Trainable parameters (weights + biases): {n_params:,}\n")


# ---------------------------------------------------------------------------
# 3. Loss and optimizer
# ---------------------------------------------------------------------------
loss_fn = nn.CrossEntropyLoss()  # softmax + cross-entropy, for 10 classes
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)


def evaluate():
    """Accuracy on the 10,000 test images (images the model never trains on)."""
    model.eval()                     # evaluation mode
    correct = 0
    with torch.no_grad():            # no gradients needed just to predict
        for X, y in test_loader:
            X, y = X.to(device), y.to(device)
            correct += (model(X).argmax(dim=1) == y).sum().item()
    return correct / len(test_data)


# ---------------------------------------------------------------------------
# 4. Training: the same four steps as the "Whole Loop in PyTorch" slide
# ---------------------------------------------------------------------------
history = {"loss": [], "acc": []}
print(f"Before training, test accuracy: {evaluate():.1%}  (about 10% = guessing)\n")

for epoch in range(1, EPOCHS + 1):
    model.train()                    # training mode
    total_loss = 0.0
    for X, y in train_loader:        # one mini-batch at a time
        X, y = X.to(device), y.to(device)
        y_hat = model(X)             # 1 forward
        loss = loss_fn(y_hat, y)     # 2 loss
        optimizer.zero_grad()        #   clear last step's gradients
        loss.backward()              # 3 backward: backpropagation
        optimizer.step()             # 4 update every weight and bias
        total_loss += loss.item() * len(X)

    avg_loss = total_loss / len(train_data)
    acc = evaluate()
    history["loss"].append(avg_loss)
    history["acc"].append(acc)
    print(f"Epoch {epoch}/{EPOCHS}   training loss {avg_loss:.4f}   test accuracy {acc:.2%}")


# ---------------------------------------------------------------------------
# 5. Look at the results
# ---------------------------------------------------------------------------
# Training curves
fig, (ax_loss, ax_acc) = plt.subplots(1, 2, figsize=(10, 4))
epochs = range(1, EPOCHS + 1)
ax_loss.plot(epochs, history["loss"], marker="o")
ax_loss.set(title="Training loss", xlabel="epoch", ylabel="cross-entropy", xticks=list(epochs))
ax_acc.plot(epochs, [100 * a for a in history["acc"]], marker="o", color="tab:green")
ax_acc.set(title="Test accuracy", xlabel="epoch", ylabel="% correct", xticks=list(epochs))
fig.tight_layout()

# Predictions on test digits: a row of ordinary examples, then a row of mistakes.
model.eval()
images, labels = next(iter(DataLoader(test_data, batch_size=2000)))
with torch.no_grad():
    probs = torch.softmax(model(images.to(device)), dim=1).cpu()  # softmax to read probabilities
preds = probs.argmax(dim=1)
wrong = (preds != labels).nonzero().flatten()

fig, axes = plt.subplots(2, 8, figsize=(12, 3.6))
rows = [("Test digits", range(8)), ("Mistakes", wrong[:8].tolist())]
for row, (name, idxs) in enumerate(rows):
    for col in range(8):
        ax = axes[row, col]
        ax.axis("off")
        if col >= len(idxs):
            continue
        i = idxs[col]
        ax.imshow(images[i, 0], cmap="gray")
        ok = preds[i] == labels[i]
        title = f"{preds[i].item()} ({probs[i, preds[i]].item():.0%})"
        if not ok:
            title += f", true {labels[i].item()}"
        ax.set_title(title, color="green" if ok else "red", fontsize=9)
    axes[row, 0].text(-0.3, 0.5, name, transform=axes[row, 0].transAxes,
                      ha="right", va="center", fontsize=11, rotation=90)
fig.suptitle("Network's guess (confidence)")
fig.tight_layout()

plt.show()
