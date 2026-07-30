---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Ethical Considerations and Failure Modes'
info: |
  ## Ethical Considerations and Failure Modes
  Anticipate how deployed systems can fail and cause harm
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
glowSeed: 1030
---

# Ethical Considerations and Failure Modes

### Anticipate how deployed systems can fail and cause harm

<div class="pt-8 opacity-80 text-lg">Broader Context · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This unit closes out the semester's technical arc by asking a question the earlier units deliberately set aside: what happens after a model is trained, validated, and shipped? Every previous deck — regression, trees, ensembles, neural networks — treated "a good model" as one with strong held-out performance on a fixed test set. That is necessary but not sufficient. A model can pass every offline check and still fail in production, and it can fail in ways that are invisible until real people are harmed by a wrong prediction.

Four failure families structure this deck: (1) distribution shift, where the world the model now sees no longer matches the world it was trained on; (2) feedback loops, where the model's own predictions change the data that future models will be trained on; (3) confident errors at the edges of the input space, including adversarial examples and out-of-distribution inputs; and (4) dual-use risk, where a capability built for one purpose can be repurposed for harm. Each failure mode gets a concrete, real-world case study rather than an abstract description, because the goal of this deck is to build an operational habit of "what could go wrong here?" before a system ships — not just to recognize the vocabulary. We close with a deployment checklist you can literally reuse on a project.
-->

---
glowSeed: 1031
---

# Why This Failure Analysis Even Exists

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The ERM assumption</span>
<span class="text-sm opacity-85"> — Empirical risk minimization picks the model that best fits a fixed training sample, under the assumption that future data is drawn from the same distribution.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">What validation actually checks</span>
<span class="text-sm opacity-85"> — A held-out test score confirms the model generalizes to more samples from the <em>same</em> distribution, not to the world after deployment.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The gap this unit fills</span>
<span class="text-sm opacity-85"> — Every failure mode in this deck is a different way that assumption breaks once the model leaves the lab.</span>
</div>
</div>
</div>
<div v-click class="mt-4" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-4>

$$
\hat{\theta} = \arg\min_\theta \; \mathbb{E}_{(x,y)\sim \mathcal{D}_{\text{train}}}\big[\ell(f_\theta(x), y)\big]
$$

<div class="text-sm opacity-85 mt-2">Nothing in this objective mentions $\mathcal{D}_{\text{deploy}}$. If $\mathcal{D}_{\text{deploy}} \ne \mathcal{D}_{\text{train}}$, low training loss guarantees nothing about real-world behavior.</div>
</div>
</div>

<!--
Recall the empirical risk minimization objective from Core ML Concepts: we pick parameters theta to minimize average loss over a training sample drawn from some distribution D_train. Cross-validation and a held-out test set only ever ask "does this generalize to more draws from D_train?" — they cannot ask "does this generalize to the world six months from now?" because that data does not exist yet at training time.

This is the single unifying idea behind every failure mode in this deck: distribution shift, feedback loops, adversarial inputs, and dual-use risk are all different mechanisms by which the deployment distribution D_deploy diverges from the training distribution D_train, silently invalidating the guarantees that cross-validation gave you. Keep this equation in mind as a throughline — each subsequent slide is a specific story about how and why D_deploy != D_train in practice, and what to do about it.
-->

---
glowSeed: 1032
---

# Distribution Shift Breaks the i.i.d. Assumption

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Covariate shift</span>
<span class="text-sm opacity-85"> — The distribution of inputs $P(X)$ changes, but the true relationship $P(Y\mid X)$ stays the same (e.g., a new user demographic starts using the product).</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Concept shift</span>
<span class="text-sm opacity-85"> — The relationship $P(Y\mid X)$ itself changes; the same input now means something different (e.g., pandemic-era spending patterns broke fraud models).</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Silent failure</span>
<span class="text-sm opacity-85"> — Softmax and regression outputs do not know they are wrong; the system keeps returning confident predictions as true accuracy quietly decays.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Line chart: model confidence stays high while true accuracy declines after launch as distribution shift accumulates" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 60 C130 62,300 66,465 70" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 65 C135 100,205 150,270 180 S385 220,465 235" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="230" r="5"/><circle cx="163" cy="170" r="5"/><circle cx="261" cy="130" r="5"/><circle cx="359" cy="95" r="5"/><circle cx="457" cy="70" r="5"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">train</text><text x="163" y="285">launch</text><text x="261" y="285">month 2</text><text x="359" y="285">month 4</text><text x="457" y="285">month 6</text></g>
  <g style="font-size: 12px"><text x="330" y="52" fill="#5eead4">reported confidence</text><text x="330" y="250" fill="#93c5fd">true accuracy</text></g>
</svg>
<div class="text-xs opacity-70 text-center mt-1">Confidence and accuracy decouple — the gap is where harm accumulates unnoticed.</div>
</div>
</div>

<!--
Distribution shift comes in two flavors that are worth distinguishing precisely because they call for different fixes. Covariate shift means the marginal distribution of inputs P(X) has changed — new users, a new sensor, a new geographic market — but the underlying relationship between input and label, P(Y|X), is still valid; retraining on fresh, representative data usually repairs this. Concept shift is more dangerous: the mapping from input to label itself has changed, so the same input now has a different correct answer (a pandemic changing what "normal" spending looks like for fraud detection, or a competitor changing the market so that yesterday's "good price" is today's overpay). No amount of retraining on old labeling logic fixes concept shift — you need new ground truth.

The diagram makes the core danger concrete: a classifier's reported confidence (softmax probability or regression certainty) is a property of the model's internal geometry, not a certified statement about the world. As the input distribution drifts further from what the model saw in training, true accuracy can decay steadily while reported confidence stays flat and high, because nothing in the model's training ever taught it to say "I don't know anymore." This is why monitoring is not a one-time validation checkbox at launch — it is an ongoing process that has to compare live outcomes against predictions, not just watch confidence scores. Next, a concrete case where this exact pattern caused a nine-figure loss.
-->

---
glowSeed: 1033
---

# Case Study — Zillow's iBuying Algorithm

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">The model</div>
<div class="text-sm leading-relaxed opacity-90">"Zestimate"-based pricing model automatically made cash offers on homes, trained on historical sale prices during a stable market.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">The shift</div>
<div class="text-sm leading-relaxed opacity-90">2021's abrupt housing-market volatility broke the historical price relationships the model had learned; it kept extrapolating stale patterns into a new regime.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">The outcome</div>
<div class="text-sm leading-relaxed opacity-90">Zillow overpaid for thousands of homes, wrote down roughly $300–500M in inventory, and shut the program down entirely in late 2021.</div>
</div>
</div>

<div v-click class="mt-6 text-sm opacity-85" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>
This was not a bug in the code — the model was doing exactly what it was trained to do: minimize error on <em>historical</em> price data. The failure was organizational: no process existed to detect that the deployment distribution had moved and to throttle automated decisions accordingly.
</div>

<!--
Zillow Offers used a machine-learned pricing model to make automated cash offers on homes it would buy, renovate, and resell — a real-money decision made directly from a regression-style prediction, with essentially no human price review at scale. The model was trained on historical housing transaction data from a relatively stable market. When the housing market became unusually volatile in 2021, with rapid price swings and labor and materials shortages complicating renovation costs, the statistical relationships the model had learned no longer held — a clean case of both covariate shift (unusual homes and markets it hadn't seen) and concept shift (the same house features no longer implied the same fair price).

The company continued to make offers based on the model's estimates faster than it could sell the resulting inventory, accumulating a large book of homes purchased above what it could resell them for. Zillow ultimately wrote down several hundred million dollars in inventory value and shut down the entire iBuying business, laying off about a quarter of its workforce. The teaching point is not "don't trust models for pricing" — it's that a model achieving low training error offers zero guarantee once the world it operates in changes, and that automated, high-stakes decisions need a monitoring and circuit-breaker mechanism that can detect this and throttle or pause the system, rather than relying on the model to know it has become unreliable. Contrast this with the next failure mode, feedback loops, where the model doesn't just fail to notice a changing world — it actively reshapes the world that will train its successor.
-->

---
glowSeed: 1034
---

# Feedback Loops Change the Data Being Predicted

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Prediction</span>
<span class="text-sm opacity-85"> — The model outputs a risk score, ranking, or recommendation.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Action</span>
<span class="text-sm opacity-85"> — A human or automated system acts on that output — allocating patrols, approving loans, ranking content.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Retraining</span>
<span class="text-sm opacity-85"> — The <em>consequences</em> of that action, not an independent ground truth, become the next training set.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Amplification</span>
<span class="text-sm opacity-85"> — A small initial bias in the loop compounds across cycles instead of averaging out.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Prediction then Decision then Observed data then Retrain, looping back to Prediction">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Prediction</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Decision</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Observed data</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Retrain ↻</div>
</div>
</div>

</div>
</div>

<!--
A feedback loop happens when a model's predictions influence the actions taken, and those actions in turn shape the data used to train the model's next version — so the model is no longer a passive observer of the world but an active participant that reshapes what future data looks like. This is fundamentally different from ordinary distribution shift: the world isn't drifting on its own, the model itself is the drift mechanism.

Concretely: (1) the model predicts something, e.g. "this neighborhood has elevated crime risk"; (2) that prediction drives a real action, e.g. more police patrols are sent there; (3) more patrols mechanically produce more recorded incidents — not because crime went up, but because more observers were present to record it; (4) that inflated incident count becomes "ground truth" for the next model, which now predicts even higher risk for the same neighborhood. Any small initial bias — even one driven by pure historical patrol allocation rather than actual crime — gets amplified each cycle rather than washed out, because the data-generating process is no longer independent of the model. Cross-validation on one static, single-cycle dataset structurally cannot detect this, because a train/test split from one moment in time captures only a single frame of a process that unfolds over many retraining cycles. Next, a specific, well-documented instance of exactly this loop.
-->

---
glowSeed: 1035
---

# Case Study — Predictive Policing Feedback Loops

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">The setup</div>
<div class="text-sm leading-relaxed opacity-90">Place-based predictive policing tools (e.g., PredPol) forecast "high-risk" locations from historical arrest and incident records, then recommend patrol allocation.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">The confound</div>
<div class="text-sm leading-relaxed opacity-90">Historical arrest data reflects <em>where police already patrolled</em>, not an unbiased census of where crime occurs — over-patrolled neighborhoods look "higher risk" purely because they were watched more.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">The loop</div>
<div class="text-sm leading-relaxed opacity-90">More predicted risk → more patrols sent → more recorded stops/arrests in that area → next model trained on inflated counts → even higher predicted risk.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">The finding</div>
<div class="text-sm leading-relaxed opacity-90">Independent audits (e.g., Lum &amp; Isaac, 2016) showed such systems can direct disproportionate attention to the same historically over-policed neighborhoods regardless of true crime distribution.</div>
</div>
</div>

<!--
Kristian Lum and William Isaac's widely cited 2016 analysis, "To Predict and Serve?", applied a predictive-policing-style algorithm to drug-crime data and compared its recommended patrol locations against a public-health estimate of where drug use actually occurred across the city. The algorithm's predictions concentrated overwhelmingly on a small number of historically over-policed, lower-income, and predominantly minority neighborhoods, while the independent estimate showed drug use was far more evenly distributed across the city. The mismatch traces directly to the feedback loop described on the previous slide: arrest records are not a neutral measurement of crime, they are a measurement of policing activity, and policing activity has historically not been allocated evenly.

The deeper lesson generalizes well beyond policing: any system where "what we recorded" is a downstream consequence of a prior decision — recommendation systems training on what users clicked after being shown a biased ranking, or content moderation systems trained on what got reported after being shown to an already-skewed audience — inherits this same self-reinforcing structure. Breaking a feedback loop requires deliberately introducing measurement that is decoupled from the model's own actions (e.g., randomized patrol audits, holdout regions with no automated intervention) so that the next model isn't just re-learning its predecessor's blind spots at higher confidence. This closes the "the world changes" and "predictions change the world" half of the deck; the next two slides turn to failures that occur even within a single, static deployment — what happens at the edges of what the model was ever shown.
-->

---
glowSeed: 1036
---

# Confidently Wrong at the Edges

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Adversarial input</div>
<div class="text-sm leading-relaxed opacity-90">A deliberately crafted, often visually imperceptible perturbation flips a prediction with high confidence — e.g., stickers placed on a stop sign made it classify as a 45 mph speed limit sign in a well-known 2018 study.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Out of distribution</div>
<div class="text-sm leading-relaxed opacity-90">An input unlike anything in training (a new object class, a sensor failure, a novel medical presentation) is still forced into one of the known output classes.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Safety implication</div>
<div class="text-sm leading-relaxed opacity-90">Safety-critical systems need explicit detection, a documented fallback behavior, and a human-review path — not just a higher softmax threshold.</div>
</div>
</div>

<div v-click class="mt-6" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>

$$
\text{softmax}(z)_i = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}
$$

<div class="text-sm opacity-85 mt-2">Softmax always distributes probability mass across the $K$ <em>known</em> classes and always sums to $1$ — there is no $(K{+}1)$-th "none of the above / unfamiliar input" option built in, so a wildly novel input still receives a normalized, often high-confidence prediction.</div>
</div>

<!--
Two related but distinct edge-case failures. Adversarial examples are inputs deliberately engineered — often via gradient-based optimization against the model itself — to cause a misclassification while looking normal or even unchanged to a human; the 2018 Eykholt et al. study physically placed small black-and-white stickers on stop signs and got a standard image classifier to read them as speed-limit signs with high confidence, across multiple viewing angles and distances, which is why this remains a standard example in the AV safety literature. Out-of-distribution (OOD) inputs are not adversarial at all — nobody engineered them — they are simply unlike anything in the training data, such as a medical scanner encountering a rare condition never seen during training, or a self-driving car's camera encountering fog for the first time.

The mathematical reason both are dangerous is visible in the softmax equation: it is a normalization, not a certification. It takes whatever raw scores (logits) the network produces and rescales them into a valid probability distribution over the K classes the model was trained to output — but if the true answer is "this doesn't belong to any of your K classes," softmax has no way to say that; it will still confidently commit probability mass to the closest-looking known class. This is exactly why "just check if confidence is high" is not a safety strategy — a wildly wrong input can still produce a very high softmax score. Robust deployments need dedicated OOD detectors (often based on comparing an input's internal representation distance to known training clusters), adversarial-robustness testing, and — critically — a defined fallback action (defer to a human, refuse to act, request more sensor input) rather than a bare prediction. This theme of "systems that were never designed to say 'I don't know'" also connects directly to the next slide on dual-use: a capability with no built-in sense of its own limits is also a capability with no built-in sense of appropriate use.
-->

---
glowSeed: 1037
---

# Dual-Use Capabilities

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Beneficial use</div>
<div class="text-sm leading-relaxed opacity-90">Facial recognition reuniting missing persons with family; accessibility tools for low-vision users; diagnostic support; fraud detection; creative assistance.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Harmful use</div>
<div class="text-sm leading-relaxed opacity-90">The <em>same</em> facial recognition model enabling mass surveillance, stalking, or discriminatory screening at a border checkpoint or protest.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Design responsibility</div>
<div class="text-sm leading-relaxed opacity-90">Threat-model foreseeable misuse at design time — access controls, audit logging, and rate limits are as much a part of "the model" as its weights.</div>
</div>
</div>

<div v-click class="mt-6 text-sm opacity-85" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>
"Dual-use" is not a property of bad actors alone — it means the <em>technology itself</em>, unmodified, serves both purposes. A model card that documents only the intended use case, and never the foreseeable misuse cases, is an incomplete risk assessment.
</div>

<!--
Dual-use describes any technology whose capability is neutral with respect to intent — the exact same trained facial recognition model that helps identify a missing child in an airport can, with no retraining at all, be pointed at a crowd of protesters to identify and later target individual attendees. The technical artifact (weights, architecture, inference code) doesn't encode "good" or "bad" — only the deployment context, access controls, and applied policy do. This differs from the earlier failure modes in the deck: distribution shift and feedback loops are unintended failures of a system doing what it was designed to do; dual-use risk is about a system being intentionally redirected to do something it was never intended to do, but is fully capable of doing.

The design responsibility this implies is to treat misuse analysis the way a security engineer treats threat modeling: as a routine, structured design practice, not an afterthought bolted on after a public incident. Concretely this means asking, before shipping: who could access this capability besides the intended user; what is the worst plausible use of it in the hands of a malicious or merely careless actor; and what technical controls (rate limiting, access logging, output watermarking, use-case restrictions in terms of service) reduce that risk without eliminating the beneficial use case. None of these controls make misuse impossible, but their absence is itself a design choice, and one this deck asks you to make deliberately rather than by default. This completes the four failure families — shift, loops, edges, and misuse — and the final two slides turn them into a practical checklist you can apply directly to a project.
-->

---
glowSeed: 1038
---

# A Human-Centered Deployment Checklist

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Affected people</div>
<div class="text-sm leading-relaxed opacity-90">Who bears the consequences of an error, and did anyone from that group have input into the system's design or evaluation criteria?</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Error costs</div>
<div class="text-sm leading-relaxed opacity-90">Who pays for a false positive versus a false negative, and are those costs symmetric? (Recall precision/recall tradeoffs from model evaluation — the "right" operating point is a value judgment, not a math problem.)</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Monitoring</div>
<div class="text-sm leading-relaxed opacity-90">How will distribution shift and feedback-loop amplification be detected <em>after</em> launch, not just validated once before it?</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Appeal</div>
<div class="text-sm leading-relaxed opacity-90">Can a person contest a decision and obtain a human review before consequences become irreversible (denial of a loan, a flagged account, a medical triage decision)?</div>
</div>
</div>

<!--
This checklist is meant to be used literally, on a real project, not admired abstractly. "Affected people" forces you to separate the user of a system (who benefits from convenience) from the subject of a system (who may bear the risk without ever consenting to it) — in a hiring-screening model, the affected person is the rejected applicant, not the recruiter using the dashboard. "Error costs" connects directly back to the precision/recall and confusion-matrix material from model evaluation: choosing a classification threshold is not a purely technical decision once you recognize that a false negative in a cancer screening model and a false positive in a spam filter have wildly different real-world costs, and that those costs often fall on different people than the ones setting the threshold.

"Monitoring" operationalizes the distribution-shift and feedback-loop material from earlier in this deck: a model that passed validation needs a live comparison between its predictions and eventual real-world outcomes, tracked over time, with alerting when the gap grows — this is the technical leakage/imbalance checklist from model evaluation extended into production. "Appeal" is the practical, human safety net underneath everything else: because no monitoring system catches every failure instantly, a deployed decision system needs a path for an individual to say "this was wrong about me" and get a human to look, especially before a decision becomes practically irreversible. Combine all four questions before every deployment, not only for systems that feel obviously high-stakes — the questions are cheap to ask and expensive to have skipped.
-->

---
glowSeed: 1039
---

# Failure-Mode Thinking

<div class="mt-4"><div class="grid grid-cols-4 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Shift</div>
<div class="text-sm leading-relaxed opacity-90">The world changes; the model's guarantees do not automatically transfer.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Loops</div>
<div class="text-sm leading-relaxed opacity-90">Predictions change the world, and the next model learns from that changed world.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Edges</div>
<div class="text-sm leading-relaxed opacity-90">Adversarial and out-of-distribution inputs get confidently wrong answers.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Misuse</div>
<div class="text-sm leading-relaxed opacity-90">The same capability can serve or harm depending only on who deploys it and how.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: fairness, bias, and interpretability — asking what a model does, and to whom.</div>

<!--
The goal of this deck was never to memorize four named failure categories — it was to build a repeatable habit: before any system ships, ask "how could this fail once it leaves the validation environment, and who would that hurt?" The four families here are not exhaustive, but they cover the most common and best-documented real-world patterns: distribution shift (Zillow), feedback loops (predictive policing), confidently wrong edge cases (adversarial stop signs, OOD medical inputs), and dual-use misuse (facial recognition). Each connects back to a concrete idea from earlier in the course — the i.i.d. assumption behind ERM, precision/recall tradeoffs, and the limits of a single train/test split — extended into a deployment setting where the stakes are no longer just an accuracy number.

The next deck asks a related but distinct question: not just "can this fail," but "does this system, even when it's performing exactly as validated, treat people fairly, and can anyone understand why it made a particular decision?" Fairness, bias, and interpretability pick up immediately where this deck's "affected people" and "appeal" checklist items left off, giving you the formal vocabulary and metrics to reason about those questions rigorously rather than just intuitively.
-->
