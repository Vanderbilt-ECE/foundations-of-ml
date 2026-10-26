<script setup lang="ts">
// Free parameters of a K = 3 mixture as the number of features d grows, per covariance_type:
//   means Kd + weights (K-1) + covariances: spherical K · diag Kd · tied d(d+1)/2 · full K d(d+1)/2.
// At d = 2 these are the p badges of the previous slide (11, 14, 11, 17).
import { computed } from 'vue'
import { useActive } from '../utils/gmm'

const K = 3; const D = 30
const fns: { key: string, c: string, f: (d: number) => number }[] = [
  { key: 'full', c: '#2dd4bf', f: d => K * d + K * d * (d + 1) / 2 + K - 1 },
  { key: 'tied', c: '#a78bfa', f: d => K * d + d * (d + 1) / 2 + K - 1 },
  { key: 'diag', c: '#fbbf24', f: d => 2 * K * d + K - 1 },
  { key: 'spherical', c: '#60a5fa', f: d => K * d + K + K - 1 },
]
const W = 560; const H = 300; const YMAX = 1500
const sx = (d: number) => 50 + (d - 1) / (D - 1) * (W - 140)
const sy = (v: number) => H - 30 - v / YMAX * (H - 50)
const { active, isPrintMode } = useActive()
const on = computed(() => active.value || isPrintMode.value)
const path = (f: (d: number) => number) => Array.from({ length: D }, (_, i) => `${i ? 'L' : 'M'}${sx(i + 1).toFixed(1)},${sy(f(i + 1)).toFixed(1)}`).join('')
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Parameter count against number of features: the full-covariance line curves up quadratically, the others grow linearly">
    <line :x1="sx(1)" :x2="sx(D)" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#475569' }" />
    <line :x1="sx(1)" :x2="sx(1)" :y1="sy(0)" :y2="sy(YMAX)" :style="{ stroke: '#475569' }" />
    <g v-for="v in [0, 500, 1000, 1500]" :key="v">
      <text :x="sx(1) - 8" :y="sy(v) + 4" text-anchor="end" :style="{ fill: '#64748b', fontSize: '11px' }">{{ v }}</text>
    </g>
    <g v-for="d in [1, 10, 20, 30]" :key="`d${d}`">
      <text :x="sx(d)" :y="sy(0) + 16" text-anchor="middle" :style="{ fill: '#64748b', fontSize: '11px' }">{{ d }}</text>
    </g>
    <text :x="sx(D)" :y="sy(0) - 6" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">features d →</text>
    <text :x="sx(1) + 6" :y="sy(YMAX) + 4" :style="{ fill: '#94a3b8', fontSize: '12px' }">free parameters (K = 3)</text>
    <path v-for="(g, i) in fns" :key="g.key" :d="path(g.f)" pathLength="1" class="ln" :class="{ on }" :style="{ fill: 'none', stroke: g.c, strokeWidth: 3, transitionDelay: `${i * 250}ms` }" />
    <text v-for="g in fns" :key="`t${g.key}`" :x="sx(D) + 8" :y="sy(g.f(D)) + 4 + (g.key === 'spherical' ? 8 : g.key === 'diag' ? -4 : 0)" :style="{ fill: g.c, fontSize: '13px', fontWeight: 700 }">{{ g.key }} {{ g.f(D) }}</text>
  </svg>
</template>

<style scoped>
.ln { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 1.4s ease; }
.ln.on { stroke-dashoffset: 0; }
</style>
