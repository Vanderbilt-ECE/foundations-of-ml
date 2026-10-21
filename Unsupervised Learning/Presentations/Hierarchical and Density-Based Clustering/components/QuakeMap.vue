<script setup lang="ts">
// The 2024 M4.5+ earthquakes on a flat map centered on the Pacific (data/quakes.json), so the Ring of Fire is
// in one piece. stage 0: raw events · 1: k-means with K = 20 (on 3D unit vectors) · 2: DBSCAN (haversine,
// ε = 150 km, minPts = 10), gray = noise. Nearby clusters get different colors (assigned in make_data.py).
import { computed } from 'vue'
import d from '../data/quakes.json'
import { GRAY, PALETTE } from '../utils/clusters'

const props = withDefaults(defineProps<{ stage?: number }>(), { stage: 0 })
const W = 900; const lat0 = -66; const lat1 = 76
const H = W * (lat1 - lat0) / 360
const shift = (lon: number) => ((lon - 150 + 540) % 360) - 180 // 150°E at the center
const X = (lon: number) => (shift(lon) + 180) / 360 * W
const Y = (lat: number) => (lat1 - lat) / (lat1 - lat0) * H
const coast = d.coast.map((line) => {
  let p = ''
  let prev: number | null = null
  for (const [lo, la] of line) {
    const s = shift(lo)
    const jump = prev !== null && Math.abs(s - prev) > 180
    p += `${p && !jump ? 'L' : 'M'}${X(lo).toFixed(1)},${Y(la).toFixed(1)}`
    prev = s
  }
  return p
}).join('')
const fill = computed(() => d.lat.map((_, i) => {
  if (props.stage === 1) return PALETTE[d.kmCol[d.km[i]]]
  if (props.stage >= 2) return d.db[i] < 0 ? GRAY : PALETTE[d.dbCol[d.db[i]]]
  return '#e2e8f0'
}))
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="World map centered on the Pacific with 6,397 earthquakes, colored by cluster">
    <rect :width="W" :height="H" rx="8" :style="{ fill: 'rgba(255,255,255,0.025)' }" />
    <path :d="coast" :style="{ stroke: '#475569', strokeWidth: 1, fill: 'none' }" />
    <circle
      v-for="(la, i) in d.lat" :key="i" :cx="X(d.lon[i])" :cy="Y(la)" r="1.9" class="q"
      :style="{ fill: fill[i], fillOpacity: stage >= 2 && d.db[i] < 0 ? 0.55 : 0.85 }"
    />
  </svg>
</template>

<style scoped>
.q { transition: fill 0.6s ease; }
</style>
