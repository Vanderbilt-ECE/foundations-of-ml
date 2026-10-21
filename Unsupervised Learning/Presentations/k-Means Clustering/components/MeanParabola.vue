<script setup lang="ts">
// Why the centroid is the mean: five 1D points and a candidate center c.
// Each point's squared distance is drawn as a square (area ∝ (x - c)²);
// below, the total J(c) traces a parabola whose minimum sits at the mean.
// c is chosen by the click count: cs[clicks].
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import { useTween } from '../utils/kmeans'

const props = withDefaults(defineProps<{ cs?: number[] }>(), { cs: () => [5.6, 1.2, 3.1] })
const xs = [1, 2, 2.5, 4, 6]
const mean = xs.reduce((a, b) => a + b) / xs.length
const J = (c: number) => xs.reduce((s, x) => s + (x - c) ** 2, 0)

const { $clicks } = useSlideContext()
const target = computed(() => props.cs[Math.min($clicks.value, props.cs.length - 1)])
const c = useTween(() => [target.value], 800)
const atMean = computed(() => Math.abs(target.value - mean) < 1e-6)

const W = 560; const L = 40; const R = 530
const lo = 0; const hi = 7
const sx = (v: number) => L + (v - lo) / (hi - lo) * (R - L)
const lineY = 190
const sq = 30 // px per unit of distance for the squares (area stays ∝ d²)
const pT = 252; const pB = 400
const jmax = J(hi)
const py = (v: number) => pB - Math.min(v, jmax) / jmax * (pB - pT)
const curve = Array.from({ length: 141 }, (_, i) => lo + i * (hi - lo) / 140).map(v => `${sx(v).toFixed(1)},${py(J(v)).toFixed(1)}`).join(' ')
const cols = ['#2dd4bf', '#60a5fa', '#a78bfa', '#fb923c', '#f472b6']
</script>

<template>
  <svg :viewBox="`0 0 ${W} 412`" class="w-full" role="img" :aria-label="`Five points on a line; the sum of squared distances to a center is smallest when the center is the mean, ${mean.toFixed(1)}`">
    <!-- squares: one per point, side = |x - c| -->
    <g v-for="(x, i) in xs" :key="i">
      <rect
        :x="x < c[0] ? sx(x) : sx(x) - Math.abs(x - c[0]) * sq"
        :y="lineY - Math.abs(x - c[0]) * sq - 2"
        :width="Math.abs(x - c[0]) * sq" :height="Math.abs(x - c[0]) * sq"
        :style="{ fill: cols[i], fillOpacity: 0.16, stroke: cols[i], strokeOpacity: 0.8, strokeWidth: 1.5 }"
      />
    </g>
    <line :x1="L" :x2="R" :y1="lineY" :y2="lineY" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <g v-for="t in 8" :key="`t${t}`">
      <line :x1="sx(t - 1)" :x2="sx(t - 1)" :y1="lineY" :y2="lineY + 6" :style="{ stroke: '#64748b' }" />
      <text :x="sx(t - 1)" :y="lineY + 19" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ t - 1 }}</text>
    </g>
    <circle v-for="(x, i) in xs" :key="`p${i}`" :cx="sx(x)" :cy="lineY" r="7" :style="{ fill: cols[i], stroke: '#0b1020', strokeWidth: 2 }" />
    <!-- candidate center -->
    <g :transform="`translate(${sx(c[0])},${lineY})`">
      <line y1="-150" y2="10" :style="{ stroke: '#fbbf24', strokeWidth: 1.5, strokeDasharray: '4 4' }" />
      <path d="M0,-11L11,0L0,11L-11,0Z" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2 }" />
      <text y="-156" text-anchor="middle" :style="{ fill: '#fbbf24', fontSize: '13px', fontWeight: 700 }">c = {{ c[0].toFixed(1) }}</text>
    </g>
    <!-- J(c) parabola -->
    <line :x1="L" :x2="R" :y1="pB" :y2="pB" :style="{ stroke: '#475569' }" />
    <polyline :points="curve" :style="{ fill: 'none', stroke: '#fbbf24', strokeOpacity: 0.55, strokeWidth: 2.5 }" />
    <line :x1="sx(mean)" :x2="sx(mean)" :y1="pT - 6" :y2="pB" :style="{ stroke: '#2dd4bf', strokeDasharray: '3 4', opacity: atMean ? 1 : 0, transition: 'opacity .5s' }" />
    <text :x="sx(mean) + 6" :y="pT + 4" :style="{ fill: '#2dd4bf', fontSize: '12px', fontWeight: 700, opacity: atMean ? 1 : 0, transition: 'opacity .5s' }">mean = {{ mean.toFixed(1) }}</text>
    <circle :cx="sx(c[0])" :cy="py(J(c[0]))" r="7" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2 }" />
    <text :x="sx(c[0]) + 12" :y="py(J(c[0])) - 8" :style="{ fill: '#fde68a', fontSize: '13px', fontWeight: 700 }">J(c) = {{ J(c[0]).toFixed(1) }}</text>
    <text :x="L" :y="pT - 10" :style="{ fill: '#94a3b8', fontSize: '11px' }">total squared distance J(c)</text>
  </svg>
</template>
