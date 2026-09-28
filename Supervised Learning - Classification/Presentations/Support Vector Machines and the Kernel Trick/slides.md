---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Support Vector Machines and the Kernel Trick'
info: |
  ## Support Vector Machines and the Kernel Trick
  Maximum-margin classification and implicit nonlinear feature spaces.
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
glowSeed: 481
---

# Support Vector Machines

### Maximum margins and the kernel trick

<div class="pt-5 opacity-80 text-lg">Supervised Learning · Classification</div>

<svg role="img" aria-label="Two classes separated by a maximum margin street with circled support vectors" viewBox="0 0 760 260" class="w-full max-w-3xl mx-auto mt-7">
  <path d="M235 250 L450 10" stroke="#60a5fa" stroke-width="3" stroke-dasharray="8 6"/><path d="M315 250 L530 10" stroke="#f8fafc" stroke-width="5"/><path d="M395 250 L610 10" stroke="#fb923c" stroke-width="3" stroke-dasharray="8 6"/>
  <path d="M235 250 L450 10 L610 10 L395 250 Z" fill="#0f766e22"/>
  <g fill="#60a5fa"><circle cx="175" cy="65" r="8"/><circle cx="245" cy="110" r="8"/><circle cx="315" cy="160" r="8"/><circle cx="375" cy="205" r="8"/></g>
  <g fill="#fb923c"><circle cx="470" cy="55" r="8"/><circle cx="535" cy="105" r="8"/><circle cx="585" cy="165" r="8"/><circle cx="640" cy="210" r="8"/></g>
  <circle cx="315" cy="160" r="17" fill="none" stroke="#f8fafc" stroke-width="3"/><circle cx="535" cy="105" r="17" fill="none" stroke="#f8fafc" stroke-width="3"/>
</svg>

<!--
Ask a genuinely new question that neither logistic regression nor decision trees asked: among all the hyperplanes that separate two classes, which one is best? Logistic regression finds a boundary implicitly, as a byproduct of maximizing likelihood; a decision tree finds axis-aligned splits by greedy impurity reduction. SVM asks the geometric question directly and answers it directly: choose the separating hyperplane with the most breathing room on both sides — the maximum margin — because that boundary should be the most robust to small perturbations or new data points near the class boundary.

Roadmap for today: why maximum margin is the right criterion, the hard-margin optimization problem and its solution's dependence only on "support vectors," soft margins for data that is not perfectly separable, the hinge loss that connects SVMs back to the general empirical-risk-minimization framework, the dual formulation, and the kernel trick that lets SVMs draw nonlinear boundaries without ever explicitly constructing a high-dimensional feature map. Contrast this geometric, margin-based optimization with logistic regression's probabilistic maximum-likelihood optimization — two very different justifications that often produce visually similar decision boundaries.
-->

---
glowSeed: 482
---

# Does the Drug Work?

<div class="text-lg opacity-85 mt-1">Each patient got one dose. Afterwards we recorded whether the drug was <span class="text-sky-400 font-bold">not effective</span> or <span class="text-orange-400 font-bold">effective</span>.</div>

<svg role="img" aria-label="Dosage number line: a cluster of ineffective patients at low doses, a cluster of effective patients at high doses, a wide gap between them, and a threshold halfway through the gap" viewBox="0 0 920 300" class="w-full mt-4">
  <!-- predicted regions (appear with the threshold) -->
  <g v-click="1">
    <rect x="60" y="70" width="392" height="140" rx="6" fill="#60a5fa14"/>
    <rect x="452" y="70" width="408" height="140" rx="6" fill="#fb923c14"/>
    <text x="256" y="92" text-anchor="middle" fill="#93c5fd" style="font-size:15px">predict: not effective</text>
    <text x="656" y="92" text-anchor="middle" fill="#fdba74" style="font-size:15px">predict: effective</text>
  </g>
  <!-- number line -->
  <line x1="50" y1="150" x2="878" y2="150" stroke="#94a3b8" stroke-width="3"/>
  <polygon points="878,143 892,150 878,157" fill="#94a3b8"/>
  <g stroke="#94a3b8" stroke-width="2">
    <line x1="60" y1="143" x2="60" y2="157"/><line x1="140" y1="143" x2="140" y2="157"/><line x1="220" y1="143" x2="220" y2="157"/><line x1="300" y1="143" x2="300" y2="157"/><line x1="380" y1="143" x2="380" y2="157"/><line x1="460" y1="143" x2="460" y2="157"/><line x1="540" y1="143" x2="540" y2="157"/><line x1="620" y1="143" x2="620" y2="157"/><line x1="700" y1="143" x2="700" y2="157"/><line x1="780" y1="143" x2="780" y2="157"/><line x1="860" y1="143" x2="860" y2="157"/>
  </g>
  <g fill="#94a3b8" style="font-size:14px" text-anchor="middle">
    <text x="60" y="180">0</text><text x="140" y="180">10</text><text x="220" y="180">20</text><text x="300" y="180">30</text><text x="380" y="180">40</text><text x="460" y="180">50</text><text x="540" y="180">60</text><text x="620" y="180">70</text><text x="700" y="180">80</text><text x="780" y="180">90</text><text x="860" y="180">100</text>
  </g>
  <text x="878" y="205" text-anchor="end" fill="#cbd5e1" style="font-size:16px">dosage (mg)</text>
  <!-- observed patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="124" cy="150" r="11"/><circle cx="156" cy="150" r="11"/><circle cx="196" cy="150" r="11"/><circle cx="228" cy="150" r="11"/><circle cx="276" cy="150" r="11"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="628" cy="150" r="11"/><circle cx="668" cy="150" r="11"/><circle cx="700" cy="150" r="11"/><circle cx="740" cy="150" r="11"/><circle cx="788" cy="150" r="11"/></g>
  <!-- threshold halfway through the gap -->
  <g v-click="1">
    <line x1="452" y1="45" x2="452" y2="215" stroke="#f8fafc" stroke-width="4"/>
    <text x="452" y="34" text-anchor="middle" fill="#f8fafc" style="font-size:16px" font-weight="bold">threshold = 49 mg</text>
    <g stroke="#cbd5e1" stroke-width="1.5">
      <line x1="278" y1="122" x2="448" y2="122"/><line x1="456" y1="122" x2="626" y2="122"/>
      <line x1="278" y1="116" x2="278" y2="128"/><line x1="626" y1="116" x2="626" y2="128"/>
    </g>
    <text x="364" y="114" text-anchor="middle" fill="#cbd5e1" style="font-size:13px">22 mg</text>
    <text x="540" y="114" text-anchor="middle" fill="#cbd5e1" style="font-size:13px">22 mg</text>
  </g>
  <!-- a new patient arrives -->
  <g v-click="2">
    <circle cx="380" cy="150" r="11" fill="none" stroke="#f8fafc" stroke-width="3" stroke-dasharray="4 3"/>
    <text x="380" y="276" text-anchor="middle" fill="#f8fafc" style="font-size:15px">new patient: 40 mg</text>
    <line x1="380" y1="258" x2="380" y2="168" stroke="#f8fafc" stroke-width="1.5" stroke-dasharray="3 3"/>
  </g>
  <g v-click="3">
    <circle cx="380" cy="150" r="11" fill="#60a5fa" stroke="#f8fafc" stroke-width="3"/>
    <text x="470" y="276" fill="#93c5fd" style="font-size:15px">→ left of threshold: not effective</text>
  </g>
</svg>

<div v-click="1" class="mt-2 text-center" border="2 solid white/10" bg="white/5" rounded-lg p-3>
Put the threshold <strong>halfway between the closest points of each group</strong>: left of it → not effective, right of it → effective.
</div>

<!--
Start with the simplest classification problem imaginable, so the geometric idea behind SVMs is visible before any math appears. We ran a small trial: each patient received a single dose of a drug, and afterwards we recorded one of two outcomes — the drug either worked (orange) or did not (blue). There is only one feature, dosage, so every patient is just a point on a number line. Ask the room: looking at this picture, where would you draw the line between "not effective" and "effective"? Almost everyone will point somewhere in the wide empty stretch between 27 mg and 71 mg.

Click to reveal the threshold. A natural, defensible choice is to put it exactly halfway between the closest point of each group — the most effective-looking ineffective patient at 27 mg and the least effective-looking effective patient at 71 mg — which lands at 49 mg, leaving 22 mg of breathing room on each side. That single number is our entire classifier: anything to the left is predicted "not effective," anything to the right is predicted "effective."

Click again to bring in a new patient at 40 mg whose outcome we do not know yet, then click once more to classify them: 40 is to the left of 49, so we predict "not effective." Point out that this feels right — 40 mg is much closer to the group of patients for whom the drug failed. Keep this new patient in mind. The next slide explains why "halfway" is the right choice and gives this rule its name; the slide after that shows how fragile it actually is.
-->

---
glowSeed: 482.2
---

# Why Halfway? The Maximal Margin Classifier

<div class="text-lg opacity-85 mt-1"><strong>Margin</strong> = distance from the threshold to the closest observation. Which threshold maximizes it?</div>

<svg role="img" aria-label="Dosage number line comparing thresholds: at 33 mg or 65 mg the margin is only 6 mg, while the halfway threshold at 49 mg gives the largest margin of 22 mg on each side" viewBox="0 0 920 300" class="w-full mt-4">
  <!-- maximal margin band (final reveal) -->
  <g v-click="3">
    <rect x="276" y="60" width="352" height="150" rx="4" fill="#2dd4bf1f"/>
    <line x1="276" y1="60" x2="276" y2="210" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <line x1="628" y1="60" x2="628" y2="210" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
  </g>
  <!-- number line -->
  <line x1="50" y1="150" x2="878" y2="150" stroke="#94a3b8" stroke-width="3"/>
  <polygon points="878,143 892,150 878,157" fill="#94a3b8"/>
  <g stroke="#94a3b8" stroke-width="2">
    <line x1="60" y1="143" x2="60" y2="157"/><line x1="140" y1="143" x2="140" y2="157"/><line x1="220" y1="143" x2="220" y2="157"/><line x1="300" y1="143" x2="300" y2="157"/><line x1="380" y1="143" x2="380" y2="157"/><line x1="460" y1="143" x2="460" y2="157"/><line x1="540" y1="143" x2="540" y2="157"/><line x1="620" y1="143" x2="620" y2="157"/><line x1="700" y1="143" x2="700" y2="157"/><line x1="780" y1="143" x2="780" y2="157"/><line x1="860" y1="143" x2="860" y2="157"/>
  </g>
  <g fill="#94a3b8" style="font-size:14px" text-anchor="middle">
    <text x="60" y="180">0</text><text x="140" y="180">10</text><text x="220" y="180">20</text><text x="300" y="180">30</text><text x="380" y="180">40</text><text x="460" y="180">50</text><text x="540" y="180">60</text><text x="620" y="180">70</text><text x="700" y="180">80</text><text x="780" y="180">90</text><text x="860" y="180">100</text>
  </g>
  <text x="878" y="205" text-anchor="end" fill="#cbd5e1" style="font-size:16px">dosage (mg)</text>
  <!-- observed patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="124" cy="150" r="11"/><circle cx="156" cy="150" r="11"/><circle cx="196" cy="150" r="11"/><circle cx="228" cy="150" r="11"/><circle cx="276" cy="150" r="11"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="628" cy="150" r="11"/><circle cx="668" cy="150" r="11"/><circle cx="700" cy="150" r="11"/><circle cx="740" cy="150" r="11"/><circle cx="788" cy="150" r="11"/></g>
  <!-- candidate A: too close to the ineffective group -->
  <g v-click="[1,3]">
    <line x1="324" y1="45" x2="324" y2="215" stroke="#f8fafc" stroke-width="3"/>
    <text x="318" y="34" text-anchor="end" fill="#f8fafc" style="font-size:15px">try 33 mg</text>
    <g stroke="#f9a8d4" stroke-width="1.5"><line x1="278" y1="122" x2="322" y2="122"/><line x1="278" y1="116" x2="278" y2="128"/><line x1="322" y1="116" x2="322" y2="128"/></g>
    <text x="268" y="118" text-anchor="end" fill="#f9a8d4" style="font-size:13px">margin = 6 mg</text>
  </g>
  <!-- candidate B: too close to the effective group -->
  <g v-click="[2,3]">
    <line x1="580" y1="45" x2="580" y2="215" stroke="#f8fafc" stroke-width="3"/>
    <text x="586" y="34" fill="#f8fafc" style="font-size:15px">try 65 mg</text>
    <g stroke="#f9a8d4" stroke-width="1.5"><line x1="582" y1="122" x2="626" y2="122"/><line x1="582" y1="116" x2="582" y2="128"/><line x1="626" y1="116" x2="626" y2="128"/></g>
    <text x="636" y="118" fill="#f9a8d4" style="font-size:13px">margin = 6 mg</text>
  </g>
  <!-- the maximal margin threshold -->
  <g v-click="3">
    <line x1="452" y1="45" x2="452" y2="215" stroke="#f8fafc" stroke-width="4"/>
    <text x="452" y="34" text-anchor="middle" fill="#f8fafc" style="font-size:16px" font-weight="bold">threshold = 49 mg</text>
    <g stroke="#5eead4" stroke-width="1.5">
      <line x1="278" y1="122" x2="448" y2="122"/><line x1="456" y1="122" x2="626" y2="122"/>
      <line x1="278" y1="116" x2="278" y2="128"/><line x1="626" y1="116" x2="626" y2="128"/>
    </g>
    <text x="364" y="114" text-anchor="middle" fill="#5eead4" style="font-size:13px">22 mg</text>
    <text x="540" y="114" text-anchor="middle" fill="#5eead4" style="font-size:13px">22 mg</text>
    <text x="452" y="250" text-anchor="middle" fill="#5eead4" style="font-size:16px" font-weight="bold">largest possible margin</text>
  </g>
</svg>

<div v-click="4" class="mt-1 text-center" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
Choosing the threshold that gives the <strong>largest margin</strong> and classifying new points by which side they fall on is called a <strong>Maximal Margin Classifier</strong>.
</div>

<!--
The previous slide put the threshold "halfway between the closest points" and it felt natural, but it is worth asking why halfway is the right choice. Introduce one word first: the margin, the distance between the threshold and the closest observation to it, from either class. It is the buffer we have before a point would land on the wrong side.

Click to try a threshold at 33 mg. It separates the training data perfectly — every blue patient on the left, every orange patient on the right — but the closest point, the ineffective patient at 27 mg, is only 6 mg away. Click again to try 65 mg: also a perfect split of the training data, but now the effective patient at 71 mg is only 6 mg away. Both are valid; both leave very little room for error. A new ineffective patient at 35 mg would be misclassified by the first threshold, and a new effective patient at 63 mg by the second.

Click to show the halfway threshold at 49 mg. Moving the threshold toward either group shrinks the distance to that group's closest point, so the best we can do is sit exactly in the middle of the gap — 22 mg from the closest point on each side. That is the largest possible margin for this data, and the shaded band shows the full empty gap between the classes that the threshold is protecting.

Click to name the idea: when we choose the threshold that maximizes the margin and then classify new observations according to which side of it they fall on, we are using a maximal margin classifier. Note that only the two closest points — 27 mg and 71 mg — determine where the threshold goes; the other eight patients could move further away without changing anything. That observation is both the strength of this approach and, as the next slide shows, its biggest weakness.
-->

---
glowSeed: 482.5
---

# One Noisy Patient Moves Everything

<div class="text-lg opacity-85 mt-1">Same trial, same maximal margin classifier — but one patient responded at an unusually low dose.</div>

<svg role="img" aria-label="The same dosage number line with an extra effective patient at 31 mg, right next to the ineffective group; the halfway threshold jumps from 49 mg down to 29 mg" viewBox="0 0 920 300" class="w-full mt-4">
  <!-- new predicted regions (appear with the new threshold) -->
  <g v-click="2">
    <rect x="60" y="70" width="232" height="140" rx="6" fill="#60a5fa14"/>
    <rect x="292" y="70" width="568" height="140" rx="6" fill="#fb923c14"/>
    <text x="176" y="92" text-anchor="middle" fill="#93c5fd" style="font-size:15px">predict: not effective</text>
    <text x="576" y="92" text-anchor="middle" fill="#fdba74" style="font-size:15px">predict: effective</text>
  </g>
  <!-- number line -->
  <line x1="50" y1="150" x2="878" y2="150" stroke="#94a3b8" stroke-width="3"/>
  <polygon points="878,143 892,150 878,157" fill="#94a3b8"/>
  <g stroke="#94a3b8" stroke-width="2">
    <line x1="60" y1="143" x2="60" y2="157"/><line x1="140" y1="143" x2="140" y2="157"/><line x1="220" y1="143" x2="220" y2="157"/><line x1="300" y1="143" x2="300" y2="157"/><line x1="380" y1="143" x2="380" y2="157"/><line x1="460" y1="143" x2="460" y2="157"/><line x1="540" y1="143" x2="540" y2="157"/><line x1="620" y1="143" x2="620" y2="157"/><line x1="700" y1="143" x2="700" y2="157"/><line x1="780" y1="143" x2="780" y2="157"/><line x1="860" y1="143" x2="860" y2="157"/>
  </g>
  <g fill="#94a3b8" style="font-size:14px" text-anchor="middle">
    <text x="60" y="180">0</text><text x="140" y="180">10</text><text x="220" y="180">20</text><text x="300" y="180">30</text><text x="380" y="180">40</text><text x="460" y="180">50</text><text x="540" y="180">60</text><text x="620" y="180">70</text><text x="700" y="180">80</text><text x="780" y="180">90</text><text x="860" y="180">100</text>
  </g>
  <text x="878" y="205" text-anchor="end" fill="#cbd5e1" style="font-size:16px">dosage (mg)</text>
  <!-- old threshold: solid until the new one takes over, then a faint ghost -->
  <g v-click.hide="2">
    <line x1="452" y1="45" x2="452" y2="215" stroke="#f8fafc" stroke-width="4"/>
    <text x="452" y="34" text-anchor="middle" fill="#f8fafc" style="font-size:16px" font-weight="bold">threshold = 49 mg</text>
  </g>
  <g v-click="2">
    <line x1="452" y1="45" x2="452" y2="215" stroke="#f8fafc" stroke-width="2" stroke-dasharray="6 5" opacity="0.35"/>
    <text x="460" y="34" fill="#f8fafc" style="font-size:14px" opacity="0.45">old: 49 mg</text>
  </g>
  <!-- observed patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="124" cy="150" r="11"/><circle cx="156" cy="150" r="11"/><circle cx="196" cy="150" r="11"/><circle cx="228" cy="150" r="11"/><circle cx="276" cy="150" r="11"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="628" cy="150" r="11"/><circle cx="668" cy="150" r="11"/><circle cx="700" cy="150" r="11"/><circle cx="740" cy="150" r="11"/><circle cx="788" cy="150" r="11"/></g>
  <!-- the noisy effective patient -->
  <g v-click="1">
    <circle cx="308" cy="150" r="19" fill="none" stroke="#fb923c" stroke-width="2" stroke-dasharray="4 3"/>
    <circle cx="308" cy="150" r="11" fill="#fb923c" stroke="#0b1220" stroke-width="2"/>
    <line x1="308" y1="258" x2="308" y2="171" stroke="#fdba74" stroke-width="1.5" stroke-dasharray="3 3"/>
    <text x="308" y="276" text-anchor="middle" fill="#fdba74" style="font-size:15px">noisy patient: effective at 31 mg</text>
  </g>
  <!-- new threshold squeezed against the ineffective group -->
  <g v-click="2">
    <line x1="292" y1="45" x2="292" y2="215" stroke="#f8fafc" stroke-width="4"/>
    <text x="286" y="34" text-anchor="end" fill="#f8fafc" style="font-size:16px" font-weight="bold">threshold = 29 mg</text>
    <line x1="444" y1="56" x2="304" y2="56" stroke="#f472b6" stroke-width="2.5"/>
    <polygon points="304,50 292,56 304,62" fill="#f472b6"/>
    <text x="458" y="61" fill="#f9a8d4" style="font-size:14px">dragged 20 mg left</text>
  </g>
  <!-- margin collapses, and the new patient flips -->
  <g v-click="3">
    <g stroke="#f9a8d4" stroke-width="1.5"><line x1="276" y1="122" x2="308" y2="122"/><line x1="276" y1="116" x2="276" y2="128"/><line x1="308" y1="116" x2="308" y2="128"/></g>
    <text x="258" y="118" text-anchor="end" fill="#f9a8d4" style="font-size:13px">only 2 mg each side</text>
    <circle cx="380" cy="150" r="11" fill="#fb923c" stroke="#f8fafc" stroke-width="3"/>
    <line x1="380" y1="198" x2="380" y2="168" stroke="#f8fafc" stroke-width="1.5" stroke-dasharray="3 3"/>
    <text x="388" y="212" fill="#f8fafc" style="font-size:14px">40 mg patient now → effective</text>
  </g>
</svg>

<div class="grid grid-cols-2 gap-4 mt-1 text-sm">
<div v-click="3" border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3>The threshold now <strong>hugs the ineffective group</strong>. The wide empty gap between the classes is ignored.</div>
<div v-click="4" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>The weakness of the <strong>maximal margin classifier</strong>: it is <strong>extremely sensitive to outliers</strong>. Can we choose a threshold that tolerates a few noisy points?</div>
</div>

<!--
Replay the exact same trial with one extra patient: someone who responded to the drug at only 31 mg (click to reveal). Maybe they had an unusually strong reaction, maybe the dose was recorded wrong, maybe the outcome was misjudged — for classification purposes it does not matter why. It is a noisy observation that sits much closer to the ineffective group than to the rest of the effective group.

Click to refit the maximal margin classifier from the previous slide — the threshold that maximizes the margin, halfway between the closest points of each group. The closest effective point is now the noisy one at 31 mg, not the one at 71 mg, so the threshold jumps from 49 mg all the way down to 29 mg. One patient out of eleven dragged the entire decision boundary 20 mg to the left.

Click again to show the consequences. The buffer on each side of the threshold has collapsed from 22 mg to just 2 mg: the boundary is now pressed right up against the ineffective group, completely ignoring the large empty gap between the bulk of the two classes. And look at the 40 mg patient from the first slide — the rule now calls them "effective," even though nearly every piece of evidence (five failures between 8 and 27 mg, successes only from 71 mg upward, with one exception) says they probably would not respond.

End on the question that motivates the rest of the lecture: this is the fundamental weakness of the maximal margin classifier. Because the threshold is determined entirely by the single closest point on each side, it is extremely sensitive to outliers. Is there a way to choose a threshold that still respects the gap between the classes, even when a few observations are noisy? Answering that leads to allowing a few points to violate the margin on purpose — the soft margin at the heart of support vector machines.
-->

---
glowSeed: 482.8
---

# Soft Margins: Allow a Few Mistakes

<div class="text-lg opacity-85 mt-1">Relax the rule: let some observations sit <strong>inside the margin</strong> — or even on the wrong side of the threshold.</div>

<svg role="img" aria-label="The dosage data with the noisy 31 mg patient. A soft margin from 27 to 71 mg with the threshold back at 49 mg lets the noisy patient be misclassified; the points on the margin edges and inside it are circled as support vectors" viewBox="0 18 920 268" class="w-full mt-3">
  <!-- hard-margin threshold from the previous slide, faint -->
  <g v-click.hide="1">
    <line x1="292" y1="45" x2="292" y2="215" stroke="#f8fafc" stroke-width="2" stroke-dasharray="6 5" opacity="0.4"/>
    <text x="286" y="34" text-anchor="end" fill="#f8fafc" style="font-size:14px" opacity="0.5">hard margin: 29 mg</text>
  </g>
  <!-- the soft margin -->
  <g v-click="1">
    <rect x="276" y="60" width="352" height="150" rx="4" fill="#2dd4bf1f"/>
    <line x1="276" y1="60" x2="276" y2="210" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <line x1="628" y1="60" x2="628" y2="210" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <line x1="452" y1="45" x2="452" y2="215" stroke="#f8fafc" stroke-width="4"/>
    <text x="452" y="34" text-anchor="middle" fill="#f8fafc" style="font-size:16px" font-weight="bold">threshold = 49 mg</text>
    <text x="452" y="240" text-anchor="middle" fill="#5eead4" style="font-size:16px" font-weight="bold">soft margin</text>
  </g>
  <!-- number line -->
  <line x1="50" y1="150" x2="878" y2="150" stroke="#94a3b8" stroke-width="3"/>
  <polygon points="878,143 892,150 878,157" fill="#94a3b8"/>
  <g stroke="#94a3b8" stroke-width="2">
    <line x1="60" y1="143" x2="60" y2="157"/><line x1="140" y1="143" x2="140" y2="157"/><line x1="220" y1="143" x2="220" y2="157"/><line x1="300" y1="143" x2="300" y2="157"/><line x1="380" y1="143" x2="380" y2="157"/><line x1="460" y1="143" x2="460" y2="157"/><line x1="540" y1="143" x2="540" y2="157"/><line x1="620" y1="143" x2="620" y2="157"/><line x1="700" y1="143" x2="700" y2="157"/><line x1="780" y1="143" x2="780" y2="157"/><line x1="860" y1="143" x2="860" y2="157"/>
  </g>
  <g fill="#94a3b8" style="font-size:14px" text-anchor="middle">
    <text x="60" y="180">0</text><text x="140" y="180">10</text><text x="220" y="180">20</text><text x="300" y="180">30</text><text x="380" y="180">40</text><text x="460" y="180">50</text><text x="540" y="180">60</text><text x="620" y="180">70</text><text x="700" y="180">80</text><text x="780" y="180">90</text><text x="860" y="180">100</text>
  </g>
  <text x="878" y="205" text-anchor="end" fill="#cbd5e1" style="font-size:16px">dosage (mg)</text>
  <!-- observed patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="124" cy="150" r="11"/><circle cx="156" cy="150" r="11"/><circle cx="196" cy="150" r="11"/><circle cx="228" cy="150" r="11"/><circle cx="276" cy="150" r="11"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="628" cy="150" r="11"/><circle cx="668" cy="150" r="11"/><circle cx="700" cy="150" r="11"/><circle cx="740" cy="150" r="11"/><circle cx="788" cy="150" r="11"/></g>
  <circle cx="308" cy="150" r="11" fill="#fb923c" stroke="#0b1220" stroke-width="2"/>
  <!-- the noisy patient is now allowed to be misclassified -->
  <g v-click="1">
    <line x1="308" y1="258" x2="308" y2="171" stroke="#f9a8d4" stroke-width="1.5" stroke-dasharray="3 3"/>
    <text x="268" y="276" fill="#f9a8d4" style="font-size:15px">31 mg: inside the margin and misclassified — allowed</text>
  </g>
  <!-- support vectors: on the edge of or inside the soft margin -->
  <g v-click="4" fill="none" stroke="#f8fafc" stroke-width="2.5">
    <circle cx="276" cy="150" r="18"/><circle cx="308" cy="150" r="18"/><circle cx="628" cy="150" r="18"/>
  </g>
  <g v-click="4" fill="#f8fafc" style="font-size:14px">
    <text x="266" y="116" text-anchor="end">support vectors</text>
    <text x="638" y="116">support vector</text>
  </g>
</svg>

<div class="grid grid-cols-3 gap-3 mt-1 text-sm leading-snug">
<div v-click="2" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-3 py-2><strong>How soft?</strong> Use <strong>cross validation</strong>: try different amounts of allowed misclassification, keep the best on held-out data.</div>
<div v-click="3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>A soft margin threshold gives a <strong>Soft Margin Classifier</strong>, a.k.a. a <strong>Support Vector Classifier</strong>.</div>
<div v-click="4" border="2 solid white/10" bg="white/5" rounded-lg px-3 py-2><strong>Support vectors</strong>: observations on the edge of and inside the soft margin. They alone set the threshold.</div>
</div>

<!--
The maximal margin classifier failed because it insisted on a margin with no observations inside it and none on the wrong side, so a single noisy patient could drag the threshold wherever it wanted. The fix is to relax that rule. Instead of requiring a perfectly clean margin, we allow some observations to sit inside the margin, and even allow some to be misclassified. A margin that permits these violations is called a soft margin.

Click to show a soft margin for this data. It runs from 27 mg to 71 mg, and the threshold goes back to 49 mg, the middle of the real gap between the two groups. The noisy 31 mg patient now sits inside the margin, on the "not effective" side of the threshold, so it is misclassified, and we accept that on purpose. In exchange, the threshold respects where the bulk of the data actually is. The 40 mg patient from the first slide is predicted "not effective" again, which matches the evidence.

Click to raise the obvious question: how soft should the margin be? We could allow zero violations (the fragile hard margin), one violation, two, or many, and each choice puts the margin and threshold in a different place. There is no rule that tells us the right amount in advance, so we treat it like any other hyperparameter: use cross validation. Try several amounts of allowed misclassification, fit on the training folds, measure accuracy on the held-out folds, and keep whichever soft margin predicts new patients best. This is exactly how we chose k for k-nearest neighbors or the depth of a decision tree.

Click to name the model. When we use a soft margin to decide where the threshold goes, the classifier is called a soft margin classifier, more commonly a support vector classifier.

Click once more to explain where that name comes from. The observations on the edge of the soft margin and inside it (here the ineffective patient at 27 mg, the noisy patient at 31 mg, and the effective patient at 71 mg) are called support vectors. They are the only points that matter: every other patient could move further from the threshold, or be removed, and the threshold would not change.
-->

---
glowSeed: 483
---

# Adding a Second Feature

<div class="grid grid-cols-[2fr_3fr] gap-6 mt-2 items-center">
<div>

Suppose the drug's effect also depends on **age**: older patients need a bigger dose.

<v-clicks>

- Each patient is now a point with two numbers: $X = (x_1, x_2)$
- A dosage-only cutoff can't separate the groups — something is always on the wrong side
- Tilt the threshold and it separates them cleanly: **the threshold is now a line**

</v-clicks>

</div>

<svg role="img" aria-label="Scatter plot of dosage versus age. A vertical dosage-only cutoff misclassifies two patients, while a tilted line separates the ineffective and effective patients" viewBox="0 0 500 420" class="w-full">
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- dosage-only cutoff -->
  <g v-click="[2,3]">
    <line x1="250" y1="30" x2="250" y2="360" stroke="#f8fafc" stroke-width="2.5" stroke-dasharray="7 5"/>
    <text x="256" y="26" fill="#f8fafc" style="font-size:13px">dosage-only cutoff</text>
    <g fill="none" stroke="#f472b6" stroke-width="2.5"><circle cx="260" cy="60" r="16"/><circle cx="240" cy="320" r="16"/></g>
    <text x="220" y="352" text-anchor="middle" fill="#f9a8d4" style="font-size:13px">wrong side</text>
    <text x="282" y="65" fill="#f9a8d4" style="font-size:13px">wrong side</text>
  </g>
  <!-- tilted threshold -->
  <g v-click="3">
    <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
    <text x="341.6" y="88" dy="-7" transform="rotate(-51.3 341.6 88)" text-anchor="end" fill="#f8fafc" style="font-size:14px">threshold is a line</text>
  </g>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
</svg>
</div>

<!--
So far every patient has been a single number, their dose, so the whole problem lived on a number line and the threshold was a single point. Real problems almost always have more than one feature. Suppose the trial also recorded each patient's age, and it turns out older patients need a larger dose before the drug works. Plot each patient with dosage on the horizontal axis and age on the vertical axis: blue patients (not effective) sit toward the upper left — low dose for their age — and orange patients (effective) toward the lower right.

Click: each patient is now described by two numbers, X = (x1, x2), dosage and age. Nothing else about the problem has changed; we still want a rule that says "effective" or "not effective" for a new patient.

Click: try the old approach and ignore age, putting a single vertical cutoff on dosage. No matter where you put it, some patients land on the wrong side — here an older ineffective patient at a fairly high dose and a younger effective patient at a fairly low dose. Dosage alone is not enough information.

Click: tilt the threshold. A slanted line separates the two groups perfectly, because it accounts for both features at once: the older the patient, the higher the dose has to be before we predict "effective." In two dimensions the threshold is no longer a point — it is a line. The next slide writes down that line.
-->

---
glowSeed: 483.5
---

# The Threshold Becomes $w\cdot X+b=0$

<div class="grid grid-cols-[2fr_3fr] gap-6 mt-1 items-center">
<div class="text-sm">

<div border="2 solid white/10" bg="white/5" rounded-lg px-3 py-2>

**1 feature:** $x - 49 = 0$ &nbsp;(threshold at 49 mg)

</div>

<div v-click="1" class="mt-3" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-2>

**2 features:** $w_1x_1 + w_2x_2 + b = 0$

$$w\cdot X + b = 0$$

</div>

<div v-click="2" class="mt-3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>

**Classify** by the sign of the score $w\cdot X+b$:
positive → effective, negative → not effective

</div>

<div v-click="3" class="mt-3 opacity-90">

$w$ is perpendicular to the line and sets its **tilt**. $b$ slides the line without turning it.

</div>
</div>

<svg role="img" aria-label="The dosage versus age plot split by the line w dot X plus b equals zero. The ineffective side has a negative score, the effective side a positive score, and the vector w points perpendicular to the line toward the effective side" viewBox="0 0 500 420" class="w-full">
  <g v-click="2">
    <polygon points="60,40 380,40 124,360 60,360" fill="#60a5fa14"/>
    <polygon points="380,40 480,40 480,360 124,360" fill="#fb923c14"/>
    <text x="72" y="58" fill="#93c5fd" style="font-size:14px">w·X + b &lt; 0</text>
    <text x="472" y="348" text-anchor="end" fill="#fdba74" style="font-size:14px">w·X + b &gt; 0</text>
  </g>
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
  <g v-click="1">
    <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
    <text x="181.6" y="288" dy="-7" transform="rotate(-51.3 181.6 288)" text-anchor="start" fill="#f8fafc" style="font-size:15px">w·X + b = 0</text>
  </g>
  <g v-click="3">
    <line x1="300" y1="140" x2="342.9" y2="174.4" stroke="#f472b6" stroke-width="3"/>
    <polygon points="342.9,174.4 339.3,164.5 332.5,173.0" fill="#f472b6"/>
    <text x="350.9" y="168.4" fill="#f9a8d4" style="font-size:18px" font-weight="bold">w</text>
    <line x1="292" y1="360" x2="480" y2="125" stroke="#f8fafc" stroke-width="2" stroke-dasharray="5 5" opacity="0.35"/>
    <text x="471.2" y="136" dy="-7" transform="rotate(-51.3 471.2 136)" text-anchor="end" fill="#cbd5e1" style="font-size:12px">change b → line slides</text>
  </g>
</svg>
</div>

<!--
Connect back to one dimension first. Our threshold at 49 mg is the set of doses where x − 49 = 0: to the right of it the expression is positive (effective), to the left it is negative (not effective). That is already the form w·x + b = 0, with w = 1 and b = −49.

Click: with two features, the same idea becomes w1·x1 + w2·x2 + b = 0. Collect the two weights into a vector w = (w1, w2) and the patient's features into X = (x1, x2), and the sum w1·x1 + w2·x2 is just the dot product w·X. So the threshold is the set of points where w·X + b = 0 — which, in two dimensions, is a straight line.

Click: to classify a patient, plug their dosage and age into w·X + b and look at the sign. Everyone on one side of the line gets a positive score (effective); everyone on the other side gets a negative score (not effective); points exactly on the line score zero. This is the same "which side of the threshold are you on" rule from the number line, just computed with a dot product.

Click: give w and b a picture. The vector w always points perpendicular to the line, toward the positive side, so changing w rotates the line and sets its tilt. Changing b, with w held fixed, slides the line parallel to itself without turning it — the dashed line shows the same w with a different b. Keep the math light: the only takeaway students need is that w controls the direction and b controls the position.
-->

---
glowSeed: 484
---

# Point → Line → Plane → Hyperplane

<svg role="img" aria-label="Three panels: with one feature the threshold is a point on a number line, with two features it is a line in a plane, with three features it is a flat plane in 3D space" viewBox="0 0 900 300" class="w-full mt-2">
  <!-- 1 feature -->
  <g>
    <text x="150" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:18px" font-weight="bold">1 feature</text>
    <line x1="20" y1="160" x2="280" y2="160" stroke="#94a3b8" stroke-width="2.5"/>
    <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="40" cy="160" r="8"/><circle cx="62" cy="160" r="8"/><circle cx="90" cy="160" r="8"/><circle cx="110" cy="160" r="8"/></g>
    <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="190" cy="160" r="8"/><circle cx="215" cy="160" r="8"/><circle cx="238" cy="160" r="8"/><circle cx="262" cy="160" r="8"/></g>
    <line x1="150" y1="120" x2="150" y2="200" stroke="#f8fafc" stroke-width="4"/>
    <text x="150" y="250" text-anchor="middle" fill="#5eead4" style="font-size:16px">threshold = a <tspan font-weight="bold">point</tspan></text>
  </g>
  <!-- 2 features -->
  <g v-click="1">
    <text x="450" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:18px" font-weight="bold">2 features</text>
    <line x1="330" y1="220" x2="580" y2="220" stroke="#94a3b8" stroke-width="2"/><line x1="330" y1="220" x2="330" y2="50" stroke="#94a3b8" stroke-width="2"/>
    <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="355" cy="120" r="7"/><circle cx="380" cy="80" r="7"/><circle cx="360" cy="170" r="7"/><circle cx="410" cy="100" r="7"/><circle cx="390" cy="145" r="7"/></g>
    <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="470" cy="190" r="7"/><circle cx="510" cy="150" r="7"/><circle cx="540" cy="110" r="7"/><circle cx="500" cy="200" r="7"/><circle cx="555" cy="170" r="7"/></g>
    <line x1="380" y1="220" x2="520" y2="55" stroke="#f8fafc" stroke-width="4"/>
    <text x="450" y="250" text-anchor="middle" fill="#5eead4" style="font-size:16px">threshold = a <tspan font-weight="bold">line</tspan></text>
  </g>
  <!-- 3 features -->
  <g v-click="2">
    <text x="750" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:18px" font-weight="bold">3 features</text>
    <g stroke="#94a3b8" stroke-width="2"><line x1="650" y1="210" x2="870" y2="210"/><line x1="650" y1="210" x2="650" y2="50"/><line x1="650" y1="210" x2="720" y2="160"/></g>
    <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="672" cy="90" r="7"/><circle cx="695" cy="60" r="7"/><circle cx="690" cy="140" r="7"/><circle cx="712" cy="175" r="7"/></g>
    <polygon points="720,215 800,160 830,45 750,100" fill="#2dd4bf38" stroke="#5eead4" stroke-width="2.5"/>
    <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="835" cy="175" r="7"/><circle cx="855" cy="120" r="7"/><circle cx="820" cy="200" r="7"/><circle cx="862" cy="70" r="7"/></g>
    <text x="750" y="250" text-anchor="middle" fill="#5eead4" style="font-size:16px">threshold = a <tspan font-weight="bold">plane</tspan></text>
  </g>
</svg>

<div v-click="3" class="text-center mt-1" border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>

With $p$ features, $w\cdot X+b=0$ is a **hyperplane**: a flat boundary with $p-1$ dimensions. We can't draw it, but the equation and the rule are exactly the same.

</div>

<!--
Line up the three cases side by side so students see that nothing conceptually new happens as dimensions increase. With one feature (dosage only), the threshold w·x + b = 0 is a single point on the number line. Click: with two features (dosage and age), the same equation w·X + b = 0 describes a line through the plane. Click: add a third feature — say body weight — and each patient becomes a point in 3D space; now w·X + b = 0 is a flat plane that slices the space in two, with not-effective patients on one side and effective patients on the other.

Click: the pattern continues forever. With p features, w and X both have p entries, and w·X + b = 0 describes a flat boundary with one fewer dimension than the space it lives in: a point in 1D, a line in 2D, a plane in 3D, and in general a hyperplane. We cannot picture a hyperplane in, say, 50 dimensions, but we never need to — the classification rule is still "compute w·X + b and look at the sign," and everything about margins on the next slide carries over unchanged.
-->

---
glowSeed: 484.25
clicks: 4
---

# Scores for Training Points

<div class="grid grid-cols-2 gap-6 mt-1 items-center derivation-layout">
<div class="derivation-copy">

<div v-click="1">

For training point $x_i$, the **raw score** is

$$f(x_i)=w\cdot x_i+b.$$

Its sign determines the predicted class.

</div>

<div v-click="2">

The **true label** is $y_i=+1$ (effective) or $y_i=-1$ (not effective).

</div>

<div v-click="3">

The **label-adjusted score** is

$$m_i=y_i f(x_i)=y_i(w\cdot x_i+b).$$

Correct side: $m_i>0$. Wrong side: $m_i<0$.

For example: $(+1)(+2)=2$ and $(-1)(-2)=2$.

</div>

<div v-click="4">

**Separable:** a boundary exists with all $m_i>0$.

We will rescale so $\min_i m_i=1$.

These scores are neither probabilities nor distances.

</div>
</div>

<svg role="img" aria-label="Training scores: raw score signs on either side of the boundary and true class labels" viewBox="0 0 500 420" class="w-full">
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
  <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
  <text x="380" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:15px" font-weight="bold">0</text>
  <text x="294" y="30" text-anchor="end" fill="#cbd5e1" style="font-size:14px">w·x + b =</text>
<g v-click="1">
<text x="80" y="50" fill="#93c5fd" style="font-size:16px">f(x) &lt; 0</text>
<text x="345" y="285" fill="#fdba74" style="font-size:16px">f(x) &gt; 0</text>
</g>
<g v-click="2">
<text x="80" y="70" fill="#93c5fd" style="font-size:16px">y = −1</text>
<text x="345" y="305" fill="#fdba74" style="font-size:16px">y = +1</text>
</g>
<g v-click="3">
<text x="80" y="90" fill="#5eead4" style="font-size:16px">y f(x) &gt; 0</text>
<text x="345" y="325" fill="#5eead4" style="font-size:16px">y f(x) &gt; 0</text>
</g>
</svg>
</div>

<style>
.derivation-copy { font-size: 17px; line-height: 1.45; }
.derivation-copy p { margin: 0.65em 0; }
.derivation-copy .katex-display { margin: 0.7em 0; font-size: 0.91em; }
</style>

<!--
Click 1: give the expression we already use a name: f(x_i), the raw score for training observation i. Lowercase x_i is the feature vector for observation i, the same kind of vector previously written X. The subscript i indexes patients, not feature coordinates. The sign determines our prediction, while a score of zero means the point is exactly on the boundary. The graph labels the signs on the two sides, not numerical scores for individual dots.

Click 2: distinguish a prediction from the known answer. The true training label y_i comes from the observed outcome. We encode effective as plus one and not effective as minus one. These are class labels, not the raw scores. The graph shows a separator that correctly classifies the pictured patients.

Click 3: multiply the raw score by the true label and call the result m_i, the label-adjusted score, also known as the functional margin. For a positive patient with raw score plus two, the product is plus two. For a negative patient with raw score minus two, the product is also plus two. These numbers are illustrative, not computed values for the plotted points. Both correct predictions now have positive adjusted scores. In contrast, a negative patient with raw score plus two has adjusted score minus two and is misclassified. At the boundary the adjusted score is zero. Ask students to compute the adjusted score for a positive patient whose raw score is minus three.

Click 4: separable means that there exists a boundary putting every training point strictly on its correct side, so all m_i are positive. The smallest m_i is the least positive adjusted score. For fixed w and b in this separable case, it belongs to a nearest training point because geometric distance is m_i divided by the same norm w for everyone. We will derive that distance formula next.

Preview normalization without assuming it: the raw score scale is arbitrary. Multiplying both w and b by a positive constant changes all raw and adjusted scores by that factor, but leaves the boundary and predictions unchanged. Later we choose the factor that makes the minimum m_i equal one. One is a convenient score convention, not a probability or a physical distance. For now, students only need to remember the two definitions f(x_i) and m_i.
-->

---
glowSeed: 484.50
clicks: 5
---

# The Shortest Path to a Hyperplane

<div class="grid grid-cols-2 gap-6 mt-1 items-center derivation-layout">
<div class="derivation-copy">

<div v-click="1">

For $w\ne0$, the decision boundary is $w\cdot x+b=0$.

</div>

<div v-click="2">

Any two points $u,v$ on it satisfy

$$w\cdot(u-v)=0.$$

</div>

<div v-click="3">

So $w$ is **perpendicular** to the hyperplane.

</div>

<div v-click="4">

Let $x_p$ be the closest point on the plane to $x_0$. Moving along the unit normal gives

$$x_0=x_p+r\frac{w}{\|w\|}.$$

</div>

<div v-click="5">

Here $r$ is a **signed distance**; $w/\|w\|$ has length 1.

</div>

</div>

<svg role="img" aria-label="SVM geometry with annotations revealed alongside derivation step 1" viewBox="0 0 500 420" class="w-full">
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
  <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
  <text x="380" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:15px" font-weight="bold">0</text>
  <text x="294" y="30" text-anchor="end" fill="#cbd5e1" style="font-size:14px">w·x + b =</text>
<g v-click="2">
<circle cx="252" cy="200" r="5" fill="#f9a8d4" stroke="#0b1220" stroke-width="2"/><circle cx="300" cy="140" r="5" fill="#f9a8d4" stroke="#0b1220" stroke-width="2"/><line x1="252" y1="200" x2="300" y2="140" stroke="#5eead4" stroke-width="2.5"/><text x="233" y="220" fill="#5eead4" style="font-size:15px" font-weight="bold">u</text><text x="280" y="135" fill="#5eead4" style="font-size:15px" font-weight="bold">v</text>
</g><g v-click="3">
<line x1="284" y1="160" x2="323" y2="191.2" stroke="#f472b6" stroke-width="2.5"/><polygon points="323,191.2 319.8,182.5 313.8,190" fill="#f472b6"/><text x="327" y="183" fill="#f9a8d4" style="font-size:15px" font-weight="bold">w</text>
</g><g v-click="4">
<circle cx="341.6" cy="88" r="5" fill="#f9a8d4" stroke="#0b1220" stroke-width="2"/><circle cx="400" cy="134.72" r="5" fill="#f9a8d4" stroke="#0b1220" stroke-width="2"/><line x1="341.6" y1="88" x2="400" y2="134.72" stroke="#f472b6" stroke-width="2.5"/><text x="319" y="78" fill="#f9a8d4" style="font-size:15px" font-weight="bold">xₚ</text><text x="407" y="125" fill="#f9a8d4" style="font-size:15px" font-weight="bold">x₀</text><text x="364" y="100" fill="#f9a8d4" style="font-size:15px" font-weight="bold">r</text>
</g><g v-click="5">
<text x="348" y="166" fill="#f9a8d4" style="font-size:15px" font-weight="bold">w / ‖w‖</text>
</g>
</svg>
</div>

<style>
.derivation-copy { font-size: 17px; line-height: 1.45; }
.derivation-copy p { margin: 0.65em 0; }
.derivation-copy .katex-display { margin: 0.7em 0; font-size: 0.91em; }
</style>

<!--
Click 1: introduce the zero-score boundary. Click 2: show u and v on it and subtract their equations. Click 3: show the normal w. Click 4: show x_0, its projection x_p, and signed distance r. Click 5: explain the unit normal.

We will derive the margin width rather than simply state it. Use lowercase x for a feature vector, the same quantity labeled X in the graph. First assume w is nonzero, otherwise it does not define a normal direction.

Why is w perpendicular? Both u and v lie on the decision boundary, so w dot u + b = 0 and w dot v + b = 0. Subtract the equations: w dot (u-v) = 0. Every direction along the plane is orthogonal to w.

Now choose any point x_0, not necessarily a training observation. Its closest point on the plane is x_p. The shortest route is perpendicular, so the displacement x_0 minus x_p is a multiple of the unit normal w divided by its norm. The multiplier r has units of distance and may be negative, depending on the side of the plane.

The graph stays as our geometric reference. The pink segment now runs from x_p on the central white line to x_0; its signed length is r. The margin edges will appear when we introduce normalization. The graph is schematic: distances are measured in the feature coordinates used by the model, typically after standardization, not in physical screen pixels.
-->

---
glowSeed: 484.58
clicks: 5
---

# Deriving the Point-to-Plane Distance

<div class="grid grid-cols-2 gap-6 mt-1 items-center derivation-layout">
<div class="derivation-copy">

<div v-click="1">

Since $x_p$ lies on the plane,

$$w\cdot x_p+b=0.$$

</div>

<div v-click="2">

Substitute $x_p=x_0-r\,w/\|w\|$:

$$0=w\cdot\left(x_0-r\frac{w}{\|w\|}\right)+b.$$

</div>

<div v-click="3">

$$0=w\cdot x_0+b-r\frac{w\cdot w}{\|w\|}.$$

</div>

<div v-click="4">

Using $w\cdot w=\|w\|^2$:

$$0=w\cdot x_0+b-r\|w\|.$$

</div>

<div v-click="5">

$$r=\frac{w\cdot x_0+b}{\|w\|},\qquad d=\frac{|w\cdot x_0+b|}{\|w\|}.$$

</div>

</div>

<svg role="img" aria-label="SVM geometry with annotations revealed alongside derivation step 2" viewBox="0 0 500 420" class="w-full">
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
  <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
  <text x="380" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:15px" font-weight="bold">0</text>
  <text x="294" y="30" text-anchor="end" fill="#cbd5e1" style="font-size:14px">w·x + b =</text>
<g v-click="1">
<circle cx="341.6" cy="88" r="5" fill="#f9a8d4" stroke="#0b1220" stroke-width="2"/><circle cx="400" cy="134.72" r="5" fill="#f9a8d4" stroke="#0b1220" stroke-width="2"/><line x1="341.6" y1="88" x2="400" y2="134.72" stroke="#f472b6" stroke-width="2.5"/><text x="319" y="78" fill="#f9a8d4" style="font-size:15px" font-weight="bold">xₚ</text><text x="407" y="125" fill="#f9a8d4" style="font-size:15px" font-weight="bold">x₀</text><text x="364" y="100" fill="#f9a8d4" style="font-size:15px" font-weight="bold">r</text>
</g><g v-click="5">
<text x="285" y="175" fill="#f9a8d4" style="font-size:15px" font-weight="bold">distance d = |r|</text>
</g>
</svg>
</div>

<style>
.derivation-copy { font-size: 17px; line-height: 1.45; }
.derivation-copy p { margin: 0.65em 0; }
.derivation-copy .katex-display { margin: 0.7em 0; font-size: 0.91em; }
</style>

<!--
Click 1: show the projected point and its zero-score equation. Click 2: substitute for x_p. Click 3: distribute the dot product. Click 4: use w dot w = norm squared. Click 5: solve for signed distance and take its absolute value.

Start from the fact that the projected point x_p lies on the boundary, so its score is zero. Substitute the expression for x_p from the previous slide. Distribute the dot product carefully: r is a scalar, and the dot product of w with w is the sum of its squared components, or norm squared.

Cancel one factor of the norm in that fraction. Rearranging leaves r times norm w equal to the score at x_0. Thus the score divided by norm w is signed geometric distance. A positive score means positive signed distance in the direction of w, and a negative score means the opposite side. Absolute value gives the usual nonnegative distance d.

Pause to check: if x_0 already lies on the plane, its score is zero and the formula gives distance zero. Also rescaling both w and b by a positive constant multiplies numerator and denominator equally, so distance to the same plane does not change.
-->

---
glowSeed: 484.66
clicks: 4
---

# Fixing the Scale at $\pm1$

<div class="grid grid-cols-2 gap-6 mt-1 items-center derivation-layout">
<div class="derivation-copy">

<div v-click="1">

Multiplying $w$ and $b$ by the same $c>0$ leaves the decision boundary unchanged:

$$w\cdot x+b=0\iff cw\cdot x+cb=0.$$

</div>

<div v-click="2">

For **separable data**, fix the scale so the smallest **label-adjusted score** is 1:

$$\min_i m_i=\min_i y_i(w\cdot x_i+b)=1.$$

</div>

<div v-click="3">

The margin edges then have scores

$$w\cdot x+b=+1,\qquad w\cdot x+b=-1.$$

</div>

<div v-click="4">

At the hard-margin optimum, the closest points touch these edges.

</div>

</div>

<svg role="img" aria-label="SVM geometry with annotations revealed alongside derivation step 3" viewBox="0 0 500 420" class="w-full">
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
  <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
  <text x="380" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:15px" font-weight="bold">0</text>
  <text x="294" y="30" text-anchor="end" fill="#cbd5e1" style="font-size:14px">w·x + b =</text>
<g v-click="3">
<g>
    <polygon points="60,360 316,40 444,40 188,360" fill="#2dd4bf1f"/>
    <line x1="60" y1="360" x2="316" y2="40" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <line x1="188" y1="360" x2="444" y2="40" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <text x="316" y="30" text-anchor="middle" fill="#5eead4" style="font-size:15px" font-weight="bold">−1</text>
    <text x="444" y="30" text-anchor="middle" fill="#5eead4" style="font-size:15px" font-weight="bold">+1</text>
  </g>
</g><g v-click="4">
<g fill="none" stroke="#f8fafc" stroke-width="2.5"><circle cx="188" cy="200" r="15"/><circle cx="92" cy="320" r="15"/><circle cx="316" cy="200" r="15"/></g>
</g>
</svg>
</div>

<style>
.derivation-copy { font-size: 17px; line-height: 1.45; }
.derivation-copy p { margin: 0.65em 0; }
.derivation-copy .katex-display { margin: 0.7em 0; font-size: 0.91em; }
</style>

<!--
Click 1: explain rescaling. Click 2: recall m_i = y_i f(x_i), then fix its minimum at one. Click 3: reveal the two margin edges at plus and minus one. Click 4: circle the support vectors that touch them.

For this part of the derivation, temporarily return to the separable, hard-margin case. Labels are plus one and minus one. A correctly classified point has positive y_i times its score. Multiplying w and b together by a positive constant preserves the decision boundary and predictions, but changes all raw scores.

For any strict separator on a finite training set, let m be the minimum label-adjusted training score, min_i m_i. Since m is positive, dividing w and b by m makes the minimum signed score exactly one. This removes the arbitrary scaling. At least one training point now touches an edge; at the maximum-margin solution, support points from both classes hold the band in place.

The choices plus one and minus one are a normalization convention, not probabilities and not distances of one unit. We still need to divide by norm w to convert a score into distance.

This qualification matters because we have already introduced soft margins. With soft margins, some support vectors lie inside the band or are misclassified; they do not all have scores exactly plus or minus one. The edge equations remain useful, but violations will be penalized instead of forbidden.
-->

---
glowSeed: 484.74
clicks: 4
---

# From Distance to Margin Width

<div class="grid grid-cols-2 gap-6 mt-1 items-center derivation-layout">
<div class="derivation-copy">

<div v-click="1">

For a point $x_+$ on the positive margin edge,

$$d_+=\frac{|w\cdot x_++b|}{\|w\|}=\frac{1}{\|w\|}.$$

</div>

<div v-click="2">

For a point $x_-$ on the negative edge,

$$d_-=\frac{|-1|}{\|w\|}=\frac{1}{\|w\|}.$$

</div>

<div v-click="3">

The edges are parallel and on opposite sides, so the **full margin width** is

$$M=d_++d_-=\frac{2}{\|w\|}.$$

</div>

<div v-click="4">

Each half has width $1/\|w\|$; the pink arrow spans both halves.

</div>

</div>

<svg role="img" aria-label="SVM geometry with annotations revealed alongside derivation step 4" viewBox="0 0 500 420" class="w-full">
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
  <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
  <text x="380" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:15px" font-weight="bold">0</text>
  <text x="294" y="30" text-anchor="end" fill="#cbd5e1" style="font-size:14px">w·x + b =</text>
<g>
    <polygon points="60,360 316,40 444,40 188,360" fill="#2dd4bf1f"/>
    <line x1="60" y1="360" x2="316" y2="40" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <line x1="188" y1="360" x2="444" y2="40" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <text x="316" y="30" text-anchor="middle" fill="#5eead4" style="font-size:15px" font-weight="bold">−1</text>
    <text x="444" y="30" text-anchor="middle" fill="#5eead4" style="font-size:15px" font-weight="bold">+1</text>
  </g><g v-click="1">
<line x1="341.6" y1="88" x2="380.6" y2="119.2" stroke="#f472b6" stroke-width="2.5"/><text x="394" y="68" fill="#f9a8d4" style="font-size:15px" font-weight="bold">1 / ‖w‖</text>
</g><g v-click="2">
<line x1="302.6" y1="56.8" x2="341.6" y2="88" stroke="#f472b6" stroke-width="2.5"/><text x="240" y="104" fill="#f9a8d4" style="font-size:15px" font-weight="bold">1 / ‖w‖</text>
</g><g v-click="3">
<line x1="302.6" y1="56.8" x2="380.6" y2="119.2" stroke="#f472b6" stroke-width="2.5"/><polygon points="380.6,119.2 377.4,110.5 371.4,118" fill="#f472b6"/><polygon points="302.6,56.8 311.8,58 305.8,65.5" fill="#f472b6"/><text x="340" y="176" fill="#f9a8d4" style="font-size:15px" font-weight="bold">M = 2 / ‖w‖</text>
</g>
</svg>
</div>

<style>
.derivation-copy { font-size: 17px; line-height: 1.45; }
.derivation-copy p { margin: 0.65em 0; }
.derivation-copy .katex-display { margin: 0.7em 0; font-size: 0.91em; }
</style>

<!--
Click 1: reveal the positive half-width. Click 2: reveal the negative half-width. Click 3: join them into the full width. Click 4: reinforce the distinction between half-width and full width.

Apply the distance formula to a point on the plus-one edge. Its numerator is exactly one, so the distance to the central boundary is one over norm w. On the minus-one edge, the signed distance is negative one over norm w, but its absolute distance is the same positive value.

The two hyperplanes are parallel because they share the same normal vector w. Travel along that normal from one edge to the center, then from the center to the other edge. These distances add, giving two over norm w. Point to the full pink arrow in the graph.

Terminology varies: some texts call one over norm w the geometric margin and others call the full gap the margin. Here M explicitly denotes the full width. Either convention leads to the same optimizer because the factor two is constant.

Ask students: after fixing the score scale, what happens to the full width when norm w doubles? It halves. That inverse relationship is the reason for the objective on the next slide.
-->

---
glowSeed: 484.82
clicks: 4
---

# Why Minimize $\tfrac12\|w\|^2$?

<div class="grid grid-cols-2 gap-6 mt-1 items-center derivation-layout">
<div class="derivation-copy">

<div v-click="1">

With the score scale fixed, a smaller $\|w\|$ gives a wider margin:

$$\max_{w,b}\frac{2}{\|w\|}\iff\min_{w,b}\|w\|\iff\min_{w,b}\tfrac12\|w\|^2.$$

</div>

<div v-click="2">

These have the same solution **under the same constraints**:

$$y_i(w\cdot x_i+b)\ge1\quad\text{for every }i.$$

</div>

<div v-click="3">

Squaring preserves the ordering of nonnegative norms. The factor $\tfrac12$ simplifies the derivative:

$$\nabla_w\!\left(\tfrac12\|w\|^2\right)=w.$$

</div>

<div v-click="4">

The constraints prevent shrinking $w$ to zero. Soft margins later allow penalized violations.

</div>

</div>

<svg role="img" aria-label="SVM geometry with annotations revealed alongside derivation step 5" viewBox="0 0 500 420" class="w-full">
  <!-- axes -->
  <line x1="60" y1="360" x2="490" y2="360" stroke="#94a3b8" stroke-width="2"/>
  <line x1="60" y1="360" x2="60" y2="30" stroke="#94a3b8" stroke-width="2"/>
  <g stroke="#94a3b8" stroke-width="2"><line x1="60" y1="360" x2="60" y2="367"/><line x1="160" y1="360" x2="160" y2="367"/><line x1="260" y1="360" x2="260" y2="367"/><line x1="360" y1="360" x2="360" y2="367"/><line x1="460" y1="360" x2="460" y2="367"/><line x1="53" y1="360" x2="60" y2="360"/><line x1="53" y1="280" x2="60" y2="280"/><line x1="53" y1="200" x2="60" y2="200"/><line x1="53" y1="120" x2="60" y2="120"/><line x1="53" y1="40" x2="60" y2="40"/></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="middle"><text x="60" y="384">0</text><text x="160" y="384">25</text><text x="260" y="384">50</text><text x="360" y="384">75</text><text x="460" y="384">100</text></g>
  <g fill="#94a3b8" style="font-size:13px" text-anchor="end"><text x="48" y="364">20</text><text x="48" y="284">35</text><text x="48" y="204">50</text><text x="48" y="124">65</text><text x="48" y="44">80</text></g>
  <text x="275" y="410" text-anchor="middle" fill="#cbd5e1" style="font-size:15px">x₁ = dosage (mg)</text>
  <text x="14" y="200" text-anchor="middle" fill="#cbd5e1" style="font-size:15px" transform="rotate(-90 14 200)">x₂ = age (years)</text>
  <!-- patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="100" cy="280" r="9"/><circle cx="140" cy="220" r="9"/><circle cx="172" cy="140" r="9"/><circle cx="120" cy="120" r="9"/><circle cx="220" cy="80" r="9"/><circle cx="260" cy="60" r="9"/><circle cx="188" cy="200" r="9"/><circle cx="92" cy="320" r="9"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="240" cy="320" r="9"/><circle cx="300" cy="260" r="9"/><circle cx="360" cy="200" r="9"/><circle cx="428" cy="140" r="9"/><circle cx="280" cy="340" r="9"/><circle cx="420" cy="240" r="9"/><circle cx="412" cy="100" r="9"/><circle cx="316" cy="200" r="9"/></g>
  <line x1="124" y1="360" x2="380" y2="40" stroke="#f8fafc" stroke-width="4"/>
  <text x="380" y="30" text-anchor="middle" fill="#f8fafc" style="font-size:15px" font-weight="bold">0</text>
  <text x="294" y="30" text-anchor="end" fill="#cbd5e1" style="font-size:14px">w·x + b =</text>
<g>
    <polygon points="60,360 316,40 444,40 188,360" fill="#2dd4bf1f"/>
    <line x1="60" y1="360" x2="316" y2="40" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <line x1="188" y1="360" x2="444" y2="40" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
    <text x="316" y="30" text-anchor="middle" fill="#5eead4" style="font-size:15px" font-weight="bold">−1</text>
    <text x="444" y="30" text-anchor="middle" fill="#5eead4" style="font-size:15px" font-weight="bold">+1</text>
  </g><g v-click="1">
<line x1="302.6" y1="56.8" x2="380.6" y2="119.2" stroke="#f472b6" stroke-width="2.5"/><polygon points="380.6,119.2 377.4,110.5 371.4,118" fill="#f472b6"/><polygon points="302.6,56.8 311.8,58 305.8,65.5" fill="#f472b6"/><text x="340" y="176" fill="#f9a8d4" style="font-size:15px" font-weight="bold">M = 2 / ‖w‖</text>
</g><g v-click="2">
<g fill="none" stroke="#f8fafc" stroke-width="2.5"><circle cx="188" cy="200" r="15"/><circle cx="92" cy="320" r="15"/><circle cx="316" cy="200" r="15"/></g>
</g>
</svg>
</div>

<style>
.derivation-copy { font-size: 17px; line-height: 1.45; }
.derivation-copy p { margin: 0.65em 0; }
.derivation-copy .katex-display { margin: 0.7em 0; font-size: 0.91em; }
</style>

<!--
Click 1: show the equivalent objectives and full width. Click 2: reveal the constraints and circle the support vectors. Click 3: explain the squared norm and derivative. Click 4: emphasize why the data stop the margin from widening indefinitely.

The first equivalence follows because two divided by a positive number is strictly decreasing in that number. The second follows because squaring is strictly increasing on nonnegative numbers. Multiplying by one half cannot change which feasible parameters minimize the objective. All three optimization problems must use the same normalized feasible set.

The constraints require positive-class scores of at least plus one and negative-class scores of at most minus one. Absolute score at least one alone would not be sufficient: a confidently wrong prediction also has a large absolute score. Multiplication by the true label enforces both the side and the distance requirement.

The squared norm is a smooth convex quadratic, and one half makes its gradient exactly w. Do not interpret this as arbitrary rescaling making a classifier better. Without fixed score constraints, norm w can be made arbitrarily small without changing the separator. The constraints tie the scale to the data. With both classes present, w equal to zero cannot satisfy them, and the distance formula itself is undefined at w equal to zero.

We now have the hard-margin objective. The next slide uses the dosage example to show how the constraint stops w from shrinking too far. Finally, the soft-margin formulation keeps this squared-norm term but adds penalties for violations. In that case the full objective balances width and violations; it does not maximize width alone.
-->

---
glowSeed: 485.5
---

# …Subject to a Constraint

<div class="grid grid-cols-[2fr_3fr] gap-6 mt-1 items-center">
<div class="text-sm">

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-1>

$$\min_{w,b}\ \tfrac12\|w\|^2$$

</div>

<div v-click="1" class="mt-3">

On its own this is silly: the answer is $w=0$. This gives a constant score and no separating hyperplane.

</div>

<div v-click="2" class="mt-3" border="2 solid pink-800" bg="pink-800/20" rounded-lg px-3 py-1>

$$\text{subject to}\quad y_i\,(w\cdot X_i+b)\ \ge\ 1\ \text{ for every patient } i$$

$y_i=+1$ (effective) or $-1$ (not). Every patient must be on the correct side **and outside the margin**.

</div>

<div v-click="3" class="mt-3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>

Shrink $w$ until the margin edges **hit the closest patients**. Those support vectors hold the margin in place.

</div>
</div>

<svg role="img" aria-label="Three number lines with the same threshold: w equal to one fifth gives a narrow valid margin, w equal to one thirty-fifth gives a margin so wide that patients fall inside it, violating the constraint, and w equal to one twenty-second gives the widest margin that keeps every patient outside" viewBox="0 0 560 390" class="w-full">
  <g>
    <text x="20" y="20" fill="#cbd5e1" style="font-size:15px" font-weight="bold">w = 1/5 · margin 10 mg</text>
    <text x="540" y="20" text-anchor="end" fill="#cbd5e1" style="font-size:14px">✓ valid, not the widest</text>
    <rect x="248.8" y="40" width="52.0" height="64" fill="#cbd5e1" opacity="0.14"/>
    <line x1="248.8" y1="40" x2="248.8" y2="104" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 4"/>
    <line x1="300.8" y1="40" x2="300.8" y2="104" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 4"/>
    <line x1="14" y1="72" x2="548" y2="72" stroke="#94a3b8" stroke-width="2"/>
    <line x1="274.8" y1="36" x2="274.8" y2="108" stroke="#f8fafc" stroke-width="3"/>
    <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="61.6" cy="72" r="7"/><circle cx="82.4" cy="72" r="7"/><circle cx="108.4" cy="72" r="7"/><circle cx="129.2" cy="72" r="7"/><circle cx="160.4" cy="72" r="7"/></g>
    <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="389.2" cy="72" r="7"/><circle cx="415.2" cy="72" r="7"/><circle cx="436.0" cy="72" r="7"/><circle cx="462.0" cy="72" r="7"/><circle cx="493.2" cy="72" r="7"/></g>

  </g>
  <g v-click="2">
    <text x="20" y="150" fill="#f472b6" style="font-size:15px" font-weight="bold">w = 1/35 · margin 70 mg</text>
    <text x="540" y="150" text-anchor="end" fill="#f472b6" style="font-size:14px">✗ patients inside the margin</text>
    <rect x="92.8" y="170" width="364.0" height="64" fill="#f472b6" opacity="0.14"/>
    <line x1="92.8" y1="170" x2="92.8" y2="234" stroke="#f472b6" stroke-width="1.5" stroke-dasharray="4 4"/>
    <line x1="456.8" y1="170" x2="456.8" y2="234" stroke="#f472b6" stroke-width="1.5" stroke-dasharray="4 4"/>
    <line x1="14" y1="202" x2="548" y2="202" stroke="#94a3b8" stroke-width="2"/>
    <line x1="274.8" y1="166" x2="274.8" y2="238" stroke="#f8fafc" stroke-width="3"/>
    <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="61.6" cy="202" r="7"/><circle cx="82.4" cy="202" r="7"/><circle cx="108.4" cy="202" r="7"/><circle cx="129.2" cy="202" r="7"/><circle cx="160.4" cy="202" r="7"/></g>
    <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="389.2" cy="202" r="7"/><circle cx="415.2" cy="202" r="7"/><circle cx="436.0" cy="202" r="7"/><circle cx="462.0" cy="202" r="7"/><circle cx="493.2" cy="202" r="7"/></g>
    <circle cx="108.4" cy="202" r="12" fill="none" stroke="#f472b6" stroke-width="2.5"/><circle cx="129.2" cy="202" r="12" fill="none" stroke="#f472b6" stroke-width="2.5"/><circle cx="160.4" cy="202" r="12" fill="none" stroke="#f472b6" stroke-width="2.5"/><circle cx="389.2" cy="202" r="12" fill="none" stroke="#f472b6" stroke-width="2.5"/><circle cx="415.2" cy="202" r="12" fill="none" stroke="#f472b6" stroke-width="2.5"/><circle cx="436.0" cy="202" r="12" fill="none" stroke="#f472b6" stroke-width="2.5"/>
  </g>
  <g v-click="3">
    <text x="20" y="280" fill="#2dd4bf" style="font-size:15px" font-weight="bold">w = 1/22 · margin 44 mg</text>
    <text x="540" y="280" text-anchor="end" fill="#2dd4bf" style="font-size:14px">✓ smallest w that fits</text>
    <rect x="160.4" y="300" width="228.8" height="64" fill="#2dd4bf" opacity="0.14"/>
    <line x1="160.4" y1="300" x2="160.4" y2="364" stroke="#2dd4bf" stroke-width="1.5" stroke-dasharray="4 4"/>
    <line x1="389.2" y1="300" x2="389.2" y2="364" stroke="#2dd4bf" stroke-width="1.5" stroke-dasharray="4 4"/>
    <line x1="14" y1="332" x2="548" y2="332" stroke="#94a3b8" stroke-width="2"/>
    <line x1="274.8" y1="296" x2="274.8" y2="368" stroke="#f8fafc" stroke-width="3"/>
    <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="61.6" cy="332" r="7"/><circle cx="82.4" cy="332" r="7"/><circle cx="108.4" cy="332" r="7"/><circle cx="129.2" cy="332" r="7"/><circle cx="160.4" cy="332" r="7"/></g>
    <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="389.2" cy="332" r="7"/><circle cx="415.2" cy="332" r="7"/><circle cx="436.0" cy="332" r="7"/><circle cx="462.0" cy="332" r="7"/><circle cx="493.2" cy="332" r="7"/></g>

  </g>
</svg>
</div>

<!--
Minimizing ½‖w‖² alone cannot be the whole story. Click: if the only goal were a small w, the optimizer would pick w = 0 — the score would be flat, the distance formula would be undefined, and every patient would get the same score. There is no separating hyperplane. We need a condition that forces the model to actually separate the data.

Start from the top number line, w = 1/5: every patient is on the correct side and outside the 10 mg margin, so this w is allowed — but it is not the widest margin we could get, so the optimizer keeps shrinking w.

Click: this is the constraint. Encode the labels as y_i = +1 for effective and y_i = −1 for not effective. The requirement y_i(w·X_i + b) ≥ 1 says, in words: every effective patient must score at least +1, and every not-effective patient must score at most −1. Multiplying by y_i just folds both cases into one inequality. Geometrically, every patient must be on the correct side of the threshold and outside the margin. The middle number line shows what goes wrong if w shrinks too far, to 1/35: the 70 mg margin swallows the closest patients (circled in pink), so their scores are between −1 and +1 and the constraint is violated. That w is not allowed.

Click: the answer is the balance point. Shrink w as far as possible, stopping at the moment the margin edges touch the closest patients — here w = 1/22 and a 44 mg margin, exactly the maximal margin classifier from the start of the lecture. The patients touching the edges are the support vectors: they are the constraints that are "tight," and they are what stops w from shrinking further. Every other patient's constraint is comfortably satisfied and does not affect the answer.
-->

---
glowSeed: 486
---

# The Full Soft-Margin Problem

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-1 class="text-sm">

$$\min_{w,b,\xi}\ \tfrac12\|w\|^2\ +\ C\sum_i\xi_i\qquad\text{subject to}\qquad y_i\,(w\cdot X_i+b)\ \ge\ 1-\xi_i,\quad \xi_i\ge0$$

</div>

<svg role="img" aria-label="The dosage number line with the noisy effective patient at 31 mg inside the soft margin. An arrow labeled xi shows how far it falls short of the effective side's margin edge at 71 mg" viewBox="0 40 920 180" class="w-full">
  <rect x="276" y="70" width="352" height="140" rx="4" fill="#2dd4bf1f"/>
  <line x1="276" y1="70" x2="276" y2="210" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
  <line x1="628" y1="70" x2="628" y2="210" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="6 5"/>
  <text x="276" y="62" text-anchor="middle" fill="#5eead4" style="font-size:14px">score −1</text>
  <text x="628" y="62" text-anchor="middle" fill="#5eead4" style="font-size:14px">score +1</text>
  <line x1="452" y1="70" x2="452" y2="210" stroke="#f8fafc" stroke-width="4"/>
  <text x="452" y="62" text-anchor="middle" fill="#f8fafc" style="font-size:14px" font-weight="bold">0</text>
  <!-- number line -->
  <line x1="50" y1="150" x2="878" y2="150" stroke="#94a3b8" stroke-width="3"/>
  <polygon points="878,143 892,150 878,157" fill="#94a3b8"/>
  <g stroke="#94a3b8" stroke-width="2">
    <line x1="60" y1="143" x2="60" y2="157"/><line x1="140" y1="143" x2="140" y2="157"/><line x1="220" y1="143" x2="220" y2="157"/><line x1="300" y1="143" x2="300" y2="157"/><line x1="380" y1="143" x2="380" y2="157"/><line x1="460" y1="143" x2="460" y2="157"/><line x1="540" y1="143" x2="540" y2="157"/><line x1="620" y1="143" x2="620" y2="157"/><line x1="700" y1="143" x2="700" y2="157"/><line x1="780" y1="143" x2="780" y2="157"/><line x1="860" y1="143" x2="860" y2="157"/>
  </g>
  <g fill="#94a3b8" style="font-size:14px" text-anchor="middle">
    <text x="60" y="180">0</text><text x="140" y="180">10</text><text x="220" y="180">20</text><text x="300" y="180">30</text><text x="380" y="180">40</text><text x="460" y="180">50</text><text x="540" y="180">60</text><text x="620" y="180">70</text><text x="700" y="180">80</text><text x="780" y="180">90</text><text x="860" y="180">100</text>
  </g>
  <text x="878" y="205" text-anchor="end" fill="#cbd5e1" style="font-size:16px">dosage (mg)</text>
  <!-- observed patients -->
  <g fill="#60a5fa" stroke="#0b1220" stroke-width="2"><circle cx="124" cy="150" r="11"/><circle cx="156" cy="150" r="11"/><circle cx="196" cy="150" r="11"/><circle cx="228" cy="150" r="11"/><circle cx="276" cy="150" r="11"/></g>
  <g fill="#fb923c" stroke="#0b1220" stroke-width="2"><circle cx="628" cy="150" r="11"/><circle cx="668" cy="150" r="11"/><circle cx="700" cy="150" r="11"/><circle cx="740" cy="150" r="11"/><circle cx="788" cy="150" r="11"/></g>
  <circle cx="308" cy="150" r="11" fill="#fb923c" stroke="#0b1220" stroke-width="2"/>
  <g v-click="1">
    <line x1="322" y1="118" x2="616" y2="118" stroke="#f472b6" stroke-width="2.5"/>
    <polygon points="626,118 614,112 614,124" fill="#f472b6"/>
    <circle cx="308" cy="150" r="17" fill="none" stroke="#f472b6" stroke-width="2.5"/>
    <text x="388" y="108" text-anchor="middle" fill="#f9a8d4" style="font-size:18px" font-weight="bold">ξ</text>
  </g>
</svg>

<div class="grid grid-cols-3 gap-3 text-sm leading-snug">
<div v-click="1" border="2 solid pink-800" bg="pink-800/20" rounded-lg px-3 py-2>

**Slack** $\xi_i$: how far patient $i$ falls short of its margin edge. Patients safely outside the margin have $\xi_i=0$.

</div>
<div v-click="2" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-3 py-2>

**C** is the price of slack. Small $C$: wider margin, more violations. Large $C$: narrower margin, fewer. **Cross validation picks C.**

</div>
<div v-click="3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>The problem is <strong>convex</strong>: one best answer, no local minima. Standard solvers find it, e.g. <code>SVC(kernel="linear", C=1)</code>.</div>
</div>

<!--
Put the two pieces together and add the soft margin from earlier in the lecture. The hard constraint y_i(w·X_i + b) ≥ 1 is exactly what made the maximal margin classifier so fragile: a single noisy patient had to be satisfied, no matter what it cost. The soft-margin version relaxes each patient's constraint by an amount ξ_i (xi), called slack, and charges for it.

Click: slack measures how far a patient falls short of its own margin edge. The noisy effective patient at 31 mg should have scored at least +1 — it should be out past the right-hand edge at 71 mg — but it sits deep on the wrong side, so it needs a large ξ. Patients comfortably outside the margin need no slack at all, so ξ_i = 0 for them. A patient inside the margin but on the correct side has 0 < ξ_i < 1; a misclassified patient has ξ_i > 1.

Click: the objective now has two terms pulling against each other. ½‖w‖² still wants the widest possible margin; C·Σξ_i charges a price for every unit of slack. C is the knob from the soft-margin slide: a small C makes violations cheap, so the optimizer happily accepts a wide margin with several points inside it; a large C makes violations expensive, so it narrows the margin to satisfy as many points as possible — and as C → ∞ we are back to the fragile hard margin. There is no right value in advance, so C is chosen by cross validation, exactly as described earlier.

Click: finally, how is it actually solved? Stay high level: the objective is a smooth bowl (quadratic) and the constraints are straight-line (linear) inequalities, so this is a convex optimization problem called a quadratic program. Convex means there is exactly one best answer and no local minima to get stuck in, and well-tested solvers find it reliably. In practice you never write the solver yourself — scikit-learn's SVC (or LinearSVC) solves this problem when you call fit, and C is its main hyperparameter.
-->

---
glowSeed: 487
clicks: 3
---

# Effective Only in the Middle

<div class="text-lg opacity-85">An illustrative trial: low and high doses are ineffective; middle doses work.</div>

<DoseFeatureLift :step="$clicks" problem style="height: 295px; width: 100%" />

<div class="text-base text-center">
<div v-click="1">One threshold can put the middle doses on the effective side.</div>
<div v-click="2">But it also puts <strong>one of the ineffective groups</strong> on that side.</div>
<div v-click="3" class="text-teal-300 mt-2">What if we keep the dose and add <strong>dose squared</strong> as a second feature?</div>
</div>

<!--
Return to the same dosage number line and the same color convention: blue means ineffective and orange means effective. This is a new, deliberately constructed classification dataset, not a claim about a real drug. The observations are ineffective at doses 5, 10, and 15; effective at 38, 44, 50, 56, and 62; and ineffective again at 85, 90, and 95. No new patient is added during the following animation.

Click 1: try a threshold at 25 and predict effective to the right. It gets the middle right but misclassifies every high-dose observation, circled in pink.

Click 2: reverse the rule and try 75, predicting effective to the left. That gets the middle right but misclassifies every low-dose observation. A linear score in one dimension changes sign at most once. Here the labels change from blue to orange and back to blue, requiring two transitions. Moving the single threshold cannot solve this.

Click 3: propose a new representation. We will retain d and add d squared, computed from the same measurement. No new outcome information is available. Soft margins could tolerate errors, but cannot make a single linear threshold express this middle-only rule. The next slide changes the features instead.
-->

---
glowSeed: 488
clicks: 3
---

# Adding Dose Squared

<DoseFeatureLift :step="$clicks" style="height: 325px; width: 100%" />

<div class="relative text-center text-base" style="height: 82px">
<div v-if="$clicks === 0">
The same patients, with one coordinate each: dose $d$.
</div>
<div v-if="$clicks === 1">

$$\phi(d)=(d,d^2)$$

Each patient moves vertically to its squared dose. The original dose stays on the horizontal axis.
</div>
<div v-if="$clicks === 2">

In the new coordinates $(d,z)$, a <strong>straight line</strong> separates the classes:

$$f(d,z)=100d-z-1875=0.$$

</div>
<div v-if="$clicks >= 3">

Substitute $z=d^2$: $f(d)=100d-d^2-1875=-(d-25)(d-75)$.

<strong>Effective for $25<d<75$:</strong> one line in 2D becomes two cutoffs in 1D.
</div>
</div>

<!--
Initially the plot is the same one-dimensional number line from the previous slide. Keep students watching individual points as you advance.

Click 1: the number line moves down to become the horizontal axis, the vertical axis appears, and the existing point elements animate upward to dose squared. For example, the 50 mg patient moves to (50, 2500). We did not obtain a second independent measurement: the new coordinate is a deterministic feature transformation. All observations lie on the parabola z = d squared. The axes use different display scales so both coordinates are readable; this picture demonstrates separation rather than geometric margin measurements in raw physical units.

Click 2: reveal z = 100d - 1875. Every orange point lies below it, and every blue point lies above it. In the two-dimensional feature space, the score 100d - z - 1875 is linear in the two coordinates d and z. This is one valid separating line selected for clear arithmetic, not a claim that it is the trained maximum-margin solution. A linear SVM could now search for a maximum-margin separator in these features.

Click 3: substitute the definition of z back into the score. The factorization gives roots at 25 and 75. The score is positive between them and negative outside, so the decision rule selects an interval in the original dosage space. Pink marks show where the separating line meets the parabola and project those intersections to the original dosage axis. Ask students to check the signs at d = 10, 50, and 90.

The key idea is representation: a linear classifier in transformed coordinates can have a nonlinear boundary in the original coordinates. Adding arbitrary features does not guarantee useful separation on every dataset. Feature scaling also matters when we optimize margins; these unscaled units are chosen only to make the transformation concrete.
-->

---
glowSeed: 489
clicks: 4
---

# Feature Maps and Kernels

<div class="grid grid-cols-2 gap-9 kernel-copy">
<div>
<div v-click="1">

A **feature map** creates new coordinates:

$$x\longmapsto\phi(x).$$

For dosage, $\phi(d)=(d,d^2)$.

</div>
<div v-click="2" class="mt-7">

A **kernel** computes an inner product in that feature space:

$$K(x,x')=\phi(x)\cdot\phi(x').$$

It takes <strong>two observations</strong> and returns one number.

</div>
</div>
<div>
<div v-click="3">

For our dosage map,

$$
\begin{aligned}
K(d,e)&=(d,d^2)\cdot(e,e^2)\\[5pt]
&=de+d^2e^2.
\end{aligned}
$$

We can evaluate this using only $d$ and $e$.

</div>
<div v-click="4" class="mt-7 text-teal-300">

The **kernel trick** uses these inner products without constructing the expanded feature vectors.

</div>
</div>
</div>

<style>
.kernel-copy { font-size: 19px; line-height: 1.5; }
.kernel-copy p { margin: 0.7em 0; }
.kernel-copy .katex-display { font-size: 0.95em; margin: 0.9em 0; }
</style>

<!--
Click 1: distinguish the representation from the computational shortcut. Phi is the feature map. It takes one observation and returns its coordinates in a new space. Our first example raises a scalar dose to the two-coordinate representation (d, d squared). A feature map can be higher dimensional, but dimensional expansion is not required for every kernel, as the linear kernel will show.

Click 2: a kernel is a function of two observations. Its output equals their dot product after a particular feature map. The prime on x prime means another observation, not a derivative. People often say that a kernel lifts the data, but the precise distinction is that phi supplies the implicit representation and K gives the inner product in it.

Click 3: expand the dot product for the exact map used in our animation. The result de + d squared e squared can be computed from the two original scalar doses. This particular kernel is valid because we have explicitly exhibited its feature map. It is not identical to the standard degree-two polynomial kernel (1 + de) squared; that kernel has different constant and scaling terms. In two dimensions constructing the vectors would be easy, but the same shortcut becomes valuable when there are thousands or infinitely many features.

Click 4: this shortcut is the kernel trick. It works for algorithms whose relevant computations can be expressed using inner products, including the dual form of an SVM. Not every arbitrary similarity function is a valid kernel: positive-semidefinite kernel matrices ensure an inner-product representation. Do not introduce the full matrix theory here; established kernels give us that property.

Reference: https://scikit-learn.org/stable/modules/svm.html#kernel-functions
-->

---
glowSeed: 490
clicks: 4
---

# Lifting a Ring into Three Dimensions

<div class="grid gap-4 items-center" style="grid-template-columns: 36% 64%">
<div class="kernel-ring-copy">

An orange cluster sits inside a blue ring.

<div v-click="1">

No straight line separates the classes in $(x_1,x_2)$.

</div>
<div v-click="2">

Add squared distance from the origin:

$$z=x_1^2+x_2^2.$$

Each point becomes

$\phi(x)=(x_1,x_2,x_1^2+x_2^2)$.

</div>
<div v-click="3">

The horizontal plane $z=2$ separates low orange points from high blue points.

</div>
<div v-click="4" class="text-pink-300">

Back in 2D, the boundary is the circle $x_1^2+x_2^2=2$.

</div>
</div>
<RingFeatureLift :step="$clicks" style="width: 100%; height: 395px" />
</div>

<style>
.kernel-ring-copy { font-size: 17px; line-height: 1.4; }
.kernel-ring-copy p { margin: 0.65em 0; }
.kernel-ring-copy .katex-display { margin: 0.65em 0; }
</style>

<!--
Start with the orange class near the origin and a blue class surrounding it. This is a separate, constructed two-feature dataset, with coordinates already in comparable units. Preserve all point identities and colors while changing the view.

Click 1: show one attempted line. A line gives two half-planes. A complete surrounding ring cannot be put on one side while its center stays on the other; the center lies in the convex hull of the ring. The dashed line is an example, not a claim that checking one candidate proves nonseparability.

Click 2: define z as squared radius. As the camera tilts into a three-dimensional view, each existing point rises to z = x1 squared + x2 squared. The first two coordinates stay unchanged. Orange points have squared radius at most 0.7225; blue points have squared radius at least 3.61, so the outer ring rises much farther. Faint vertical guides connect lifted points to their footprints on the original plane. A point at (2, 0) would move to (2, 0, 4), and a point at (0.5, 0.5) to (0.5, 0.5, 0.5).

Click 3: reveal the horizontal plane z = 2. The orange points lie below it and all blue points above it. The score 2 - z is linear in the three feature coordinates and separates the classes. The plane is translucent so the low orange points remain visible; screen-space overlap in a 3D projection does not mean the classes intersect. Again, this is an illustrative separating plane, not an optimized SVM margin.

Click 4: the footprint of the decision boundary is the circle x1 squared + x2 squared = 2, with radius square root of two, shown dashed in pink on the base plane. The lifted observations lie on a paraboloid; intersecting that surface with a horizontal plane produces a circle. This hand-chosen feature map solves the ring pattern without needing an RBF kernel.

The next slide turns this explicit feature map into a kernel by taking dot products between pairs of mapped points.
-->

---
glowSeed: 490.5
clicks: 3
---

# From Squared Radius to a Kernel

<div class="ring-kernel">
<div v-click="1">

The ring example first defines a **feature map**:

$$\phi(x)=(x_1,x_2,z),\qquad z=x_1^2+x_2^2.$$

This maps each 2D point to an explicit 3D point.

</div>
<div v-click="2">

For two inputs $x$ and $x'$, take the dot product of their mapped coordinates:

$$K(x,x')=\phi(x)\cdot\phi(x').$$

</div>
<div v-click="3">

For this map, that gives

$$
K(x,x')=x_1x_1'+x_2x_2'+(x_1^2+x_2^2)(x_1'^2+x_2'^2).
$$

</div>
</div>

<div class="ring-kernel-takeaway">
Feature map φ creates each point’s coordinates. Kernel K compares a pair of points in that feature space.
</div>

<style>
.ring-kernel { font-size: 21px; line-height: 1.5; }
.ring-kernel p { margin: 0.8em 0; }
.ring-kernel .katex-display { margin: 0.8em 0; }
.ring-kernel div[v-click="3"] .katex-display { font-size: 0.8em; }
.ring-kernel-takeaway { margin-top: 1.1em; font-size: 21px; text-align: center; color: #5eead4; }
</style>

<!--
This slide makes precise how the ring example leads to a kernel. Keep three objects distinct: the original input x with two coordinates, the feature map phi that computes a new three-coordinate point, and the kernel K that takes a pair of inputs and returns one number.

Click 1: recall the vertical feature from the animation, z equals x1 squared plus x2 squared. The full map retains both original coordinates and adds z: phi(x) = (x1, x2, x1 squared plus x2 squared). This explicit feature map raises each point from 2D to 3D. For the shown ring data, its z values separate the center and ring with a plane.

Click 2: a kernel is not the new coordinate z. A kernel compares two inputs. For this chosen map, take the dot product of phi(x) with phi(x prime). The two prime marks simply refer to the second point.

Click 3: multiply corresponding coordinates and add them. The result is x1 times x1 prime plus x2 times x2 prime, plus the product of the two squared radii. This is an exact kernel for this particular explicit map. It returns the same dot product we would get by building both three-dimensional mapped points. Since we can easily build this map, this example illustrates the definition rather than saving much computation.

Transition: the next slide explains the general computational idea. Some useful feature maps are enormous or infinite. If we can evaluate their kernel directly from x and x prime, the SVM can use their feature-space dot products without constructing the expanded coordinate vectors. The kernel still computes a value for each required pair; it does not return the coordinates or eliminate all training cost.

This kernel is a valid kernel because it is explicitly a feature-map dot product. It is not the standard degree-two polynomial kernel on the original two coordinates; its formula includes squared-radius products. The next slide keeps the distinction between feature map and kernel clear.
-->

---
glowSeed: 490.7
---

# What Does a Kernel Value Tell Us?

<div class="kernel-meaning">

$$K(x_i,x_j)=\phi(x_i)\cdot\phi(x_j)$$

This dot product measures how aligned two training points are in the higher-dimensional feature space.

<div class="kernel-meaning-flow">
The SVM uses these pairwise values, together with the class labels, during training to find a maximum-margin separating boundary.
</div>

</div>

<style>
.kernel-meaning { margin: 1.2em auto 0; max-width: 850px; text-align: center; font-size: 25px; line-height: 1.5; }
.kernel-meaning .katex-display { margin: 0.8em 0; font-size: 1.15em; }
.kernel-meaning-flow { margin: 1.5em auto 0; max-width: 760px; padding: 0.8em 1em; border-left: 4px solid #5eead4; background: #5eead414; text-align: left; }
</style>

<!--
For any pair of training points, the kernel returns the dot product their feature-map vectors would have in the higher-dimensional space. You can think of this as measuring alignment, but the exact scale depends on the kernel and on the lengths of the feature vectors; it is not automatically a distance, probability, or normalized similarity.

During training, the SVM uses the pairwise kernel values and class labels to choose the maximum-margin boundary. The kernel provides the feature-space relationships needed by the optimization without requiring us to explicitly construct every high-dimensional feature vector.
-->

---
glowSeed: 491
clicks: 3
---

# Compute in Feature Space Without Building It

<div class="kernel-concept">
<div v-click="1">

**Conceptually, lift each input:** $x\mapsto\phi(x)$. A linear SVM in this space scores

$$f(x)=w\cdot\phi(x)+b.$$

</div>
<div v-click="2">

Training needs inner products between transformed training points. A kernel supplies each one directly:

$$K(x_i,x_j)=\phi(x_i)\cdot\phi(x_j).$$

The values $K(x_i,x_j)$ form the training similarity matrix.

</div>
<div v-click="3">

The SVM can find its maximum-margin boundary from these similarities and the class labels, without constructing the expanded vectors $\phi(x_i)$.

</div>
<div v-click="3" class="kernel-concept-takeaway">

For a new input $x$, the model computes kernel similarities to support vectors, then predicts which side of the learned boundary $x$ belongs on.

</div>
</div>

<style>
.kernel-concept { font-size: 21px; line-height: 1.5; }
.kernel-concept p { margin: 0.9em 0; }
.kernel-concept .katex-display { margin: 0.8em 0; }
.kernel-concept-takeaway { color: #5eead4; margin-top: 1.15em; }
</style>

<!--
Use the two feature-lifting examples to connect the ideas. The feature map phi says what coordinates we would use if we explicitly built the transformed data. In that space, the separating rule remains linear: its score is w dot phi(x) plus b.

Click 1: make the lift conceptual. For a small explicit example like (d,d squared), we can calculate every transformed vector. But in large or infinite feature spaces, explicitly making those vectors may be impractical.

Click 2: identify the only quantities the kernel SVM needs during training: inner products between pairs of transformed training points. The kernel K(x_i,x_j) returns exactly that dot product using the original inputs. Evaluating it for training pairs creates the kernel, or Gram, matrix. The labels and this matrix let the SVM optimize the maximum-margin classifier. Each observation is still in the optimization; the kernel avoids explicitly constructing the expanded coordinate vectors.

Click 3: state the central answer. With a valid, suitable kernel, we can fit the SVM without first building the high-dimensional feature table. We do still compute kernel values, commonly for many pairs of training observations. This shortcut can make a huge or infinite feature representation usable; it does not make all training computation free. The earlier tradeoff slide discusses sample count and cost.

Click 4: at prediction time, the learned decision score can be evaluated through similarities between the new point and the support vectors. The resulting boundary is linear in feature space and can be curved in the original input space. A kernel must be chosen for the data and must define a valid inner product, as standard linear, polynomial, and RBF kernels do. Cross-validation helps assess whether it is a useful choice.

The previous version introduced alpha coefficients and the dual weight-vector identity before students had seen their derivation. This conceptual explanation deliberately leaves those coefficients out. If students later take an optimization-focused course, the dual derivation explains why the kernel values are sufficient.

Reference: https://scikit-learn.org/stable/modules/svm.html#kernel-functions
-->

---
glowSeed: 492
clicks: 3
---

# Linear and Polynomial Kernels

<div class="grid grid-cols-2 gap-8 kernel-family">
<div v-click="1">

### Linear

$$K(x,x')=x\cdot x'.$$

The identity map $\phi(x)=x$ keeps the original features.

The boundary is linear in the input space.

No nonlinear expansion is added.

</div>
<div>
<div v-click="2">

### Polynomial

$$K(x,x')=(\gamma\,x\cdot x'+c_0)^q.$$

The degree $q$ controls powers and interactions. For $c_0>0$, the map includes terms up to degree $q$.

</div>
<div v-click="3" class="mt-5">

For scalar inputs, with $\gamma=c_0=1$ and $q=2$:

$$K(d,e)=(1+de)^2=1+2de+d^2e^2.$$

One matching map is $\phi(d)=(1,\sqrt{2}d,d^2)$.

</div>
</div>
</div>

<style>
.kernel-family { font-size: 18px; line-height: 1.45; }
.kernel-family p { margin: 0.8em 0; }
.kernel-family h3 { color: #5eead4; margin-top: 0.65em; }
.kernel-family .katex-display { font-size: 0.85em; margin: 1em 0; }
</style>

<!--
Introduce two of the three common kernel families covered here. These are not the only kernels that exist; custom kernels can encode domain structure.

Click 1: the linear kernel is the ordinary dot product. Its feature map can be the identity, so it is equivalent to a linear SVM on the supplied features. If we manually supplied dose and dose squared first, a linear kernel on those transformed inputs could still yield a nonlinear rule in the original dose. Thus the phrase original features always refers to the actual representation given to the solver.

Click 2: a polynomial kernel adds products of input coordinates implicitly. Choose a positive integer degree q, gamma greater than zero, and c0 greater than or equal to zero for the standard valid form. With c0 equal to zero the homogeneous map has terms of exactly degree q; with positive c0 it includes lower degrees as well. In multiple dimensions there are cross terms such as x1 times x2, not only separate powers of each feature. A degree-two model therefore can represent interactions as well as squared terms.

Click 3: expand (1 + de) squared. The coefficient two explains the square root of two in the map: dotting (1, sqrt(2)d, d squared) with its counterpart at e gives exactly this kernel. This is a small example students can check by hand. It also clarifies that the standard polynomial kernel does not use precisely the unweighted two-feature map from the dosage animation, even though both can express a quadratic decision rule.

Reference: https://scikit-learn.org/stable/modules/metrics.html#polynomial-kernel
-->

---
glowSeed: 493
clicks: 3
---

# The Radial Basis Function Kernel

<div class="grid grid-cols-2 gap-7 items-center kernel-rbf">
<div>
<div v-click="1">

The Gaussian **RBF** kernel is

$$K(x,x')=e^{-\gamma\|x-x'\|^2},\quad\gamma>0.$$

Nearby observations have high similarity; distant ones have low similarity.

</div>
<div v-click="2">

Its feature space is <strong>infinite dimensional</strong>: the expansion contains polynomial terms of every degree.

One exponential computes the inner product. No infinite vector is constructed.

</div>
<div v-click="3">

<strong>Larger $\gamma$:</strong> more local influence, allowing more detailed boundaries.

<strong>Smaller $\gamma$:</strong> broader influence, usually smoother boundaries.

</div>
</div>
<RbfSimilarity :step="$clicks" style="width: 100%" />
</div>

<style>
.kernel-rbf { font-size: 17px; line-height: 1.45; }
.kernel-rbf p { margin: 0.7em 0; }
.kernel-rbf .katex-display { font-size: 0.92em; margin: 0.8em 0; }
</style>

<!--
Click 1: RBF stands for radial basis function. Here we mean the Gaussian RBF kernel, which depends only on the Euclidean distance between observations. At zero distance it equals one. As distance increases, similarity falls toward zero. The plot shows this function of distance, not an SVM decision boundary and not a probability.

Click 2: the infinite-dimensional interpretation is exact on a continuous input domain. Expand the squared distance to factor the kernel as exp(-gamma norm(x)^2) exp(-gamma norm(x prime)^2) exp(2 gamma x dot x prime). The last factor has the Taylor expansion sum from k = 0 to infinity of (2 gamma x dot x prime)^k / k factorial. Each degree contributes polynomial feature terms. The two leading exponential factors supply the corresponding input-dependent weights. For a scalar input, explicit coordinates are exp(-gamma x^2) times sqrt((2 gamma)^k / k factorial) times x^k, for k = 0, 1, 2, and so on. Their dot product is exactly the Gaussian kernel.

We evaluate that entire inner product with a squared distance and one exponential, rather than materializing infinitely many coordinates. With p input features, a kernel evaluation takes order p arithmetic. This is efficient relative to explicit expansion, not a promise that fitting an RBF SVM is fast on millions of observations. A finite training set still yields a finite n by n kernel matrix.

Click 3: reveal the second curve. The teal curve uses gamma 0.5, and the pink one gamma 2. Larger gamma makes the similarity decay over a shorter distance, allowing the model to respond very locally. Whether it overfits also depends on C and the dataset. The model combines many such similarities, weighted by the learned support-vector coefficients, to form its score.

References: https://scikit-learn.org/stable/modules/metrics.html#rbf-kernel ; https://scikit-learn.org/stable/modules/kernel_approximation.html#radial-basis-function-kernel
-->

---
glowSeed: 494
clicks: 4
---

# Kernel Tradeoffs

<table class="kernel-tradeoffs">
<thead><tr><th>Kernel</th><th>What it can represent</th><th>Generalization risk</th><th>Computational cost</th></tr></thead>
<tbody>
<tr v-click="1"><td>Linear</td><td>A hyperplane in the supplied features</td><td>Can underfit curved patterns</td><td>Dedicated linear solvers scale well; prediction uses one weight vector</td></tr>
<tr v-click="2"><td>Polynomial</td><td>Global polynomial structure and interactions</td><td>High degree can fit noise and magnify scale differences</td><td>A compact kernel avoids expansion, but pairwise training can be costly</td></tr>
<tr v-click="3"><td>RBF</td><td>Flexible, local nonlinear structure</td><td>Large γ with weak regularization can overfit</td><td>Each kernel is cheap; many training pairs and support vectors add cost</td></tr>
</tbody>
</table>

<div v-click="4" class="text-base mt-5">

A full kernel matrix has $n^2$ entries. <strong>Sample count and support-vector count matter</strong>, even when feature expansion is implicit.

</div>

<style>
.kernel-tradeoffs { width: 100%; margin-top: 22px; border-collapse: collapse; font-size: 17px; line-height: 1.4; }
.kernel-tradeoffs th { color: #5eead4; text-align: left; font-weight: 600; padding: 10px 12px; border-bottom: 1px solid #94a3b855; }
.kernel-tradeoffs td { padding: 17px 12px; vertical-align: top; border-bottom: 1px solid #94a3b833; }
.kernel-tradeoffs td:first-child { width: 12%; font-weight: 600; }
.kernel-tradeoffs th:nth-child(2) { width: 25%; }
.kernel-tradeoffs th:nth-child(3) { width: 28%; }
</style>

<!--
Click 1: use linear models when the supplied representation already makes a roughly linear boundary reasonable, or when sample size makes pairwise kernel training impractical. They can still overfit, especially with many features and weak regularization; linear does not guarantee good generalization. Dedicated solvers such as LinearSVC avoid the usual kernel-SVC scaling bottleneck. Merely choosing kernel='linear' in SVC does not turn it into the same scalable implementation.

Click 2: polynomial kernels impose a global algebraic structure. Degree is a modeling choice. Higher degree need not improve held-out performance and may amplify large coordinate values. The kernel avoids explicitly enumerating all monomials. A single evaluation is a dot product followed by a power, so increasing degree does not necessarily explode the cost of each evaluation; the training problem and its conditioning still matter.

Click 3: RBF gives local flexibility. There is no universal runtime ordering between polynomial and RBF kernels: both are cheap to evaluate relative to explicit expansion, and fitting cost depends heavily on n, C, kernel parameters, solver behavior, and support-vector count. Large gamma and large C can encourage intricate boundaries, but tuning decides what generalizes.

Click 4: n is the number of training observations, not the number of lifted coordinates. There are n squared pairwise entries in a full Gram matrix. Solvers often cache only part of it, so this statement does not mean every implementation always stores the full matrix. Exact kernel SVC training commonly grows at least quadratically with n and can approach cubic behavior. Prediction sums similarities over support vectors. If exact kernel training is too large, possible alternatives are a dedicated linear solver or an approximate feature map such as random Fourier features or Nystrom followed by a linear model.

References: https://scikit-learn.org/stable/modules/svm.html#complexity ; https://scikit-learn.org/stable/modules/kernel_approximation.html
-->

---
glowSeed: 495
clicks: 3
---

# Scaling and Regularization Still Matter

<div class="grid grid-cols-2 gap-9 kernel-practice">
<div v-click="1">

### Scale the features

Dot products and distances depend on units.

Standardize using the <strong>training fold only</strong>; apply those same statistics to validation data.

A pipeline keeps preprocessing inside cross-validation.

</div>
<div>
<div v-click="2">

### Tune the right controls

$C$ penalizes margin violations for every kernel.

Polynomial: tune degree $q$ and $C$.

RBF: tune $\gamma$ and $C$ together.

</div>
<div v-click="3" class="mt-6 text-teal-300">

Choose with cross-validation. Keep the test set for the final evaluation.

More dimensions can improve fit; they do not guarantee better predictions.

</div>
</div>
</div>

<style>
.kernel-practice { font-size: 20px; line-height: 1.5; }
.kernel-practice h3 { margin-top: 0.7em; color: #5eead4; }
.kernel-practice p { margin: 0.85em 0; }
</style>

<!--
Click 1: scaling is particularly important for SVMs because both margins and kernels are sensitive to the geometry of the inputs. A variable measured in thousands can dominate a variable measured in tenths. For the dosage example we deliberately kept raw units to make the square visible; a real modeling pipeline should consider how the transformed features are scaled. For RBF, rescaling every input by a factor a multiplies squared distances by a squared, equivalent to changing gamma by that factor if all else stays fixed.

Compute preprocessing statistics only from the training portion of each fold. A StandardScaler followed by SVC in a pipeline is the standard way to avoid leakage while tuning. The same learned scaler must also transform future observations.

Click 2: C controls the cost of violations of the margin constraints, regardless of kernel. Larger C means less willingness to accept those violations, often called weaker regularization. Gamma controls the spatial reach of an RBF similarity. They are different knobs, so tune them together instead of assuming one can replace the other. Polynomial degree is the most visible polynomial control, but gamma and coef0 can matter there too.

Click 3: compare validation performance across sensible parameter ranges, typically logarithmic ranges for C and gamma. Use a held-out test set only after model selection. Infinite-dimensional feature space does not mean automatic overfitting: the kernel geometry and regularization constrain the learned function. Conversely, perfect training separation alone provides no evidence that predictions on new points will improve.

Reference: https://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html ; https://scikit-learn.org/stable/modules/svm.html#tips-on-practical-use
-->

---
glowSeed: 496
clicks: 4
---

# Support Vector Machines: Summary

<div class="kernel-summary">
<div v-click="1">

**Margins:** with normalized scores, full width is $2/\|w\|$. Training balances $\tfrac12\|w\|^2$ against margin violations.

</div>
<div v-click="2">

**Feature maps:** $(d,d^2)$ separates a middle-dose interval; $(x_1,x_2,x_1^2+x_2^2)$ separates a center from a ring.

</div>
<div v-click="3">

**Kernel trick:** $K(x,x')=\phi(x)\cdot\phi(x')$ gives feature-space inner products without constructing all the coordinates.

</div>
<div v-click="4">

**Model choice:** compare linear, polynomial, and RBF kernels. Scale features, tune regularization, and judge on unseen data.

</div>
</div>

<style>
.kernel-summary { font-size: 23px; line-height: 1.65; margin-top: 26px; }
.kernel-summary p { margin: 1.1em 0; }
.kernel-summary strong { color: #5eead4; }
</style>

<!--
Click 1: reconnect to the derivation. The feature-space classifier still has a margin, and the soft-margin objective balances squared norm against violations. Support vectors determine the resulting decision function. For nonlinear kernels, the margin is measured in feature space, not as ordinary distance to the curved boundary in the input plot.

Click 2: ask students to explain the animations without formulas first: the middle-dose group could be separated after adding a squared coordinate, and the outer ring rose farther than the inner group after adding squared radius. Then recover each feature map. The separating boundary stayed linear in the expanded coordinates.

Click 3: distinguish phi from K one last time. Phi creates a representation conceptually; K computes an inner product between two represented observations. That shortcut makes large or infinite feature spaces computationally accessible, while sample count still limits exact kernel methods.

Click 4: finish on generalization. The best-looking training boundary is not necessarily the best model. Feature scaling and C still matter, polynomial degree and RBF gamma control flexibility, and cross-validation chooses the tradeoff. Suggested verbal check: does doubling gamma add a second explicit coordinate to each observation? No: it changes similarity decay, and therefore the implicit geometry, rather than appending one finite feature.
-->
