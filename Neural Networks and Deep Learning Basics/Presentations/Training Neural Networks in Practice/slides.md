---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Training Neural Networks in Practice'
info: |
  ## Training Neural Networks in Practice
  From "the code runs" to "the network trains well" on real data
class: text-center
transition: fade-out
lineNumbers: false
drawings:
  persist: false
mdc: true
duration: 50min
vite:
  server:
    fs:
      strict: false
glowSeed: 450
---

# Training Neural Networks in Practice {.!text-5xl}

### From "the code runs" to "the network trains well" on real data

<div class="mt-4 max-w-2xl mx-auto">
<TitleCurves />
</div>

<div class="opacity-70 text-sm">Neural Networks and Deep Learning Basics · Foundations of Machine Learning</div>

<!--
Last lecture ended with a complete, working training loop: forward, loss, backward, update. That loop is all the machinery there is. But students who try it on their own data quickly find that "it runs" and "it trains well" are very different things. This lecture is about closing that gap.

The chart is real: it's the training and validation error of the network in today's demo, predicting California house prices. Every curve and number in this deck comes from an actual run, and the demo script reproduces them (Neural Networks and Deep Learning Basics/demos/california_housing_mlp.py).

Roadmap, about 50 minutes:
1. Prepare the data (8 min): splitting, scaling, categorical features.
2. Build the model (10 min): output layer, activations, initialization.
3. Optimize (12 min): learning rate, batch size, momentum, Adam, schedules.
4. Generalize (8 min): learning curves, early stopping, weight decay, dropout, batch norm.
5. Go deeper (7 min): why very deep networks fail to train, and residual connections.
6. A working recipe (5 min): sanity checks, common bugs, defaults.
-->

---
glowSeed: 451
---

# Same Loop, Real Data

<div class="text-lg opacity-85 mt-1">The four-line training loop doesn't change. Everything around it does.</div>

<div class="grid grid-cols-5 gap-3 mt-8 text-left text-sm">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>
<div class="font-bold text-blue-300 mb-1">1 · Data</div>
Split first. Scale the inputs. Encode categories.
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
<div class="font-bold text-teal-300 mb-1">2 · Model</div>
Output layer and loss. ReLU. A sensible initialization.
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>
<div class="font-bold text-amber-300 mb-1">3 · Optimize</div>
Learning rate first. Batch size, momentum, Adam, schedules.
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3>
<div class="font-bold text-violet-300 mb-1">4 · Generalize</div>
Read the curves. Early stopping, weight decay, dropout.
</div>

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-3>
<div class="font-bold text-red-300 mb-1">5 · Go deeper</div>
Why deep nets stall, and how residual connections fix it.
</div>

</div>

<div v-click class="mt-10 text-base opacity-90">

Running example: **California Housing**, predict a district's median house value from 8 features (20,640 districts, 1990 census).

</div>

<!--
Frame the lecture as a pipeline. Students already have the middle of it (the training loop from last time). Today fills in everything before it (the data and the model) and everything around it (choosing the optimizer and its settings, and checking whether training worked).

[click] Data. [click] Model. [click] Optimizer. [click] Generalization. [click] Depth: a short section on why simply stacking more layers can make a network worse, and the residual connection, the idea that made 100-layer networks trainable. It's also the idea behind every transformer, two lectures from now.

[click] One running example throughout: California Housing, built into scikit-learn. Eight numeric features per district (median income, house age, average rooms, average bedrooms, population, average occupancy, latitude, longitude), and the target is the median house value in units of $100,000, capped at $500,000 in the census data. It's small enough to train in seconds on a laptop and messy enough to show real problems.
-->

---
layout: center
class: text-center
glowSeed: 452
---

# 1 · Prepare the Data

<div class="opacity-70">Most training failures start before the first epoch.</div>

---
glowSeed: 453
clicks: 2
---

# Split First, Then Preprocess

<SplitScaler :step="$clicks" />

<!--
The order matters, and getting it wrong is the most common way to fool yourself.

Start: split the rows into training (60%), validation (20%), and test (20%) before doing anything else. The validation set is for choosing settings (learning rate, when to stop); the test set is touched once, at the very end.

[click] Then fit the scaler on the training rows only: compute each feature's mean and standard deviation from training data. Apply that same transformation to all three sets. Validation and test get scaled with the training statistics, exactly as a brand-new house would be at prediction time.

[click] The wrong way: fitting the scaler on all the data before splitting. Now the test rows' mean and spread have leaked into the preprocessing. The effect is often small for a scaler, but the habit is dangerous: the same mistake with feature selection or target encoding can inflate scores badly. Callback to the Data Leakage lecture in Model Evaluation. scikit-learn Pipelines make the right order automatic, as we'll see in a few slides.
-->

---
glowSeed: 454
clicks: 1
---

# Features Live on Wildly Different Scales

<FeatureScales :step="$clicks" />

<div class="grid grid-cols-2 gap-4 mt-2 text-sm text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-1>

**Standardize** (the default): $\; z = \dfrac{x - \mu_{\text{train}}}{\sigma_{\text{train}}}$ → mean 0, std 1

</div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-1>

**Normalize** (min-max): $\; x' = \dfrac{x - \min}{\max - \min}$ → range $[0, 1]$. Images: divide by 255.

</div>
</div>

<!--
These are the real training rows. Each bar spans the middle 90% of a feature's values (5th to 95th percentile), and the thin line runs from min to max. The axis is logarithmic, because otherwise population would squash everything else flat: median income runs from 0.5 to 15, while population runs from 3 to 35,682.

Why it matters: the first layer computes a weighted sum. With these raw numbers, population contributes thousands to that sum and income contributes single digits, purely because of units. The network has to undo that with tiny weights for some features and large ones for others, which makes gradient descent slow or unstable. Next slide shows exactly why.

[click] After standardizing: each feature is shifted by its training mean and divided by its training standard deviation. Now every middle-90% bar sits in roughly the same range, about −2 to 2.

But look at the whiskers: average occupancy reaches 80 standard deviations and average bedrooms 71. Standardizing doesn't remove outliers, it just measures them in standard deviations. For heavy-tailed features like these, it can help to clip extreme values or take a log first. Good to mention; we won't need it for the demo.

The two formulas: standardization is the usual choice for tabular data. Min-max normalization squeezes values into [0, 1]; for images, the standard version is just dividing pixel values by 255 (last lecture's MNIST demo did that with ToTensor, then also standardized with Normalize).
-->

---
glowSeed: 455
clicks: 2
---

# Why Scaling Matters: The Shape of the Loss

<ScaleBowl :step="$clicks" />

<!--
This is the same idea from the gradient descent lecture, now with a reason to care.

Both panels show loss contours for a model with two weights, and gradient descent starting from the same point with the same learning rate.

Left: one input feature is on a much larger scale than the other. The loss bowl becomes a long, narrow valley. The gradient points mostly across the valley, not along it.

[click] Run gradient descent. On the left it zigzags from wall to wall: the learning rate that's safe in the steep direction is far too small for the shallow direction. Any larger, and it bounces out of the valley entirely. On the right, with standardized inputs, the bowl is nearly round, so the gradient points almost straight at the minimum.

[click] The takeaway: one learning rate has to work for every direction at once. Scaling makes the directions comparable, so one learning rate can.
-->

---
glowSeed: 456
clicks: 2
---

# On Real Data: Raw Inputs Break SGD

<DemoScaling :step="$clicks" />

<!--
These are actual validation curves from the demo: the same 8 → 64 → 64 → 1 network, 100 epochs, trained four ways.

Start: plain SGD (learning rate 0.01). With standardized inputs (solid), it trains smoothly to a validation RMSE of about 0.56, meaning predictions are typically off by about $56,000. With raw inputs, there is no curve to draw: population values in the thousands made the very first gradient steps enormous, the loss overflowed, and every weight became NaN in the first epoch.

[click] Adam (learning rate 0.001). Adam rescales each weight's step by the size of its recent gradients, which partly compensates for badly scaled inputs. So unscaled Adam does train, but it's noisy and stuck around 0.76. Standardized Adam reaches 0.53, the best of the four.

[click] The lesson: a smarter optimizer can survive bad scaling, but it still trains worse. Scaling is cheap, so always do it.
-->

---
glowSeed: 457
---

# Categories and Missing Values: Build a Pipeline

<div class="grid grid-cols-[1.35fr_1fr] gap-6 mt-2 text-left items-center">
<div>

```python
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric = ["income", "house_age", "rooms"]
categorical = ["ocean_proximity"]

prep = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median"),
                          StandardScaler()), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])
X_train_ready = prep.fit_transform(X_train)   # fit on train only
X_val_ready = prep.transform(X_val)           # reuse train statistics
```

</div>
<div class="flex flex-col gap-3 text-sm">

<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
<b class="text-amber-300">Categories → one-hot.</b> "NEAR BAY" becomes a column of 0s and 1s. Never number them 1, 2, 3: that invents an order.
</div>

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-2>
<b class="text-blue-300">Missing values → impute.</b> NaN in, NaN out: one missing value poisons the whole batch.
</div>

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
<b class="text-teal-300">Regression targets</b> with a large range: standardize <i>y</i> too, and undo it on the predictions.
</div>

</div>
</div>

<div class="text-xs opacity-60 mt-2">Illustrative columns: scikit-learn's California Housing is all numeric; the Kaggle version adds the categorical <code>ocean_proximity</code>.</div>

<!--
Real tables are rarely all clean numbers. This is the standard scikit-learn pattern for getting them into shape, and the output is a plain numeric array ready for torch.tensor.

The ColumnTransformer applies different preprocessing to different columns: numeric columns get missing values filled with the training median and are then standardized; categorical columns are one-hot encoded. fit_transform on the training set learns the medians, means, standard deviations, and category list; transform on validation and test reuses them. That's slide 4's rule, enforced automatically.

One-hot: a categorical column with 5 values becomes 5 columns of 0s and 1s. Don't encode categories as 1, 2, 3 ...: the network would treat "ISLAND" as 4 times "INLAND" and assume an order that doesn't exist. handle_unknown="ignore" means a category that never appeared in training becomes all zeros instead of crashing.

Missing values: a single NaN in an input makes that row's output NaN, the loss NaN, and then every gradient NaN. Impute (median is robust) or drop rows, and consider adding a 0/1 "was missing" column if missingness itself is informative.

Targets: for regression with large target values (prices in dollars, say), standardize the target as well, then invert the transformation on predictions. Our demo's target is already in $100,000s, so it's fine as is.

The column names here are illustrative: the scikit-learn version of the dataset is all numeric. The Kaggle version adds an ocean_proximity column, which is where this example comes from.
-->

---
layout: center
class: text-center
glowSeed: 458
---

# 2 · Build the Model

<div class="opacity-70">Output layer, activations, and where the weights start.</div>

---
glowSeed: 459
---

# The Problem Picks the Output Layer and the Loss

<div class="grid grid-cols-3 gap-5 mt-6 text-left">

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 text-lg mb-2">Regression</div>
<div class="text-sm opacity-85 mb-2">House price, temperature</div>

<code>nn.Linear(h, 1)</code>, no activation

<code>nn.MSELoss()</code>

</div>

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 text-lg mb-2">Binary</div>
<div class="text-sm opacity-85 mb-2">Fault or OK, spam or not</div>

<code>nn.Linear(h, 1)</code>, one logit

<code>nn.BCEWithLogitsLoss()</code>

</div>

<div border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 text-lg mb-2">Multiclass</div>
<div class="text-sm opacity-85 mb-2">Digit 0–9, species</div>

<code>nn.Linear(h, K)</code>, K logits

<code>nn.CrossEntropyLoss()</code>

</div>

</div>

<div class="mt-6 text-base opacity-90">The sigmoid and softmax live <b>inside</b> the PyTorch losses. Apply them yourself only to read off probabilities.</div>

<!--
A quick recap from last lecture, because it's the first decision when building a model and the one with no flexibility: the type of target fixes the output layer and the loss.

Regression: one output, no activation (the output must be free to take any value), mean squared error.
Binary: one output, the raw score or logit; BCEWithLogitsLoss applies the sigmoid internally.
Multiclass: K outputs, one per class; CrossEntropyLoss applies the softmax internally.

The reminder at the bottom matters: putting nn.Sigmoid or nn.Softmax at the end of the model and also using these losses applies the function twice. It still trains, but worse. Doing it inside the loss is also numerically stable.

The hidden layers are where we have choices. That's the next few slides.
-->

---
glowSeed: 460
clicks: 2
---

# Why Not Sigmoid in Hidden Layers?

<GradientChain :step="$clicks" />

<!--
Backpropagation multiplies one derivative per layer on its way back to the early layers. So the derivative of the activation function gets multiplied in once for every layer.

Left: the sigmoid and its slope. The slope is at most 0.25, at z = 0, and almost zero once |z| is more than about 4: the sigmoid "saturates," going flat at 0 or 1.

[click] Right: the best case for sigmoid, every unit sitting exactly at its steepest point, multiplying in 0.25 per layer. After 5 layers the gradient is 0.25⁵ ≈ 0.001 of its size; after 10 layers, about one in a million. The early layers barely learn. This is the vanishing gradient problem, and in practice it's worse than this, because saturated units multiply in nearly 0.

[click] ReLU's slope is exactly 1 for every active unit, so it passes the gradient back without shrinking it. That's the main reason ReLU replaced sigmoid and tanh in hidden layers. (Initialization matters too; that's coming up.)

Sigmoid is still the right choice at the output of a binary classifier, where it turns a score into a probability. The problem is only stacking it in hidden layers.
-->

---
glowSeed: 461
clicks: 1
---

# Dying ReLU, and Its Fixes

<ReluVariants :step="$clicks" />

<!--
ReLU has one failure mode. Its slope is 0 for negative inputs. If a unit's weights get pushed so that its input is negative for every training example, the unit outputs 0 for everything, gets gradient 0, and can never recover. It's "dead."

This isn't hypothetical. [click] In the demo, training with a learning rate of 0.1 (too large) killed 100% of the second hidden layer: every unit outputs zero for every house. The network's prediction is then the same number, $208,560, for every district, just the output bias. Its error matches the "always predict the average" baseline. With the learning rate at 0.001, only 14% of units were dead, and the rest carry the model.

Fixes:
- A sensible learning rate (the most common cause of mass death is a learning rate that's too large).
- Leaky ReLU: a small slope, typically 0.01, for negative inputs, so the gradient is never exactly zero. nn.LeakyReLU().
- GELU: a smooth curve that dips slightly below zero. It's the default in transformers. nn.GELU().

For most MLPs plain ReLU with a reasonable learning rate is fine. Reach for Leaky ReLU or GELU if you find many dead units.
-->

---
glowSeed: 462
clicks: 2
---

# Initialization: Don't Start at Zero

<Symmetry :step="$clicks" />

<!--
Why not initialize every weight to zero, or to the same constant?

Start: two hidden units with identical incoming weights. They compute the same output for every input.

[click] So during backprop they receive identical gradients, and after the update their weights are still identical. Forever. However many hidden units you have, they behave like one. This is the symmetry problem.

[click] Random initialization breaks the tie: each unit starts different, computes something different, gets a different gradient, and learns a different feature. That's why weights start random. Biases can start at zero, since the random weights already break the symmetry.

Next: random, but how large?
-->

---
glowSeed: 463
clicks: 3
---

# Initialization: The Scale Has to Be Right

<InitSpread :step="$clicks" />

<!--
Measured, not simulated: random inputs pushed through 10 ReLU layers of width 256 in PyTorch. The y-axis (log scale) is the standard deviation of each layer's activations: how big the signal is as it travels forward. The same factor applies to gradients on the way back.

Start: weights with standard deviation 0.01, a "small random number" that seems harmless. Each layer shrinks the signal about tenfold. By layer 4 it's about 0.0001, and by layer 10 it's 2 × 10⁻¹⁰: ten orders of magnitude smaller than the input. Nothing usable reaches the output, and gradients vanish just the same on the way back.

[click] Too large, standard deviation 0.15: each layer amplifies by about 1.6, and after 10 layers the activations are about 128 and growing. Exploding signals mean exploding gradients and NaN losses.

[click] He initialization, standard deviation √(2 / fan-in), here 0.088: the signal stays at roughly the same size through all 10 layers. That's the whole goal: keep the variance constant from layer to layer.

[click] PyTorch's default for nn.Linear is not He: it's about 1/√(3 · fan-in), here 0.036, roughly 2.4 times smaller. The signal shrinks over the first few layers, then the biases hold it near 0.02. For a 2–3 layer MLP, like today's demo, that's fine. For a deep ReLU network, initialize with He explicitly (next slide).
-->

---
glowSeed: 464
---

# He and Xavier Initialization

<div class="grid grid-cols-2 gap-6 mt-4 text-left">

<div class="flex flex-col gap-3">

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<div class="font-bold text-teal-300">He (Kaiming): for ReLU</div>

$$
w \sim \mathcal N\!\left(0,\; \frac{2}{n_{\text{in}}}\right)
$$

<div class="text-sm opacity-85">The 2 makes up for ReLU zeroing half its inputs.</div>
</div>

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-2>
<div class="font-bold text-blue-300">Xavier (Glorot): for tanh, sigmoid</div>

$$
w \sim \mathcal N\!\left(0,\; \frac{2}{n_{\text{in}} + n_{\text{out}}}\right)
$$

</div>

</div>
<div>

```python
def init_he(m):
    if isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight,
                                nonlinearity="relu")
        nn.init.zeros_(m.bias)

model.apply(init_he)   # every Linear layer
```

<div class="text-sm opacity-85 mt-3" border="2 solid white/10" bg="white/5" rounded-lg px-3 py-2>
PyTorch's default: std ≈ 1/√(3·n<sub>in</sub>). Fine for shallow MLPs; use He for deep ReLU stacks.
</div>

</div>
</div>

<!--
Both rules come from the same requirement: keep the variance of the signal constant from layer to layer.

He initialization (Kaiming He et al., 2015): variance 2/n_in, where n_in (the fan-in) is the number of inputs to the layer. A neuron sums n_in terms, so its variance grows with n_in; dividing by n_in cancels that. The factor of 2 compensates for ReLU, which sets about half its inputs to zero and so halves the variance.

Xavier initialization (Glorot and Bengio, 2010): designed for tanh and sigmoid, it averages fan-in and fan-out to balance the forward signal and the backward gradient.

The code: model.apply calls the function on every submodule, so this re-initializes every Linear layer with He weights and zero biases. Use nonlinearity="relu" to get the factor of 2.

When to bother: for the 2–3 layer networks in today's demo, PyTorch's default is fine. Deeper ReLU networks benefit from He explicitly, and very deep ones also need the residual connections from the end of this lecture.
-->

---
layout: center
class: text-center
glowSeed: 465
---

# 3 · Optimize

<div class="opacity-70">If you tune only one thing, tune the learning rate.</div>

---
glowSeed: 466
---

# The Learning Rate: Too Small, Too Big, Just Right

<LRPlay />

<!--
This slide is interactive: drag the slider, or click the three presets.

Gradient descent on a two-weight loss surface, starting from the same point every time. Left: the path on the contours. Right: the loss after each step (log scale).

- Too small (η = 0.02): every step is safe and tiny. The loss falls, but painfully slowly; after 40 steps it's still far from the bottom. On real data this looks like a training curve that's still sloping down when you run out of time.
- Just right (η = 0.3): a few confident steps and it's at the bottom (loss down to 1% of its start in 6 steps).
- Too big (η = 0.55): each step overshoots the valley floor and lands higher up the other side. The path bounces back and forth, the loss grows, and on a real network it ends in NaN.

Practical note: after dragging the slider, click the slide background before pressing → to advance (a focused slider takes the arrow keys).

There's a sharp edge between "fast" and "diverges." Here it's at η = 0.5. The best learning rate is usually a bit below that edge, which is why the search on the next slide looks for where the loss starts to blow up.
-->

---
glowSeed: 467
clicks: 2
---

# Finding a Good Learning Rate on Real Data

<LRSearch :step="$clicks" />

<!--
Two ways to choose the learning rate, both on the demo's data.

Left: a learning-rate range test. Train for a few hundred mini-batches while raising the learning rate exponentially every batch, from 10⁻⁶ to 1, and record the (smoothed) loss. At first nothing happens: the steps are too small. Then the loss drops quickly. Then it bottoms out and blows up.

[click] The loss is lowest around 0.09 and blows up past about 0.2. A common rule of thumb: pick a learning rate about ten times smaller than the minimum, here about 0.01. The whole test costs less than one epoch.

[click] Right: the slower, more reliable way: train fully at a few learning rates on a log scale. 10⁻⁴ is still creeping down after 100 epochs. 10⁻³ and 10⁻² both reach about 0.53, with 10⁻² getting there fastest, matching the range test. 10⁻¹ is a disaster: this is the run whose ReLUs all died, stuck at the "predict the average" error.

Always search on a log scale: 0.0001, 0.001, 0.01, 0.1. The difference between 0.001 and 0.002 rarely matters; the difference between 0.001 and 0.1 is everything.
-->

---
glowSeed: 468
---

# Mini-Batch Size: Noisy but Cheap

<BatchNoise />

<!--
Each arrow is the gradient estimated from one mini-batch, with new batches drawn continuously. The white arrow is the true gradient over the whole training set.

With a batch of 1, the estimates are scattered all over: individual examples disagree wildly about which way is downhill. With 16, they cluster. With 256, they're almost exactly the true gradient.

The spread shrinks like 1/√B: a batch 16 times larger is only 4 times less noisy, but costs 16 times as much computation per step.

Practical guidance:
- 32 to 256 is the usual range for MLPs. 64 or 128 is a good default.
- Bigger batches use the hardware (especially GPUs) more efficiently per example, but take fewer steps per epoch.
- If you increase the batch size, you can usually increase the learning rate too, because each step's direction is more trustworthy.
- Some noise is helpful: it jostles the optimizer out of sharp, narrow minima.
-->

---
glowSeed: 469
---

# Momentum: Build Up Speed Along the Valley

<OptimRace :methods="['sgd', 'momentum']" />

<div class="grid grid-cols-2 gap-4 mt-1 text-sm text-left">
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-1>

$v \leftarrow \beta\, v + \nabla L(w) \qquad w \leftarrow w - \eta\, v$

</div>
<div border="2 solid white/10" bg="white/5" rounded-lg px-3 py-1>

$\beta = 0.9$: the velocity remembers about the last 10 gradients. <code>SGD(..., momentum=0.9)</code>

</div>
</div>

<!--
Back to the narrow valley from the scaling slide, because even with scaled inputs, real loss surfaces are full of valleys like this.

Plain gradient descent (gray) zigzags: across the valley the gradient flips sign on every single step, while along the valley it's small and consistent, so progress along the valley is slow. It takes 37 steps to get the loss down to 1% of where it started.

Momentum (amber) keeps a running velocity: each step adds the new gradient to a decaying memory of the previous ones. Along the valley the gradients all point the same way, so they add up and the steps grow. Across the valley they alternate in sign and partly cancel. The result: it reaches 1% of the starting loss in 17 steps, more than twice as fast. Notice it isn't perfectly smooth: it carries speed, so it overshoots and swings back, like a heavy ball rolling down a valley rather than a hiker who can only see the slope under their feet. It changes sides far less often than plain gradient descent, though.

β = 0.9 is the standard choice: the velocity is a weighted average over roughly the last 1/(1 − β) = 10 gradients. In PyTorch it's one argument: torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9).
-->

---
glowSeed: 470
---

# Adam: A Step Size for Every Weight

<OptimRace :methods="['sgd', 'momentum', 'adam']" />

<div class="grid grid-cols-2 gap-4 mt-1 text-sm text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-0 class="adam-eq">

$$
\begin{aligned}
m &\leftarrow \beta_1 m + (1-\beta_1)\, g, \qquad s \leftarrow \beta_2 s + (1-\beta_2)\, g^2 \\
w &\leftarrow w - \eta\, m \,/\, (\sqrt{s} + \epsilon)
\end{aligned}
$$

</div>
<div border="2 solid white/10" bg="white/5" rounded-lg px-3 py-1>

Defaults: $\eta = 10^{-3}$, $\beta_1 = 0.9$, $\beta_2 = 0.999$. The first thing to try. <code>Adam(params, lr=1e-3)</code>

</div>
</div>

<style>
.adam-eq .katex-display { margin: 0.4em 0; font-size: 1em; }
</style>

<!--
Adam (Kingma and Ba, 2015) combines momentum with a second idea: a separate effective step size for every weight.

m is momentum: a running average of gradients. s is a running average of squared gradients, a measure of how large each weight's gradients typically are. The update divides m by √s, so weights with large, steep gradients take smaller steps and weights with small gradients take larger ones. (The real algorithm also corrects m and s for starting at zero; PyTorch handles it.)

On the race (teal): Adam rescales the steep direction and the shallow one to comparable step sizes, so it takes the straightest path of the three, with almost no zigzag. Here it reaches 1% of the starting loss in 20 steps, momentum in 17, plain gradient descent in 37. This valley lines up with the two weights, which is the case Adam's per-weight scaling handles best, and exactly the situation badly scaled inputs create.

That per-weight rescaling is also why unscaled Adam survived on the real data where unscaled SGD diverged: it partly undoes bad input scaling. Partly. Scaled inputs still won by a wide margin.

In practice: Adam with lr = 0.001 is the default first choice for most problems. Well-tuned SGD with momentum sometimes generalizes a little better on large image tasks, but it needs more tuning.
-->

---
glowSeed: 471
clicks: 3
---

# Learning-Rate Schedules: Big Steps, Then Small

<LRSchedules :step="$clicks" />

```python
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=90)
for epoch in range(90):
    train_one_epoch(model, loader, optimizer)
    scheduler.step()                  # once per epoch, after the optimizer steps
```

<!--
A constant learning rate is a compromise: large steps make fast early progress but bounce around the minimum at the end; small steps settle precisely but start slowly. A schedule changes the learning rate during training to get both.

Start: constant.

[click] Step decay: multiply the learning rate by 0.1 every so often (here at epochs 30 and 60). Each drop usually produces a visible step down in the loss curve. StepLR in PyTorch.

[click] Cosine annealing: glide smoothly from the starting learning rate down to nearly zero along a half cosine. Popular because it has no "when to drop" settings to tune. CosineAnnealingLR.

[click] Warmup then cosine: start tiny and ramp up over the first few epochs, then decay. Warmup protects the early steps, when the weights are random and gradients can be large and erratic. Standard for transformers and large batches.

A simple and robust alternative: ReduceLROnPlateau, which cuts the learning rate whenever the validation loss stops improving.

In code, call scheduler.step() once per epoch, after the optimizer steps.
-->

---
layout: center
class: text-center
glowSeed: 472
---

# 4 · Generalize

<div class="opacity-70">Training loss tells you what the network memorized. Validation loss tells you what it learned.</div>

---
glowSeed: 473
clicks: 4
---

# Read the Learning Curves

<CurveDoctor :step="$clicks" />

<!--
The single most useful diagnostic skill: plot training and validation loss every epoch and read the shapes. These four are illustrative but typical.

[click] Underfitting: both curves are high and close together. The model can't even fit the training data. Fix: a bigger model (more units or layers), train longer, or a larger learning rate.

[click] Overfitting: training loss keeps falling while validation loss turns around and rises. The model is memorizing training examples. Fix: early stopping, more data, weight decay, dropout, or a smaller model.

[click] Learning rate too high: both curves are jagged, jumping up and down, or the loss shoots up to NaN. Fix: lower the learning rate (a factor of 3 to 10).

[click] Good fit: both fall and level off, with a small gap. Stop around where validation levels off.

Encourage students to always plot both curves; a single final number hides all of this.
-->

---
glowSeed: 474
---

# Early Stopping: Keep the Best Weights

<EarlyStop />

<!--
The real curves from the demo's third experiment: a bigger network (256 units per layer) that's capable of overfitting.

Watch the animation: after every epoch we check the validation error. Whenever it reaches a new low, we save a copy of the weights: that's a checkpoint (the star). If it hasn't improved for a set number of epochs, the patience (20 here, shaded), we stop and reload the checkpoint.

Here the best validation error came at epoch 22. Training kept improving the training error for 20 more epochs, but validation got no better, so training stopped at epoch 42 and the model reverted to its epoch-22 weights. Those weights then scored 0.530 on the untouched test set (about $53,000 typical error).

Two points:
- Keep the best weights, not the last. The last epoch is almost never the best one.
- Early stopping uses the validation set to make a decision, which is exactly why we report a separate test score.

In code it's a few lines in the loop: track the best validation loss, copy model.state_dict() when it improves, break when patience runs out. The demo script does exactly that.
-->

---
glowSeed: 475
clicks: 2
---

# Two More Regularizers: Weight Decay and Dropout

<div class="grid grid-cols-2 gap-6 mt-2 text-left">

<div class="flex flex-col gap-3 text-sm">

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-2>
<div class="font-bold text-blue-300 mb-1">Weight decay = L2 regularization</div>

Shrink every weight a little each step, so no single weight grows huge:

$$
w \leftarrow w - \eta\,(\nabla L + \lambda w)
$$

</div>

<div v-click="1" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-2>

<code>Adam(..., weight_decay=λ)</code> adds λw to the gradient, so Adam's rescaling weakens it. <code>AdamW(..., weight_decay=0.01)</code> applies the shrinkage separately, and is the one to use.

</div>

</div>

<div>
<DropoutNet :step="$clicks" />
</div>

</div>

<!--
Two standard ways to fight overfitting besides early stopping.

Weight decay is the L2 regularization from the Overfitting and Regularization lecture, applied to a network: add λ times the sum of squared weights to the loss, which adds λw to each gradient. Every step pulls each weight slightly toward zero, which discourages the very large weights that let a network memorize noise.

[click] A PyTorch subtlety. Adam's weight_decay argument adds λw to the gradient before Adam's per-weight rescaling, so weights with large gradients get much less decay than intended. AdamW (Loshchilov and Hutter, 2019) applies the decay directly to the weights, separately from the gradient step. Use AdamW when you want weight decay with Adam; 0.01 is a common starting value.

Dropout (right): during training, each hidden unit is switched off at random with probability p (here 0.5), a new random set every mini-batch. The animation shows different units dropping out on each step. The network can't rely on any single unit, so it learns redundant, more robust features. It's like training a huge ensemble of thinned networks that share weights.

[click] At evaluation time, dropout is off and every unit is active. PyTorch uses "inverted" dropout: during training, the surviving units' outputs are multiplied by 1/(1 − p), here 2, so the expected size of each layer's output is the same in training and evaluation, and nothing needs to change at test time.

This is why model.train() and model.eval() matter: they switch dropout on and off. Forgetting model.eval() before evaluating gives noisy, worse predictions. nn.Dropout(p=0.5) after a hidden layer's activation; 0.1 to 0.5 is typical.
-->

---
glowSeed: 476
---

# Batch Normalization

<div class="grid grid-cols-[1fr_1.1fr] gap-6 mt-4 text-left">

<div class="flex flex-col gap-3">

<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2>
<div class="font-bold text-violet-300 mb-1">Standardize inside the network</div>

For each unit, over the mini-batch:

$$
\hat h = \frac{h - \mu_{\text{batch}}}{\sqrt{\sigma^2_{\text{batch}} + \epsilon}}, \qquad y = \gamma\,\hat h + \beta
$$

<div class="text-sm opacity-85">γ and β are learned, so the layer can undo the normalization if that helps.</div>
</div>

</div>

<div class="flex flex-col gap-3 text-sm">

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">Why:</b> the same reason we scale inputs. Every layer's inputs stay well scaled, so training is faster and tolerates larger learning rates.
</div>

<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
<b class="text-amber-300">Train vs. eval:</b> training uses each batch's own mean and variance and keeps running averages of them. <code>model.eval()</code> switches to the running averages, so one prediction doesn't depend on the rest of its batch.
</div>

<div border="2 solid white/10" bg="white/5" rounded-lg px-4 py-2>
<code>nn.Linear(64, 64), nn.BatchNorm1d(64), nn.ReLU()</code>
</div>

</div>
</div>

<!--
Batch normalization (Ioffe and Szegedy, 2015) applies the "standardize your inputs" idea to every hidden layer.

For each unit, compute the mean and variance of its values over the current mini-batch, standardize, then scale and shift by two learned parameters, γ and β. Those let the network keep the normalization, undo it, or anything in between.

Why it helps: each layer's inputs stay in a well-scaled range even as the earlier layers change, so the loss surface is better conditioned (the scaling slide, inside the network). In practice networks with batch norm train faster, tolerate larger learning rates, and are less sensitive to initialization.

Train vs. eval: during training, statistics come from the current batch, and the layer also keeps a running average of them. In evaluation mode it uses the running averages. That's the second reason model.eval() matters: without it, a prediction would depend on whichever other examples happened to share its batch.

Placement: usually Linear → BatchNorm → activation. For small MLPs it's optional; it matters more in deep networks, and it's standard in CNNs (next lecture). Transformers use a close relative, layer normalization, which normalizes across a single example's features instead of across the batch.
-->

---
layout: center
class: text-center
glowSeed: 477
---

# 5 · Go Deeper

<div class="opacity-70">More layers should never hurt. In practice, they do.</div>

---
glowSeed: 478
clicks: 2
---

# Deeper Should Be Better… But It Isn't

<DepthDegradation :step="$clicks" />

<!--
A puzzle. A deeper network can represent everything a shallower one can: the extra layers could just learn to pass their input through unchanged. So a deeper network should never fit the training data worse.

These are real training curves on California Housing (training error, not validation, so this isn't overfitting).

Start: a plain 4-layer network trains normally, reaching a training RMSE of about 0.50.

[click] The same kind of network with 22 layers, same optimizer and learning rate: it barely moves. Its training error stays around 1.15, which is what you'd get by always predicting the average price. Adding layers made it fail to train at all.

This is the degradation problem that He et al. reported in 2015 (their 56-layer network had higher training error than their 20-layer one). It isn't overfitting, since the training error itself is worse. The deeper network is simply much harder to optimize.

[click] The fix, in teal: the same 22 layers with residual connections. It trains as well as the shallow network, slightly better in fact. The next three slides explain what changed.
-->

---
glowSeed: 479
clicks: 2
---

# The Residual Block: Learn the Change

<ResidualBlock :step="$clicks" />

<!--
The fix (He, Zhang, Ren, and Sun, 2015, "Deep Residual Learning," the ResNet paper) is a single wire.

Start: a plain block. Two layers transform the input x into some output; call that transformation F(x). Each block has to produce the full new representation.

[click] A residual block adds a skip connection: the input x bypasses the two layers and is added back to their output. The block computes y = x + F(x). Now the layers F only have to learn the change, or residual, to apply to x, not the whole output.

[click] Why that's easier: if the best thing a block can do is nothing, a plain block has to learn the identity function exactly through its weights, which is surprisingly hard. A residual block just has to push F toward zero, and small random weights already start it near there. So extra residual blocks start out as "almost pass-through" and can only help. That's exactly the "deeper can't be worse" argument from the previous slide, now actually true.
-->

---
glowSeed: 480
clicks: 2
---

# Why It Works: A Highway for the Gradient

<GradHighway :step="$clicks" />

<!--
The other half of the explanation is what happens on the backward pass.

[click] The measured gradient for each block's first layer, at initialization, in the 22-layer plain network. Block 10 (nearest the output) gets a healthy gradient. Moving toward the input, it collapses by roughly a factor of 5 to 8 per block, and by block 1 it's 4 × 10⁻⁸, about seven million times smaller than at block 10. The early layers receive essentially no learning signal, which is why the plain deep network was stuck.

[click] The residual network, same depth: the gradient reaches every block. It's between about 1 and 4 everywhere: not identical, but the same order of size from the first block to the last, instead of collapsing by a factor of thousands.

The formula explains it. For y = x + F(x), the derivative is ∂y/∂x = 1 + ∂F/∂x. Backprop multiplies one such factor per block. In a plain network each factor is ∂F/∂x alone, and a product of many factors smaller than 1 vanishes, like the sigmoid chain earlier. With the skip, each factor is 1 plus something, and the "1" gives the gradient a direct path back through every block: a highway. Even if every F contributed nothing, the gradient would still arrive intact.

If a sharp student asks: this block outputs ReLU(x + F(x)), so the exact derivative also multiplies by the ReLU's slope at each unit (1 if active, 0 if not). For the active units the "1 +" path is intact, which is what keeps the gradient alive; some designs move the ReLU inside F so the skip path is a pure identity.
-->

---
glowSeed: 481
---

# A Residual Block in PyTorch

<div class="grid grid-cols-[1.25fr_1fr] gap-6 mt-2 text-left items-center">
<div>

```python {all|8|all}
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
```

</div>
<div class="flex flex-col gap-3 text-sm">

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">The input and output must have the same shape</b> to add them. If the width changes, pass x through a Linear layer on the skip path.
</div>

<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2>
<b class="text-violet-300">Everywhere now:</b> ResNet-50 and ResNet-152 for images (next lecture), and every layer of a transformer.
</div>

</div>
</div>

<!--
The whole idea is the one line, x + self.f(x). This is exactly the network from the depth experiment: 10 residual blocks of width 64, 22 Linear layers in total.

[click] Line 8: the addition. Everything else is an ordinary small network.

Shapes: x and f(x) are added element by element, so they must have the same shape. Within a block of fixed width, that's automatic. When a network changes width between stages, the skip path gets its own small Linear layer (a projection) to match the shapes.

Where residual connections show up: they're what made the 152-layer ResNet possible in 2015, the architecture that won that year's ImageNet competition, which we'll see in the CNN lecture. And every layer of a transformer is wrapped in a residual connection: x + Attention(x), then x + MLP(x). Without them, deep transformers wouldn't train either.
-->

---
layout: center
class: text-center
glowSeed: 482
---

# 6 · A Working Recipe

<div class="opacity-70">Cheap checks first, long runs second.</div>

---
glowSeed: 483
clicks: 2
---

# Sanity Checks Before a Long Run

<SanityChecks :step="$clicks" />

<!--
Three checks that take a minute and catch most bugs before you waste an hour of training. These numbers are from the MNIST and California Housing demos.

1. Check the starting loss. Before any training, a randomly initialized classifier should be guessing, giving each of K classes probability about 1/K, so the cross-entropy should be about ln K. For MNIST's 10 classes that's ln 10 ≈ 2.303, and the untrained network measures 2.305. If the starting loss is much higher, the network is confidently wrong at the start: often a sign of bad initialization or forgetting to scale the inputs.

[click] 2. Overfit one tiny batch. Take 32 examples and train on only those. A working network and training loop should drive the loss to almost zero: here from 2.30 to under 0.001 in 100 steps. If it can't memorize 32 examples, something is broken: the labels don't match the inputs, gradients aren't flowing, zero_grad is missing, or the learning rate is far off. This is the single most useful debugging step.

[click] 3. Compare with a baseline. On California Housing, always predicting the average price gives a test RMSE of 1.16 ($116,000); linear regression gives 0.73. Our MLP gets 0.53. Without the baselines, "0.53" means nothing. If your network can't beat linear regression, look for a bug before tuning.
-->

---
glowSeed: 484
---

# Common Bugs

<div class="grid grid-cols-3 gap-4 mt-6 text-left text-sm">

<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<b class="text-red-300">Forgot <code>zero_grad()</code></b><br>Gradients add up across steps; training becomes erratic.
</div>

<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<b class="text-red-300">Forgot <code>model.eval()</code></b><br>Dropout and batch norm stay in training mode while you evaluate.
</div>

<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<b class="text-red-300">Softmax twice</b><br>A softmax layer in the model and <code>CrossEntropyLoss</code>.
</div>

<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<b class="text-amber-300">Scaler fit on all data</b><br>Test statistics leak into training.
</div>

<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<b class="text-amber-300">Not shuffling</b><br>Sorted data gives every mini-batch the same kind of examples.
</div>

<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<b class="text-amber-300">Shape mismatch</b><br>Predictions (N, 1) vs. targets (N,) broadcast to (N, N) in <code>MSELoss</code>.
</div>

</div>

<!--
Six bugs that every practitioner has made. None of them crash; they just make training quietly worse, which is why they're dangerous.

Red, in the training loop:
- zero_grad: PyTorch adds new gradients to the stored ones. Without optimizer.zero_grad() each step, every step uses the sum of all previous gradients.
- model.eval(): needed before evaluation whenever the model has dropout or batch norm. And model.train() before training again.
- Double softmax: covered last lecture; CrossEntropyLoss already applies it.

Amber, in the data:
- Leaky scaling: slide 4.
- Not shuffling: if the data is sorted (by date, by class, by price), consecutive mini-batches are all alike and the gradient swings from batch to batch. DataLoader(shuffle=True) for training.
- Shapes: if the model outputs shape (N, 1) and the targets have shape (N,), MSELoss broadcasts them to an (N, N) matrix of every prediction minus every target. PyTorch prints a warning, but the loss is silently wrong. Make them match: y.unsqueeze(1) or pred.squeeze(1). The demo uses unsqueeze(1) for exactly this reason.
-->

---
glowSeed: 485
---

# The Default Recipe

<div class="grid grid-cols-[1.1fr_1fr] gap-6 mt-3 text-left">

<div class="text-sm flex flex-col gap-2">

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-1.5><b class="text-blue-300">Data:</b> split, then standardize (fit on train). One-hot categories.</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-1.5><b class="text-teal-300">Model:</b> 2–3 hidden layers of 64–256 ReLU units. Output and loss from the problem type.</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-1.5><b class="text-amber-300">Optimizer:</b> Adam (or AdamW), lr 10⁻³, batch 64–128. Tune lr first, on a log scale.</div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-3 py-1.5><b class="text-violet-300">Monitor:</b> plot train and validation loss. Early stopping, keep the best weights.</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-1.5><b class="text-red-300">If needed:</b> weight decay, dropout, schedules, He init, residual blocks for depth.</div>

</div>

<div>
<RecipeResults />
</div>

</div>

<!--
Everything today, compressed into defaults that work for most tabular problems. Start here, then change one thing at a time while watching the learning curves.

The order of the "if needed" items matters: weight decay and dropout when the curves show overfitting; a schedule when training plateaus at the end; He initialization and residual connections only when going deep.

Right: what the recipe got on California Housing's test set, data the model never saw during training or tuning. The MLP's typical error is about $53,000, against $73,000 for linear regression and $116,000 for always guessing the average. Students can reproduce every number with uv run california_housing_mlp.py.
-->

---
glowSeed: 486
---

# Summary

<div class="grid grid-cols-2 gap-x-8 gap-y-3 mt-6 text-left text-base max-w-4xl mx-auto">

<div v-click>🧹 <b>Scale the inputs</b>, with statistics from the training set only.</div>
<div v-click>🎯 <b>The learning rate</b> matters most. Search on a log scale.</div>
<div v-click>⚡ <b>ReLU and the right initialization</b> keep signals and gradients alive.</div>
<div v-click>🏃 <b>Momentum and Adam</b> handle narrow valleys and uneven scales.</div>
<div v-click>📈 <b>Read both learning curves</b>; stop early and keep the best weights.</div>
<div v-click>🛣️ <b>Residual connections</b> make very deep networks trainable.</div>

</div>

<div v-click class="mt-12 opacity-85"><b>Next:</b> Convolutional Neural Networks: networks built for images, where depth and residual connections really pay off.</div>

<!--
Six takeaways, one per section.

[click] Scaling, with the training-set statistics only.
[click] The learning rate is the first thing to tune, on a log scale, and a range test finds a good starting point in under an epoch.
[click] ReLU plus a variance-preserving initialization keeps signals and gradients from vanishing or exploding.
[click] Momentum smooths the zigzag; Adam adds a per-weight step size and is the default first choice.
[click] Always plot training and validation loss; use early stopping and keep the best checkpoint.
[click] When going deep, residual connections give the gradient a highway back to the first layers.

[click] Next lecture: convolutional networks. Images have structure an MLP ignores (nearby pixels are related, and a cat is a cat anywhere in the picture). CNNs build that in, and they're where very deep, residual networks first proved themselves.

Homework suggestion: run california_housing_mlp.py, then change one setting at a time (no scaling, a different learning rate, a bigger network without early stopping) and predict what the curves will do before looking.
-->
