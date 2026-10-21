<script setup lang="ts">
// Choosing ε with the k-distance plot (data/kdist.json; the moons + noise data, minPts = 5).
// Left: every point's distance to its 4th-nearest other point, sorted. A point is core exactly when
// this distance is ≤ ε, so the horizontal line splits core (below) from non-core (above).
// The shaded band is every ε that gives exactly the two moons. Right: DBSCAN with that ε.
// Clicks step through ε too small → too large → just past the bend.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/kdist.json'
import { useTween } from '../utils/clusters'

const { $clicks } = useSlideContext()
const seq = [0, 2, 1] // runs are stored as [too small, picked, too large]
const run = computed(() => d.runs[seq[Math.min($clicks.value, 2)]])
const W = 420; const H = 330; const L = 50; const R = 410; const T = 14; const B = 290
const n = d.kd.length
const ymax = 0.55
const X = (i: number) => L + i / (n - 1) * (R - L)
const Y = (v: number) => B - Math.min(v, ymax) / ymax * (B - T)
const curve = d.kd.map((v, i) => `${i ? 'L' : 'M'}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join('')
const ly = useTween(() => [Y(run.value.eps)], 600)
const below = computed(() => d.kd.filter(v => v <= run.value.eps).length)
const verdict = computed(() => [
  'Too small: most points are not core, so the moons shatter into fragments and noise.',
  'Just past the bend: the dense points fall below the line, the scattered ones rise sharply above it.',
  'Too large: even scattered points become core, and everything merges into one cluster.',
][seq[Math.min($clicks.value, 2)]])
</script>

<template>
  <div>
    <div class="grid grid-cols-[1fr_1.05fr] gap-5 items-center">
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Sorted distance to the 4th nearest neighbor, with a horizontal line at the chosen epsilon">
        <line :x1="L" :x2="R" :y1="B" :y2="B" :style="{ stroke: '#475569' }" />
        <line :x1="L" :x2="L" :y1="T" :y2="B" :style="{ stroke: '#475569' }" />
        <g v-for="v in [0, 0.1, 0.2, 0.3, 0.4, 0.5]" :key="v">
          <text :x="L - 7" :y="Y(v) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v.toFixed(1) }}</text>
        </g>
        <text :x="(L + R) / 2" :y="H - 12" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">points, sorted by that distance</text>
        <text x="13" :y="(T + B) / 2" text-anchor="middle" :transform="`rotate(-90 13 ${(T + B) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">distance to 4th-nearest neighbor</text>
        <rect :x="L" :y="ly[0]" :width="X(below) - L" :height="B - ly[0]" :style="{ fill: 'rgba(45,212,191,0.10)' }" />
        <path :d="curve" :style="{ stroke: '#e2e8f0', strokeWidth: 2.2, fill: 'none' }" />
        <rect :x="L" :y="Y(d.good[1])" :width="R - L" :height="Y(d.good[0]) - Y(d.good[1])" :style="{ fill: 'rgba(251,191,36,0.10)' }" />
        <text :x="L + 6" :y="Y(d.good[1]) + 13" :style="{ fill: '#fbbf24', fontSize: '11px' }">ε in {{ d.good[0] }}–{{ d.good[1] }}: two moons</text>
        <circle :cx="X(d.pickRank)" :cy="Y(d.pick)" r="5" :style="{ fill: '#fbbf24' }" />
        <text :x="X(d.pickRank) - 8" :y="Y(d.pick) + 4" text-anchor="end" :style="{ fill: '#fbbf24', fontSize: '12px', fontWeight: 700 }">bend</text>
        <line :x1="L" :x2="R" :y1="ly[0]" :y2="ly[0]" :style="{ stroke: '#2dd4bf', strokeWidth: 2, strokeDasharray: '7 5' }" />
        <text :x="L + 8" :y="ly[0] - 7" :style="{ fill: '#2dd4bf', fontSize: '13px', fontWeight: 700 }">ε = {{ run.eps }} · {{ below }} core</text>
      </svg>
      <div>
        <ClusterPlot :pts="d.pts" :lab="run.lab" frame :w="420" :h="300" :r="3" :label="`DBSCAN with epsilon ${run.eps}`" />
        <div class="text-center font-mono text-sm mt-1">{{ run.k }} cluster{{ run.k === 1 ? '' : 's' }} · {{ run.noise }} noise</div>
      </div>
    </div>
    <div class="text-sm text-center mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 2.6em">{{ verdict }}</div>
  </div>
</template>
