# Neural Networks Demos

Hands-on PyTorch scripts for the Neural Networks and Deep Learning unit. They use the same
building blocks as the slides: `nn.Linear` layers, an activation, a loss, and the
forward → loss → backward → update training loop.

```bash
cd "Neural Networks and Deep Learning Basics/demos"

uv run mnist_mlp.py                # a multilayer perceptron that reads handwritten digits (~97.5% in ~30 s)
uv run california_housing_mlp.py   # training in practice: scaling, learning rate, early stopping (~15 s)
```

## `mnist_mlp.py`

A multilayer perceptron for MNIST: each 28×28 image is flattened to 784 inputs, passed through
two hidden ReLU layers (128 and 64 units), and turned into 10 scores, one per digit. It trains
for 5 epochs with Adam and cross-entropy loss, printing the test accuracy after each epoch.
Then it opens two windows:

- the training loss and test accuracy per epoch
- a row of test digits with the network's guess and confidence, and a row of digits it got wrong

The settings at the top of the script (`EPOCHS`, `BATCH_SIZE`, `LEARNING_RATE`, `HIDDEN`) are
meant to be changed. Things to try: one hidden layer instead of two, many more or fewer units,
a much larger or smaller learning rate, or removing the `nn.ReLU()` layers (accuracy drops to
about 92%, roughly what logistic regression gets, because the layers collapse into one linear layer).

The first run downloads MNIST (about 12 MB) into `data/` (git ignores this folder). The script
uses an NVIDIA or Apple-silicon GPU if there is one; otherwise the CPU, which is fast enough.

## `california_housing_mlp.py`: training in practice on real tabular data

The companion to the *Training Neural Networks in Practice* lecture: every curve and number on
those slides comes from this script. It predicts a California district's median house value
(in $100,000s) from 8 numeric features, splits the data 60/20/20 into train/validation/test,
and fits the `StandardScaler` on the training rows only. Then it runs three experiments:

1. **Scaling:** the same 8 → 64 → 64 → 1 network on raw vs. standardized inputs, with plain SGD
   and with Adam. SGD on raw inputs blows up to NaN in the first epoch; Adam survives but does
   much worse than on standardized inputs.
2. **Learning rate:** Adam at 1e-4, 1e-3, 1e-2 and 1e-1. Too small crawls; 1e-1 kills every ReLU
   in the second layer, and the network predicts the same price for every district.
3. **Early stopping:** a bigger network (256 units per layer) trained until the validation error
   stops improving for 20 epochs, keeping the best weights rather than the last.

It finishes with the test error against two baselines (always predicting the average, and linear
regression) and opens one figure with all three experiments. The dataset (~1 MB) downloads into
`data/` on the first run. Uses the CPU; the whole script takes about 15 seconds.

The functions (`load_data`, `train`, `rmse`) are importable, and the lecture's
`scripts/make_data.py` reuses them, so the slides and the demo can't drift apart.

## `har_mlp.py`: smartphone activity recognition

```bash
uv run har_mlp.py
# Save the plots without opening windows:
uv run har_mlp.py --no-show
```

Uses the supplied `data/human+activity+recognition+using+smartphones/UCI HAR Dataset.zip`
directly, without downloading or extracting it. The task is to distinguish walking,
walking upstairs, walking downstairs, sitting, standing, and laying from a phone
worn at the waist.

Each example is a 2.56-second window with 128 sensor samples at 50 Hz. The demo plots
one example per activity with the phone's x/y/z total acceleration (including gravity),
so both movement and changes in orientation are visible. These are illustrative
windows, not averages over an activity.

The MLP uses the dataset's **561 engineered features** (summaries of accelerometer
and gyroscope signals in time and frequency), rather than the raw traces. A second
plot shows those actual feature vectors before standardization. The model is
`561 → 128 → 64 → 6`, with ReLU hidden layers and cross-entropy loss. Change `HIDDEN`,
`EPOCHS`, `BATCH_SIZE`, and `LEARNING_RATE` at the top of the script to experiment;
`HIDDEN = ()` gives a linear classifier for comparison.

The official train/test split keeps participants separate. The demo also reserves
participants from the training split for validation, fits its standardizer only on
the remaining training participants, and selects the epoch with the lowest validation
loss. It evaluates the official test set at the end, printing a majority-class baseline,
accuracy, and per-activity precision/recall. This avoids splitting overlapping windows
from the same person across training and validation.

Four figures are saved in `outputs/har_mlp/` and also opened interactively by default:

- `sensor_examples.png`: three acceleration axes for one window per activity
- `feature_examples.png`: the 561 input features for those same windows
- `training_curves.png`: training/validation loss and accuracy
- `confusion_matrix.png`: which activities the model confuses on the test set

Dataset: UCI HAR, supplied README and feature descriptions inside the archive.
