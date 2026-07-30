---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Capstone Project: An End-to-End ML Pipeline'
info: |
  ## Capstone Project: An End-to-End ML Pipeline
  Integrate the whole semester into one defensible project
class: text-center
transition: fade-out
lineNumbers: false
drawings:
  persist: false
mdc: true
vite:
  server:
    fs:
      strict: false
glowSeed: 1110
---

# Capstone Project: An End-to-End ML Pipeline

### Integrate the whole semester into one defensible project

<div class="pt-8 opacity-80 text-lg">Capstone - Project Time · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This is the synthesis lecture for the course. Every prior unit taught a piece in isolation — Mathematical Foundations gave us vectors, gradients, and matrix operations; Core ML Concepts gave us the bias-variance tradeoff, loss functions, and the train/validation/test discipline; Supervised Learning and Ensemble Methods gave us a toolbox of models; Model Evaluation gave us metrics and pitfalls; Optimization in Practice gave us tuning strategy; Broader Context gave us the ethical lens. A capstone project is where all of that has to work together at once, under your own judgment, without a homework file telling you which formula to apply.

Today's deck is not a new algorithm — it is a project management discipline for applied machine learning. We will walk one running case study end to end: predicting which subscribers of a fictional service will churn (cancel) next month. Every stage of the pipeline — problem framing, cleaning, splitting, feature engineering, baselining, model comparison, tuning, evaluation, interpretation, and write-up — will be grounded in that one dataset so you can see how decisions at one stage constrain the stages that follow. Treat this deck as the checklist you return to while building your own capstone.
-->

---
glowSeed: 1111
---

# The Capstone Pipeline, End to End

<div class="mt-4" role="img" aria-label="Ten-stage pipeline: problem framing, EDA and cleaning, split, preprocessing and features, baseline, model comparison, tuning, evaluation, interpretation, write-up">
<div class="grid grid-cols-5 gap-3 text-center text-sm">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>1. Frame the problem</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>2. EDA & cleaning</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>3. Split first</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>4. Preprocess & engineer</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>5. Baseline</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>6. Compare models (CV)</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>7. Tune hyperparameters</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3>8. Evaluate on test</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3>9. Interpret & check fairness</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3>10. Write it up</div>
</div>
</div>

<div v-click class="mt-8 text-center text-sm" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-3>Each arrow is a place where information can leak backward and quietly invalidate your results.</div>

<!--
Preview the whole map before diving into any one box, so each later slide has a home. The ten stages fall into four phases, color-coded above: understanding and cleaning the data (teal), establishing an honest information boundary between train and test data (blue), building and selecting a model (amber), and communicating the result responsibly (violet).

The single sentence at the bottom is the thesis of this entire lecture: nearly every capstone mistake is a leakage mistake — information from the future, from the test set, or from the target variable sneaking into a stage where it should not be visible yet. Stage 2 (split before you touch the data) is the single most common place students get this wrong, so we will spend real time on it. Keep this slide's stage numbers in mind; later slides will refer back to "Stage 3" or "Stage 6" using this same numbering.
-->

---
glowSeed: 1112
---

# Choose a Clear, Feasible Problem

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Target</div>
<div class="text-sm leading-relaxed opacity-90">Regression for continuous outcomes; classification for discrete labels.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Scale</div>
<div class="text-sm leading-relaxed opacity-90">Enough rows for honest splits, small enough for fast iteration.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Interest</div>
<div class="text-sm leading-relaxed opacity-90">Domain curiosity improves feature engineering and error analysis.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Success</div>
<div class="text-sm leading-relaxed opacity-90">State in one sentence what a useful model would accomplish.</div>
</div>
</div>

<!--
Before any code is written, pin down what kind of prediction problem you have. A regression target is a continuous number — price, temperature, days until an event — and is evaluated with error metrics like RMSE or R-squared, the tools built in Supervised Learning - Regression. A classification target is a discrete label — churn or not, spam or not, one of several species — and is evaluated with the confusion-matrix-derived metrics from Model Evaluation. Getting this wrong at the start (for example, treating an ordinal satisfaction score as unordered categories) cascades into every later choice of model and metric.

Scale matters because cross-validation and a held-out test set both need enough rows to produce stable estimates; a few hundred rows makes every metric noisy, which is exactly the concern the upcoming Statistical Significance slide addresses. Structured tabular data — rows of individual observations, columns of features — is the safest scope for this course capstone: it plays to every tool the course covered, and it is honest about what you can defend in the time available. Text, image, or streaming projects are welcome but carry extra preprocessing risk. Next: we will fix a single example problem and follow it through every remaining stage.
-->

---
glowSeed: 1113
---

# Meet the Worked Example: Subscription Churn

<div class="grid grid-cols-2 gap-8 items-start mt-4">
<div>
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Problem</span>
<span class="text-sm opacity-85"> — Predict which active subscribers cancel in the next billing cycle.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Data</span>
<span class="text-sm opacity-85"> — 5,000 customers; tenure, charges, contract type, support tickets, login activity.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Target</span>
<span class="text-sm opacity-85"> — Binary label <code>churned</code>: about 16% of customers churn (imbalanced classes).</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Use</span>
<span class="text-sm opacity-85"> — Flag likely churners so retention offers reach them before they cancel.</span>
</div>
</div>
</div>
<div>

```python
import pandas as pd

df = pd.read_csv("subscribers.csv")
print(df.shape)
print(df.columns.tolist())
```

<div v-click class="mt-3 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<code>tenure_months, monthly_charges, total_charges,<br/>
contract_type, plan_type, support_tickets,<br/>
last_login_gap_days, cancellation_request_date, churned</code>
</div>

</div>
</div>

<!--
From this slide forward, every code example and every number on screen refers to this one dataset, so you can watch a single project accumulate decisions across the whole pipeline rather than seeing ten disconnected snippets. This is a binary classification problem: churned is 1 if the customer cancels next cycle, 0 otherwise. Only about 16% of rows are churners — a class imbalance that will matter heavily once we choose metrics in Stage 4, because a model that just predicts "no churn" for everyone will already look deceptively accurate.

Notice one column name deliberately planted here: cancellation_request_date. In a real subscription system this field is only populated after a customer has already initiated cancellation — which means it is downstream of the outcome we are trying to predict. Keep that column in mind; it becomes the running example of target leakage two slides from now. This is exactly the kind of trap the Model Evaluation unit's "Common Pitfalls" lecture warns about, and it is far easier to plant deliberately in a lecture than to catch by accident in your own project, so build the habit of asking "could this column only exist because the label already happened?" for every feature.
-->

---
glowSeed: 1114
---

# Stage 1 — EDA and Cleaning

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Understand</div>
<div class="text-sm leading-relaxed opacity-90">Shape, types, missingness, duplicates, and outliers.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Investigate</div>
<div class="text-sm leading-relaxed opacity-90">Suspiciously perfect target relationships may signal leakage.</div>
</div>
</div>

```python
df = pd.read_csv("subscribers.csv")
df.info()
print(df.describe())
print(df.isna().sum())
print("duplicates:", df.duplicated().sum())

target_corr = df.corr(numeric_only=True)["churned"]
print(target_corr.sort_values(ascending=False))
```

<!--
Exploratory data analysis (EDA) is the disciplined first look at a dataset before any modeling decision is made. df.info() reports column data types and non-null counts in one pass — a column read as "object" when you expected numbers usually means stray text like "N/A" or a currency symbol got mixed into a numeric field. df.describe() gives count, mean, standard deviation, and quartiles for every numeric column, which is how you first notice an outlier: a max monthly_charges of $9,999 next to a 75th percentile of $95 is not a wealthy customer, it is a data entry error. df.isna().sum() counts missing values per column, which sets up the next slide.

The last two lines are the leakage check promised on the previous slide: correlating every numeric column against the churned target. In our subscriber data, a hypothetical numeric encoding of cancellation_request_date would show a correlation near 1.0 with churned — a huge red flag, because no legitimate predictive feature should be nearly perfectly aligned with the outcome before the model has done any work. A correlation that good is not a gift; it almost always means the feature encodes the answer. Document every cleaning decision you make in a notebook cell or README as you go — do not silently overwrite or drop rows, because a reviewer (or your future self debugging a metric drop) needs to reconstruct exactly what changed and why.
-->

---
glowSeed: 1115
---

# Stage 1b — Handling Missing Data

<div class="grid grid-cols-2 gap-4 mt-5">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Listwise deletion</div>
<div class="text-sm leading-relaxed opacity-90">Drop rows with missing values. Safe only if missingness is rare and unrelated to the target (MCAR); otherwise it biases the sample.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Mean / median / mode</div>
<div class="text-sm leading-relaxed opacity-90">Fill with a training-set statistic. Fast and stable; median resists outliers better than mean for skewed columns like charges.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Model-based (KNN / iterative)</div>
<div class="text-sm leading-relaxed opacity-90">Predict the missing value from other columns. More accurate, more expensive, and still fit on training data only.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Missingness indicator</div>
<div class="text-sm leading-relaxed opacity-90">Add a binary flag column recording where a value was missing — sometimes "missing" is itself informative.</div>
</div>
</div>

<!--
Not all missing data behaves the same way, and the right fix depends on why values are missing. Statisticians distinguish three mechanisms: MCAR (missing completely at random — a sensor glitch unrelated to anything), MAR (missing at random given other observed variables — older customers skip an optional survey field at a different rate, but that rate is explained by tenure), and MNAR (missing not at random — customers who are about to churn stop logging in, so last_login_gap_days is missing precisely because of the outcome we care about). Listwise deletion is only defensible under MCAR with a small fraction of rows affected; under MAR or MNAR it silently removes exactly the customers who matter most and biases every downstream estimate.

For our subscriber data, missing total_charges typically means a customer joined this billing cycle and has no history yet — that is closer to MAR, explainable by tenure_months. Imputing with the training set's median total_charges is a reasonable default; imputing with the mean would be pulled upward by the high-paying long-tenure customers with heavy skew. When missingness itself carries signal — as it likely does for last_login_gap_days on customers approaching churn — add a separate boolean indicator column so the model can use "this value was missing" as a feature in its own right, rather than only its imputed replacement. Whatever you choose, treat it as a learned transformation: as the next stage will stress, imputation statistics must be computed from the training fold only, then applied unchanged to validation and test data.
-->

---
glowSeed: 1116
---

# Stage 1c — Outliers, Duplicates, and Leakage

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Outliers</div>
<div class="text-sm leading-relaxed opacity-90">Cap, transform (log), or investigate as data-entry errors — do not delete without a reason.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Duplicates</div>
<div class="text-sm leading-relaxed opacity-90">Exact-row duplicates inflate certain customers' influence and can leak across a split.</div>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">Leakage</div>
<div class="text-sm leading-relaxed opacity-90"><code>cancellation_request_date</code> only exists after churn — drop it before modeling.</div>
</div>
</div>

```python
df = df.drop_duplicates()
df = df.drop(columns=["cancellation_request_date"])

cap = df["monthly_charges"].quantile(0.99)
df["monthly_charges"] = df["monthly_charges"].clip(upper=cap)
```

<!--
An outlier is a value far from the bulk of the distribution; the question is always whether it reflects a real (if rare) customer or a data-entry mistake. The safest default is to investigate before deleting: a monthly_charges value of $9,999 is almost certainly an error and worth capping (clipping) at a high percentile such as the 99th, which limits its influence without discarding the row entirely. A genuinely large but plausible value — a long-tenure enterprise customer paying a premium plan — should usually stay, because removing real high-value cases can bias the model against exactly the customers a business most wants to understand.

Exact duplicate rows inflate the effective weight of whichever customer they represent during training and, worse, can end up split across train and test if you deduplicate after splitting instead of before — meaning the model is partly tested on rows it already memorized. Always deduplicate before the train/validation/test split in Stage 2. Finally, we act on the leakage flag raised two slides ago: cancellation_request_date is dropped outright, not imputed or transformed, because no legitimate version of this feature can exist at prediction time — when you are trying to flag an active customer, you by definition do not yet know if or when they requested cancellation. This is the single most common reason a capstone reports an unbelievably high score in development and then fails in a real deployment or a held-out check.
-->

---
glowSeed: 1117
---

# Stage 2 — Split, Then Preprocess

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Split first</span>
<span class="text-sm opacity-85"> — Create train, validation, and test boundaries before learned preprocessing.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Pipeline</span>
<span class="text-sm opacity-85"> — Fit imputers, encoders, and scalers only on training folds.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Stratify</span>
<span class="text-sm opacity-85"> — Preserve the 16% churn rate in every split so each set is representative.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Raw data then Train / val / test then Pipeline fit on train then Transform held-out">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Raw data</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Train / val / test</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Pipeline fit on train</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Transform held-out</div>
</div>
</div>

</div>
</div>

<!--
This is the capstone's non-negotiable leakage boundary, and it directly extends the Core ML Concepts lecture on Train-Validation-Test Splits and Cross-Validation. The rule is: compute the split first, on raw (but cleaned) data, and only after that split exists should any statistic be learned — a mean for imputation, a category vocabulary for encoding, a min/max or standard deviation for scaling. If you impute or scale using the full dataset before splitting, information about the validation and test rows leaks into the numbers the training pipeline learns from, which inflates your reported performance in a way that will not reproduce on truly new customers.

Because churned is imbalanced at roughly 16%, use a stratified split (scikit-learn's train_test_split with stratify=y, or StratifiedKFold for cross-validation) so every split preserves that same rate — an unstratified split on a small dataset can accidentally produce a validation fold with almost no churners, making every metric on it unstable. In practice you enforce the fit-on-train-only rule by building a scikit-learn Pipeline that chains the imputer, encoder, scaler, and model into one object: calling .fit() on that pipeline with only the training rows guarantees every learned parameter comes from training data, and calling .transform() or .predict() on validation or test data reuses those exact parameters rather than relearning them. Next, we turn the cleaned, split data into model-ready features.
-->

---
glowSeed: 1118
---

# Stage 2b — Encoding and Feature Engineering

<div class="grid grid-cols-2 gap-3 mt-3">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
<div class="font-bold text-teal-300 mb-1 text-sm">One-hot encoding</div>
<div class="text-xs leading-snug opacity-90"><code>contract_type</code> has no natural order — one-hot avoids inventing a false ranking.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>
<div class="font-bold text-blue-300 mb-1 text-sm">Ordinal encoding</div>
<div class="text-xs leading-snug opacity-90"><code>plan_type</code> (basic &lt; standard &lt; premium) has real order — an integer code preserves it.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>
<div class="font-bold text-amber-300 mb-1 text-sm">Scaling</div>
<div class="text-xs leading-snug opacity-90">Standardize numeric columns for distance- or gradient-based models (KNN, SVM, logistic regression).</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3>
<div class="font-bold text-violet-300 mb-1 text-sm">Engineered feature</div>
<div class="text-xs leading-snug opacity-90"><code>charges_per_month_tenure</code> = total_charges / tenure_months captures spending trend.</div>
</div>
</div>

```python {all|1-2|4-8}
numeric = ["tenure_months", "monthly_charges", "support_tickets"]
categorical = ["contract_type", "plan_type"]

preprocess = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                       ("scale", StandardScaler())]), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])
```

<!--
Most models need every feature expressed as a number, so categorical columns must be encoded — but which encoding is correct depends on whether the categories have a natural order. contract_type has no order, so one-hot encoding creates a separate 0/1 column per category, and no encoding accidentally implies "two-year contract" is numerically "greater than" month-to-month. plan_type, by contrast, has a genuine order (basic, standard, premium), so an ordinal integer code (0, 1, 2) is appropriate and lets tree-based models split on it efficiently without exploding the column count. Using one-hot encoding on a truly ordinal variable throws away information; using ordinal encoding on a truly unordered variable invents a false relationship the model will try to exploit.

Numeric scaling matters for some models and not others: distance-based methods like k-Nearest Neighbors and margin-based methods like Support Vector Machines (covered in Supervised Learning - Classification) are sensitive to feature scale, because a column measured in dollars will dominate a column measured in months unless both are standardized to comparable ranges. Tree-based models (Decision Trees, Random Forests, Gradient Boosting) are scale-invariant and do not need this step, but it rarely hurts to include it in a shared pipeline. Feature engineering is where domain knowledge earns its keep: charges_per_month_tenure normalizes spending by how long someone has been a customer, which can separate "a new customer paying a lot" from "a loyal customer paying a lot" — a distinction the raw columns alone cannot make. Build every engineered feature only from information available at prediction time, using the same fit-on-train discipline from the previous slide.
-->

---
glowSeed: 1119
---

# Stage 3 — Establish a Baseline

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Dummy baseline</div>
<div class="text-sm leading-relaxed opacity-90">Predicting "no churn" for everyone scores <strong>85% accuracy</strong> — because only 16% of customers churn.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Simple model</div>
<div class="text-sm leading-relaxed opacity-90">Try logistic regression before complex learners; it is fast, interpretable, and a real benchmark.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Earn complexity</div>
<div class="text-sm leading-relaxed opacity-90">A forest or boosted model should beat both benchmarks by more than noise to justify itself.</div>
</div>
</div>

<div v-click class="mt-8 text-center text-sm" border="2 solid red-800" bg="red-800/20" rounded-lg px-6 py-3>85% accuracy sounds strong, but a model that never predicts churn is useless for retention — this is why accuracy alone is the wrong metric here.</div>

<!--
A baseline is the score you would get from a trivial or near-trivial predictor, and it exists to give every later number context. scikit-learn's DummyClassifier with strategy="most_frequent" always predicts the majority class — here, "not churned" — and because only 16% of customers actually churn, that trivial rule already scores 85% accuracy without learning anything about the data. This is the class-imbalance trap that the Model Evaluation unit's Common Pitfalls lecture names directly: whenever one class dominates, accuracy stops being a meaningful metric, because a model can look impressive while being operationally useless — it would never flag a single at-risk customer.

The fix is not to abandon baselines, but to also fit a simple, honest model — logistic regression is the natural second baseline, connecting back to Supervised Learning - Classification. It is fast to train, its coefficients are directly interpretable (a positive coefficient on support_tickets means more tickets is associated with higher churn odds), and if a complex ensemble cannot beat it by a meaningful margin on the right metric, the added complexity is not earning its keep — a direct application of the bias-variance reasoning from Core ML Concepts: more flexible models reduce bias but raise variance, and that trade only pays off when the reduction in error is real, not noise. We will pick the "right metric" — not accuracy — on the Stage 4 slides ahead. First, we need a menu of candidate models to compare.
-->

---
glowSeed: 1120
---

# Stage 3b — Choosing Candidate Models

<div class="grid grid-cols-2 gap-4 mt-5">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div bg="teal-800/40" px-4 py-2 font-bold>Linear / probabilistic</div>
<div px-4 py-3 text-sm leading-relaxed>
<strong>Logistic Regression</strong> — interpretable coefficients, strong baseline.<br/>
<strong>Naive Bayes</strong> — fast, works well with limited data, assumes feature independence.
</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>
<div bg="blue-800/40" px-4 py-2 font-bold>Instance / margin based</div>
<div px-4 py-3 text-sm leading-relaxed>
<strong>k-Nearest Neighbors</strong> — simple, sensitive to scale and irrelevant features.<br/>
<strong>SVM (kernel trick)</strong> — strong on smaller, well-scaled feature sets.
</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div bg="amber-800/40" px-4 py-2 font-bold>Trees</div>
<div px-4 py-3 text-sm leading-relaxed>
<strong>Decision Tree</strong> — interpretable splits, prone to overfitting alone.
</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div bg="violet-800/40" px-4 py-2 font-bold>Ensembles</div>
<div px-4 py-3 text-sm leading-relaxed>
<strong>Random Forest</strong> (bagging) — averages many trees, reduces variance.<br/>
<strong>Gradient Boosting</strong> — sequentially corrects errors, often the strongest tabular performer.
</div>
</div>
</div>

<!--
The capstone is where the Supervised Learning and Ensemble Methods units become a decision, not just a catalog. For our churn problem — mixed numeric and categorical tabular features, a moderate number of rows, a need to eventually explain predictions to a retention team — several families are reasonable starting candidates rather than one obviously correct answer. Logistic Regression and Naive Bayes are cheap, interpretable, and give a sense of how linearly separable the classes are; Naive Bayes's independence assumption between features is rarely exactly true but it degrades gracefully and trains almost instantly, making it a useful sanity check.

k-Nearest Neighbors and Support Vector Machines both depend on distances between data points, so they need the scaling step from Stage 2b to behave well, and both can struggle when many features are uninformative, since irrelevant dimensions distort distance calculations. A single Decision Tree is easy to explain to a non-technical audience but, as the Core ML Concepts unit on Overfitting and Regularization showed, an unconstrained tree memorizes training noise. That is exactly the weakness the Ensemble Methods unit addresses: Random Forests average many decorrelated trees (bagging) to cut variance without raising bias much, and Gradient Boosting builds trees sequentially, each one correcting the previous ensemble's errors, which frequently gives the best raw performance on structured tabular data of the type we have here — the "Why Ensembles Work" lecture explains the variance-reduction argument behind both. The right move is not to guess which wins, but to compare several fairly, which is the next slide.
-->

---
glowSeed: 1121
---

# Compare Models With Cross-Validation

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Same folds</div>
<div class="text-sm leading-relaxed opacity-90">Every candidate sees the identical stratified folds — a fair, paired comparison.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Right metric</div>
<div class="text-sm leading-relaxed opacity-90">Score on F1, not accuracy, because churn is imbalanced.</div>
</div>
</div>

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
models = {
    "baseline": DummyClassifier(strategy="most_frequent"),
    "logistic": LogisticRegression(max_iter=1000),
    "forest": RandomForestClassifier(random_state=42),
    "boosting": GradientBoostingClassifier(random_state=42),
}
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1")
    print(f"{name}: {scores.mean():.2f} +/- {scores.std():.2f}")
# baseline: 0.00   logistic: 0.51 +/- 0.04
# forest:   0.58 +/- 0.03   boosting: 0.62 +/- 0.03
```

<!--
Cross-validation, introduced in Core ML Concepts, splits the training data into k folds (here, five, via StratifiedKFold so each fold keeps the 16% churn rate) and repeatedly trains on k-1 folds while validating on the remaining one, cycling through all k. This produces k performance estimates per model rather than a single number, which is what lets us judge not just the average score but how much it varies — a model with mean F1 0.60 and std 0.01 is more trustworthy than one with mean 0.60 and std 0.10, even though their averages tie.

We score on F1 — the harmonic mean of precision and recall — instead of accuracy, precisely because of the imbalance problem raised in Stage 3: the DummyClassifier baseline scores F1 = 0.00 despite its 85% accuracy, because it never predicts the positive (churn) class at all, so both its precision and recall on that class are undefined-to-zero. That contrast alone justifies the metric choice. Reading the printed results, boosting (0.62) and the forest (0.58) both clearly beat logistic regression (0.51) and, more importantly, both beat the useless baseline by a wide margin. Whether boosting's edge over the forest is a real difference or noise from the ±0.03 standard deviations is a question we defer to a dedicated Stage 4 slide on statistical significance — do not eyeball two overlapping means and declare a winner. Next, before we lock in a model family, we improve it with hyperparameter tuning.
-->

---
glowSeed: 1122
---

# Tune Hyperparameters, Broad to Narrow

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">1. Random search</div>
<div class="text-sm leading-relaxed opacity-90">Sample widely across a broad range to find promising regions cheaply.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">2. Grid search</div>
<div class="text-sm leading-relaxed opacity-90">Exhaustively search a narrowed grid around the best region found.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">3. Validate, don't peek</div>
<div class="text-sm leading-relaxed opacity-90">Select on cross-validation score only; the test set stays untouched.</div>
</div>
</div>

```python
from sklearn.model_selection import RandomizedSearchCV

param_dist = {
    "n_estimators": [100, 200, 400],
    "max_depth": [2, 3, 4, 5],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
}
search = RandomizedSearchCV(
    GradientBoostingClassifier(random_state=42),
    param_dist, n_iter=20, scoring="f1", cv=cv, random_state=42,
)
search.fit(X_train, y_train)
print(search.best_params_, search.best_score_)
```

<!--
Hyperparameters are the settings you choose before training rather than the parameters the model learns from data — for Gradient Boosting, that includes how many trees to build (n_estimators), how deep each tree can grow (max_depth), and how much each tree corrects the previous ensemble (learning_rate). The Optimization in Practice unit's Hyperparameter Tuning Strategies lecture recommends a broad-to-narrow search: start with RandomizedSearchCV sampling widely across a large space, because with several hyperparameters an exhaustive grid grows combinatorially and wastes budget on clearly bad regions. Once random search identifies a promising neighborhood, a smaller GridSearchCV around those values refines the choice more precisely.

Every candidate configuration in this search is still scored with the same cross-validation procedure from the previous slide — cv=cv reuses the identical stratified folds — so tuning is just cross-validated model comparison over a much larger set of "models" (one per hyperparameter combination). The critical discipline, repeated for emphasis because it is the second most common capstone mistake after target leakage: hyperparameter selection uses only cross-validation scores on the training data, never the test set. If you tune until the test score looks good, you have turned the test set into a second validation set and lost your only unbiased estimate of real-world performance. The learning_rate parameter here also connects back to Optimization in Practice's Gradient Descent Variants lecture — boosting's learning rate plays the same overfitting-versus-convergence-speed role as a step size does in gradient descent. With a tuned model in hand, we now need to evaluate it properly.
-->

---
glowSeed: 1123
---

# Stage 4 — Rigorous Evaluation: Choosing Metrics

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Accuracy</span>
<span class="text-sm opacity-85"> — Misleading here: 85% by always predicting "no churn."</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Precision</span>
<span class="text-sm opacity-85"> — Of customers flagged as churners, what fraction really churn? Costs a wasted retention offer.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Recall</span>
<span class="text-sm opacity-85"> — Of true churners, what fraction did we catch? Missing one costs the whole customer.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">F1 / ROC-AUC</span>
<span class="text-sm opacity-85"> — Balance the two, or summarize ranking quality across all thresholds.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-8 text-sm leading-relaxed" border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
Missing a churner (false negative) loses a customer worth ~$600/yr. A wasted retention offer (false positive) costs ~$20. This 30:1 asymmetry means we should favor <strong>recall</strong> even at some cost to precision.
</div>
</div>
</div>

<!--
Choosing the right metric, from Model Evaluation's Accuracy, Precision, Recall, F1, ROC-AUC lecture, always starts with the real-world cost of each error type, not a default scikit-learn setting. Precision answers "when the model says churn, how often is it right?" — low precision means retention offers are wasted on customers who were never leaving. Recall answers "of everyone who actually churns, how many did the model catch?" — low recall means the business loses customers it never even tried to save. These trade off against each other as you move the classification threshold: lowering the threshold for predicting "churn" catches more true churners (raises recall) but also flags more false alarms (lowers precision).

For our subscriber case, a missed churner costs roughly a year of subscription revenue (~$600) while a wasted retention offer costs a small discount or promotional credit (~$20) — a roughly 30:1 cost asymmetry that argues for prioritizing recall, even accepting a meaningfully lower precision, because the business loses far more from false negatives than false positives. F1, the harmonic mean of precision and recall, is a reasonable single-number summary when you want a balanced tradeoff rather than an explicit cost model; ROC-AUC measures how well the model ranks positive cases above negative ones across every possible threshold, which is useful for comparing models independent of any one threshold choice, but it can look optimistic under heavy class imbalance since it weights both classes symmetrically. The next slide grounds these definitions in one concrete confusion matrix from our tuned model.
-->

---
glowSeed: 1124
---

# Stage 4b — Reading the Confusion Matrix

<div class="grid grid-cols-2 gap-8 items-center mt-4">
<div>
<div role="img" aria-label="Confusion matrix for the tuned gradient boosting churn model on 1000 test customers: 96 true positives, 54 false positives, 64 false negatives, 786 true negatives" class="max-w-md mx-auto">
<div class="grid grid-cols-[7rem_1fr_1fr] gap-2 text-center text-sm">
<div></div><div class="font-bold text-blue-300">Predicted<br/>churn</div><div class="font-bold text-blue-300">Predicted<br/>retain</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual churn</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 class="text-xl font-bold">TP<br/>96</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4 class="text-xl font-bold">FN<br/>64</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual retain</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4 class="text-xl font-bold">FP<br/>54</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 class="text-xl font-bold">TN<br/>786</div>
</div>
</div>
</div>
<div>
<div v-click class="text-sm leading-relaxed" border="2 solid white/5" bg="white/5" rounded-lg p-4>
On 1,000 test customers (160 true churners):<br/><br/>
Precision = 96 / (96+54) = <strong>0.64</strong><br/>
Recall = 96 / (96+64) = <strong>0.60</strong><br/>
F1 = <strong>0.62</strong><br/>
Accuracy = (96+786)/1000 = <strong>88.2%</strong>
</div>
</div>
</div>

<!--
The confusion matrix, from Model Evaluation's dedicated Confusion Matrices lecture, is the four-number breakdown every classification metric is computed from. Reading it: true positives (TP = 96) are churners the model correctly flagged; false negatives (FN = 64) are churners the model missed entirely — the costly error from the previous slide's asymmetry; false positives (FP = 54) are loyal customers incorrectly flagged as at-risk — the cheaper error; true negatives (TN = 786) are loyal customers correctly left alone. Every metric is a different ratio over these same four counts.

Working through the numbers on the right: precision of 0.64 means that when this model flags a customer as a churn risk, it is right about two-thirds of the time — the retention team will waste an offer on the remaining third. Recall of 0.60 means the model catches 60% of the 160 customers who actually churn in the test set, leaving 64 churners undetected. The F1 score of 0.62 balances these two. Notice the accuracy of 88.2% looks only marginally better than the 85% dummy baseline from Stage 3, yet the two models behave completely differently in practice: the dummy model catches zero churners, while this model catches 96 of 160 — accuracy alone would never reveal that gap, which is exactly why we scored on F1 during model comparison instead. Whether this tuned model's F1 advantage over the untuned random forest is statistically real is the next question.
-->

---
glowSeed: 1125
---

# Stage 4c — Is the Difference Real?

<div class="mt-4">

```python
from scipy import stats

forest_folds = [0.55, 0.60, 0.57, 0.61, 0.59]     # per-fold F1
boosting_folds = [0.63, 0.60, 0.64, 0.60, 0.63]   # per-fold F1

t_stat, p_value = stats.ttest_rel(boosting_folds, forest_folds)
print(f"mean diff: {sum(boosting_folds)/5 - sum(forest_folds)/5:.3f}")
print(f"paired t-test p-value: {p_value:.3f}")
# mean diff: 0.028   p-value: 0.041
```

</div>

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Paired test</div>
<div class="text-sm leading-relaxed opacity-90">Compare the <em>same</em> folds across models to cancel out fold-to-fold difficulty.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Small samples, small effects</div>
<div class="text-sm leading-relaxed opacity-90">With only 5 folds, a 0.028 F1 gap is real here (p = 0.041) but easily could not have been.</div>
</div>
</div>

<!--
Stage 3's cross-validation gave boosting a higher mean F1 than the random forest, but means alone cannot tell you whether that gap reflects a genuine, reproducible difference or random fold-to-fold noise — the question the Model Evaluation unit's Statistical Significance in Model Comparison lecture is built around. A paired t-test is the right tool here because both models were evaluated on the exact same five folds: pairing cancels out the fact that some folds are simply harder than others (perhaps one fold happened to contain more ambiguous customers), isolating the model-to-model difference rather than confounding it with fold difficulty.

The result above, p = 0.041, is below the conventional 0.05 threshold, so we would conclude the boosting model's edge is unlikely to be pure chance — but notice how close that is to the boundary, and how few folds (five) generated it. This is a genuine caution, not a formality: with a small number of folds, both a real effect and a lucky draw can produce a similarly small p-value, and a slightly different random seed for the folds could easily flip the conclusion. The practical lesson for your own capstone is to report the comparison honestly — the estimated difference, its uncertainty, and the significance test — rather than silently picking whichever model scored numerically highest on a single run and presenting that as fact. Next, before finalizing this model, we run the broader robustness checks the Common Pitfalls lecture recommends.
-->

---
glowSeed: 1126
---

# Stage 4d — Robustness Checks

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Imbalance</div>
<div class="text-sm leading-relaxed opacity-90">Re-check that stratified splits and F1-based scoring held throughout tuning, not just at the first comparison.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Leakage</div>
<div class="text-sm leading-relaxed opacity-90">Re-audit the final feature list — did an engineered feature accidentally use post-outcome data?</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Distribution shift</div>
<div class="text-sm leading-relaxed opacity-90">Compare training-period and test-period feature distributions; a big shift means the model may be stale in production.</div>
</div>
</div>

<div v-click class="mt-8 text-sm text-center" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-3>Touch the test set once, only after every one of these checks passes on validation data.</div>

<!--
Before spending your one allowed look at the test set, re-run the checklist from Model Evaluation's Common Pitfalls - Data Leakage and Class Imbalance lecture as a final gate, because tuning is exactly when small mistakes creep back in. Re-confirm imbalance handling: it is easy to have started with StratifiedKFold and F1 scoring in Stage 3, then quietly switched to plain accuracy or an unstratified split somewhere inside a later grid search without noticing — always re-print the fold sizes and scoring metric right before the final run.

Re-audit leakage on the final feature set specifically, not just the raw columns from Stage 1c: an engineered feature built in Stage 2b can reintroduce leakage even after the obviously bad column was dropped — for example, a feature computed from a customer's total historical support tickets that was, by an indexing bug, summed over the full dataset including future months rather than only up to the prediction date. Distribution shift means the statistical properties of the input features have changed between the period the training data was collected and the period you are evaluating (or eventually deploying) on; a large shift — say, monthly_charges trending sharply upward due to a pricing change — means a model trained on older data may already be stale, no matter how well it scored on a same-period test set. Only once all three checks pass on validation data do you touch the test set — a single, final, unrepeated evaluation, because reusing it to fix problems turns it into another validation set and destroys its unbiased guarantee.
-->

---
glowSeed: 1127
---

# Stage 5 — Interpret and Write Honestly

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Explain</div>
<div class="text-sm leading-relaxed opacity-90">Feature importance or SHAP values should agree with domain sense — tenure and support tickets should matter, a customer ID should not.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Limitations</div>
<div class="text-sm leading-relaxed opacity-90">Name populations, conditions, and inputs the model does not cover — e.g., customers who joined in the last month.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Consequences</div>
<div class="text-sm leading-relaxed opacity-90">Discuss the cost of false positives and negatives, monitoring plans, and an appeal path for flagged customers.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Narrative</div>
<div class="text-sm leading-relaxed opacity-90">Problem → evidence → choices → results → limitations, in that order.</div>
</div>
</div>

<!--
A model's coefficients or built-in feature_importances_ tell you which features it leaned on most, but this needs a sanity check, not blind trust: if support_tickets and tenure_months rank high, that agrees with intuition about churn drivers; if an arbitrary customer_id or row index ranks high, something is wrong — likely a subtle leakage or overfitting problem missed in earlier stages, connecting back to Overfitting and Regularization. SHAP (SHapley Additive exPlanations) values go further, attributing each individual prediction to a signed contribution per feature, which is useful when a retention team wants to know why a specific customer was flagged, not just which features matter on average across the dataset.

Limitations are not an admission of failure, they are part of a credible result: state plainly which customers the model was not trained or validated on — for instance, if the training data is drawn from established customers, the model's predictions for brand-new sign-ups are extrapolation and should be flagged as lower-confidence. Consequences means connecting the confusion matrix numbers from Stage 4b back to real costs: with 64 missed churners and 54 wasted offers, what retention capacity does the business actually have, and does the chosen threshold match it? A strong project report follows one consistent narrative arc — state the problem, present the evidence (EDA, baseline, comparison, tuning, final evaluation), explain the choices made at each stage and why, report results plainly including the confidence and significance caveats from Stage 4c, and close with limitations. A leaderboard score alone tells a reader nothing about whether to trust the model.
-->

---
glowSeed: 1128
---

# Stage 5b — Fairness and Broader Consequences

<div class="grid grid-cols-2 gap-8 items-start mt-4">
<div>
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Check subgroups</span>
<span class="text-sm opacity-85"> — Does recall differ sharply across customer segments (region, plan tier, tenure band)?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Consider the decision, not just the score</span>
<span class="text-sm opacity-85"> — A flagged customer receives an offer, not a denial — lower-stakes than credit or hiring, but not zero-stakes.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Plan for drift</span>
<span class="text-sm opacity-85"> — Commit to monitoring performance after deployment, not a one-time evaluation.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
⚠️ <strong>Common student mistake</strong><br/>
<span class="text-sm">Reporting one overall F1 and stopping. A model can look fair in aggregate while systematically under-serving one subgroup.</span>
</div>
</div>
</div>

<!--
The Broader Context unit's Fairness, Bias, and Interpretability lecture applies directly at this stage: an aggregate F1 of 0.62 can hide very different behavior across subgroups. Compute precision and recall separately for each customer segment you have available — region, plan tier, tenure band — because a model with strong recall for long-tenure customers but weak recall for new customers is not equally useful to every part of the business, and if any segment correlates with a protected characteristic, that unevenness becomes a fairness concern, not just a modeling detail. This check costs a few extra lines of pandas groupby code and catches a failure mode a single aggregate metric cannot reveal.

Also weigh what actually happens to a customer flagged by the model: here, it triggers a retention offer, which is low-stakes compared to the credit, hiring, or criminal-justice examples the Ethical Considerations and Failure Modes lecture discusses, but "low-stakes" is not "no-stakes" — a customer who is never offered a retention deal because the model missed them is a real, if modest, harm, and one worth naming explicitly in your write-up rather than glossing over. Finally, commit to monitoring: any model deployed against real customers will encounter distribution shift as pricing, competitors, or customer behavior change over time, so a one-time evaluation is not a permanent guarantee — say explicitly, in your report, how and how often the model's performance should be re-checked. The single most common mistake at this stage is reporting one clean overall number and calling the fairness question closed; do not make that mistake in your own capstone.
-->

---
glowSeed: 1129
---

# The Complete Pipeline

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-2 mt-4 text-sm">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-teal-300">EDA & cleaning</span>
<span class="opacity-85"> — Core ML Concepts, Model Evaluation pitfalls</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-blue-300">Split + features</span>
<span class="opacity-85"> — Train-Val-Test Splits & Cross-Validation</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">Model + tune</span>
<span class="opacity-85"> — Supervised Learning, Ensemble Methods, Optimization in Practice</span>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2>
<span class="font-bold text-violet-300">Evaluate + explain</span>
<span class="opacity-85"> — Model Evaluation, Broader Context</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="EDA then Split + features then Model + tune then Evaluate + explain">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">EDA</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Split + features</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Model + tune</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Evaluate + explain</div>
</div>
</div>

</div>
</div>

<!--
Walk the churn project once more, end to end, and notice how directly each stage maps onto a specific earlier lecture rather than a vague "use what you learned" instruction. EDA and cleaning drew on Core ML Concepts' emphasis on understanding data before modeling and on Model Evaluation's pitfalls lecture for the leakage check that caught cancellation_request_date. The split-and-feature stage was governed entirely by the Train-Validation-Test Splits and Cross-Validation lecture's fit-on-train-only rule, with stratification handling the class imbalance discovered during EDA.

Model and tuning drew on three units at once: Supervised Learning gave the candidate model families (logistic regression, trees, SVMs), Ensemble Methods explained why random forests and gradient boosting outperformed a single tree, and Optimization in Practice supplied the broad-to-narrow hyperparameter search strategy and the statistical-significance test that kept us from overclaiming boosting's edge. Evaluation and explanation drew on Model Evaluation for the metric choice (F1 over accuracy, given the cost asymmetry) and the confusion-matrix breakdown, and on Broader Context for the subgroup fairness check and the honest limitations section. The capstone is intentionally less prescribed than any single homework assignment — no problem set tells you which stage needs more attention on your own dataset — so the judgment to notice where your project's risks concentrate, and to spend your effort there, is itself the skill this course has been building toward.
-->

---
glowSeed: 1130
---

# Common Mistakes at Each Stage

<div class="grid grid-cols-2 gap-3 mt-4 text-sm">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-xl">🧹</div>
<div><strong>Cleaning:</strong> silently dropping rows without logging why, or deleting real (if rare) high-value cases as "outliers."</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-xl">🚧</div>
<div><strong>Splitting:</strong> fitting a scaler or imputer before splitting, letting test-set statistics leak into training.</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-xl">📊</div>
<div><strong>Metrics:</strong> reporting accuracy on an imbalanced target without checking what a trivial baseline scores.</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-xl">🎯</div>
<div><strong>Tuning:</strong> selecting hyperparameters by peeking at test performance instead of cross-validation.</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-xl">🔁</div>
<div><strong>Comparison:</strong> declaring a winner from two overlapping mean scores without a significance check.</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-xl">📝</div>
<div><strong>Write-up:</strong> presenting a single leaderboard number with no discussion of limitations or subgroup behavior.</div>
</div>
</div>

<!--
This slide is a deliberately compressed checklist of the specific traps this deck walked through with the churn example — worth returning to while you build your own project, since these mistakes recur across nearly every capstone submission regardless of dataset or domain. Cleaning mistakes and split-order mistakes are the two most damaging because they are silent: a leaked feature or a scaler fit on the full dataset does not throw an error, it just inflates every metric you compute afterward in a way that looks like good news until the model fails outside the notebook.

The metrics and tuning mistakes are the two most common because scikit-learn's defaults make them easy to fall into by accident — .score() defaults to accuracy, and it takes one extra keyword argument (scoring="f1", or the estimator's own default) to change that, so an unexamined default is a choice, whether or not you meant to make it. The comparison mistake — eyeballing two means and picking the higher one — is subtle because it produces a plausible-sounding sentence ("boosting outperformed the forest") that is not actually supported by the evidence unless you ran the paired significance test from Stage 4c. And the write-up mistake undoes all the careful work in the earlier stages: a single number without context, limitations, or subgroup analysis asks the reader to trust you rather than showing them why the result is trustworthy. Use this list as a pre-submission checklist, not just lecture content.
-->

---
glowSeed: 1131
---

# Final Course Takeaways

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Foundations</div>
<div class="text-sm leading-relaxed opacity-90">Linear algebra, probability, and calculus are not abstractions — they are the mechanics behind every model you fit.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Method</div>
<div class="text-sm leading-relaxed opacity-90">Split before you touch the data, validate honestly, and check whether a difference is real before you report it.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Responsibility</div>
<div class="text-sm leading-relaxed opacity-90">Consider who is affected by an error, and say plainly what your model does not know.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Build one complete, clear, reproducible project—and tell the truth about what it can and cannot do.</div>

<!--
Three takeaways to close the semester, each traceable to a specific unit rather than a generic platitude. Foundations: every gradient step in logistic regression or boosting is literally the calculus from Mathematical Foundations; every loss function is the probability and empirical-risk-minimization framing from Core ML Concepts' Loss Functions lecture; the math was never separate from the applied work, it was always underneath it, and understanding it is what lets you debug a model that behaves strangely instead of only being able to call .fit() on it.

Method: the discipline demonstrated across this entire churn walkthrough — split before touching the data, fit every learned transformation on training folds only, choose a metric that matches the real cost of errors, and check statistical significance before declaring a winner — is more durable than any single algorithm, because algorithms and libraries will keep changing over your career while this discipline will not. Responsibility: a model's job is not finished when its F1 score is computed; Stage 5b's fairness check and limitations section are not optional extras, they are part of what makes a result trustworthy enough to act on. As you start your own capstone, use this deck's churn walkthrough as a template — substitute your own dataset and target, but keep every stage, in order, and be honest in the write-up about what worked, what did not, and what you are still unsure of.
-->
