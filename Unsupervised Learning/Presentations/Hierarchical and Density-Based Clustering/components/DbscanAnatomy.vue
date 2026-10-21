<script setup lang="ts">
// DBSCAN's three kinds of point on 20 points (data/anatomy.json), ε = 1, minPts = 4 (the point itself counts).
// stage 0 plain points · 1 one point's ε-ball and its count · 2 every ε-ball and count
// 3 core points · 4 border points (linked to a core neighbor) · 5 noise · 6 the two clusters.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/anatomy.json'
import { color, equalScale } from '../utils/clusters'

const { $clicks } = useSlideContext()
const s = computed(() => Math.min($clicks.value, 6))
const W = 600; const H = 340
const S = equalScale({ x: [-1.05, 9.45], y: [-1.05, 5.85] }, W, H)
const rEps = d.eps * S.kx
const n = d.pts.length
const dist = (i: number, j: number) => Math.hypot(d.pts[i][0] - d.pts[j][0], d.pts[i][1] - d.pts[j][1])
// the example: the core point with the most neighbors
const ex = d.count.indexOf(Math.max(...d.count))
const exNb = new Set(Array.from({ length: n }, (_, j) => j).filter(j => dist(ex, j) <= d.eps))
const kind = (i: number) => (d.core[i] ? 'core' : d.lab[i] >= 0 ? 'border' : 'noise')
const borderLink = Array.from({ length: n }, (_, i) => {
  if (kind(i) !== 'border') return null
  let best = -1; let bd = Infinity
  for (let j = 0; j < n; j++) if (d.core[j] && dist(i, j) <= d.eps && dist(i, j) < bd) { bd = dist(i, j); best = j }
  return best
})
const KIND = { core: '#2dd4bf', border: '#fbbf24', noise: '#f87171' } as const
function fill(i: number) {
  if (s.value >= 6) return d.lab[i] >= 0 ? color(d.lab[i]) : '#94a3b8'
  const k = kind(i)
  if (s.value >= 3 && k === 'core') return KIND.core
  if (s.value >= 4 && k === 'border') return KIND.border
  if (s.value >= 5 && k === 'noise') return KIND.noise
  if (s.value === 1) return exNb.has(i) ? '#e2e8f0' : '#64748b'
  return '#cbd5e1'
}
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Points with their epsilon-balls; core, border and noise points colored">
    <g class="fade" :style="{ opacity: s >= 2 && s < 6 ? 1 : 0 }">
      <circle v-for="(p, i) in d.pts" :key="`b${i}`" :cx="S.sx(p[0])" :cy="S.sy(p[1])" :r="rEps" :style="{ fill: 'none', stroke: s >= 3 && d.core[i] ? '#2dd4bf' : '#94a3b8', strokeOpacity: s >= 3 && d.core[i] ? 0.35 : 0.18, strokeWidth: 1 }" />
    </g>
    <g class="fade" :style="{ opacity: s === 1 ? 1 : 0 }">
      <circle :cx="S.sx(d.pts[ex][0])" :cy="S.sy(d.pts[ex][1])" :r="rEps" :style="{ fill: 'rgba(45,212,191,0.12)', stroke: '#2dd4bf', strokeWidth: 2 }" />
      <line :x1="S.sx(d.pts[ex][0])" :y1="S.sy(d.pts[ex][1])" :x2="S.sx(d.pts[ex][0]) + rEps" :y2="S.sy(d.pts[ex][1])" :style="{ stroke: '#2dd4bf', strokeWidth: 1.5, strokeDasharray: '3 3' }" />
      <text :x="S.sx(d.pts[ex][0]) + rEps / 2" :y="S.sy(d.pts[ex][1]) - 6" text-anchor="middle" :style="{ fill: '#2dd4bf', fontSize: '14px', fontWeight: 700 }">ε</text>
    </g>
    <g class="fade" :style="{ opacity: s >= 4 && s < 6 ? 1 : 0 }">
      <template v-for="(j, i) in borderLink" :key="`l${i}`">
        <line v-if="j !== null" :x1="S.sx(d.pts[i][0])" :y1="S.sy(d.pts[i][1])" :x2="S.sx(d.pts[j][0])" :y2="S.sy(d.pts[j][1])" :style="{ stroke: '#fbbf24', strokeWidth: 2, strokeDasharray: '4 3' }" />
      </template>
    </g>
    <g v-for="(p, i) in d.pts" :key="i">
      <circle :cx="S.sx(p[0])" :cy="S.sy(p[1])" :r="i === ex && s === 1 ? 9 : 7" class="pt" :style="{ fill: fill(i), stroke: '#0b1020', strokeWidth: 2 }" />
      <g v-if="s >= 5 && s < 6 && kind(i) === 'noise'">
        <path :d="`M${S.sx(p[0]) - 12},${S.sy(p[1]) - 12}l24,24m0,-24l-24,24`" :style="{ stroke: '#f87171', strokeWidth: 2 }" />
      </g>
      <text v-if="s === 2 || (s === 1 && i === ex)" :x="S.sx(p[0]) + 9" :y="S.sy(p[1]) - 9" :style="{ fill: d.count[i] >= d.minPts ? '#5eead4' : '#e2e8f0', fontSize: '13px', fontWeight: 700, paintOrder: 'stroke', stroke: '#0b1020', strokeWidth: 3 }">{{ d.count[i] }}</text>
    </g>
  </svg>
</template>

<style scoped>
.pt { transition: fill 0.5s ease, r 0.3s ease; }
.fade { transition: opacity 0.5s ease; }
</style>
