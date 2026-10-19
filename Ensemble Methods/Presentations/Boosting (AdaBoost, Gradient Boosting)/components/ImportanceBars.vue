<script setup lang="ts">
// Two views of the same fitted model on California housing (data/importance.json):
// impurity importance (built into the model, share of total) and permutation importance
// (rise in held-out MSE when one column is shuffled). The last row is the column added for the demo.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/importance.json'

const props = defineProps<{ src: 'noise' | 'copy' }>()
const o = props.src === 'noise' ? d.noise : d.copy
const rows = o.names.map((n, i) => ({ name: n, mdi: o.mdi[i], perm: o.perm[i], extra: i === o.names.length - 1 }))

const W = 640
const T = 34
const rowH = 30
const H = T + rows.length * rowH + 4
const L = 112
const P1 = { x0: L, x1: 340, max: 0.6, ticks: [0, 0.2, 0.4, 0.6], color: '#a78bfa', title: 'Impurity importance', sub: 'share of total' }
const P2 = { x0: 392, x1: 620, max: 2.0, ticks: [0, 1, 2], color: '#2dd4bf', title: 'Permutation importance', sub: 'rise in test MSE' }
const sx = (p: typeof P1, v: number) => p.x0 + Math.max(v, 0) / p.max * (p.x1 - p.x0)
const fmt = (v: number) => v.toFixed(v < 0.1 ? 3 : 2)
</script>

<template>
  <svg role="img" :aria-label="`Feature importance for California housing, impurity and permutation: ${rows.map(r => `${r.name} ${r.mdi.toFixed(3)} and ${r.perm.toFixed(3)}`).join('; ')}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <g v-for="p in [P1, P2]" :key="p.title">
      <text :x="p.x0" y="12" :style="{ fill: p.color, fontSize: '14px', fontWeight: 700 }">{{ p.title }}</text>
      <text :x="p.x0" y="27" :style="{ fill: '#cbd5e1', fontSize: '11px' }">{{ p.sub }}</text>
      <line v-for="t in p.ticks" :key="t" :x1="sx(p, t)" :x2="sx(p, t)" :y1="T" :y2="T + rows.length * rowH" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    </g>
    <g v-for="(r, i) in rows" :key="r.name">
      <text :x="L - 10" :y="T + i * rowH + rowH / 2 + 4" text-anchor="end" :style="{ fill: r.extra ? '#f87171' : '#e2e8f0', fontSize: '13px', fontWeight: r.extra ? 700 : 500 }">{{ r.name }}</text>
      <rect :x="P1.x0" :y="T + i * rowH + 6" :width="sx(P1, r.mdi) - P1.x0" :height="rowH - 12" rx="3" :style="{ fill: r.extra ? '#f87171' : P1.color, fillOpacity: 0.75 }" />
      <text :x="sx(P1, r.mdi) + 6" :y="T + i * rowH + rowH / 2 + 4" :style="{ fill: '#e2e8f0', fontSize: '12px' }">{{ fmt(r.mdi) }}</text>
      <rect :x="P2.x0" :y="T + i * rowH + 6" :width="sx(P2, r.perm) - P2.x0" :height="rowH - 12" rx="3" :style="{ fill: r.extra ? '#f87171' : P2.color, fillOpacity: 0.75 }" />
      <text :x="sx(P2, r.perm) + 6" :y="T + i * rowH + rowH / 2 + 4" :style="{ fill: '#e2e8f0', fontSize: '12px' }">{{ fmt(r.perm) }}</text>
    </g>
  </svg>
</template>
