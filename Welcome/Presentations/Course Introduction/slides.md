---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Course Introduction'
info: |
  ## Foundations of Applied Machine Learning
  Welcome deck: who the course is for, what it covers, how it's graded, and who's teaching it.
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
glowSeed: 229
---

# Foundations of Applied Machine Learning

### ECE 4608 / 5608 — Course Introduction

<div class="pt-6 opacity-80 text-lg">
Mathematical foundations, core algorithms, and evaluation practices of classical machine learning — with an introduction to neural networks and deep learning.
</div>

<div class="pt-10 text-sm opacity-60">
Dr. Jonathan Jaramillo · Vanderbilt University
</div>

<!--
Opening slide. Introduce yourself, welcome the room, and set expectations for the deck: who
this course is for, what's in it, how it's graded, and a bit about who's teaching it.
-->

---
glowSeed: 140
---

# Who Should Take This Course

<div class="grid grid-cols-3 gap-4 mt-8">

<div v-click border="2 solid teal-700" bg="teal-800/20" rounded-lg overflow-hidden>
<div bg="teal-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:idea text-teal-300 text-xl />
<span font-bold>Curious builders</span>
</div>
<div px-4 py-3 text-sm>
You want to actually <strong>implement</strong> machine learning models, not just hear about them — weekly hands-on coding is core to the course.
</div>
</div>

<div v-click border="2 solid blue-700" bg="blue-800/20" rounded-lg overflow-hidden>
<div bg="blue-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:calculator text-blue-300 text-xl />
<span font-bold>Comfortable with the basics</span>
</div>
<div px-4 py-3 text-sm>
No ML background assumed — but you should be ready to work with <strong>linear algebra, probability, and calculus</strong>. We review all three early in the course.
</div>
</div>

<div v-click border="2 solid orange-700" bg="orange-800/20" rounded-lg overflow-hidden>
<div bg="orange-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:chat text-orange-300 text-xl />
<span font-bold>Ready to talk, not just listen</span>
</div>
<div px-4 py-3 text-sm>
This is a <strong>flipped classroom</strong>. Class time is discussion and problem-solving, not lecture — you need to show up prepared to engage.
</div>
</div>

</div>

<!--
Frame the audience: no prior ML required, but real math and real code are involved, and the
format rewards students who prepare before class rather than sit passively during it.
-->

---
glowSeed: 96
---

# What This Course Is For

<div class="grid grid-cols-2 gap-8 mt-6">

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>
<div bg="white/10" backdrop-blur px-4 py-2 flex items-center gap-2>
<div i-carbon:code text-blue-300 text-xl />
<span font-bold>Practical implementation skills</span>
</div>
<div px-5 py-4 text-sm>

Weekly coding assignments build the muscle memory for real ML work — data cleaning, model fitting, and evaluation in Python and scikit-learn.

<div class="mt-3 text-sm opacity-80">Assignments are completion-graded, not correctness-graded — they're for learning, not scoring.</div>

</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div bg="teal-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:certificate text-teal-300 text-xl />
<span font-bold>Conceptual mastery</span>
</div>
<div px-5 py-4 text-sm>

Weekly quizzes, structured in-class discussion, and two group projects with an oral defense confirm that <strong>you</strong> understand the material — not just a tool acting on your behalf.

</div>
</div>

</div>

<div v-click class="mt-8 flex justify-center">
<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-3 text-lg text-center>
By the end: you can build, evaluate, and <strong>explain</strong> a classical ML pipeline end to end.
</div>
</div>

<!--
This is the course's central design decision: coding assignments teach, but quizzes,
participation, and project defenses are what actually get graded, because those are the
assessments an AI tool can't complete on a student's behalf.
-->

---
glowSeed: 205
---

# Course Format: A Flipped Classroom

<div class="text-sm opacity-70 mb-6">Lectures are pre-recorded. Class time is discussion, problem-solving, and collaborative coding.</div>

<div class="grid grid-cols-3 gap-4">

<div v-click border="2 solid violet-700" bg="violet-800/20" rounded-lg overflow-hidden>
<div bg="violet-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:video text-violet-300 text-xl />
<span font-bold>Before Mon / Wed</span>
</div>
<div px-4 py-3 text-sm>
Watch the pre-recorded lecture and complete a short, low-stakes comprehension check.
</div>
</div>

<div v-click border="2 solid blue-700" bg="blue-800/20" rounded-lg overflow-hidden>
<div bg="blue-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:group text-blue-300 text-xl />
<span font-bold>Monday / Wednesday</span>
</div>
<div px-4 py-3 text-sm>
Discussion, problem-solving, and group work. Cold-calling and group report-outs — not optional review time.
</div>
</div>

<div v-click border="2 solid amber-700" bg="amber-800/20" rounded-lg overflow-hidden>
<div bg="amber-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:code-hide text-amber-300 text-xl />
<span font-bold>Friday</span>
</div>
<div px-4 py-3 text-sm>
A 10&#8211;15 minute quiz (this week's material, plus cumulative questions), then in-class coding lab time.
</div>
</div>

</div>

<!--
Emphasize: this format only works if students actually watch lectures before class. The
Monday/Wednesday sessions assume you've already seen the material.
-->

---
glowSeed: 118
---

# What's In the Course — Foundations to Evaluation

<div class="text-sm opacity-70 mb-3">Topics build in this order — exact pacing may shift as the semester goes.</div>

<v-clicks>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-2 mb-2>
<div class="text-3xl font-bold text-teal-400 w-14 text-center">1</div>
<div class="pt-1"><strong>Mathematical Foundations</strong> — linear algebra, probability &amp; statistics, calculus for optimization</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-2 mb-2>
<div class="text-3xl font-bold text-teal-400 w-14 text-center">2</div>
<div class="pt-1"><strong>Core ML Concepts</strong> — learning types, bias-variance tradeoff, train/val/test splits, overfitting, loss functions</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-2 mb-2>
<div class="text-3xl font-bold text-teal-400 w-14 text-center">3</div>
<div class="pt-1"><strong>Supervised Learning: Regression</strong> — linear &amp; polynomial regression, ridge/lasso regularization</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-2 mb-2>
<div class="text-3xl font-bold text-teal-400 w-14 text-center">4</div>
<div class="pt-1"><strong>Supervised Learning: Classification</strong> — logistic regression, k-NN, Naive Bayes, decision trees, SVMs</div>
</div>

<div border="2 solid amber-800" bg="amber-800/20" rounded-lg flex items-start gap-4 px-5 py-2 mb-2>
<div class="text-3xl font-bold text-amber-400 w-14 text-center">5</div>
<div class="pt-1"><strong>Model Evaluation</strong> — accuracy, precision/recall/F1, ROC-AUC, confusion matrices, common pitfalls · <em>midterm project follows</em></div>
</div>

</v-clicks>

<!--
First stretch of the semester: math scaffolding, then core concepts taught before any
algorithms exist, then regression and classification, closing with detailed evaluation
metrics right before the midterm project. No week numbers on purpose — pacing can shift.
-->

---
glowSeed: 261
---

# What's In the Course — Ensembles to Neural Networks

<div class="text-sm opacity-70 mb-4">Topics build in this order — exact pacing may shift as the semester goes.</div>

<v-clicks>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-3xl font-bold text-blue-400 w-14 text-center">6</div>
<div class="pt-1"><strong>Ensemble Methods</strong> — bagging &amp; random forests, boosting, why ensembles work</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-3xl font-bold text-blue-400 w-14 text-center">7</div>
<div class="pt-1"><strong>Unsupervised Learning</strong> — k-means &amp; hierarchical clustering, PCA / t-SNE / UMAP, Gaussian mixture models</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-3xl font-bold text-blue-400 w-14 text-center">8</div>
<div class="pt-1"><strong>Neural Networks &amp; Deep Learning Basics</strong> — perceptrons, backprop, activations, a light touch on CNNs/RNNs</div>
</div>

</v-clicks>

<!--
Ensembles and unsupervised learning round out classical ML, then a deliberately "light touch"
pass through neural networks begins the back half of the course.
-->

---
glowSeed: 275
---

# What's In the Course — Optimization to Capstone

<div class="text-sm opacity-70 mb-4">Topics build in this order — exact pacing may shift as the semester goes.</div>

<v-clicks>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-3xl font-bold text-blue-400 w-14 text-center">9</div>
<div class="pt-1"><strong>Optimization in Practice</strong> — SGD, momentum, Adam, hyperparameter tuning strategies</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-3xl font-bold text-blue-400 w-14 text-center">10</div>
<div class="pt-1"><strong>Broader Context</strong> — fairness, bias, interpretability, ethics, classical ML vs. modern deep learning</div>
</div>

<div border="2 solid violet-800" bg="violet-800/20" rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-3xl font-bold text-violet-400 w-14 text-center">11</div>
<div class="pt-1"><strong>Capstone / Project Time</strong> — full end-to-end final project: data cleaning, model selection, evaluation, write-up · <em>final project follows</em></div>
</div>

</v-clicks>

<!--
Modern optimization, then a step back to broader context, ending in the capstone that
closes out the semester.
-->

---
glowSeed: 88
---

# How You're Graded

<div class="grid grid-cols-2 gap-x-10 gap-y-3 mt-6">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 flex items-center justify-between>
<span font-bold>Quizzes</span>
<span class="text-2xl font-bold text-teal-400">25%</span>
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3 flex items-center justify-between>
<span font-bold>Participation</span>
<span class="text-2xl font-bold text-blue-400">20%</span>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg px-4 py-3 flex items-center justify-between>
<span font-bold>Pre-lecture checks / checkpoints</span>
<span class="text-2xl font-bold opacity-90">10%</span>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3 flex items-center justify-between>
<span font-bold>Midterm project + defense</span>
<span class="text-2xl font-bold text-amber-400">15%</span>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3 flex items-center justify-between col-span-2>
<span font-bold>Final project + defense</span>
<span class="text-2xl font-bold text-violet-400">30%</span>
</div>

</div>

<div v-click class="mt-6 flex justify-center">
<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-3 text-sm text-center>
Weekly coding assignments are <strong>not graded for correctness</strong> — quizzes and project defenses are what confirm the understanding is yours.
</div>
</div>

<!--
Walk through the weighting. The heaviest weight (45%) sits on the two project defenses,
because that's the assessment format an AI tool cannot complete on a student's behalf.
-->

---
glowSeed: 300
---

# Projects: Pairs, With an Oral Defense

<div class="grid grid-cols-2 gap-8 mt-6">

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div bg="amber-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:task text-amber-300 text-xl />
<span font-bold>Midterm — 15%</span>
</div>
<div px-5 py-4 text-sm>

After Module 5 (Model Evaluation). Scoped to regression, classification, and evaluation metrics.

<div class="mt-3 text-sm opacity-80">Both partners are questioned on <strong>both halves</strong> of the project — not just their own contribution.</div>

</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div bg="violet-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:trophy text-violet-300 text-xl />
<span font-bold>Final — 30%</span>
</div>
<div px-5 py-4 text-sm>

The capstone deliverable, drawing on the full course — ensembles, unsupervised learning, and neural network basics included.

<div class="mt-3 text-sm opacity-80">Pairs may be reshuffled or continued from the midterm. Emphasis on design choices and explaining the work live.</div>

</div>
</div>

</div>

<div v-click class="mt-6 flex justify-center">
<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-3 text-sm text-center>
A brief private peer evaluation is submitted after each project to help ensure fair credit within pairs.
</div>
</div>

<!--
Both projects are done in pairs, both end in an oral defense where either partner can be
asked about either half of the work — this is deliberate, to keep credit honest.
-->

---
glowSeed: 214
---

# AI Policy

<div class="max-w-4xl mx-auto mt-4">

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg px-5 py-4 mb-4>
⚠️ <strong>The premise:</strong> AI coding assistants can complete most weekly assignments end to end. Grading is built around that reality, not in denial of it.
</div>

<div class="grid grid-cols-2 gap-4">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div bg="teal-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:checkmark text-teal-300 text-xl />
<span font-bold>AI tools allowed</span>
</div>
<div px-4 py-3 text-sm>
Weekly coding assignments and project <strong>implementation</strong> (debugging, boilerplate, library exploration).
</div>
</div>

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg overflow-hidden>
<div bg="red-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:close text-red-300 text-xl />
<span font-bold>No AI tools</span>
</div>
<div px-4 py-3 text-sm>
Quizzes (closed-book, in class) and pre-lecture comprehension checks.
</div>
</div>

</div>

<div v-click class="mt-4 text-sm opacity-80 text-center">
Project design decisions, analysis, and interpretation must be your own. If you can't explain a design choice or a piece of code in the oral defense, it counts against your grade — regardless of who or what wrote it.
</div>

</div>

<!--
This is one of the more distinctive parts of the syllabus and worth dwelling on — it sets
expectations for how AI use is treated differently across assignments, quizzes, and defenses.
-->

---
glowSeed: 342
---

# Logistics

<div class="grid grid-cols-2 gap-4 mt-6">

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div i-carbon:book text-blue-300 text-2xl />
<div><strong>Textbook</strong> — <em>Hands-On Machine Learning with Scikit-Learn and PyTorch</em>, Aurélien Géron (O'Reilly, 2025)</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div i-carbon:laptop text-blue-300 text-2xl />
<div><strong>Hardware</strong> — a laptop is required every session (tablets aren't sufficient)</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div i-carbon:code text-blue-300 text-2xl />
<div><strong>Software</strong> — Python 3 and scikit-learn</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div i-carbon:machine-learning-model text-blue-300 text-2xl />
<div><strong>Recommended</strong> — a paid/Pro AI assistant subscription (Claude or ChatGPT), given the AI Policy</div>
</div>

</div>

<div v-click class="mt-6 flex justify-center">
<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-3 text-sm text-center>
Late work: <strong>10% off per day</strong> without prior instructor permission · Two unexcused absences before participation is impacted
</div>
</div>

<!--
Quick practical slide — what to bring, what to buy, what the late-work and attendance
policies actually mean day to day.
-->

---
glowSeed: 190
---

# Meet Your Instructor

<v-clicks>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-2xl w-14 text-center pt-1">🎓</div>
<div class="pt-1"><strong>BS, Physics &amp; Computer Science</strong> — Houghton University, 2017</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-2xl w-14 text-center pt-1">🛰️</div>
<div class="pt-1"><strong>Systems Engineer, Lockheed Martin</strong> — signal processing &amp; sensor fusion for aerospace platforms</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-2xl w-14 text-center pt-1">🔬</div>
<div class="pt-1"><strong>PhD, Electrical &amp; Computer Engineering</strong> — Cornell University; robotics, computer vision, and AI, centered on digital agriculture</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-2xl w-14 text-center pt-1">🧑‍🏫</div>
<div class="pt-1"><strong>Faculty, Cornell Systems Engineering</strong> — taught Robotics, IoT, Embedded Systems, and Cyber-Physical Systems; led multiple open-source robotics platforms; partnered with SparkFun Electronics, Experiential Robotics, Arm, and FIRST Robotics</div>
</div>

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg flex items-start gap-4 px-5 py-3 mb-3>
<div class="text-2xl w-14 text-center pt-1">🏛️</div>
<div class="pt-1"><strong>Assistant Professor of the Practice, Vanderbilt University</strong> — starting Summer 2026</div>
</div>

</v-clicks>

<!--
Walk the room through the path from physics/CS undergrad, through aerospace industry work,
into a robotics/CV/AI PhD applied to agriculture, into teaching, and now to Vanderbilt.
-->

---
layout: center
class: text-center
glowSeed: 229
---

# Welcome to the Course

### Let's build something real together

<div class="pt-6 opacity-80">
Dr. Jonathan Jaramillo · Foundations of Applied Machine Learning
</div>

<div class="pt-8 text-sm opacity-60">
Questions welcome — see office hours and contact info on the syllabus
</div>

<!--
Closing slide. Invite questions, point students to the full syllabus document for policy
details, and hand off to the first module.
-->
