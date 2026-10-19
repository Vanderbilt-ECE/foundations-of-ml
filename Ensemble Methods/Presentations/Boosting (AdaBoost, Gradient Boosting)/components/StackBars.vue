<script setup lang="ts">
// Test MSE on the 2,000 held-out California districts (data/stacking.json), same 2,000 training rows
// as the scoreboard. Three base models, then three ways of combining them. Shorter bars are better.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/stacking.json'

const rows = [
  { key: 'lin', label: 'linear regression', v: d.lin, color: '#fbbf24' },
  { key: 'rf', label: 'random forest', v: d.rf, color: '#2dd4bf' },
  { key: 'gb', label: 'gradient boosting', v: d.gb, color: '#a78bfa' },
  { key: 'avg', label: 'plain average of the 3', v: d.avg, color: '#94a3b8' },
  { key: 'blend', label: 'blending (80/20 split)', v: d.blend, color: '#f472b6' },
  { key: 'stack', label: 'stacking (5-fold)', v: d.stack, color: '#e879f9' },
]
const W = 640
const L = 210
const R = 580
const rowH = 38
const T = 8
const H = T + rows.length * rowH + 26
const max = 0.6
const sx = (v: number) => L + v / max * (R - L)
const ticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
</script>

<template>
  <svg role="img" :aria-label="`Test MSE on California housing: ${rows.map(r => `${r.label} ${r.v.toFixed(3)}`).join(', ')}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in ticks" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="T + rows.length * rowH" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="T + 3 * rowH" :y2="T + 3 * rowH" :style="{ stroke: '#64748b', strokeWidth: 1.5, strokeDasharray: '4 4' }" />
    <g v-for="(r, i) in rows" :key="r.key">
      <text :x="L - 12" :y="T + i * rowH + rowH / 2 + 5" text-anchor="end" :style="{ fill: r.color, fontSize: '14px', fontWeight: 700 }">{{ r.label }}</text>
      <rect :x="L" :y="T + i * rowH + 7" :width="sx(r.v) - L" :height="rowH - 14" rx="4" :style="{ fill: r.color, fillOpacity: 0.75 }" />
      <text :x="sx(r.v) + 8" :y="T + i * rowH + rowH / 2 + 5" :style="{ fill: '#e2e8f0', fontSize: '14px', fontWeight: 700 }">{{ r.v.toFixed(3) }}</text>
    </g>
    <text v-for="t in ticks" :key="`x${t}`" :x="sx(t)" :y="T + rows.length * rowH + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t.toFixed(1) }}</text>
  </svg>
</template>
