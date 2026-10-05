---
theme: default
highlighter: shiki
colorSchema: dark
title: 'Evaluating Classifiers: Errors, Metrics, and Thresholds'
info: 'A combined lesson on confusion matrices, classification metrics, and application-specific decisions.'
transition: fade-out
lineNumbers: false
drawings:
  persist: false
mdc: true
canvasWidth: 980
aspectRatio: 16/9
class: cover
glowSeed: 610
glowOpacity: 0.25
---

# Evaluating Classifiers

<div v-click="1">

## Errors, metrics, and thresholds

</div>

<p v-click="2" style="margin-top:50px;font-size:26px">Which mistakes matter for this application?</p>

<p v-click="2" class="caption">Foundations of Machine Learning · Model Evaluation</p>

<!--
This lesson joins the binary confusion matrix and metrics into one continuous story. Prior knowledge: train/validation/test splits and a classifier that outputs scores. Core slides 1–40 include the multiclass extension; allow additional time for its worked example and discussion. Slides 41–46 are optional extensions and references. All transaction counts, scores, costs, and application constraints are invented teaching examples, not empirical findings or policy recommendations. The 1,000-case example deliberately uses 10% fraud for readable arithmetic; real deployment prevalence can differ substantially. Sources: https://scikit-learn.org/stable/modules/model_evaluation.html and https://scikit-learn.org/stable/modules/classification_threshold.html .
-->

---
glowSeed: 611
---

# A fraud detector with 99% accuracy

<div v-click="1">

A payment service sees **9,900 legitimate transactions** and **100 fraudulent transactions**.

</div>

<div v-click="2">

Its new detector lets every transaction through.

</div>

<div v-click="3" class="big">99% accuracy</div>

<div v-click="4" class="question">Would you deploy it?</div>

<!--
Pause before calling the classifier useless. Ask what the system exists to accomplish. Predicting legitimate every time gets 9,900 of 10,000 decisions right but catches no fraud. This is an intentionally separate opening scenario, not the 1,000-case cohort introduced next. Accuracy alone does not reveal performance on fraud. A trivial majority-class baseline is essential, and different applications may legitimately value different errors.
-->

---
glowSeed: 612
---

# The action behind a positive prediction

<div v-click="1">

For our payment example:

</div>

<div class="concept-stack">

<div v-click="2" class="concept-box teal"><div class="concept-label">Positive class</div><div>Fraud.</div></div>

<div v-click="3" class="concept-box blue"><div class="concept-label">Positive prediction</div><div>Flag the transaction for review.</div></div>

<div v-click="4" class="concept-box amber"><div class="concept-label">Negative prediction</div><div>Allow it without review.</div></div>

</div>

<div v-click="5" class="question">Is flagging for review the same decision as blocking a payment?</div>

<!--
No. Reviewing, requesting verification, delaying, and declining have different costs and consequences. Keep the chosen action explicit when discussing FP and FN. Positive does not mean good; it means the class of interest. Later we change the action and see the preferred threshold change. Ground truth is whether the transaction truly was fraudulent, independent of our decision.
-->

---
glowSeed: 613
---

# One cohort for the worked example

<div class="columns">

<div>

<div v-click="1">

## 1,000 transactions

100 fraudulent<br>900 legitimate

</div>

<div v-click="2">

## At the current threshold

170 transactions get flagged.<br>80 of those really are fraud.

</div>

</div>

<div>

<div v-click="3">

## What happened to the rest?

20 fraud cases slipped through.<br>810 legitimate payments passed.

</div>

<p v-click="3" class="caption">Illustrative validation data, not a real fraud dataset.</p>

</div>

</div>

<!--
This is the main running cohort. Use validation rather than test data because we will explore thresholds. The model and score distribution stay fixed throughout the threshold examples. Give students time to reconstruct the remaining 90 flagged legitimate transactions from 170 total alerts minus 80 real fraud cases. No metrics yet.
-->

---
glowSeed: 614
---

# Four possible outcomes

<table>
<thead><tr v-click="1"><th style="text-align:left">Outcome</th><th style="text-align:left">Payment example</th><th style="text-align:right">Count</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">True positive, TP</td><td style="text-align:left">Fraud correctly flagged</td><td style="text-align:right">80</td></tr>
<tr v-click="2"><td style="text-align:left">False positive, FP</td><td style="text-align:left">Legitimate payment flagged</td><td style="text-align:right">90</td></tr>
<tr v-click="3"><td style="text-align:left">False negative, FN</td><td style="text-align:left">Fraud allowed through</td><td style="text-align:right">20</td></tr>
<tr v-click="4"><td style="text-align:left">True negative, TN</td><td style="text-align:left">Legitimate payment allowed through</td><td style="text-align:right">810</td></tr>
</tbody>
</table>

<div v-click="5" class="question">Which errors cost the payment service money? Which affect its customers?</div>

<!--
Both error types can cost money and affect customers. FP may cause friction, review workload, or an abandoned purchase. FN may cause a loss or harm a cardholder. Avoid assigning universal costs yet. Have students state each outcome in plain language before moving to abbreviations. Do not conflate the classification error terms with formal hypothesis-test Type I/II errors in this introductory lesson.
-->

---
glowSeed: 615
---

# The confusion matrix

<ConfusionTable v-click="1" />

<div v-click="2">

**Rows = actual class. Columns = predicted class.**

</div>

<div v-click="3">

Row totals: 900 legitimate and 100 fraud.<br>Column totals: 830 allowed and 170 flagged.

</div>

<!--
Read axes before reading cells. This course follows scikit-learn: actual rows, predicted columns, with labels [0,1] where 1 is fraud. Other resources may reverse orientation. The two correct cells lie on the diagonal, and the off-diagonal separates the directions of error. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html .
-->

---
glowSeed: 650
---

# Classification terminology

<div class="columns" style="gap:20px;margin-bottom:18px">
<div v-click="1" class="concept-box teal"><div class="concept-label">Positive / negative</div><div>In these terms, this names the predicted class.</div></div>
<div v-click="2" class="concept-box blue"><div class="concept-label">True / false</div><div>This tells us whether the prediction agrees with the ground truth.</div></div>
</div>

<table>
<thead><tr v-click="3"><th>Term</th><th>Prediction</th><th>Ground truth</th></tr></thead>
<tbody>
<tr v-click="3"><td>True Positive (TP)</td><td>Positive</td><td>Positive</td></tr>
<tr v-click="4"><td>False Positive (FP)</td><td>Positive</td><td>Negative</td></tr>
<tr v-click="5"><td>True Negative (TN)</td><td>Negative</td><td>Negative</td></tr>
<tr v-click="6"><td>False Negative (FN)</td><td>Negative</td><td>Positive</td></tr>
</tbody>
</table>

<!--
Read each term as two pieces. Positive or negative names the model's prediction. True means that prediction agrees with the actual label; false means it disagrees. Ground truth means the actual class. In our fraud example, positive means fraud and negative means legitimate. Thus a false positive is a legitimate payment predicted to be fraud, while a false negative is a fraudulent payment predicted to be legitimate. The word positive also labels the actual class in the ground-truth column; the naming rule here specifically concerns the compound terms TP, FP, TN, and FN. Reveal the two explanations first, then the table rows in the order TP, FP, TN, FN.
Source: https://scikit-learn.org/stable/modules/model_evaluation.html#confusion-matrix .
-->

---
glowSeed: 616
---

# Accuracy: how often were we correct?

<div class="columns">

<ConfusionTable v-click="1" focus="accuracy"/>

<div>

<div v-click="2">

$$\mathrm{Accuracy}=\frac{TP+TN}{N}$$

</div>

<div v-click="3">

$$\frac{80+810}{1000}=0.89$$

</div>

<div v-click="4">

**89% accuracy**

</div>

<div v-click="5" class="question">Without any additional information, do we know if this is the best possible classifier?</div>

</div>

</div>

<!--
The final question asks whether 89% accuracy is enough to establish that this is the best possible classifier. It is not: we need information about alternative models, a baseline, the kinds of mistakes, and the costs and constraints of the application. Let students name the missing information before moving to precision and recall. Accuracy has a clear meaning: fraction correct. It remains valid on imbalanced data, but can obscure important minority-class behavior. Source: https://scikit-learn.org/stable/modules/model_evaluation.html#accuracy-score .
-->

---
glowSeed: 617
---

# Precision: how trustworthy are the alerts?

<div class="columns">

<ConfusionTable v-click="1" focus="precision"/>

<div>

<div v-click="2">

$$\mathrm{Precision}=\frac{TP}{TP+FP}$$

</div>

<div v-click="3">

$$\frac{80}{80+90}=0.471$$

</div>

<div v-click="4">

**47.1% of flagged payments really are fraud.**

</div>

<div v-click="5">

The denominator is the 170 alerts.

</div>

</div>

</div>

<div v-click="6" class="concept-box teal" style="margin-top:24px">You can trust the fraud alerts <strong>47.1% of the time</strong>.</div>

<!--
The predicted-positive column is highlighted. Precision conditions on what the model predicted. Ask a student to point to the group we are dividing by before revealing the formula. Of the 170 flagged payments, 80 are genuine fraud, so 90 are false alarms. Precision describes alert quality and can matter greatly for review workload or intrusive actions. Source: https://scikit-learn.org/stable/modules/model_evaluation.html#precision-recall-f-measure-metrics .
-->

---
glowSeed: 618
---

# Recall: how much fraud did we catch?

<div class="columns">

<ConfusionTable v-click="1" focus="recall"/>

<div>

<div v-click="2">

$$\mathrm{Recall}=\frac{TP}{TP+FN}$$

</div>

<div v-click="3">

$$\frac{80}{80+20}=0.80$$

</div>

<div v-click="4">

**We caught 80% of the fraud.**

</div>

<div v-click="5">

The denominator is the 100 real fraud cases.

</div>

</div>

</div>

<div v-click="6" class="concept-box teal" style="margin-top:24px"><strong>20% of fraud</strong> goes undetected.</div>

<!--
The actual-positive row is highlighted. Recall conditions on what truly happened, not on what the model predicted. Contrast the same TP numerator with the two different groups in the denominator. Recall is also called sensitivity or true-positive rate. Source: https://scikit-learn.org/stable/modules/model_evaluation.html#precision-recall-f-measure-metrics .
-->

---
glowSeed: 619
---

# Precision and recall in everyday language

<table>
<thead><tr v-click="1"><th style="text-align:left">Question</th><th style="text-align:left">Group we look at</th><th style="text-align:left">Metric</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">How many of our alerts were real?</td><td style="text-align:left">Predicted positives</td><td style="text-align:left">Precision</td></tr>
<tr v-click="2"><td style="text-align:left">How many real cases did we find?</td><td style="text-align:left">Actual positives</td><td style="text-align:left">Recall</td></tr>
</tbody>
</table>

<div v-click="3" class="concept-box teal" style="margin-top:18px;font-size:24px;font-weight:650">Recall is also called sensitivity.</div>

<!--
Contrast the two denominators: precision looks at predicted positives, while recall looks at actual positives. Ask students to explain each question in their own words. Both measures are useful, and quoting one alone can hide the other.
-->

---
glowSeed: 620
---

# Same accuracy, different mistakes

<div class="columns">

<div>

<div v-click="1">

## Model A

<ConfusionTable :tn="840" :fp="60" :fn="20" :tp="80" />

</div>

<div v-click="2">

Precision **57.1%** · Recall **80%**

</div>

</div>

<div>

<div v-click="3">

## Model B

<ConfusionTable :tn="870" :fp="30" :fn="50" :tp="50" />

</div>

<div v-click="4">

Precision **62.5%** · Recall **50%**

</div>

</div>

</div>

<div v-click="5">

Both have **92% accuracy** on the same class totals.

</div>

<!--
These are two candidate classifiers on a cohort with the same 900/100 class totals. They are not two thresholds of the main model. A catches more fraud but generates more false alarms. B has better precision and fewer false alarms, but misses half the fraud. Ask which they would prefer for a low-friction verification step versus an automatic decline. Do not claim one is always superior. This preserves the strongest comparison from the existing confusion matrix deck.
-->

---
glowSeed: 651
class: tradeoff
---

# False alerts or missed fraud?

<div class="columns">
<div>
<div v-click="1">

## Model A

<ConfusionTable :tn="890" :fp="10" :fn="40" :tp="60" />

</div>
<div v-click="2">

Precision **85.7%** · Recall **60%**

</div>
</div>
<div>
<div v-click="3">

## Model B

<ConfusionTable :tn="700" :fp="200" :fn="0" :tp="100" />

</div>
<div v-click="4">

Precision **33.3%** · Recall **100%**

</div>
</div>
</div>

<div v-click="5" class="question">Would you prefer more false fraud alerts with no missed fraud, or fewer false alerts with more fraud going undetected?</div>

<p v-click="5" class="caption">Illustrative predictions on the same 1,000 transactions: 100 fraud, 900 legitimate.</p>

<!--
Compare two illustrative predictors on identical transactions. Model A has higher precision but lower recall: TP=60, FP=10, FN=40, TN=890. Precision=60/70=85.7%; recall=60/100=60%. It raises 70 alerts, only 10 of them false, but misses 40 fraud cases. Model B has lower precision but higher recall: TP=100, FP=200, FN=0, TN=700. Precision=100/300=33.3%; recall=100/100=100%. It raises 300 alerts, 200 of them false, but misses none of the fraud in this dataset. The two predictors are separate candidates, not thresholds of the running model. Zero misses in these invented observations does not guarantee zero misses on future transactions.
Ask students to choose from a customer's perspective and then from a payment service's perspective. The preferred predictor depends on the action attached to an alert, the cost of customer friction, the loss from missed fraud, and review capacity. Avoid declaring one predictor universally better. Reveal Model A and its metrics, then Model B and its metrics, then the discussion question. The later threshold section develops the same decision tradeoff while holding a single model fixed.
-->

---
glowSeed: 621
---

# F1: a combined precision-recall summary

<div class="columns">

<div>

<div v-click="1">

$$F_1=\frac{2PR}{P+R}$$

</div>

<div v-click="2">

$$F_1=\frac{2TP}{2TP+FP+FN}$$

</div>

</div>

<div>

<div v-click="4">

The surface shows F1 for every precision–recall pair.

</div>

<div v-click="5">

When either value is low, F1 stays low.

</div>

<div v-click="6">

At precision = recall, F1 equals that shared value.

</div>

<F1Surface v-click="4" />

</div>

</div>

<!--
Introduce the harmonic mean only now that the inputs have meaning. The count form gives 160/(160+90+20)=160/270=0.5925926 for our original cohort. The 3D surface makes the harmonic-mean relationship visible: F1 is zero when either input is zero and reaches one at precision=recall=1. Along the diagonal P=R, F1=P. F1 is a summary, not a universal measure of usefulness. It omits TN and is tied to the chosen positive class. Source: https://scikit-learn.org/stable/modules/model_evaluation.html#precision-recall-f-measure-metrics .
-->

---
glowSeed: 622
---

# A high F1 does not settle the decision

<div v-click="1">

F1 combines precision and recall with equal emphasis.

</div>

<div v-click="2">

It leaves out:

</div>

<div class="concept-grid">

<div v-click="3" class="concept-box teal"><div class="concept-label">Missed fraud</div><div>The cost of each fraud case that slips through.</div></div>

<div v-click="4" class="concept-box blue"><div class="concept-label">Customer disruption</div><div>The cost of flagging a legitimate payment.</div></div>

<div v-click="5" class="concept-box amber"><div class="concept-label">Review capacity</div><div>How many alerts the team can handle.</div></div>

</div>

<div v-click="6" class="question">What objective would you choose if reviewers can handle only 100 alerts per day?</div>

<!--
The correct response should specify a constrained objective, such as maximize detected fraud subject to at most 100 alerts, instead of maximizing F1 without regard to workload. Equal emphasis in the harmonic mean does not imply equal monetary cost of FP and FN. If costs vary per transaction, a single aggregate count cost can be too crude; this is addressed later. Do not frame F1 as the inevitable solution to class imbalance.
-->

---
glowSeed: 623
---

# Scores become decisions through a threshold

<div v-click="1">

$$\widehat y=\begin{cases}1 & s\geq t\\0 & s<t\end{cases}$$

</div>

<div v-click="2" class="concept-box teal" style="margin-top:12px;padding:10px 16px">

Common default for probability scores: **t = 0.50**<br>Score ≥ t: flag positive · Score &lt; t: predict negative

</div>

<div v-click="3" class="columns" style="margin-top:24px">

<div class="concept-box teal"><div class="concept-label">Lower threshold</div><div>Catch more positives<br>More false positives</div></div>

<div class="concept-box amber"><div class="concept-label">Higher threshold</div><div>Fewer false positives<br>More missed positives</div></div>

</div>

<p v-click="3" class="caption">The score cutoff can be changed; the score itself stays the same. Scores need not be calibrated probabilities.</p>

<!--
The convention throughout this deck is score >= threshold, including ties. For probability-based binary classification, 0.5 is a common default; other estimators can use a different decision score and default. On a fixed dataset, lowering the threshold adds positive predictions, so true positives and false positives can only increase or stay the same; raising it reduces both or leaves them unchanged. A score can provide a useful ranking without accurately expressing a probability. Source: https://scikit-learn.org/stable/modules/classification_threshold.html .
-->

---
glowSeed: 624
---

# A small set of transactions

<table>
<thead><tr v-click="1"><th style="text-align:left">Transaction</th><th style="text-align:right">Score</th><th style="text-align:left">Actual class</th><th style="text-align:left">Flagged at t = 0.50?</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">A</td><td style="text-align:right">0.90</td><td style="text-align:left">Fraud</td><td style="text-align:left">Yes</td></tr>
<tr v-click="2"><td style="text-align:left">B</td><td style="text-align:right">0.80</td><td style="text-align:left">Legitimate</td><td style="text-align:left">Yes</td></tr>
<tr v-click="3"><td style="text-align:left">C</td><td style="text-align:right">0.60</td><td style="text-align:left">Fraud</td><td style="text-align:left">Yes</td></tr>
<tr v-click="4"><td style="text-align:left">D</td><td style="text-align:right">0.40</td><td style="text-align:left">Fraud</td><td style="text-align:left">No</td></tr>
<tr v-click="5"><td style="text-align:left">E</td><td style="text-align:right">0.20</td><td style="text-align:left">Legitimate</td><td style="text-align:left">No</td></tr>
<tr v-click="6"><td style="text-align:left">F</td><td style="text-align:right">0.10</td><td style="text-align:left">Legitimate</td><td style="text-align:left">No</td></tr>
</tbody>
</table>

<div v-click="7" class="question">What changes if the threshold moves to 0.40?</div>

<!--
A six-transaction teaching example makes thresholding visible before the larger demo. At 0.50 TP=2 FP=1 FN=1 TN=2, precision=2/3 and recall=2/3. At 0.40 TP=3 FP=1 FN=0 TN=2, precision=3/4 and recall=1. This deliberately shows a case where lowering the threshold improves both precision and recall, so students do not learn a false monotonic rule for precision. These scores are illustrative, not probabilities.
-->

---
glowSeed: 625
---

# What lowering the threshold guarantees

<div v-click="1">

On a fixed set of scores, lowering the threshold:

</div>

<ul style="margin-left:0;padding-left:0;list-style-position:inside">
<li v-click="2">Adds positive predictions, or leaves them unchanged.</li>
<li v-click="3">Increases or preserves both TP and FP.</li>
<li v-click="4">Increases or preserves recall and false-positive rate.</li>
</ul>

<div v-click="5" class="concept-box amber"><div class="concept-label">Precision can rise or fall</div><div>It depends on the newly flagged cases.</div></div>

<p v-click="5" class="caption">In the six-transaction example, adding one fraud case improved both precision and recall.</p>

<!--
Lowering a threshold creates nested predicted-positive sets, so TP and FP cannot decrease. Since actual positive/negative totals are fixed, recall and FPR cannot decrease either. Precision has a changing numerator and denominator and need not move monotonically. A broad precision-recall tradeoff is common, but a guaranteed inverse relationship is incorrect. Source: https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html .
-->

---
glowSeed: 626
---

# Threshold lab: the same fraud model

<ThresholdLab v-click="1" />

<!--
Return to the main 1,000-case cohort. Invite students to predict outcomes before moving the slider. The buttons jump to three thresholds used in later decision examples. The five score bins are [0.90:50 fraud/10 legitimate], [0.70:20/20], [0.50:10/60], [0.30:15/110], [0.10:5/700]. All counts come from this single fixed dataset. At threshold 1 no cases are flagged and precision is mathematically undefined; the lab displays that explicitly. At threshold 0 all cases are flagged. PDF readers see the default 0.50 snapshot.
-->

---
glowSeed: 628
---

# Threshold choice depends on the action

<table>
<thead><tr v-click="1"><th style="text-align:left">Application and action</th><th style="text-align:left">Consequence of a false positive</th><th style="text-align:left">Consequence of a false negative</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">Fraud: request verification</td><td style="text-align:left">Customer friction</td><td style="text-align:left">Fraud passes without review</td></tr>
<tr v-click="2"><td style="text-align:left">Spam: quarantine the email</td><td style="text-align:left">A real message is hidden</td><td style="text-align:left">Spam reaches the inbox</td></tr>
<tr v-click="3"><td style="text-align:left">Safety: send an item for inspection</td><td style="text-align:left">Extra inspection</td><td style="text-align:left">A hazardous item passes</td></tr>
</tbody>
</table>

<div v-click="4">

**The positive class and the response must be explicit.**

</div>

<!--
These are application scenarios, not recommended operational policies. In fraud, review may favor broader detection while a hard decline may justify stricter alert quality. Spam can be nuanced too: quarantining with easy recovery differs from permanently deleting email. Safety screening may place strong emphasis on catching hazards while still facing finite inspection capacity. Ask students to name the action before recommending a threshold. This applies the decision-problem distinction in https://scikit-learn.org/stable/modules/classification_threshold.html .
-->

---
glowSeed: 627
---

# Three operating points

<table>
<thead><tr v-click="1"><th style="text-align:left">Threshold</th><th style="text-align:right">TP</th><th style="text-align:right">FP</th><th style="text-align:right">FN</th><th style="text-align:right">Alerts</th><th style="text-align:right">Precision</th><th style="text-align:right">Recall</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">0.80</td><td style="text-align:right">50</td><td style="text-align:right">10</td><td style="text-align:right">50</td><td style="text-align:right">60</td><td style="text-align:right">83.3%</td><td style="text-align:right">50%</td></tr>
<tr v-click="2"><td style="text-align:left">0.50</td><td style="text-align:right">80</td><td style="text-align:right">90</td><td style="text-align:right">20</td><td style="text-align:right">170</td><td style="text-align:right">47.1%</td><td style="text-align:right">80%</td></tr>
<tr v-click="3"><td style="text-align:left">0.20</td><td style="text-align:right">95</td><td style="text-align:right">200</td><td style="text-align:right">5</td><td style="text-align:right">295</td><td style="text-align:right">32.2%</td><td style="text-align:right">95%</td></tr>
</tbody>
</table>

<div v-click="4">

Same model. Same cohort. Different decisions.

</div>

<div v-click="5" class="question">Which threshold would you choose? What information is missing?</div>

<!--
Pause here and resist declaring a winner. Needed information includes the action, costs, capacity, acceptable risk, and representativeness of validation data. TN values are 890,810,700 respectively. The five score bins mean a range of thresholds yields each operating point, so the displayed thresholds are representative cutoffs, not uniquely optimal numerical values. Compare only these three candidates in the next two exercises.
-->

---
glowSeed: 629
---

# The cost of missed fraud changes the choice

<div v-click="1">

Suppose a false alert costs **\$5** and a missed fraud case costs **\$100**.

</div>

<div v-click="2">

$$\mathrm{Total\ error\ cost}(t)=5\,FP(t)+100\,FN(t)$$

</div>

<table>
<thead><tr v-click="3"><th style="text-align:left">Threshold</th><th style="text-align:right">False-alert cost</th><th style="text-align:right">Missed-fraud cost</th><th style="text-align:right">Total</th></tr></thead>
<tbody>
<tr v-click="3"><td style="text-align:left">0.80</td><td style="text-align:right">&#36;50</td><td style="text-align:right">&#36;5,000</td><td style="text-align:right">&#36;5,050</td></tr>
<tr v-click="4"><td style="text-align:left">0.50</td><td style="text-align:right">&#36;450</td><td style="text-align:right">&#36;2,000</td><td style="text-align:right">&#36;2,450</td></tr>
<tr v-click="5"><td style="text-align:left">0.20</td><td style="text-align:right">&#36;1,000</td><td style="text-align:right">&#36;500</td><td style="text-align:right"><strong>&#36;1,500</strong></td></tr>
</tbody>
</table>

<p v-click="5" class="caption">Illustrative constant costs. Lowest cost among these three candidates: t = 0.20.</p>

<!--
This is realized total error cost on the validation cohort, not an expectation computed from probabilities. Costs are invented for the exercise and constant within each error type. Correct outcomes have zero cost under this simplified assumption. Lowest cost among the three candidates is threshold 0.20. We are not claiming it is optimal over all thresholds or real-world fraud economics. In a richer model include investigation cost on TP as well, varying fraud amounts, recovered losses, and customer effects.
-->

---
glowSeed: 630
---

# Changing the action changes the preferred threshold

<div v-click="1">

Now a false decline costs **\$100**, while a missed fraud case costs **\$20**.

</div>

<div v-click="2">

$$\mathrm{Total\ error\ cost}(t)=100\,FP(t)+20\,FN(t)$$

</div>

<table>
<thead><tr v-click="3"><th style="text-align:left">Threshold</th><th style="text-align:right">False-decline cost</th><th style="text-align:right">Missed-fraud cost</th><th style="text-align:right">Total</th></tr></thead>
<tbody>
<tr v-click="3"><td style="text-align:left">0.80</td><td style="text-align:right">&#36;1,000</td><td style="text-align:right">&#36;1,000</td><td style="text-align:right"><strong>&#36;2,000</strong></td></tr>
<tr v-click="4"><td style="text-align:left">0.50</td><td style="text-align:right">&#36;9,000</td><td style="text-align:right">&#36;400</td><td style="text-align:right">&#36;9,400</td></tr>
<tr v-click="5"><td style="text-align:left">0.20</td><td style="text-align:right">&#36;20,000</td><td style="text-align:right">&#36;100</td><td style="text-align:right">&#36;20,100</td></tr>
</tbody>
</table>

<p v-click="5" class="caption">Same scores and counts. Lowest cost among these candidates: t = 0.80.</p>

<!--
The hypothetical costs intentionally reverse the preference. Interpret FP as an automatic false decline rather than a review alert. These dollar values are pedagogical, not claims about actual payment systems. Ask students to explain why a model can need a different threshold without retraining. The threshold is part of the decision policy, and the policy depends on the action. General source: https://scikit-learn.org/stable/modules/classification_threshold.html .
-->

---
glowSeed: 631
---

# A capacity limit can rule out a threshold

<div v-click="1">

The review team can handle **at most 100 alerts** per cohort.

</div>

<table>
<thead><tr v-click="2"><th style="text-align:left">Threshold</th><th style="text-align:right">Alerts</th><th style="text-align:right">Fraud caught</th><th style="text-align:left">Within capacity?</th></tr></thead>
<tbody>
<tr v-click="2"><td style="text-align:left">0.80</td><td style="text-align:right">60</td><td style="text-align:right">50</td><td style="text-align:left">Yes</td></tr>
<tr v-click="3"><td style="text-align:left">0.50</td><td style="text-align:right">170</td><td style="text-align:right">80</td><td style="text-align:left">No</td></tr>
<tr v-click="4"><td style="text-align:left">0.20</td><td style="text-align:right">295</td><td style="text-align:right">95</td><td style="text-align:left">No</td></tr>
</tbody>
</table>

<div v-click="5">

**Among these candidates**, t = 0.80 is the only feasible choice.

</div>

<p v-click="5" class="caption">Other policies include reviewing the highest-scoring cases or expanding capacity.</p>

<!--
Capacity is a constraint rather than merely an FP cost. All alerts consume review capacity, including true positives. A fixed threshold may yield different volumes as the population changes. A top-k policy adapts to available capacity but needs a tie-handling rule: in our grouped toy scores, selecting the top 100 cuts through a score tie. Do not imply an arbitrary tie order improves ranking. If no candidate meets a required recall and capacity simultaneously, report the conflict rather than silently ignoring one requirement.
-->

---
glowSeed: 632
---

# A threshold objective needs a complete sentence

<div v-click="1">

Examples of useful objectives:

</div>

<div class="concept-stack">

<div v-click="2" class="concept-box teal"><div class="concept-label">Cost objective</div><div>Minimize error cost using agreed costs for false alerts and missed fraud.</div></div>

<div v-click="3" class="concept-box blue"><div class="concept-label">Capacity constraint</div><div>Maximize recall while generating no more than 100 review alerts.</div></div>

<div v-click="4" class="concept-box amber"><div class="concept-label">Detection requirement</div><div>Maximize precision while maintaining at least 90% recall.</div></div>

</div>

<div v-click="5" class="question">For automatic spam quarantine, what objective would you propose and why?</div>

<!--
Spend two minutes on pairs drafting an objective. Require that they specify positive class, action, metric, constraint, and how they will check feasibility. A pure maximize-recall objective has the trivial solution predict everything positive. A pure maximize-precision objective can catch almost nothing and has an undefined edge case when no positives are predicted. Constraints give the objective operational meaning. Source: https://scikit-learn.org/stable/modules/classification_threshold.html .
-->

---
glowSeed: 633
---

# Threshold tuning belongs on validation data

<table>
<thead><tr v-click="1"><th style="text-align:left">Stage</th><th style="text-align:left">What we do</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">Training</td><td style="text-align:left">Fit the model and preprocessing</td></tr>
<tr v-click="2"><td style="text-align:left">Validation</td><td style="text-align:left">Select the model, threshold, and decision rule</td></tr>
<tr v-click="3"><td style="text-align:left">Test</td><td style="text-align:left">Evaluate the locked model and decision rule</td></tr>
</tbody>
</table>

<div v-click="4">

**The test set stays out of threshold selection.**

</div>

<p v-click="4" class="caption">With limited data, use an appropriate cross-validation procedure.</p>

<!--
Repeatedly choosing a threshold based on test performance adapts to the test set and biases the reported result. If validation is also used for many model choices, account for that selection process with sufficient held-out data or nested evaluation. The built-in TunedThresholdClassifierCV offers internal CV, but its scoring objective must fit the application. Group/time-aware splits are still needed when cases are dependent. Source: https://scikit-learn.org/stable/modules/classification_threshold.html#post-tuning-the-decision-threshold .
-->

---
glowSeed: 634
---

# False Positive Rate (FPR)

<div class="columns">

<ConfusionTable v-click="1" focus="negative"/>

<div>

<div v-click="2">

**False positive rate (FPR):** the share of actual negatives incorrectly flagged positive.

</div>

<div v-click="3">

$$\mathrm{FPR}=\frac{FP}{FP+TN}$$

</div>

<div v-click="4">

$$\frac{90}{90+810}=0.10$$

</div>

<div v-click="5">

**10% of legitimate payments are flagged.**

</div>

<div v-click="6">

Recall = TPR = **80%**

</div>

</div>

</div>

<!--
FPR conditions on actual negatives, so its denominator is 900 legitimate transactions. It is not 1 minus precision: 90/900 versus 90/170. A useful check is to ask students to explain each denominator verbally. Specificity is 1-FPR and appears in optional extensions. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html .
-->

---
glowSeed: 642
---

# What is an ROC curve?

<div class="columns">

<div class="concept-stack compact-boxes" style="gap: 8px; margin: 8px 0">

<div v-click="1" class="concept-box teal"><div class="concept-label">ROC = receiver operating characteristic</div>A curve showing how a classifier separates positives from negatives as its threshold changes.</div>

<div v-click="2" class="concept-box blue"><div class="concept-label">Each point is one threshold</div>It plots the true positive rate (recall) against the false positive rate.</div>

<div v-click="3" class="concept-box amber"><div class="concept-label">Why it matters</div>Compare the sensitivity and false-alarm tradeoff across thresholds, without committing to one threshold first.</div>

</div>

<div v-click="2" class="pt-4">

<EvaluationCurve />

</div>

</div>

<p v-click="4" class="caption">Closer to the upper-left means better separation; the diagonal marks chance-level ranking.</p>

<!--
Introduce the acronym before students see it in the next slide title. ROC means receiver operating characteristic. Each threshold maps to a point: x is false-positive rate (the fraction of actual negatives flagged positive) and y is true-positive rate / recall (the fraction of actual positives found). Sweeping the threshold traces the curve and shows the tradeoff between catching positives and generating false alarms. The curve describes ranking discrimination across thresholds; it does not choose the deployment threshold or show whether predicted probabilities are calibrated. The dashed diagonal is the expected curve for random ranking. AUC summarizes the ranking represented by this curve in the following slide.
-->

---
glowSeed: 635
---

# Each threshold gives a point on the ROC curve

<div class="columns">

<div>

<table>
<thead><tr v-click="1"><th style="text-align:left">Threshold</th><th style="text-align:right">FPR</th><th style="text-align:right">Recall / TPR</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">0.80</td><td style="text-align:right">0.011</td><td style="text-align:right">0.50</td></tr>
<tr v-click="2"><td style="text-align:left">0.50</td><td style="text-align:right">0.100</td><td style="text-align:right">0.80</td></tr>
<tr v-click="3"><td style="text-align:left">0.20</td><td style="text-align:right">0.222</td><td style="text-align:right">0.95</td></tr>
</tbody>
</table>

<div v-click="4">

Sweeping every distinct score produces the full curve.

</div>

</div>

<EvaluationCurve v-click="5" />

</div>

<p v-click="5" class="caption">Curve calculated from all five score bins in the running example.</p>

<!--
The chart uses actual toy-data coordinates, not a decorative hand-drawn ROC. Full vertices are (0,0), (10/900,.5), (30/900,.7), (90/900,.8), (200/900,.95), (1,1). Lines interpolate the effect of tied score groups. The orange point is the 0.50 operating point. The diagonal is the expected no-skill curve. A point at the upper-left corner has TPR=1 and FPR=0. Thresholds above the maximum produce no alerts; thresholds at or below the minimum flag all cases. Scores need not lie in [0,1] in general.
-->

---
glowSeed: 636
---

# ROC-AUC: area under the ROC curve

<p class="text-lg mt-0">ROC-AUC is the area under the ROC curve. It measures how well a model separates positive from negative examples across thresholds, regardless of the final threshold chosen.</p>

<p class="caption text-center mt-2">Vertical axis: true-positive rate (TPR) · Horizontal axis: false-positive rate (FPR)</p>

<div class="grid grid-cols-3 gap-5 mt-8">

<div class="text-center">
<div class="font-bold text-teal-300 mb-1" style="min-height: 58px; display: flex; align-items: center; justify-content: center">Good · AUC ≈ 0.89</div>
<svg viewBox="0 0 300 235" role="img" aria-label="Good ROC curve with area under the curve about 0.89" style="width:100%;max-height:300px">
<path d="M45 180 C60 95 85 48 125 31 C170 20 230 20 280 20 L280 180 Z" fill="#2dd4bf" fill-opacity=".16"/>
<path d="M45 180 L280 20" fill="none" stroke="#94a3b8" stroke-dasharray="5 5"/>
<path d="M45 180 C60 95 85 48 125 31 C170 20 230 20 280 20" fill="none" stroke="#2dd4bf" stroke-width="4"/>
<path d="M45 20 V180 H280" fill="none" stroke="#cbd5e1" stroke-width="2"/>
</svg>
</div>

<div class="text-center">
<div class="font-bold text-blue-300 mb-1" style="min-height: 58px; display: flex; align-items: center; justify-content: center">Random guessing · AUC = 0.50</div>
<svg viewBox="0 0 300 235" role="img" aria-label="Diagonal ROC curve for random guessing with area under the curve 0.50" style="width:100%;max-height:300px">
<path d="M45 180 L280 20 L280 180 Z" fill="#60a5fa" fill-opacity=".12"/>
<path d="M45 180 L280 20" fill="none" stroke="#60a5fa" stroke-width="4"/>
<path d="M45 20 V180 H280" fill="none" stroke="#cbd5e1" stroke-width="2"/>
</svg>
</div>

<div class="text-center">
<div class="font-bold text-amber-300 mb-1" style="min-height: 58px; display: flex; align-items: center; justify-content: center">Worse than random guessing · AUC ≈ 0.11</div>
<svg viewBox="0 0 300 235" role="img" aria-label="ROC curve below the diagonal for worse than random guessing with area under the curve about 0.11" style="width:100%;max-height:300px">
<path d="M45 180 C225 174 263 145 280 20 L280 180 Z" fill="#fbbf24" fill-opacity=".12"/>
<path d="M45 180 L280 20" fill="none" stroke="#94a3b8" stroke-dasharray="5 5"/>
<path d="M45 180 C225 174 263 145 280 20" fill="none" stroke="#fbbf24" stroke-width="4"/>
<path d="M45 20 V180 H280" fill="none" stroke="#cbd5e1" stroke-width="2"/>
</svg>
</div>

</div>

<!--
ROC-AUC is the area under the ROC curve and measures ranking separation across thresholds; it does not select the deployment threshold. A curve above the diagonal has AUC > 0.5, random guessing follows the diagonal with AUC = 0.5, and a curve below it has AUC < 0.5. The low-AUC example represents scores that tend to rank positives below negatives; flipping the score direction would reverse that ranking. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html .
-->

---
glowSeed: 637
---

# Rare positives can create many false alerts

<div v-click="1">

A different deployment population has **10 fraud cases** and **9,990 legitimate payments**.

</div>

<div v-click="2">

The detector catches 8 fraud cases and raises 92 false alerts.

</div>

<table>
<thead><tr v-click="3"><th style="text-align:left">Measure</th><th style="text-align:left">Calculation</th><th style="text-align:right">Value</th></tr></thead>
<tbody>
<tr v-click="3"><td style="text-align:left">Recall</td><td style="text-align:left">8/10</td><td style="text-align:right">80%</td></tr>
<tr v-click="4"><td style="text-align:left">False-positive rate</td><td style="text-align:left">92/9,990</td><td style="text-align:right">0.92%</td></tr>
<tr v-click="5"><td style="text-align:left">Precision</td><td style="text-align:left">8/(8+92)</td><td style="text-align:right"><strong>8%</strong></td></tr>
</tbody>
</table>

<p v-click="5" class="caption">A small false-positive rate can still produce a large share of false alerts.</p>

<!--
Explicitly switch populations for this standalone rare-event example. We have only one operating point here; do not infer AUC from it. The low precision does not itself establish that the system has no value: 8% is much larger than the 0.1% prevalence, and usefulness depends on benefits, costs, and review capacity. The point is that ROC coordinates alone do not communicate alert burden. Source for why precision-recall is useful with imbalance: https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html .
-->

---
glowSeed: 638
---

# Precision-recall curves describe alert quality

<div class="columns">

<div>

<div v-click="1">

Back to our **1,000 transactions**:

</div>

<ul v-click="1">
<li>Horizontal axis: recall.</li>
<li>Vertical axis: precision.</li>
<li>Each operating point uses a threshold.</li>
</ul>

<div v-click="1" class="concept-box teal"><div class="concept-label">Average precision</div><div>0.657 for this score ranking.</div></div>

<p v-click="1" class="caption">Dashed baseline: 10% prevalence in this cohort.</p>

</div>

<EvaluationCurve v-click="6" kind="pr" />

</div>

<!--
Return to the main toy dataset. Use average precision (AP) as the explicitly named summary. This displayed step interpolation is chosen to match AP: precision weighted by increments in recall. It is not trapezoidal PR-AUC. Toy-data AP=0.6570311, verify via script. The endpoint with zero predicted positives is conventionally plotted at precision=1, recall=0 even though the ratio at that classifier is undefined. No-skill baseline equals prevalence in expectation. AP and ROC-AUC measure different summaries and their values should not be directly compared as if on the same yardstick. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html .
-->

---
glowSeed: 639
---

# Which evidence answers which question?

<table>
<thead><tr v-click="1"><th style="text-align:left">Question</th><th style="text-align:left">Evidence</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">What mistakes occur at this threshold?</td><td style="text-align:left">Confusion matrix</td></tr>
<tr v-click="2"><td style="text-align:left">How reliable are positive predictions?</td><td style="text-align:left">Precision</td></tr>
<tr v-click="3"><td style="text-align:left">How many real cases do we catch?</td><td style="text-align:left">Recall</td></tr>
<tr v-click="4"><td style="text-align:left">How do precision and recall combine?</td><td style="text-align:left">F1</td></tr>
<tr v-click="5"><td style="text-align:left">How well do scores rank the classes?</td><td style="text-align:left">ROC-AUC and precision-recall curve / AP</td></tr>
<tr v-click="6"><td style="text-align:left">Should we take this action?</td><td style="text-align:left">Costs, constraints, and validation results</td></tr>
</tbody>
</table>

<!--
This consolidates the distinction between a fixed-threshold decision and a ranking over thresholds. A single confusion matrix cannot determine ROC-AUC or AP. Ranking quality cannot by itself justify an action. A good report uses metrics that answer the intended question, labels the positive class, and reports the chosen threshold. Definitions supported by https://scikit-learn.org/stable/modules/model_evaluation.html .
-->

---
glowSeed: 652
---

# From two classes to many classes

<div v-click="1">A wildlife camera assigns each image to <strong>deer, fox, or dog</strong>.</div>

<div class="columns" style="margin-top:20px">

<MulticlassTable v-click="2" />

<div>
<div v-click="3" class="concept-box blue"><div class="concept-label">Same axes, more categories</div>Rows = actual class.<br>Columns = predicted class.<br>K classes → a K × K matrix.</div>
<div v-click="4" class="concept-box teal" style="margin-top:16px"><div class="concept-label">Read the cells</div>Diagonal = correct predictions.<br>Off-diagonal = specific mistakes.</div>
</div>

</div>

<div v-click="5" class="question">What does the 7 in the Fox row, Dog column mean?</div>

<!--
Start by connecting this 3 × 3 matrix to the earlier 2 × 2 matrix. There is one actual class and one predicted class per image: this is single-label multiclass classification. All 100 images are fictional. Seven actual foxes were predicted to be dogs; the reverse error has count 4. Row totals are 50 deer, 20 foxes, and 30 dogs. Column totals are 46 deer, 19 foxes, and 35 dogs. Accuracy still counts the diagonal: (45+12+26)/100=83%. In general C_ij counts actual class i predicted as class j. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html .
-->

---
glowSeed: 653
---

# Treat one class as positive

<div v-click="1">To evaluate <strong>fox</strong>, group deer and dog together as <strong>not fox</strong>.</div>

<div class="columns" style="margin-top:20px">

<MulticlassTable v-click="2" focus="one-vs-rest" />

<div>
<div v-click="3" class="concept-box teal"><div class="concept-label">True positives</div>12 foxes predicted as fox.</div>
<div v-click="4" class="concept-box blue" style="margin-top:12px"><div class="concept-label">False positives</div>3 deer + 4 dogs predicted as fox = 7.</div>
<div v-click="5" class="concept-box amber" style="margin-top:12px"><div class="concept-label">False negatives</div>1 fox called deer + 7 called dog = 8.</div>
</div>

</div>

<p v-click="6" class="caption">Repeat this “one versus the rest” view for each class.</p>

<!--
This changes how we count outcomes for evaluation; it does not require training separate binary classifiers. For fox: TP=12, FP=7, FN=8, TN=73. The four cells outside the fox row and fox column are TN, including deer/dog confusions: those are errors for the original task but correctly negative for “is this a fox?” The labels TP/FP/FN/TN are relative to the class currently selected. Ask how the labels would change if dog became positive. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.multilabel_confusion_matrix.html .
-->

---
glowSeed: 654
---

# Multiclass precision: look down a column

<div class="columns">

<div>
<MulticlassTable v-click="1" focus="precision" />
<p v-click="2" class="caption">The Fox column contains all 19 predictions of fox.</p>
</div>

<div>
<div v-click="2">Of images <strong>predicted as fox</strong>, how many really are fox?</div>
<div v-click="3">

$$\mathrm{Precision}_{\text{fox}}=\frac{12}{3+12+4}=63.2\%$$

</div>
<div v-click="4" class="concept-box teal"><div class="concept-label">For any class k</div>Correct predictions of k ÷ all predictions of k.</div>
<div v-click="4">

$$P_k=\frac{TP_k}{TP_k+FP_k}$$

</div>
</div>

</div>

<!--
The original definition of precision survives unchanged once we name a positive class. The highlighted column is the denominator and its diagonal cell is the numerator. Of 19 fox predictions, 12 are correct and 7 are false alarms. Deer precision=45/46=97.8%; dog precision=26/35=74.3%. A class with no predictions has undefined precision; a reporting convention such as zero_division=0 must be stated if used. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html .
-->

---
glowSeed: 655
---

# Multiclass recall: look across a row

<div class="columns">

<div>
<MulticlassTable v-click="1" focus="recall" />
<p v-click="2" class="caption">The Fox row contains all 20 actual fox images.</p>
</div>

<div>
<div v-click="2">Of images that <strong>really are fox</strong>, how many did we identify?</div>
<div v-click="3">

$$\mathrm{Recall}_{\text{fox}}=\frac{12}{1+12+7}=60\%$$

</div>
<div v-click="4" class="concept-box teal"><div class="concept-label">For any class k</div>Correct predictions of k ÷ all actual examples of k.</div>
<div v-click="4">

$$R_k=\frac{TP_k}{TP_k+FN_k}$$

</div>
</div>

</div>

<!--
Recall uses the actual-class row as its denominator and the same diagonal cell as precision for its numerator. Eight of 20 foxes are missed. Deer recall=45/50=90%; dog recall=26/30=86.7%. A class absent from the evaluation data has undefined recall. Each off-diagonal mistake is a false negative for its actual class and a false positive for its predicted class. Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html .
-->

---
glowSeed: 656
---

# From class metrics to a summary

<table class="compact">
<thead><tr v-click="1"><th>Class</th><th>Actual count</th><th>Precision</th><th>Recall</th></tr></thead>
<tbody>
<tr v-click="1"><td>Deer</td><td>50</td><td>97.8%</td><td>90.0%</td></tr>
<tr v-click="1"><td>Fox</td><td>20</td><td>63.2%</td><td>60.0%</td></tr>
<tr v-click="1"><td>Dog</td><td>30</td><td>74.3%</td><td>86.7%</td></tr>
</tbody>
</table>

<table class="compact" style="margin-top:18px">
<thead><tr v-click="2"><th>Average</th><th>How to combine class metrics</th><th>Precision</th><th>Recall</th></tr></thead>
<tbody>
<tr v-click="2"><td>Macro</td><td>Give each class equal weight.</td><td>78.4%</td><td>78.9%</td></tr>
<tr v-click="3"><td>Weighted</td><td>Weight by actual class count.</td><td>83.8%</td><td>83.0%</td></tr>
<tr v-click="4"><td>Micro</td><td>Pool TP, FP, and FN before dividing.</td><td>83.0%</td><td>83.0%</td></tr>
</tbody>
</table>

<div v-click="5" class="concept-box teal" style="margin-top:18px">Report the averaging method and inspect important classes directly.</div>

<!--
Use unrounded class ratios for calculations. Precision=[45/46,12/19,26/35]; recall=[45/50,12/20,26/30]; support=[50,20,30]. Macro precision=78.419%; macro recall=78.889%. Weighted precision=83.830%; weighted recall=83%. Macro makes each class matter equally; weighted gives more influence to frequent actual classes, including when averaging precision. Micro pools counts: TP=83, FP=17, FN=17, giving both precision and recall 83%. In single-label multiclass classification over all classes, each wrong prediction contributes one FP and one FN; micro precision, recall, and F1 equal accuracy. This equality need not hold for multilabel tasks or a subset of labels. If reporting F1, compute it per class and then average; macro F1 generally differs from F1 of macro precision and macro recall. Discuss how the summaries can conceal 60% fox recall. Sources: https://scikit-learn.org/stable/modules/model_evaluation.html#multiclass-and-multilabel-classification and https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html .
-->

---
glowSeed: 640
---

# A threshold in Python

<div v-click="1">

```python
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score

# The fitted model's classes are [0, 1]; 1 means fraud.
fraud_column = np.flatnonzero(model.classes_ == 1).item()
s_val = model.predict_proba(X_val)[:, fraud_column]
t = 0.20  # chosen using validation costs or constraints
pred_val = (s_val >= t).astype(int)

print(confusion_matrix(y_val, pred_val, labels=[0, 1]))
print(precision_score(y_val, pred_val, zero_division=0))
print(recall_score(y_val, pred_val, zero_division=0))
```

</div>

<div v-click="2">

After selection, apply the **locked threshold** to test scores.

</div>

<!--
This is a minimal API pattern, not a standalone training program. It assumes numeric labels [0,1] and a fitted model. Looking up class 1 avoids assuming it is always column 1. labels=[0,1] fixes confusion matrix order. zero_division=0 is a reporting convention when the metric denominator vanishes, not a mathematical definition. ROC-AUC and AP should receive scores, not pred_val. The companion examples/threshold_demo.py is standalone and reproduces all numeric running-example results. Sources: scikit-learn predict_proba estimator documentation and https://scikit-learn.org/stable/modules/model_evaluation.html .
-->

---
glowSeed: 641
---

# Your deployment recommendation

<div v-click="1">

Your review team can handle **200 alerts** per 1,000 transactions.

</div>

<div v-click="2">

Stakeholders require **at least 80% recall**.

</div>

<div v-click="3">

Choose among **t = 0.80, 0.50, and 0.20**.

</div>

<div v-click="4" class="question">Which meets both requirements? What would you report?</div>

<div v-click="5"><strong>t = 0.50:</strong> 170 alerts, 80% recall, 47.1% precision.<br>Report the confusion matrix, threshold, cohort, and constraints.</div>

<!--
Closing core activity. Give students two minutes and ask them to reject the infeasible candidates explicitly: .80 has recall only 50%, .20 has 295 alerts. .50 meets both. The valid statement is feasible among these candidates, not proven globally optimal. Ask what to do if no threshold meets both: communicate the constraint conflict, change capacity/action, improve the model, or revisit requirements with stakeholders. This activity makes application-specific threshold choice the final core takeaway. Next slides are optional extensions.
-->

---
glowSeed: 642
layout: section
---

# Optional extensions

<div v-click="1">

## More ways to examine classifier behavior

Specificity and negative predictive value<br>Probability calibration<br>Prevalence changes<br>Thresholds from calibrated probabilities

</div>

<p v-click="1" class="caption">The core lesson ends with the deployment recommendation.</p>

<!--
Skip this section for a shorter session or use it for a second meeting. These extensions preserve important material from the original decks while avoiding interrupting the binary decision narrative. Speaker notes include worked answers and exact qualifications.
-->

---
glowSeed: 643
---

# Specificity and negative predictive value

<table>
<thead><tr v-click="1"><th style="text-align:left">Measure</th><th style="text-align:left">Question</th><th style="text-align:right">Running example</th></tr></thead>
<tbody>
<tr v-click="1"><td style="text-align:left">Specificity</td><td style="text-align:left">Of actual negatives, how many pass correctly?</td><td style="text-align:right">810/900 = 90%</td></tr>
<tr v-click="2"><td style="text-align:left">Negative predictive value</td><td style="text-align:left">Of negative predictions, how many are correct?</td><td style="text-align:right">810/830 = 97.6%</td></tr>
</tbody>
</table>

<div v-click="3">

$$\mathrm{Specificity}=\frac{TN}{TN+FP}=1-\mathrm{FPR}$$

</div>

<div v-click="4">

$$\mathrm{NPV}=\frac{TN}{TN+FN}$$

</div>

<!--
Recall is sensitivity. Specificity conditions on true negatives while NPV conditions on predicted negatives, mirroring recall versus precision. NPV and precision depend on prevalence. Distinguish a high NPV in a mostly negative population from a guarantee that every cleared individual is safe. Source: https://scikit-learn.org/stable/modules/model_evaluation.html .
-->

---
glowSeed: 646
---

# Ranking and probability calibration

<div v-click="1">

Model A says **0.80** for a group of transactions.<br>Model B says **0.99** for exactly the same group.

</div>

<div v-click="2">

If only 80% of those transactions are fraud, Model A better matches the observed frequency.

</div>

<div v-click="3">

**The two models can still have identical rankings and ROC-AUC.**

</div>

<p v-click="3" class="caption">Reliability diagrams compare predicted probabilities with observed frequencies.</p>

<!--
Interpret the two models as identical ordering with different numeric score values. Perfectly matching this one bin does not establish whole-model calibration, and calibration estimates need enough observations. Reliability diagrams examine more bins; log loss and Brier score assess probability quality but are not pure measures of calibration alone. Fit calibration methods within training/model-selection data, never on the final test data. Source: https://scikit-learn.org/stable/modules/calibration.html .
-->

---
glowSeed: 647
---

# A prevalence change alters precision

<div v-click="1">

Keep recall at **80%** and FPR at **10%**.

</div>

<table>
<thead><tr v-click="2"><th style="text-align:left">Population</th><th style="text-align:right">TP</th><th style="text-align:right">FP</th><th style="text-align:right">Precision</th></tr></thead>
<tbody>
<tr v-click="2"><td style="text-align:left">100 fraud, 900 legitimate</td><td style="text-align:right">80</td><td style="text-align:right">90</td><td style="text-align:right">47.1%</td></tr>
<tr v-click="3"><td style="text-align:left">10 fraud, 990 legitimate</td><td style="text-align:right">8</td><td style="text-align:right">99</td><td style="text-align:right">7.5%</td></tr>
</tbody>
</table>

<div v-click="4">

The conditional rates stayed fixed, but alert quality changed.

</div>

<div v-click="5">

**Recheck thresholds and workload in the deployment population.**

</div>

<!--
This hypothetical pure prevalence shift holds sensitivity and FPR constant by assumption. Precision=8/107=.0747664 in the second row. In practice those conditional rates can also change, so monitor rather than assume stability. A validation sample deliberately enriched with positives will not directly estimate deployment precision. Use representative evaluation or appropriate reweighting. Source: https://scikit-learn.org/stable/modules/model_evaluation.html and https://scikit-learn.org/stable/modules/calibration.html .
-->

---
glowSeed: 648
---

# A cost threshold from calibrated probabilities

<div v-click="1">

Assume **p is a calibrated fraud probability** and each error type has a constant cost.

</div>

<div v-click="2">

Allow: expected cost = $p\,C_{FN}$<br>Flag: expected cost = $(1-p)\,C_{FP}$

</div>

<div v-click="3">

Flag when:

</div>

<div v-click="4">

$$p\geq\frac{C_{FP}}{C_{FP}+C_{FN}}$$

</div>

<p v-click="4" class="caption">This simplified rule assumes zero cost for correct decisions and no capacity constraint.</p>

<!--
Derive (1-p)C_FP <= p C_FN, then solve. Costs must correspond to the actual action. With C_FP=5 and C_FN=100 this gives 5/105≈.0476, but do not apply that numerical rule to our toy scores, which are not calibrated probabilities. Our earlier tables instead estimated realized cost on validation data. The formula changes when correct actions have costs or benefits, errors vary by transaction, capacity constrains actions, or action does not prevent the assumed loss. A real decision policy can therefore be more complex than one global threshold. General source: https://scikit-learn.org/stable/auto_examples/model_selection/plot_cost_sensitive_learning.html .
-->

---
glowSeed: 649
---

# References and example data

<div class="source-list">

<div v-click="1">

[Scikit-learn: metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html)

</div>

<div v-click="2">

[Scikit-learn: decision threshold tuning](https://scikit-learn.org/stable/modules/classification_threshold.html)

</div>

<div v-click="3">

[Scikit-learn: precision-recall example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)

</div>

<div v-click="4">

[Scikit-learn: probability calibration](https://scikit-learn.org/stable/modules/calibration.html)

</div>

</div>

<p v-click="4" class="caption">All numerical scenarios in this presentation are illustrative. The supplied Python example reproduces the fraud cohort, threshold results, ROC-AUC, and average precision.</p>

<!--
The data live in examples/fraud-data.json, and examples/threshold_demo.py is the companion calculation script. Technical sources appear in relevant slide notes as well. References verified September 28, 2026. Presentation creation or QA notes belong in the README, not on the teaching slides.
-->
