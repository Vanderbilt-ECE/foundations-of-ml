<script setup lang="ts">
// Why EM never goes downhill (data/bound.json). A 1D two-component model where only mu_1 is free.
// White: log L(mu_1). Each E-step builds a lower bound (colored) that touches log L at the current mu_1;
// the M-step jumps to the top of that bound. The new point is at least as high on log L.
//   step 0: log L and the start mu_1 = -3 · step s >= 1: bound s and the jump it makes
import { computed } from 'vue'
import d from '../data/bound.json'
import { useTween } from '../utils/clusters'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const W = 620; const H = 330; const X0 = -4; const X1 = 4; const Y0 = -1000; const Y1 = -370
const sx = (x: number) => 50 + (x - X0) / (X1 - X0) * (W - 70)
const sy = (y: number) => 20 + (Y1 - y) / (Y1 - Y0) * (H - 60)
const idx = d.grid.map((g, i) => (g >= X0 - 1e-9 && g <= X1 + 1e-9 ? i : -1)).filter(i => i >= 0)
const path = (ys: number[]) => idx.map((i, j) => `${j ? 'L' : 'M'}${sx(d.grid[i]).toFixed(1)},${sy(Math.max(ys[i], Y0 - 200)).toFixed(1)}`).join('')
const llPath = path(d.ll)
const COLORS = ['#2dd4bf', '#fbbf24', '#a78bfa', '#60a5fa']
const n = computed(() => Math.max(0, Math.min(3, props.step)))
const pos = useTween(() => [n.value === 0 ? d.steps[0].mu : d.steps[n.value - 1].next], 900)
const llAt = (m: number) => {
  const i = d.grid.findIndex(g => g >= m)
  if (i <= 0) return d.ll[0]
  const t = (m - d.grid[i - 1]) / (d.grid[i] - d.grid[i - 1])
  return d.ll[i - 1] + t * (d.ll[i] - d.ll[i - 1])
}
const bmax = (s: number) => Math.max(...d.steps[s].bound)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="A log-likelihood curve with a sequence of lower-bound curves, each touching it at the current value and lifting the estimate toward the peak">
    <defs><clipPath id="bc-clip"><rect :x="sx(X0)" :y="sy(Y1)" :width="sx(X1) - sx(X0)" :height="sy(Y0) - sy(Y1)" /></clipPath></defs>
    <line :x1="sx(X0)" :x2="sx(X1)" :y1="sy(Y0)" :y2="sy(Y0)" :style="{ stroke: '#475569' }" />
    <g v-for="t in [-4, -3, -2, -1, 0, 1, 2, 3, 4]" :key="t">
      <text :x="sx(t)" :y="sy(Y0) + 16" text-anchor="middle" :style="{ fill: '#64748b', fontSize: '11px' }">{{ t }}</text>
    </g>
    <text :x="sx(X1)" :y="sy(Y0) + 32" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">μ₁ (μ₂ = 4, σ = 1, π = ½ fixed)</text>
    <text :x="sx(X0)" :y="sy(Y1) - 6" :style="{ fill: '#94a3b8', fontSize: '12px' }">log-likelihood of 200 points</text>
    <g clip-path="url(#bc-clip)">
      <path :d="llPath" :style="{ fill: 'none', stroke: '#f8fafc', strokeWidth: 3 }" />
      <template v-for="s in 3" :key="s">
        <path
          :d="path(d.steps[s - 1].bound)" pathLength="1" class="bnd" :class="{ on: n >= s }"
          :style="{ fill: 'none', stroke: COLORS[s - 1], strokeWidth: 2.5, strokeOpacity: n === s ? 1 : 0.35 }"
        />
      </template>
    </g>
    <template v-for="s in 3" :key="`a${s}`">
      <g v-if="n >= s" :style="{ opacity: n === s ? 1 : 0.35 }">
        <line :x1="sx(d.steps[s - 1].next)" :x2="sx(d.steps[s - 1].next)" :y1="sy(bmax(s - 1))" :y2="sy(llAt(d.steps[s - 1].next))" :style="{ stroke: COLORS[s - 1], strokeWidth: 1.5, strokeDasharray: '3 3' }" />
        <circle :cx="sx(d.steps[s - 1].next)" :cy="sy(bmax(s - 1))" r="4.5" :style="{ fill: COLORS[s - 1] }" />
      </g>
    </template>
    <circle :cx="sx(pos[0])" :cy="sy(llAt(pos[0]))" r="7.5" :style="{ fill: '#f8fafc', stroke: '#0b1020', strokeWidth: 2.5 }" />
    <text :x="sx(pos[0])" :y="sy(llAt(pos[0])) - 14" text-anchor="middle" :style="{ fill: '#f8fafc', fontSize: '13px', fontWeight: 700 }">μ₁ = {{ pos[0].toFixed(2) }}</text>
  </svg>
</template>

<style scoped>
.bnd { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 1.1s ease, stroke-opacity 0.4s; }
.bnd.on { stroke-dashoffset: 0; }
</style>
