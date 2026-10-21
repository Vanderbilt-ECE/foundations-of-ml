<script setup lang="ts">
// Wholesale customers: annual spend per category, one dot per customer (data/wholesale.json).
// log=false: raw spend (each row scaled to its own max): a few huge accounts squash everyone else.
// log=true:  log(1 + spend): the bulk spreads out and the tail comes in. Dots glide between the two.
import { computed } from 'vue'
import d from '../data/wholesale.json'

const props = withDefaults(defineProps<{ log?: boolean }>(), { log: false })
const W = 600; const L = 140; const R = 585; const rowH = 46; const T = 10
const n = d.raw.length
// deterministic jitter
const jit = Array.from({ length: n }, (_, i) => ((Math.sin(i * 12.9898) * 43758.5453) % 1 + 1) % 1 - 0.5)
const rows = d.cols.map((name, j) => {
  const raw = d.raw.map(r => r[j])
  const lg = d.log.map(r => r[j])
  const rmax = Math.max(...raw)
  const lmin = Math.min(...lg); const lmax = Math.max(...lg)
  return { name: name.replace('_', ' / ').replace('Delicassen', 'Delicatessen'), raw, lg, rmax, lmin, lmax }
})
const xs = computed(() => rows.map(r => (props.log
  ? r.lg.map(v => L + (v - r.lmin) / (r.lmax - r.lmin) * (R - L))
  : r.raw.map(v => L + v / r.rmax * (R - L)))))
const H = T + rows.length * rowH + 22
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="log ? 'Spending per category after a log transform: spread out and roughly symmetric' : 'Raw spending per category: most customers bunched near zero with a long tail'">
    <g v-for="(r, j) in rows" :key="r.name">
      <text :x="L - 10" :y="T + j * rowH + rowH / 2 + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '13px' }">{{ r.name }}</text>
      <line :x1="L" :x2="R" :y1="T + j * rowH + rowH - 4" :y2="T + j * rowH + rowH - 4" :style="{ stroke: '#334155' }" />
      <circle
        v-for="(x, i) in xs[j]" :key="i" r="2.2" class="sd"
        :style="{ transform: `translate(${x}px, ${T + j * rowH + rowH / 2 + jit[i] * (rowH - 14)}px)`, fill: '#60a5fa', fillOpacity: 0.55 }"
      />
    </g>
    <text :x="L" :y="H - 4" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ log ? 'log(1 + spend), min' : '0' }}</text>
    <text :x="R" :y="H - 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ log ? 'max' : 'largest account' }}</text>
  </svg>
</template>

<style scoped>
.sd { transition: transform 1.2s cubic-bezier(.6, 0, .3, 1); }
</style>
