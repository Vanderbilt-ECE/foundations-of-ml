<script setup lang="ts">
// Which feature each tree splits on at its root, over 300 trees on California housing (data/roots.json).
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/roots.json'

const props = withDefaults(defineProps<{ model: 'bag' | 'rf' }>(), {})

const counts: number[] = d[props.model]
const color = props.model === 'bag' ? '#60a5fa' : '#2dd4bf'
const title = props.model === 'bag' ? 'Bagging (all 8 features per split)' : `Random forest (m = ${d.m} per split)`

const W = 440
const rowH = 27
const T = 30
const L = 96
const R = 400
const H = T + d.names.length * rowH + 4
const bars = d.names.map((n, i) => ({
  n,
  c: counts[i],
  y: T + i * rowH,
  w: counts[i] / d.B * (R - L),
}))
</script>

<template>
  <svg role="img" :aria-label="`${title}: root split counts ${d.names.map((n, i) => `${n} ${counts[i]}`).join(', ')}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <text x="0" y="18" :style="{ fill: color, fontSize: '15px', fontWeight: 700 }">{{ title }}</text>
    <line :x1="L" :x2="L" :y1="T - 2" :y2="H - 4" :style="{ stroke: '#64748b', strokeWidth: 1.5 }" />
    <g v-for="b in bars" :key="b.n">
      <text :x="L - 8" :y="b.y + 17" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '13px' }">{{ b.n }}</text>
      <rect :x="L" :y="b.y + 4" :width="Math.max(b.w, 0)" :height="rowH - 8" rx="3" :style="{ fill: color, fillOpacity: 0.75 }" />
      <text :x="L + b.w + 6" :y="b.y + 17" :style="{ fill: b.c ? '#e2e8f0' : '#64748b', fontSize: '12px' }">{{ b.c }}</text>
    </g>
  </svg>
</template>
