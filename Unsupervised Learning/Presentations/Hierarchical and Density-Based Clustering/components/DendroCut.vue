<script setup lang="ts">
// Ward dendrogram of all 300 blobs3 points (data/dendro.json) and a horizontal cut that moves with clicks.
// Links below the cut take their cluster's color; the scatter shows the same flat clustering.
// Ks[i] = number of clusters after i clicks.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/dendro.json'
import { color, linkPath, useTween } from '../utils/clusters'

const props = withDefaults(defineProps<{ Ks?: number[] }>(), { Ks: () => [2, 3, 4, 6] })
const { $clicks } = useSlideContext()
const K = computed(() => props.Ks[Math.min($clicks.value, props.Ks.length - 1)])
const lab = computed(() => (d.labs as Record<string, number[]>)[K.value])
const cut = computed(() => (d.cuts as Record<string, number>)[K.value])
const n = d.pts.length

const W = 460; const H = 330; const L = 46; const R = 452; const T = 12; const B = 312
const hmax = Math.max(...d.h) * 1.05
const at = (pos: number, h: number): [number, number] => [L + (pos + 0.5) / n * (R - L), B - h / hmax * (B - T)]
const cy = useTween(() => [at(0, cut.value)[1]], 650)
const ticks = [0, 10, 20, 30, 40]
const links = Array.from({ length: n - 1 }, (_, i) => linkPath(d, i, at))
</script>

<template>
  <div class="grid grid-cols-[1.1fr_1fr] gap-5 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`Dendrogram of 300 points cut into ${K} clusters`">
      <line :x1="L" :x2="L" :y1="T" :y2="B" :style="{ stroke: '#475569' }" />
      <g v-for="v in ticks" :key="v">
        <line :x1="L - 4" :x2="L" :y1="at(0, v)[1]" :y2="at(0, v)[1]" :style="{ stroke: '#475569' }" />
        <text :x="L - 8" :y="at(0, v)[1] + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v }}</text>
      </g>
      <text x="12" :y="(T + B) / 2" text-anchor="middle" :transform="`rotate(-90 12 ${(T + B) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">merge height (Ward)</text>
      <path
        v-for="(p, i) in links" :key="i" :d="p" class="lk"
        :style="{ stroke: d.h[n + i] < cut ? color(lab[d.rep[n + i]]) : '#94a3b8', strokeWidth: d.h[n + i] < cut ? 1.1 : 2, fill: 'none' }"
      />
      <line :x1="L" :x2="R" :y1="cy[0]" :y2="cy[0]" :style="{ stroke: '#fbbf24', strokeWidth: 2, strokeDasharray: '7 5' }" />
      <text :x="R - 4" :y="cy[0] - 7" text-anchor="end" :style="{ fill: '#fbbf24', fontSize: '13px', fontWeight: 700 }">cut → K = {{ K }}</text>
    </svg>
    <ClusterPlot :pts="d.pts" :lab="lab" :w="400" :h="330" :r="3.4" frame :label="`blobs3 colored by the ${K}-cluster cut`" />
  </div>
</template>

<style scoped>
.lk { transition: stroke 0.5s ease; }
</style>
