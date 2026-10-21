<script setup lang="ts">
// P(a given row is out-of-bag) = (1 − 1/n)^n for n = 1..40, approaching e^(−1) ≈ 0.368.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
const W = 460
const H = 270
const L = 50
const R = 440
const T = 16
const Bot = 228
const maxN = 40
const sx = (n: number) => L + (n - 1) / (maxN - 1) * (R - L)
const sy = (p: number) => Bot - p / 0.5 * (Bot - T)
const pts = Array.from({ length: maxN }, (_, i) => {
  const n = i + 1
  return { n, cx: sx(n), cy: sy((1 - 1 / n) ** n) }
})
const lim = Math.exp(-1)
const yTicks = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
const xTicks = [1, 10, 20, 30, 40]
</script>

<template>
  <svg role="img" aria-label="Probability a row is out-of-bag, (1 minus 1 over n) to the n, rising from 0 at n equals 1 toward 0.368" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in yTicks" :key="t" :x1="L" :x2="R" :y1="sy(t)" :y2="sy(t)" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="Bot" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="L" :y1="T" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="R" :y1="sy(lim)" :y2="sy(lim)" :style="{ stroke: '#f87171', strokeWidth: 1.8, strokeDasharray: '7 5' }" />
    <text :x="R" :y="sy(lim) - 8" text-anchor="end" :style="{ fill: '#fca5a5', fontSize: '13px', fontWeight: 700 }">e⁻¹ ≈ 0.368</text>
    <circle v-for="p in pts" :key="p.n" :cx="p.cx" :cy="p.cy" r="4" :style="{ fill: '#60a5fa' }" />
    <text v-for="t in yTicks" :key="`y${t}`" :x="L - 8" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text v-for="t in xTicks" :key="`x${t}`" :x="sx(t)" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text :x="(L + R) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">n (rows in the dataset)</text>
    <text x="14" :y="(T + Bot) / 2" text-anchor="middle" :transform="`rotate(-90 14 ${(T + Bot) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">P(row is out-of-bag)</text>
  </svg>
</template>
