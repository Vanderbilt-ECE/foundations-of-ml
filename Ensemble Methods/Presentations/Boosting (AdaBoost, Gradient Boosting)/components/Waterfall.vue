<script setup lang="ts">
// The price example from Why Ensembles Work: true price 300. Stump 1 predicts 250, stump 2 is fit
// to the leftover 50 and predicts +40, stump 3 is fit to the leftover 10 and predicts +8.
// Each bar starts where the running sum left off. Red brackets are what is still left over.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
const target = 300
const steps = [
  { key: 1, add: 250, label: 'stump 1', note: 'fit to y' },
  { key: 2, add: 40, label: 'stump 2', note: 'fit to 50 left' },
  { key: 3, add: 8, label: 'stump 3', note: 'fit to 10 left' },
]
const W = 460
const H = 290
const L = 50
const R = 448
const T = 26
const Bot = 240
const max = 320
const sy = (v: number) => Bot - v / max * (Bot - T)
const colW = (R - L) / 4
let run = 0
const bars = steps.map((s, i) => {
  const from = run
  run += s.add
  return { ...s, x: L + i * colW + 14, w: colW - 28, from, to: run, left: target - run }
})
const sumBar = { x: L + 3 * colW + 14, w: colW - 28, to: run }
const ticks = [0, 100, 200, 300]
</script>

<template>
  <svg role="img" aria-label="Running sum of three stumps: 250, then 290, then 298, approaching the true price of 300" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in ticks" :key="t" :x1="L" :x2="R" :y1="sy(t)" :y2="sy(t)" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <text v-for="t in ticks" :key="`y${t}`" :x="L - 8" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <line :x1="L" :x2="R" :y1="sy(target)" :y2="sy(target)" :style="{ stroke: '#e2e8f0', strokeWidth: 2, strokeDasharray: '6 5', opacity: 0.8 }" />
    <text :x="L + 4" :y="sy(target) - 7" :style="{ fill: '#e2e8f0', fontSize: '12px' }">true price 300</text>
    <g v-for="(b, i) in bars" :key="b.key">
      <rect :x="b.x" :y="sy(b.to)" :width="b.w" :height="Math.max(2, sy(b.from) - sy(b.to))" rx="3" :style="{ fill: '#fbbf24', fillOpacity: 0.75 }" />
      <line v-if="i < bars.length - 1" :x1="b.x + b.w" :x2="bars[i + 1].x" :y1="sy(b.to)" :y2="sy(b.to)" :style="{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '3 3' }" />
      <text v-if="i === 0" :x="b.x + b.w / 2" :y="sy(b.to) + 22" text-anchor="middle" :style="{ fill: '#0f172a', fontSize: '15px', fontWeight: 700 }">{{ b.add }}</text>
      <text v-else :x="b.x + b.w / 2" :y="sy(b.from) + 20" text-anchor="middle" :style="{ fill: '#fde68a', fontSize: '15px', fontWeight: 700 }">+{{ b.add }}</text>
      <text :x="b.x + b.w / 2" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#fbbf24', fontSize: '13px', fontWeight: 700 }">{{ b.label }}</text>
      <text :x="b.x + b.w / 2" :y="Bot + 34" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ b.note }}</text>
    </g>
    <line v-if="bars[3 - 1]" :x1="bars[2].x + bars[2].w" :x2="sumBar.x" :y1="sy(run)" :y2="sy(run)" :style="{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '3 3' }" />
    <rect :x="sumBar.x" :y="sy(sumBar.to)" :width="sumBar.w" :height="sy(0) - sy(sumBar.to)" rx="3" :style="{ fill: '#a78bfa', fillOpacity: 0.8 }" />
    <text :x="sumBar.x + sumBar.w / 2" :y="sy(sumBar.to) + 22" text-anchor="middle" :style="{ fill: '#0f172a', fontSize: '15px', fontWeight: 700 }">{{ sumBar.to }}</text>
    <text :x="sumBar.x + sumBar.w / 2" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#a78bfa', fontSize: '13px', fontWeight: 700 }">sum F₃</text>
    <text :x="sumBar.x + sumBar.w / 2" :y="Bot + 34" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">250 + 40 + 8</text>
  </svg>
</template>
