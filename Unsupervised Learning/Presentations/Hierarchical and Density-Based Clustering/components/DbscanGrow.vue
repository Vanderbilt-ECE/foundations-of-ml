<script setup lang="ts">
// DBSCAN growing clusters (data/grow.json: moons + 14 scattered points, ε = 0.2, minPts = 5).
// Click 1: cluster 1 floods outward from its seed, one breadth-first wave at a time; the ε-balls of the
// newest wave show where it can reach next. Click 2: the same for cluster 2. Click 3: what is left is noise.
// Filled dots are core points; rings are border points (they join a cluster but do not extend it).
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/grow.json'
import { color, domainOf, equalScale, useTween } from '../utils/clusters'

const { $clicks } = useSlideContext()
const W = 560; const H = 340
const S = equalScale(domainOf(d.pts, 0.05), W, H)
const rEps = d.eps * S.kx
const maxW = [0, 1].map(k => Math.max(...d.wave.filter((_, i) => d.lab[i] === k)))
const w = useTween(() => [$clicks.value >= 1 ? maxW[0] + 0.99 : -1, $clicks.value >= 2 ? maxW[1] + 0.99 : -1], 2600)
const on = (i: number) => d.lab[i] >= 0 && d.wave[i] <= w.value[d.lab[i]]
const frontier = computed(() => d.pts.map((_, i) => i).filter(i => d.core[i] && d.lab[i] >= 0 && d.wave[i] === Math.floor(w.value[d.lab[i]]) && w.value[d.lab[i]] < maxW[d.lab[i]] + 0.9))
const count = (k: number) => d.lab.filter((l, i) => l === k && d.wave[i] <= w.value[k]).length
const noise = d.lab.filter(l => l < 0).length
</script>

<template>
  <div class="grid grid-cols-[1.5fr_1fr] gap-5 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Two moons; clusters spread outward from a seed point; leftover points are noise">
      <circle v-for="i in frontier" :key="`f${i}`" :cx="S.sx(d.pts[i][0])" :cy="S.sy(d.pts[i][1])" :r="rEps" :style="{ fill: color(d.lab[i]), fillOpacity: 0.07, stroke: color(d.lab[i]), strokeOpacity: 0.5, strokeWidth: 1 }" />
      <circle
        v-for="(p, i) in d.pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" class="pt"
        :r="on(i) ? 4.4 : 3.4"
        :style="{
          fill: on(i) ? (d.core[i] ? color(d.lab[i]) : '#0b1020') : ($clicks >= 3 && d.lab[i] < 0 ? '#f87171' : '#475569'),
          stroke: on(i) ? color(d.lab[i]) : 'none', strokeWidth: 2,
        }"
      />
      <g v-for="(sd, k) in d.seeds" :key="`s${k}`" class="fade" :style="{ opacity: $clicks > k ? 1 : 0 }">
        <circle :cx="S.sx(d.pts[sd][0])" :cy="S.sy(d.pts[sd][1])" r="10" :style="{ fill: 'none', stroke: '#fff', strokeWidth: 2 }" />
        <text :x="S.sx(d.pts[sd][0])" :y="S.sy(d.pts[sd][1]) - 15" text-anchor="middle" :style="{ fill: '#fff', fontSize: '12px', fontWeight: 700, paintOrder: 'stroke', stroke: '#0b1020', strokeWidth: 3 }">seed</text>
      </g>
    </svg>
    <div class="space-y-3 text-left">
      <div v-for="k in [0, 1]" :key="k" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 class="fade" :style="{ opacity: $clicks > k ? 1 : 0.35 }">
        <div class="flex items-baseline justify-between">
          <span class="font-bold" :style="{ color: color(k) }">Cluster {{ k + 1 }}</span>
          <span class="font-mono text-xl">{{ count(k) }}</span>
        </div>
        <div class="text-xs opacity-70">points reached · wave {{ Math.max(0, Math.floor(w[k])) }} of {{ maxW[k] }}</div>
      </div>
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 class="fade" :style="{ opacity: $clicks >= 3 ? 1 : 0.35 }">
        <div class="flex items-baseline justify-between">
          <span class="font-bold text-red-300">Noise</span>
          <span class="font-mono text-xl">{{ $clicks >= 3 ? noise : '—' }}</span>
        </div>
        <div class="text-xs opacity-70">never within ε of a core point</div>
      </div>
      <div class="text-xs opacity-70 flex gap-4">
        <span><span class="inline-block w-2.5 h-2.5 rounded-full mr-1" style="background: #2dd4bf" />core</span>
        <span><span class="inline-block w-2.5 h-2.5 rounded-full mr-1" style="border: 2px solid #2dd4bf" />border</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pt { transition: fill 0.3s ease, r 0.3s ease; }
.fade { transition: opacity 0.5s ease; }
</style>
