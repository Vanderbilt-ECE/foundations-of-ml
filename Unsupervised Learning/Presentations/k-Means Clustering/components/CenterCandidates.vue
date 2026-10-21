<script setup lang="ts">
// Why the centroid is the mean: one cluster (skewed, so the candidates differ) with three candidate centers.
//   mean    coordinate-wise average          -> minimizes the sum of squared distances (J)
//   median  coordinate-wise median           -> minimizes the sum of absolute distances
//   middle  center of the bounding box       -> minimizes the largest distance
// Clicks: 0 = points only, 1 = the three candidates, 2 = their J values as bars.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import { domainOf, equalScale } from '../utils/kmeans'

// Illustrative skewed cluster (seeded): a dense core plus a tail up and to the right,
// so the three candidate centers separate visibly.
let seed = 7
const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296 }
const gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-9)) * Math.cos(2 * Math.PI * rnd())
const pts: number[][] = [
  ...Array.from({ length: 70 }, () => [gauss() * 0.7, gauss() * 0.7]),
  ...Array.from({ length: 22 }, () => { const t = -Math.log(rnd() + 1e-9) * 2.2; return [1 + t + gauss() * 0.4, 0.6 * t + gauss() * 0.5] }),
]

const avg = (v: number[]) => v.reduce((a, b) => a + b, 0) / v.length
const med = (v: number[]) => { const s = [...v].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2 }
const mid = (v: number[]) => (Math.min(...v) + Math.max(...v)) / 2
const xs = pts.map(p => p[0]); const ys = pts.map(p => p[1])
const J = (c: number[]) => pts.reduce((s, p) => s + (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2, 0)

const cands = [
  { name: 'Mean', c: [avg(xs), avg(ys)], col: '#2dd4bf' },
  { name: 'Median', c: [med(xs), med(ys)], col: '#60a5fa' },
  { name: 'Middle', c: [mid(xs), mid(ys)], col: '#fb923c' },
].map(d => ({ ...d, J: J(d.c) }))
const jmax = Math.max(...cands.map(d => d.J))

const W = 520; const H = 330
const S = equalScale(domainOf(pts, 0.08), W, H)
const { $clicks } = useSlideContext()
const shown = computed(() => $clicks.value >= 1)
const bars = computed(() => $clicks.value >= 2)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H + 90}`" class="w-full" role="img" aria-label="One cluster of points with its mean, median and middle marked, and the sum of squared distances for each">
    <rect x="1" y="1" :width="W - 2" :height="H - 2" rx="8" :style="{ fill: 'rgba(255,255,255,0.025)', stroke: 'rgba(255,255,255,0.08)' }" />
    <circle v-for="(p, i) in pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" r="3.4" :style="{ fill: '#94a3b8', fillOpacity: 0.7 }" />
    <g v-for="d in cands" :key="d.name" :style="{ opacity: shown ? 1 : 0, transition: 'opacity .5s' }" :transform="`translate(${S.sx(d.c[0]).toFixed(1)},${S.sy(d.c[1]).toFixed(1)})`">
      <circle r="10" :style="{ fill: d.col, stroke: '#0b1020', strokeWidth: 2.5 }" />
      <path d="M-4.5,0H4.5M0,-4.5V4.5" :style="{ stroke: '#0b1020', strokeWidth: 2.4 }" />
    </g>
    <!-- legend + J bars -->
    <g v-for="(d, i) in cands" :key="`b${i}`" :transform="`translate(14,${H + 16 + i * 24})`" :style="{ opacity: shown ? 1 : 0, transition: 'opacity .5s' }">
      <circle cx="6" cy="0" r="6" :style="{ fill: d.col }" />
      <text x="20" y="4" :style="{ fill: '#e2e8f0', fontSize: '13px', fontWeight: 700 }">{{ d.name }}</text>
      <g :style="{ opacity: bars ? 1 : 0, transition: 'opacity .5s' }">
        <rect x="90" y="-8" :width="(d.J / jmax) * 300" height="16" rx="3" :style="{ fill: d.col, fillOpacity: 0.55 }" />
        <text :x="90 + (d.J / jmax) * 300 + 8" y="4" :style="{ fill: '#cbd5e1', fontSize: '12px' }">J = {{ d.J.toFixed(0) }}{{ i === 0 ? ' (smallest)' : '' }}</text>
      </g>
    </g>
  </svg>
</template>
