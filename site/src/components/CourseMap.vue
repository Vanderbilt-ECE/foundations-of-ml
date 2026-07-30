<script setup>
import { reactive, ref } from 'vue';

const units = [
  { num: 1, title: 'Mathematical Foundations', tag: 'Foundations', blurb: 'Linear algebra, calculus, and probability — the vocabulary everything else is written in.', href: 'mathematical-foundations/', available: false },
  { num: 2, title: 'Core ML Concepts', tag: 'Foundations', blurb: 'Bias vs. variance, train/test splits, and why models overfit in the first place.', href: 'core-ml-concepts/', available: false },
  { num: 3, title: 'Supervised Learning: Regression', tag: 'Supervised', blurb: 'Linear and polynomial regression, regularization, and reading residuals.', href: 'supervised-learning-regression/', available: false },
  { num: 4, title: 'Supervised Learning: Classification', tag: 'Supervised', blurb: 'Logistic regression, k-NN, and support vector machines.', href: 'supervised-learning-classification/', available: false },
  { num: 5, title: 'Model Evaluation', tag: 'Evaluation', blurb: 'Accuracy is a trap. Precision, recall, ROC/AUC, and cross-validation.', href: 'model-evaluation/', available: false },
  { num: 6, title: 'Ensemble Methods', tag: 'Advanced', blurb: 'Bagging, boosting, and random forests — many weak learners, one strong one.', href: 'ensemble-methods/', available: false },
  { num: 7, title: 'Unsupervised Learning', tag: 'Unsupervised', blurb: 'Clustering, dimensionality reduction, and finding structure with no labels.', href: 'unsupervised-learning/', available: false },
  { num: 8, title: 'Neural Networks & Deep Learning Basics', tag: 'Deep Learning', blurb: 'Perceptrons, backpropagation, and a first look at convolutional nets.', href: 'neural-networks/', available: false },
  { num: 9, title: 'Optimization in Practice', tag: 'Deep Learning', blurb: 'Gradient descent variants, learning rates, and hyperparameter tuning.', href: 'optimization-in-practice/', available: false },
  { num: 10, title: 'Broader Context', tag: 'Context', blurb: 'Fairness, ethics, and what happens when a model meets the real world.', href: 'broader-context/', available: false },
  { num: 11, title: 'Capstone / Project Time', tag: 'Capstone', blurb: 'Build something real, present it, and put the whole course to use.', href: 'capstone/', available: false },
];

const mouse = reactive({ x: 0, y: 0 });
const hoveredId = ref(null);
const toast = ref(null);
let toastTimer = null;

function handleMouseMove(e) {
  const r = e.currentTarget.getBoundingClientRect();
  mouse.x = (e.clientX - r.left) / r.width - 0.5;
  mouse.y = (e.clientY - r.top) / r.height - 0.5;
}

function showToast(msg) {
  toast.value = msg;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (toast.value = null), 2200);
}

function onUnitClick(unit) {
  if (!unit.available) {
    showToast(`Unit ${unit.num} — ${unit.title} is coming soon.`);
  }
}
</script>

<template>
  <div class="hero" @mousemove="handleMouseMove">
    <div class="orb orb-1" :style="{ transform: `translate(${mouse.x * 30}px, ${mouse.y * 30}px)` }"></div>
    <div class="orb orb-2" :style="{ transform: `translate(${mouse.x * -24}px, ${mouse.y * -24}px)` }"></div>

    <div class="hero-text" :style="{ transform: `translate(${mouse.x * -10}px, ${mouse.y * -10}px)` }">
      <div class="eyebrow">Foundations of Machine Learning</div>
      <h1>From vectors to<br>working models.</h1>
      <p>Eleven units, one straight line from math to models that actually predict something. Pick a node below to start.</p>
    </div>
  </div>

  <div class="map">
    <div class="spine"></div>

    <div
      v-for="unit in units"
      :key="unit.num"
      class="row"
      @mouseenter="hoveredId = unit.num"
      @mouseleave="hoveredId = null"
    >
      <component
        :is="unit.available ? 'a' : 'div'"
        :href="unit.available ? unit.href : undefined"
        class="node"
        :class="{ hovered: hoveredId === unit.num, available: unit.available }"
        @click="onUnitClick(unit)"
      >{{ unit.num }}</component>

      <component
        :is="unit.available ? 'a' : 'div'"
        :href="unit.available ? unit.href : undefined"
        class="card"
        :class="{ hovered: hoveredId === unit.num, available: unit.available }"
        @click="onUnitClick(unit)"
      >
        <div class="card-top">
          <div>
            <div class="card-tag">{{ unit.tag }}</div>
            <div class="card-title">{{ unit.title }}</div>
          </div>
          <div class="card-status" :class="{ available: unit.available }">
            {{ unit.available ? 'Available' : 'Coming soon' }}
          </div>
        </div>
        <div class="card-blurb" :class="{ open: hoveredId === unit.num }">{{ unit.blurb }}</div>
      </component>
    </div>
  </div>

  <div v-if="toast" class="toast">{{ toast }}</div>
</template>

<style scoped>
.hero {
  position: relative;
  padding: 110px 8vw 90px;
  overflow: hidden;
  border-bottom: 1px solid #1c2130;
}
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(12px);
  pointer-events: none;
  animation: floatOrb 8s ease-in-out infinite;
}
.orb-1 {
  top: -60px;
  left: 8vw;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle at 35% 35%, #6d5ef855, transparent 70%);
}
.orb-2 {
  bottom: -80px;
  right: 6vw;
  width: 340px;
  height: 340px;
  background: radial-gradient(circle at 60% 40%, #c8ff4d33, transparent 70%);
  animation-delay: -3s;
}
@keyframes floatOrb {
  0%, 100% { translate: 0 0; }
  50% { translate: 0 -18px; }
}
.hero-text { position: relative; max-width: 900px; }
.eyebrow {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #c8ff4d;
  margin-bottom: 22px;
}
h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(40px, 6vw, 76px);
  font-weight: 700;
  line-height: 1.03;
  margin: 0 0 26px;
  letter-spacing: -0.02em;
}
.hero-text p {
  font-size: 19px;
  line-height: 1.55;
  color: #aab0c2;
  max-width: 560px;
  margin: 0;
}

.map {
  max-width: 1080px;
  margin: 0 auto;
  padding: 90px 8vw 140px;
  position: relative;
}
.spine {
  position: absolute;
  left: calc(8vw + 27px);
  top: 28px;
  bottom: 88px;
  width: 2px;
  background: #232838;
}
.row {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 28px;
  margin-bottom: 34px;
  z-index: 1;
}
.row:last-child { margin-bottom: 0; }

.node {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 18px;
  text-decoration: none;
  cursor: pointer;
  background: #12161f;
  border: 2px solid #2c3244;
  color: #7c8199;
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.35s ease;
}
.node.available { background: #6d5ef8; border-color: #6d5ef8; color: #0a0d13; }
.node.hovered { transform: scale(1.08); }
.node.hovered.available { box-shadow: 0 0 0 8px #6d5ef822; }

.card {
  flex: 1;
  padding: 22px 26px;
  border-radius: 14px;
  background: #12161f;
  border: 1px solid #1c2130;
  cursor: default;
  text-decoration: none;
  color: inherit;
  display: block;
  transition: background 0.3s ease, border-color 0.3s ease, transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.card.available { cursor: pointer; }
.card.hovered { background: #161b27; transform: translateX(6px); border-color: #3a4058; }
.card.hovered.available { border-color: #6d5ef8; }

.card-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.card-tag {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c8199;
  margin-bottom: 6px;
}
.card-title { font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 600; color: #f4f3ef; }
.card-status { font-size: 13px; font-weight: 600; letter-spacing: 0.04em; color: #5a6072; white-space: nowrap; }
.card-status.available { color: #c8ff4d; }

.card-blurb {
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  font-size: 15px;
  line-height: 1.5;
  color: #c3c8d6;
  border-top: 1px solid transparent;
  transition: max-height 0.4s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s ease, margin-top 0.4s ease, padding-top 0.4s ease, border-color 0.4s ease;
}
.card-blurb.open {
  max-height: 90px;
  opacity: 1;
  margin-top: 14px;
  padding-top: 14px;
  border-color: #232838;
}

.toast {
  position: fixed;
  bottom: 32px;
  left: 50%;
  translate: -50% 0;
  background: #171c28;
  border: 1px solid #2c3244;
  color: #f4f3ef;
  padding: 14px 22px;
  border-radius: 10px;
  font-size: 14px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}
</style>
