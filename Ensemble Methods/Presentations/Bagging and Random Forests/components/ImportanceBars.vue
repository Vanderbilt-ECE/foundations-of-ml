<script setup lang="ts">
// Random-forest feature importance on California housing plus a meaningless RowID column
// (data/importance.json). Impurity-based (MDI) vs permutation importance on held-out rows,
// each normalized to sum to 1. Sorted by permutation importance.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/importance.json'

const props = withDefaults(defineProps<{ perm?: boolean }>(), { perm: true })

const order = d.names.map((_, i) => i).sort((a, b) => d.perm[b] - d.perm[a] || d.mdi[b] - d.mdi[a])
const W = 460
const rowH = 28
const T = 34
const L = 92
const R = 400
const H = T + order.length * rowH + 4
const max = 0.55
const sw = (v: number) => v / max * (R - L)
const rows = order.map((i, k) => ({
  name: d.names[i],
  mdi: d.mdi[i],
  perm: d.perm[i],
  y: T + k * rowH,
  noise: d.names[i] === 'RowID',
}))
</script>

<template>
  <svg role="img" :aria-label="`Impurity importance vs permutation importance: ${rows.map(r => `${r.name} ${r.mdi} vs ${r.perm}`).join('; ')}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <rect x="0" y="4" width="12" height="12" rx="2" :style="{ fill: '#a78bfa' }" />
    <text x="18" y="15" :style="{ fill: '#c4b5fd', fontSize: '13px' }">impurity (MDI)</text>
    <template v-if="perm">
      <rect x="140" y="4" width="12" height="12" rx="2" :style="{ fill: '#2dd4bf' }" />
      <text x="158" y="15" :style="{ fill: '#5eead4', fontSize: '13px' }">permutation, held-out</text>
    </template>
    <line :x1="L" :x2="L" :y1="T - 2" :y2="H - 2" :style="{ stroke: '#64748b', strokeWidth: 1.5 }" />
    <g v-for="r in rows" :key="r.name">
      <rect v-if="r.noise" x="0" :y="r.y" :width="W" :height="rowH" rx="4" :style="{ fill: '#f87171', fillOpacity: 0.1 }" />
      <text :x="L - 8" :y="r.y + 18" text-anchor="end" :style="{ fill: r.noise ? '#fca5a5' : '#cbd5e1', fontSize: '13px', fontWeight: r.noise ? 700 : 400 }">{{ r.name }}</text>
      <rect :x="L" :y="r.y + 4" :width="Math.max(sw(r.mdi), 1)" :height="perm ? 9 : 18" rx="2" :style="{ fill: '#a78bfa', fillOpacity: 0.85 }" />
      <text :x="L + sw(r.mdi) + 5" :y="r.y + (perm ? 12 : 17)" :style="{ fill: '#c4b5fd', fontSize: '10.5px' }">{{ r.mdi.toFixed(3) }}</text>
      <template v-if="perm">
        <rect :x="L" :y="r.y + 15" :width="Math.max(sw(r.perm), 1)" height="9" rx="2" :style="{ fill: '#2dd4bf', fillOpacity: 0.85 }" />
        <text :x="L + sw(r.perm) + 5" :y="r.y + 23" :style="{ fill: '#5eead4', fontSize: '10.5px' }">{{ r.perm.toFixed(3) }}</text>
      </template>
    </g>
  </svg>
</template>
