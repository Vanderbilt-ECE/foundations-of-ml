<script setup lang="ts">
// Test MSE on 2,000 held-out California rows as trees are added (data/ntrees.json).
//   oob=false: one tree (dashed), bagging, random forest
//   oob=true:  random forest test MSE with its out-of-bag estimate overlaid
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/ntrees.json'

const props = withDefaults(defineProps<{ oob?: boolean }>(), { oob: false })

const W = 560
const H = 300
const L = 54
const R = 432
const T = 16
const Bot = 252
const lo = 0.28
const hi = 0.76
const maxB = 500
const sx = (B: number) => L + Math.log(B) / Math.log(maxB) * (R - L)
const sy = (v: number) => Bot - (Math.min(hi, v) - lo) / (hi - lo) * (Bot - T)
const path = (vals: (number | null)[]) => d.B
  .map((B, i) => (vals[i] == null ? null : `${sx(B).toFixed(1)},${sy(vals[i] as number).toFixed(1)}`))
  .filter(Boolean).join(' ')
const last = (vals: (number | null)[]) => vals[vals.length - 1] as number

const series = props.oob
  ? [
      { key: 'rf', label: 'RF test', color: '#2dd4bf', pts: path(d.rf), end: last(d.rf), dash: 'none' },
      { key: 'rfOob', label: 'RF out-of-bag', color: '#f87171', pts: path(d.rfOob), end: last(d.rfOob), dash: '7 5' },
    ]
  : [
      { key: 'bag', label: 'bagging', color: '#60a5fa', pts: path(d.bag), end: last(d.bag), dash: 'none' },
      { key: 'rf', label: 'random forest', color: '#2dd4bf', pts: path(d.rf), end: last(d.rf), dash: 'none' },
    ]
const yTicks = [0.3, 0.4, 0.5, 0.6, 0.7]
const xTicks = [1, 2, 5, 10, 20, 50, 100, 200, 500]
// keep end labels from colliding
const labelY = series.map(s => sy(s.end))
if (Math.abs(labelY[0] - labelY[1]) < 16) {
  const mid = (labelY[0] + labelY[1]) / 2
  const up = labelY[0] < labelY[1] ? 0 : 1
  labelY[up] = mid - 8
  labelY[1 - up] = mid + 8
}
</script>

<template>
  <svg role="img" :aria-label="oob ? `Random forest test MSE and out-of-bag MSE against number of trees; at 500 trees test ${last(d.rf)}, out-of-bag ${last(d.rfOob)}` : `Test MSE against number of trees: one tree ${d.tree}; bagging levels off at ${last(d.bag)}; random forest levels off at ${last(d.rf)}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in xTicks" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="Bot" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="Bot" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="L" :y1="T" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <template v-if="!oob">
      <line :x1="L" :x2="R" :y1="sy(d.tree)" :y2="sy(d.tree)" :style="{ stroke: '#fbbf24', strokeWidth: 1.5, strokeDasharray: '6 5' }" />
      <text :x="R + 6" :y="sy(d.tree) + 4" :style="{ fill: '#fbbf24', fontSize: '12px', fontWeight: 700 }">one tree {{ d.tree.toFixed(3) }}</text>
    </template>
    <g v-for="(s, k) in series" :key="s.key">
      <polyline :points="s.pts" :style="{ fill: 'none', stroke: s.color, strokeWidth: 3.5, strokeLinejoin: 'round', strokeDasharray: s.dash }" />
      <text :x="R + 6" :y="labelY[k] + 4" :style="{ fill: s.color, fontSize: '12px', fontWeight: 700 }">{{ s.label }} {{ s.end.toFixed(3) }}</text>
    </g>
    <text v-for="t in yTicks" :key="`y${t}`" :x="L - 8" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t.toFixed(1) }}</text>
    <text v-for="t in xTicks" :key="`x${t}`" :x="sx(t)" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text :x="(L + R) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">number of trees B (log scale)</text>
    <text x="14" :y="(T + Bot) / 2" text-anchor="middle" :transform="`rotate(-90 14 ${(T + Bot) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">MSE</text>
  </svg>
</template>
