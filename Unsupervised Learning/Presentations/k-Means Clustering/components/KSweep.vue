<script setup lang="ts">
// Sweep K on blobs6 (data/blobs6.json → sweep). Each click shows the next K in `ks`:
// the clustering on the left, and the elbow (J) and mean-silhouette curves drawn up to it.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/blobs6.json'
import { domainOf } from '../utils/kmeans'

const props = withDefaults(defineProps<{ ks?: number[] }>(), { ks: () => [1, 2, 3, 4, 5, 6, 7, 8, 6] })
const { $clicks } = useSlideContext()
const idx = computed(() => Math.min($clicks.value, props.ks.length - 1))
const K = computed(() => props.ks[idx.value])
const reach = computed(() => Math.max(...props.ks.slice(0, idx.value + 1)))
const cur = computed(() => d.sweep[K.value - 1])
const final = computed(() => idx.value === props.ks.length - 1)
const dom = domainOf(d.pts as number[][], 0.05)

const W = 300; const L = 46; const R = 288
const sx = (k: number) => L + (k - 1) / 7 * (R - L)
const jmax = d.sweep[0].J
const charts = [
  { key: 'J', title: 'Elbow: within-cluster SS  J', color: '#fbbf24', T: 24, B: 150, lo: 0, hi: jmax, fmt: (v: number) => `${Math.round(v / 1000)}k` },
  { key: 'sil', title: 'Mean silhouette (higher = better)', color: '#2dd4bf', T: 200, B: 318, lo: 0.3, hi: 0.75, fmt: (v: number) => v.toFixed(2) },
]
const sy = (c: typeof charts[number], v: number) => c.B - (v - c.lo) / (c.hi - c.lo) * (c.B - c.T)
const series = (c: typeof charts[number]) => d.sweep.filter(s => s.k <= reach.value && (s as any)[c.key] != null)
</script>

<template>
  <div class="grid grid-cols-[1.35fr_1fr] gap-5 items-center">
    <div class="relative">
      <ClusterPlot :pts="d.pts" :lab="cur.lab" :centroids="cur.c" :domain="dom" :w="520" :h="380" :r="2.8" :c-r="8" cells frame :label="`k-means with K = ${K}`" />
      <div class="absolute top-2 left-3 text-2xl font-bold">K = <span class="text-amber-300">{{ K }}</span></div>
    </div>
    <svg :viewBox="`0 0 ${W} 345`" class="w-full" role="img" :aria-label="`Elbow and silhouette curves for K from 1 to 8; both point to K = 6`">
      <g v-for="c in charts" :key="c.key">
        <text :x="L - 40" :y="c.T - 10" :style="{ fill: c.color, fontSize: '12px', fontWeight: 700 }">{{ c.title }}</text>
        <line :x1="L" :x2="R" :y1="c.B" :y2="c.B" :style="{ stroke: '#475569' }" />
        <line :x1="L" :x2="L" :y1="c.T" :y2="c.B" :style="{ stroke: '#475569' }" />
        <text :x="L - 6" :y="c.T + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ c.fmt(c.hi) }}</text>
        <text :x="L - 6" :y="c.B + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ c.fmt(c.lo) }}</text>
        <text v-for="k in 8" :key="k" :x="sx(k)" :y="c.B + 14" text-anchor="middle" :style="{ fill: k === K ? '#fff' : '#94a3b8', fontSize: '10px', fontWeight: k === K ? 700 : 400 }">{{ k }}</text>
        <polyline :points="series(c).map(s => `${sx(s.k)},${sy(c, (s as any)[c.key])}`).join(' ')" :style="{ fill: 'none', stroke: c.color, strokeWidth: 2.5 }" />
        <circle v-for="s in series(c)" :key="s.k" :cx="sx(s.k)" :cy="sy(c, (s as any)[c.key])" :r="s.k === K ? 6 : 3.5" class="dot" :style="{ fill: s.k === K ? '#fff' : c.color, stroke: c.color, strokeWidth: 2 }" />
        <text v-if="final && (cur as any)[c.key] != null" :x="sx(K) + 9" :y="sy(c, (cur as any)[c.key]) - 8" :style="{ fill: '#fff', fontSize: '11px', fontWeight: 700 }">{{ c.key === 'J' ? 'elbow' : 'peak' }}</text>
      </g>
      <text :x="(L + R) / 2" y="344" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">number of clusters K</text>
    </svg>
  </div>
</template>

<style scoped>
.dot { transition: r 0.3s ease, fill 0.3s ease; }
</style>
