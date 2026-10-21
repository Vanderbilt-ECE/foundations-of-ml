<script setup lang="ts">
// Wine, two features in very different units (data/wine.json). Driven by clicks:
//  0  raw units, drawn to the same scale on both axes (what Euclidean distance sees),
//     colored by k-means on raw data
//  1  the same points, now standardized: the raw clusters are just proline slices
//  2  recolored by k-means on the standardized data
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/wine.json'
import { color } from '../utils/kmeans'

const { $clicks } = useSlideContext()
const s = computed(() => Math.min($clicks.value, 2))
const W = 480; const H = 380; const L = 44; const R = 470; const T = 10; const B = 360
const pmin = d.range.proline[0]; const pmax = d.range.proline[1]
const kRaw = (R - L) / (pmax - pmin) // px per raw unit, both axes
const fmean = d.raw.reduce((a, p) => a + p[0], 0) / d.raw.length
const zlo = -1.8; const zhi = 3.2
const kz = Math.min((R - L) / (zhi - zlo), (B - T) / (zhi - zlo))
const zx = (v: number) => L + (v - zlo) * kz
const zy = (v: number) => B - (v - zlo) * kz
const pos = computed(() => d.raw.map((p, i) => (s.value === 0
  ? [L + (p[1] - pmin) * kRaw, (T + B) / 2 - (p[0] - fmean) * kRaw]
  : [zx(d.std[i][1]), zy(d.std[i][0])])))
const lab = computed(() => (s.value < 2 ? d.labRaw : d.labStd))
const ari = computed(() => (s.value < 2 ? d.ariRaw : d.ariStd))
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H + 10}`" class="w-full" role="img" :aria-label="s === 0 ? 'Wine data in raw units: proline spans over a thousand units, flavanoids about five, so the cloud is a flat line' : 'Wine data after standardizing both features'">
      <line :x1="L" :x2="R" :y1="B" :y2="B" :style="{ stroke: '#475569' }" />
      <line :x1="L" :x2="L" :y1="T" :y2="B" :style="{ stroke: '#475569' }" />
      <circle
        v-for="(p, i) in pos" :key="i" r="4.2" class="wp"
        :style="{ transform: `translate(${p[0]}px, ${p[1]}px)`, fill: color(lab[i]), transitionDelay: `${(i % 25) * 12}ms` }"
      />
      <text :x="(L + R) / 2" :y="H + 4" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '13px' }">{{ s === 0 ? `proline (raw: ${pmin}–${pmax})` : 'proline (standardized)' }}</text>
      <text x="16" :y="(T + B) / 2" text-anchor="middle" :transform="`rotate(-90 16 ${(T + B) / 2})`" :style="{ fill: '#cbd5e1', fontSize: '13px' }">{{ s === 0 ? `flavanoids (raw: ${d.range.flav[0]}–${d.range.flav[1]})` : 'flavanoids (standardized)' }}</text>
    </svg>
    <div class="mt-1 text-sm font-mono text-center" border="2 solid white/10" bg="black/40" rounded-lg px-3 py-1>
      agreement with grape variety (ARI): <span :class="s < 2 ? 'text-red-300' : 'text-teal-300'" class="font-bold">{{ ari.toFixed(2) }}</span>
    </div>
  </div>
</template>

<style scoped>
.wp { transition: transform 1.1s cubic-bezier(.6, 0, .3, 1), fill 0.6s ease; }
</style>
