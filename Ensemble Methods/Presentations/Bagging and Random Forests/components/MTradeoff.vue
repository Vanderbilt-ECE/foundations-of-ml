<script setup lang="ts">
// How max_features (m) trades tree strength against correlation, on California housing
// (data/mtradeoff.json, averaged over 20 training sets of 2,000 rows).
//   panel="parts": σ² of one tree and ρ between trees, each against m
//   panel="mse":   test MSE of the 200-tree forest against m
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/mtradeoff.json'

const props = withDefaults(defineProps<{ panel: 'parts' | 'mse' }>(), {})

const rows = d.rows
const W = 440
const L = 56
const R = 420
const sx = (m: number) => L + (m - 1) / 7 * (R - L)

function series(key: 'sigma2' | 'rho' | 'mse', top: number, bot: number, lo: number, hi: number) {
  const sy = (v: number) => bot - (v - lo) / (hi - lo) * (bot - top)
  return {
    top, bot, sy,
    pts: rows.map(r => ({ m: r.m, v: r[key], cx: sx(r.m), cy: sy(r[key]) })),
    line: rows.map(r => `${sx(r.m).toFixed(1)},${sy(r[key]).toFixed(1)}`).join(' '),
  }
}

const H = props.panel === 'parts' ? 330 : 300
const charts = props.panel === 'parts'
  ? [
      { ...series('sigma2', 34, 132, 0.3, 0.7), title: 'σ²: variance of one tree', color: '#fbbf24', ticks: [0.3, 0.5, 0.7], fmt: (v: number) => v.toFixed(2) },
      { ...series('rho', 190, 288, 0, 0.08), title: 'ρ: correlation between trees', color: '#2dd4bf', ticks: [0, 0.04, 0.08], fmt: (v: number) => v.toFixed(3) },
    ]
  : [
      { ...series('mse', 34, 252, 0.29, 0.37), title: 'Test MSE of the forest', color: '#2dd4bf', ticks: [0.29, 0.31, 0.33, 0.35, 0.37], fmt: (v: number) => v.toFixed(3) },
    ]
const best = rows.reduce((a, b) => (b.mse < a.mse ? b : a))
const xLabelY = H - 4
</script>

<template>
  <svg role="img" :aria-label="panel === 'parts' ? 'As m grows from 1 to 8, the variance of one tree falls from 0.62 to 0.41 while the correlation between trees rises from 0.019 to 0.075' : `Forest test MSE against m: lowest at m = ${best.m} (${best.mse}), ${rows[7].mse} at m = 8 (bagging), ${rows[0].mse} at m = 1`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <g v-for="c in charts" :key="c.title">
      <text :x="L" :y="c.top - 12" :style="{ fill: c.color, fontSize: '14px', fontWeight: 700 }">{{ c.title }}</text>
      <line v-for="t in c.ticks" :key="t" :x1="L" :x2="R" :y1="c.sy(t)" :y2="c.sy(t)" :style="{ stroke: '#334155', strokeWidth: 1 }" />
      <text v-for="t in c.ticks" :key="`t${t}`" :x="L - 8" :y="c.sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '11px' }">{{ t }}</text>
      <line :x1="L" :x2="R" :y1="c.bot" :y2="c.bot" :style="{ stroke: '#64748b', strokeWidth: 1.5 }" />
      <polyline :points="c.line" :style="{ fill: 'none', stroke: c.color, strokeWidth: 3, strokeLinejoin: 'round' }" />
      <circle v-for="p in c.pts" :key="p.m" :cx="p.cx" :cy="p.cy" r="4.5" :style="{ fill: c.color }" />
    </g>
    <template v-if="panel === 'mse'">
      <circle :cx="sx(best.m)" :cy="charts[0].sy(best.mse)" r="9" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 2.5 }" />
      <text :x="sx(best.m)" :y="charts[0].sy(best.mse) + 26" text-anchor="middle" :style="{ fill: '#fbbf24', fontSize: '13px', fontWeight: 700 }">best: m = {{ best.m }} ({{ best.mse.toFixed(3) }})</text>
      <text :x="sx(8)" :y="charts[0].sy(rows[7].mse) - 14" text-anchor="end" :style="{ fill: '#93c5fd', fontSize: '12px' }">m = 8 is bagging ({{ rows[7].mse.toFixed(3) }})</text>
      <text :x="sx(1) + 10" :y="charts[0].sy(0.37) + 14" :style="{ fill: '#cbd5e1', fontSize: '12px' }">m = 1: {{ rows[0].mse.toFixed(3) }}</text>
    </template>
    <text v-for="r in rows" :key="`x${r.m}`" :x="sx(r.m)" :y="charts[charts.length - 1].bot + 16" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ r.m }}</text>
    <text :x="(L + R) / 2" :y="xLabelY" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">m = features considered per split</text>
  </svg>
</template>
