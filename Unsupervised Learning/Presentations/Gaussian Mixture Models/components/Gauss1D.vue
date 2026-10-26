<script setup lang="ts">
// A 1D Gaussian whose mean and standard deviation drift slowly, so the bell visibly slides (mu) and
// widens/narrows (sigma) while the area stays 1. Bands mark mu +- 1 sigma (68%) and mu +- 2 sigma (95%).
// The PDF export shows the standard normal.
import { computed, ref } from 'vue'
import { pdf1, useLoop } from '../utils/gmm'

const W = 560; const H = 260; const X0 = -5; const X1 = 5; const YMAX = 0.75
const sx = (x: number) => 20 + (x - X0) / (X1 - X0) * (W - 40)
const sy = (y: number) => H - 34 - y / YMAX * (H - 60)
const mu = ref(0); const sd = ref(1)
useLoop((_, t) => {
  mu.value = 1.6 * Math.sin(0.45 * t)
  sd.value = 1 + 0.45 * Math.sin(0.75 * t + 0.6)
}, () => { mu.value = 0; sd.value = 1 })

const curve = (a: number, b: number, close = false) => {
  let d = ''
  for (let i = 0; i <= 120; i++) {
    const x = a + (b - a) * i / 120
    d += `${i ? 'L' : 'M'}${sx(x).toFixed(1)},${sy(pdf1(x, mu.value, sd.value)).toFixed(1)}`
  }
  return close ? `${d}L${sx(b).toFixed(1)},${sy(0)}L${sx(a).toFixed(1)},${sy(0)}Z` : d
}
const line = computed(() => curve(X0, X1))
const band1 = computed(() => curve(mu.value - sd.value, mu.value + sd.value, true))
const band2 = computed(() => curve(mu.value - 2 * sd.value, mu.value + 2 * sd.value, true))
const peak = computed(() => sy(pdf1(mu.value, mu.value, sd.value)))
const ticks = [-4, -2, 0, 2, 4]
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="A bell curve sliding left and right and changing width; shaded bands mark one and two standard deviations">
      <line :x1="sx(X0)" :x2="sx(X1)" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#475569', strokeWidth: 1.5 }" />
      <g v-for="t in ticks" :key="t">
        <line :x1="sx(t)" :x2="sx(t)" :y1="sy(0)" :y2="sy(0) + 5" :style="{ stroke: '#475569' }" />
        <text :x="sx(t)" :y="sy(0) + 19" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">{{ t }}</text>
      </g>
      <path :d="band2" :style="{ fill: '#2dd4bf', fillOpacity: 0.12 }" />
      <path :d="band1" :style="{ fill: '#2dd4bf', fillOpacity: 0.25 }" />
      <path :d="line" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 3 }" />
      <line :x1="sx(mu)" :x2="sx(mu)" :y1="sy(0)" :y2="peak" :style="{ stroke: '#fbbf24', strokeWidth: 2, strokeDasharray: '4 4' }" />
      <circle :cx="sx(mu)" :cy="sy(0)" r="5" :style="{ fill: '#fbbf24' }" />
      <g :transform="`translate(0, ${sy(pdf1(mu + sd, mu, sd))})`">
        <line :x1="sx(mu)" :x2="sx(mu + sd)" y1="0" y2="0" :style="{ stroke: '#a78bfa', strokeWidth: 2.5 }" />
        <path :d="`M${sx(mu + sd) - 7},-5L${sx(mu + sd)},0L${sx(mu + sd) - 7},5`" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 2.5 }" />
        <text :x="(sx(mu) + sx(mu + sd)) / 2" y="-8" text-anchor="middle" :style="{ fill: '#c4b5fd', fontSize: '14px', fontWeight: 700 }">σ</text>
      </g>
      <text :x="sx(mu) - 8" :y="sy(0) - 10" text-anchor="end" :style="{ fill: '#fcd34d', fontSize: '14px', fontWeight: 700 }">μ</text>
      <text :x="sx(mu)" :y="sy(0) - 0.32 * (sy(0) - peak)" text-anchor="middle" :style="{ fill: '#0b1020', fontSize: '11px', fontWeight: 700 }">68%</text>
      <text :x="sx(mu - 1.5 * sd)" :y="sy(0) - 8" text-anchor="middle" :style="{ fill: '#99f6e4', fontSize: '10px' }">95%</text>
    </svg>
    <div class="flex justify-center gap-8 font-mono text-sm -mt-1">
      <span class="text-amber-300">μ = {{ mu.toFixed(2) }}</span>
      <span class="text-violet-300">σ = {{ sd.toFixed(2) }}</span>
      <span class="opacity-70">area = 1</span>
    </div>
  </div>
</template>
