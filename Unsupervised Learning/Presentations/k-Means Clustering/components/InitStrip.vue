<script setup lang="ts">
// Final objective J from 50 single runs (n_init=1) on blobs6: random init vs k-means++.
// Dots stack in bins so repeated values pile up. `pp=false` hides the k-means++ row.
import { computed } from 'vue'
import d from '../data/blobs6.json'

const props = withDefaults(defineProps<{ pp?: boolean }>(), { pp: true })
const W = 620; const L = 120; const R = 600
const lo = 0; const hi = 6000
const sx = (v: number) => L + (v - lo) / (hi - lo) * (R - L)
const bin = 150
function stack(js: number[], base: number) {
  const seen: Record<number, number> = {}
  return js.map((j) => {
    const b = Math.round(j / bin)
    const n = (seen[b] = (seen[b] ?? 0) + 1) - 1
    // wrap each pile 8 dots wide so 50 identical results still fit
    return { x: sx(b * bin) + ((n % 8) - 3.5) * 6.5, y: base - 5 - Math.floor(n / 8) * 7, j }
  })
}
const rows = computed(() => [
  { name: 'random init', sub: `${d.stuckRandom}/50 stuck`, color: '#f87171', dots: stack(d.random.J, 120), base: 120, iters: d.random.iter, show: true },
  { name: 'k-means++', sub: `${d.stuckPP}/50 stuck`, color: '#2dd4bf', dots: stack(d.pp.J, 250), base: 250, iters: d.pp.iter, show: props.pp },
])
const mean = (a: number[]) => (a.reduce((s, x) => s + x, 0) / a.length).toFixed(1)
const ticks = [1000, 2000, 3000, 4000, 5000, 6000]
</script>

<template>
  <svg :viewBox="`0 0 ${W} 285`" class="w-full" role="img" :aria-label="`Final objective of 50 runs: random initialization gets stuck ${d.stuckRandom} times, k-means++ ${d.stuckPP} times`">
    <line :x1="sx(d.best)" :x2="sx(d.best)" y1="0" y2="258" :style="{ stroke: '#2dd4bf', strokeDasharray: '4 4', opacity: 0.6 }" />
    <text :x="sx(d.best) + 6" y="12" :style="{ fill: '#5eead4', fontSize: '11px' }">best J = {{ Math.round(d.best).toLocaleString() }}</text>
    <g v-for="row in rows" :key="row.name" :style="{ opacity: row.show ? 1 : 0, transition: 'opacity .6s' }">
      <line :x1="L" :x2="R" :y1="row.base" :y2="row.base" :style="{ stroke: '#475569' }" />
      <text x="8" :y="row.base - 26" :style="{ fill: row.color, fontSize: '15px', fontWeight: 700 }">{{ row.name }}</text>
      <text x="8" :y="row.base - 9" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ row.sub }} · {{ mean(row.iters) }} iters</text>
      <circle v-for="(p, i) in row.dots" :key="i" :cx="p.x" :cy="p.y" r="3.2" :style="{ fill: row.color, fillOpacity: 0.85 }" />
    </g>
    <text v-for="t in ticks" :key="t" :x="sx(t)" y="270" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ t.toLocaleString() }}</text>
    <text :x="(L + R) / 2" y="284" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">final objective J of one run (lower is better)</text>
  </svg>
</template>
