<script setup lang="ts">
// The eigenvectors of Σ as axes through the data. Same 48 centered points as the projection slide (data/drag.json).
// PC1 (amber) and PC2 (violet) are drawn as full lines through the mean, with an arrow of length 2√λ (two standard
// deviations) and the eigenvalue at the tip. step 1 projects every point onto PC1, step 2 also onto PC2.
// Right: the eigenvalues, their sum (the total variance) and each one's share. The PDF export shows step 2.
import { computed } from 'vue'
import d from '../data/drag.json'
import { useActive } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const { isPrintMode } = useActive()
const s = computed(() => (isPrintMode.value ? 2 : props.step))

const W = 460; const H = 370; const U = 64
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U

const [l1, l2] = d.lam
const total = l1 + l2
const v1 = d.v1
const v2 = [-v1[1], v1[0]]
const axes = [
  { v: v1, lam: l1, color: '#fbbf24', name: 'PC1', sub: '₁' },
  { v: v2, lam: l2, color: '#a78bfa', name: 'PC2', sub: '₂' },
]
const proj = (p: number[], v: number[]) => {
  const t = p[0] * v[0] + p[1] * v[1]
  return [t * v[0], t * v[1]]
}
const pct = (l: number) => `${(100 * l / total).toFixed(1)}%`
</script>

<template>
  <div class="grid grid-cols-[1.3fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 420px" role="img" aria-label="Scatter plot of 48 points with the two eigenvectors of the covariance matrix drawn as axes; points are projected onto each axis">
      <!-- full axis lines through the mean -->
      <line v-for="a in axes" :key="`ax${a.name}`" :x1="sx(-8 * a.v[0])" :y1="sy(-8 * a.v[1])" :x2="sx(8 * a.v[0])" :y2="sy(8 * a.v[1])" :style="{ stroke: a.color, strokeOpacity: 0.35, strokeWidth: 1.2 }" />

      <!-- eigenvector arrows (length 2√λ) with their eigenvalues -->
      <defs>
        <marker v-for="a in axes" :id="`ep-${a.name}`" :key="`m${a.name}`" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 Z" :style="{ fill: a.color }" />
        </marker>
      </defs>
      <g v-for="a in axes" :key="`ar${a.name}`">
        <line :x1="sx(0)" :y1="sy(0)" :x2="sx(2 * Math.sqrt(a.lam) * a.v[0])" :y2="sy(2 * Math.sqrt(a.lam) * a.v[1])" :marker-end="`url(#ep-${a.name})`" :style="{ stroke: a.color, strokeWidth: 3.5 }" />
      </g>
      <!-- projections: faint connector from each point to its spot on the axis, and the projected dot -->
      <g v-for="(a, k) in axes" :key="`pr${a.name}`" :style="{ opacity: s >= k + 1 ? 1 : 0, transition: 'opacity 0.5s' }">
        <line v-for="(p, i) in d.pts" :key="i" :x1="sx(p[0])" :y1="sy(p[1])" :x2="sx(proj(p, a.v)[0])" :y2="sy(proj(p, a.v)[1])" :style="{ stroke: a.color, strokeOpacity: 0.16, strokeWidth: 1 }" />
        <circle v-for="(p, i) in d.pts" :key="`q${i}`" :cx="sx(proj(p, a.v)[0])" :cy="sy(proj(p, a.v)[1])" r="3.2" :style="{ fill: a.color }" />
      </g>

      <!-- the data -->
      <circle v-for="(p, i) in d.pts" :key="`p${i}`" :cx="sx(p[0])" :cy="sy(p[1])" r="3.8" :style="{ fill: '#e2e8f0', stroke: '#0b1020', strokeWidth: 1 }" />

      <circle :cx="sx(0)" :cy="sy(0)" r="3" :style="{ fill: '#0b1020', stroke: '#e2e8f0', strokeWidth: 1.5 }" />
      <g v-for="a in axes" :key="`lb${a.name}`">
        <g :transform="`translate(${Math.min(W - 40, Math.max(40, sx((2 * Math.sqrt(a.lam) + 0.75) * a.v[0])))}, ${sy((2 * Math.sqrt(a.lam) + 0.75) * a.v[1])})`">
          <rect x="-38" y="-13" width="76" height="24" rx="5" :style="{ fill: '#0b1020', fillOpacity: 0.85, stroke: a.color, strokeOpacity: 0.6 }" />
          <text text-anchor="middle" y="4" :style="{ fill: a.color, fontSize: '14px', fontWeight: 700 }">λ{{ a.sub }} = {{ a.lam.toFixed(2) }}</text>
        </g>
      </g>
    </svg>

    <div class="text-left space-y-4">
      <div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 class="text-sm">
        <b class="text-teal-300">The directions</b>
        <div class="opacity-85 mt-1">The eigenvectors of the covariance matrix Σ are the principal components: perpendicular directions through the center of the data. Projecting onto them gives each point its new coordinates.</div>
      </div>

      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono text-sm space-y-1.5">
        <div v-for="a in axes" :key="`r${a.name}`" class="flex justify-between">
          <span :style="{ color: a.color }">{{ a.name }} · λ{{ a.sub }} = {{ a.lam.toFixed(2) }}</span>
          <span :style="{ color: a.color }">{{ pct(a.lam) }}</span>
        </div>
        <div class="flex justify-between border-t border-white/10 pt-1.5">
          <span>λ₁ + λ₂ = {{ total.toFixed(2) }}</span>
          <span class="opacity-70 font-sans text-xs self-center">total variance</span>
        </div>
        <div class="h-3 rounded-sm overflow-hidden flex mt-1">
          <div :style="{ width: pct(l1), background: '#fbbf24' }" />
          <div :style="{ width: pct(l2), background: '#a78bfa' }" />
        </div>
      </div>
    </div>
  </div>
</template>
