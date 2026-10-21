<script setup lang="ts">
// k-means++ seeding on blobs6, one center per click (data/blobs6.json → kpp).
// After s centers are chosen, every point is sized and shaded by its chance of
// being picked next, ∝ D(x)² (squared distance to the nearest chosen center).
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/blobs6.json'
import { color, domainOf, equalScale } from '../utils/kmeans'

const { $clicks } = useSlideContext()
const n = computed(() => Math.min(1 + $clicks.value, d.kpp.length))
const W = 560; const H = 380
const S = equalScale(domainOf(d.pts as number[][], 0.05), W, H)
const pts = d.pts as number[][]
const chosen = computed(() => d.kpp.slice(0, n.value).map(i => pts[i]))
const prob = computed(() => {
  const d2 = pts.map(p => Math.min(...chosen.value.map(c => (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2)))
  const tot = d2.reduce((a, b) => a + b, 0)
  return d2.map(v => v / tot)
})
const pmax = computed(() => Math.max(...prob.value))
const next = computed(() => (n.value < d.kpp.length ? d.kpp[n.value] : null))
const done = computed(() => n.value >= d.kpp.length)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`k-means++ seeding: ${n} of 6 centers chosen; far-away points are more likely to be chosen next`">
    <rect x="1" y="1" :width="W - 2" :height="H - 2" rx="8" :style="{ fill: 'rgba(255,255,255,0.025)', stroke: 'rgba(255,255,255,0.08)' }" />
    <circle
      v-for="(p, i) in pts" :key="i" class="kp" :cx="S.sx(p[0])" :cy="S.sy(p[1])"
      :r="done ? 2.6 : 1.8 + 6 * Math.sqrt(prob[i] / pmax)"
      :style="{ fill: done ? '#64748b' : '#fbbf24', fillOpacity: done ? 0.55 : 0.15 + 0.75 * prob[i] / pmax }"
    />
    <circle v-if="next !== null && !done" :cx="S.sx(pts[next][0])" :cy="S.sy(pts[next][1])" r="15" class="ring" :style="{ fill: 'none', stroke: '#fff', strokeWidth: 2, strokeDasharray: '4 3' }" />
    <g v-for="(c, k) in chosen" :key="k" :transform="`translate(${S.sx(c[0])},${S.sy(c[1])})`" class="pick">
      <circle r="14" :style="{ fill: color(k), fillOpacity: 0.2 }" />
      <circle r="9" :style="{ fill: color(k), stroke: '#0b1020', strokeWidth: 2.5 }" />
      <text y="4" text-anchor="middle" :style="{ fill: '#0b1020', fontSize: '11px', fontWeight: 800 }">{{ k + 1 }}</text>
    </g>
  </svg>
</template>

<style scoped>
.kp { transition: r 0.6s ease, fill-opacity 0.6s ease, fill 0.6s ease; }
.ring { animation: spin 6s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spin { to { transform: rotate(360deg); } }
.pick { animation: drop 0.6s cubic-bezier(.2, 1.5, .4, 1); }
@keyframes drop { from { opacity: 0; } to { opacity: 1; } }
</style>
