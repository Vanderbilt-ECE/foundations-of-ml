<script setup>
import { ref, computed } from 'vue';
import BorderGlow from './BorderGlow.vue';

// ponytail: presentations/assignments/resources are placeholder arrays until
// the deck-build pipeline (CI) is wired up to populate real links per unit.
const units = [
  { num: 1, title: 'Mathematical Foundations', tag: 'Foundations', blurb: 'Linear algebra, calculus, and probability — the vocabulary everything else is written in.', presentations: [], assignments: [], resources: [] },
  { num: 2, title: 'Core ML Concepts', tag: 'Foundations', blurb: 'Bias vs. variance, train/test splits, and why models overfit in the first place.', presentations: [], assignments: [], resources: [] },
  { num: 3, title: 'Supervised Learning: Regression', tag: 'Supervised', blurb: 'Linear and polynomial regression, regularization, and reading residuals.', presentations: [], assignments: [], resources: [] },
  { num: 4, title: 'Supervised Learning: Classification', tag: 'Supervised', blurb: 'Logistic regression, k-NN, and support vector machines.', presentations: [], assignments: [], resources: [] },
  { num: 5, title: 'Model Evaluation', tag: 'Evaluation', blurb: 'Accuracy is a trap. Precision, recall, ROC/AUC, and cross-validation.', presentations: [], assignments: [], resources: [] },
  { num: 6, title: 'Ensemble Methods', tag: 'Advanced', blurb: 'Bagging, boosting, and random forests — many weak learners, one strong one.', presentations: [], assignments: [], resources: [] },
  { num: 7, title: 'Unsupervised Learning', tag: 'Unsupervised', blurb: 'Clustering, dimensionality reduction, and finding structure with no labels.', presentations: [], assignments: [], resources: [] },
  { num: 8, title: 'Neural Networks & Deep Learning Basics', tag: 'Deep Learning', blurb: 'Perceptrons, backpropagation, and a first look at convolutional nets.', presentations: [], assignments: [], resources: [] },
  { num: 9, title: 'Optimization in Practice', tag: 'Deep Learning', blurb: 'Gradient descent variants, learning rates, and hyperparameter tuning.', presentations: [], assignments: [], resources: [] },
  { num: 10, title: 'Broader Context', tag: 'Context', blurb: 'Fairness, ethics, and what happens when a model meets the real world.', presentations: [], assignments: [], resources: [] },
  { num: 11, title: 'Capstone / Project Time', tag: 'Capstone', blurb: 'Build something real, present it, and put the whole course to use.', presentations: [], assignments: [], resources: [] },
];

const tabs = [
  { id: 'presentations', label: 'Presentations' },
  { id: 'assignments', label: 'Assignments' },
  { id: 'resources', label: 'Resources' },
];

const hoveredId = ref(null);
const selected = ref(null);
const activeTab = ref('presentations');

const currentItems = computed(() => (selected.value ? selected.value[activeTab.value] : []));

function selectUnit(unit) {
  selected.value = unit;
  activeTab.value = 'presentations';
  window.scrollTo(0, 0);
}

function closePane() {
  selected.value = null;
  window.scrollTo(0, 0);
}
</script>

<template>
  <div class="stage">
    <div class="hero" :class="{ collapsed: selected }">
      <div class="hero-text">
        <div class="eyebrow">Foundations of Machine Learning</div>
        <h1>From vectors to<br>working models.</h1>
        <p>Eleven units, one straight line from math to models that actually predict something. Pick a node below to start.</p>
      </div>
    </div>

    <div class="layout">
      <div class="map" :class="{ compact: selected }">
        <button v-if="selected" class="back" @click="closePane">&larr; All units</button>

        <div class="spine"></div>

        <div
          v-for="unit in units"
          :key="unit.num"
          class="row"
          @mouseenter="hoveredId = unit.num"
          @mouseleave="hoveredId = null"
        >
          <button
            class="node"
            :class="{ hovered: hoveredId === unit.num, selected: selected?.num === unit.num }"
            @click="selectUnit(unit)"
          >{{ unit.num }}</button>

          <button class="card-link" @click="selectUnit(unit)">
            <BorderGlow
              class-name="w-full"
              background-color="#12161f"
              :border-radius="14"
              :glow-radius="22"
              :glow-intensity="0.8"
              :edge-sensitivity="25"
              :cone-spread="30"
              glow-color="195 90% 60%"
              :colors="['#18549a', '#01b6d1', '#38bdf8']"
            >
              <div class="card" :class="{ hovered: hoveredId === unit.num }">
                <div class="card-top">
                  <div>
                    <div class="card-tag">{{ unit.tag }}</div>
                    <div class="card-title">{{ unit.title }}</div>
                  </div>
                </div>
                <div class="card-blurb" :class="{ open: hoveredId === unit.num && !selected }">{{ unit.blurb }}</div>
              </div>
            </BorderGlow>
          </button>
        </div>
      </div>

      <Transition name="pane">
        <div v-if="selected" class="pane" :key="selected.num">
          <BorderGlow
            class-name="w-full"
            background-color="#12161f"
            :border-radius="18"
            :glow-radius="26"
            :glow-intensity="0.8"
            :edge-sensitivity="20"
            :cone-spread="30"
            glow-color="195 90% 60%"
            :colors="['#18549a', '#01b6d1', '#38bdf8']"
          >
            <div class="pane-inner">
              <div class="pane-tag">{{ selected.tag }}</div>
              <h2 class="pane-title">{{ selected.title }}</h2>
              <p class="pane-blurb">{{ selected.blurb }}</p>

              <div class="tabs">
                <button
                  v-for="tab in tabs"
                  :key="tab.id"
                  class="tab"
                  :class="{ active: activeTab === tab.id }"
                  @click="activeTab = tab.id"
                >{{ tab.label }}</button>
              </div>

              <div class="tab-content">
                <p v-if="!currentItems.length" class="empty">Nothing here yet — check back soon.</p>
                <ul v-else class="item-list">
                  <li v-for="item in currentItems" :key="item.href"><a :href="item.href">{{ item.title }}</a></li>
                </ul>
              </div>
            </div>
          </BorderGlow>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
/* Centering/max-width live only here, and never change — the map/pane split
   happens entirely inside, so nothing about this box's own position animates
   (auto margins can't be transitioned smoothly, so we never toggle them). */
.stage {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 8vw;
  box-sizing: border-box;
}

.hero {
  position: relative;
  padding: 110px 0 90px;
  border-bottom: 1px solid #1c2130;
  max-height: 640px;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s ease, padding 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.hero.collapsed {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
  border-color: transparent;
  pointer-events: none;
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

.layout {
  display: flex;
  align-items: flex-start;
}

.map {
  position: relative;
  flex: 0 0 auto;
  width: 100%;
  padding: 90px 0 140px;
  box-sizing: border-box;
  transition: width 0.4s cubic-bezier(0.22, 1, 0.36, 1), padding 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.map.compact {
  width: 340px;
  padding: 48px 24px 60px 0;
}

.back {
  display: block;
  margin-bottom: 24px;
  background: none;
  border: none;
  color: #aab0c2;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}
.back:hover { color: #c8ff4d; }

.spine {
  position: absolute;
  left: 27px;
  top: 28px;
  bottom: 88px;
  width: 2px;
  background: #232838;
}
.map.compact .spine { top: 76px; }

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
  cursor: pointer;
  background: #12161f;
  border: 2px solid #2c3244;
  color: #7c8199;
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.35s ease, background 0.3s ease, border-color 0.3s ease;
}
.node.selected { background: #6d5ef8; border-color: #6d5ef8; color: #0a0d13; }
.node.hovered { transform: scale(1.08); }
.node.hovered.selected { box-shadow: 0 0 0 8px #6d5ef822; }

.card-link {
  flex: 1;
  min-width: 0;
  text-decoration: none;
  color: inherit;
  display: block;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  text-align: left;
  font-family: inherit;
}

.card {
  padding: 22px 26px;
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1), padding 0.3s ease;
}
.card.hovered { transform: translateX(6px); }
.map.compact .card { padding: 14px 18px; }
.map.compact .card .card-title { font-size: 15px; }
.map.compact .card .card-tag { font-size: 10px; margin-bottom: 3px; }

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

.pane {
  flex: 1 1 auto;
  padding: 48px 0 60px 24px;
  min-width: 0;
}
.pane-enter-active { transition: opacity 0.35s ease 0.12s, transform 0.35s cubic-bezier(0.22, 1, 0.36, 1) 0.12s; }
.pane-leave-active { transition: opacity 0.15s ease; }
.pane-enter-from { opacity: 0; transform: translateX(24px); }
.pane-leave-to { opacity: 0; }

.pane-inner { padding: 36px 40px; }
.pane-tag {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c8199;
  margin-bottom: 10px;
}
.pane-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 14px;
  color: #f4f3ef;
}
.pane-blurb { font-size: 16px; line-height: 1.55; color: #c3c8d6; margin: 0 0 32px; max-width: 640px; }

.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid #232838;
  margin-bottom: 28px;
}
.tab {
  background: none;
  border: none;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  color: #7c8199;
  padding: 10px 18px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.2s ease, border-color 0.2s ease;
}
.tab:hover { color: #c3c8d6; }
.tab.active { color: #c8ff4d; border-color: #c8ff4d; }

.empty { color: #5a6072; font-size: 15px; }
.item-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.item-list a { font-size: 15px; }

@media (max-width: 860px) {
  .layout { flex-direction: column; }
  .map.compact { width: 100%; padding: 32px 0; }
  .pane { padding: 24px 0 60px; }
}
</style>
