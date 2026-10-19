<script setup lang="ts">
// Test MSE on the 2,000 held-out California districts, every model trained on the same 2,000 rows
// as in the bagging deck (data/cal_compare.json). Shorter bars are better.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/cal_compare.json'

const rows = [
  { key: 'tree', label: 'one deep tree', v: d.tree, color: '#fbbf24' },
  { key: 'bag', label: 'bagging, 500 trees', v: d.bag, color: '#60a5fa' },
  { key: 'rf', label: 'random forest, m = 3', v: d.rf, color: '#2dd4bf' },
  { key: 'stumps', label: 'boosted stumps, 2,000 rounds', v: d.stumps, color: '#c4b5fd' },
  { key: 'gb', label: `gradient boosting, ${d.gbIters} rounds`, v: d.gb, color: '#a78bfa' },
]
const W = 640
const L = 230
const R = 580
const rowH = 40
const T = 8
const H = T + rows.length * rowH + 26
const max = 0.6
const sx = (v: number) => L + v / max * (R - L)
const ticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
</script>

<template>
  <svg role="img" :aria-label="`Test MSE on California housing: ${rows.map(r => `${r.label} ${r.v.toFixed(3)}`).join(', ')}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in ticks" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="T + rows.length * rowH" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <g v-for="(r, i) in rows" :key="r.key">
      <text :x="L - 12" :y="T + i * rowH + rowH / 2 + 5" text-anchor="end" :style="{ fill: r.color, fontSize: '14px', fontWeight: 700 }">{{ r.label }}</text>
      <rect :x="L" :y="T + i * rowH + 8" :width="sx(r.v) - L" :height="rowH - 16" rx="4" :style="{ fill: r.color, fillOpacity: 0.75 }" />
      <text :x="sx(r.v) + 8" :y="T + i * rowH + rowH / 2 + 5" :style="{ fill: '#e2e8f0', fontSize: '14px', fontWeight: 700 }">{{ r.v.toFixed(3) }}</text>
    </g>
    <text v-for="t in ticks" :key="`x${t}`" :x="sx(t)" :y="T + rows.length * rowH + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t.toFixed(1) }}</text>
  </svg>
</template>
