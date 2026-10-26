<script setup lang="ts">
// BIC for every (covariance_type, K) on the running example (data/bic.json). Ring = each type's best K.
// The constrained types need more components to imitate tilted ellipses, and still score worse than full at K = 3.
import { computed } from 'vue'
import b from '../data/bic.json'
import { useActive } from '../utils/gmm'

const TYPES = [
  { key: 'spherical', c: '#60a5fa' },
  { key: 'diag', c: '#fbbf24' },
  { key: 'tied', c: '#a78bfa' },
  { key: 'full', c: '#2dd4bf' },
] as const
const all = TYPES.flatMap(t => b.sweep[t.key].map(s => s.bic))
const Y0 = Math.floor(Math.min(...all) / 100) * 100 - 50; const Y1 = Math.ceil(Math.max(...all) / 100) * 100
const W = 600; const H = 290
const sx = (k: number) => 56 + (k - 1) / 7 * (W - 170)
const sy = (v: number) => 12 + (Y1 - v) / (Y1 - Y0) * (H - 44)
const { active, isPrintMode } = useActive()
const on = computed(() => active.value || isPrintMode.value)
const ticks = Array.from({ length: Math.floor((Y1 - Y0) / 200) + 1 }, (_, i) => Math.ceil(Y0 / 200) * 200 + i * 200).filter(v => v <= Y1)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="BIC against K for four covariance types; full covariance at K = 3 is lowest">
    <line :x1="sx(1)" :x2="sx(8)" :y1="sy(Y0)" :y2="sy(Y0)" :style="{ stroke: '#475569' }" />
    <g v-for="v in ticks" :key="v">
      <line :x1="sx(1)" :x2="sx(8)" :y1="sy(v)" :y2="sy(v)" :style="{ stroke: '#334155', strokeDasharray: '2 4' }" />
      <text :x="sx(1) - 8" :y="sy(v) + 4" text-anchor="end" :style="{ fill: '#64748b', fontSize: '11px' }">{{ v }}</text>
    </g>
    <g v-for="k in 8" :key="k"><text :x="sx(k)" :y="sy(Y0) + 16" text-anchor="middle" :style="{ fill: '#64748b', fontSize: '12px' }">{{ k }}</text></g>
    <text :x="sx(8)" :y="sy(Y0) - 6" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">K</text>
    <text :x="sx(1) + 4" :y="sy(Y1) + 4" :style="{ fill: '#94a3b8', fontSize: '12px' }">BIC (lower is better)</text>
    <g v-for="(t, i) in TYPES" :key="t.key">
      <path
        :d="b.sweep[t.key].map((s, j) => `${j ? 'L' : 'M'}${sx(j + 1).toFixed(1)},${sy(s.bic).toFixed(1)}`).join('')" pathLength="1" class="ln" :class="{ on }"
        :style="{ fill: 'none', stroke: t.c, strokeWidth: t.key === 'full' ? 3.2 : 2.2, transitionDelay: `${i * 200}ms` }"
      />
      <circle v-for="(s, j) in b.sweep[t.key]" :key="j" :cx="sx(j + 1)" :cy="sy(s.bic)" r="2.6" :style="{ fill: t.c }" />
      <circle :cx="sx(b.best[t.key])" :cy="sy(b.sweep[t.key][b.best[t.key] - 1].bic)" r="8" :style="{ fill: 'none', stroke: t.c, strokeWidth: 2 }" />
      <text :x="sx(5.3)" :y="34 + i * 20" :style="{ fill: t.c, fontSize: '12px', fontWeight: 700 }">{{ t.key }} · best K={{ b.best[t.key] }}</text>
    </g>
  </svg>
</template>

<style scoped>
.ln { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 1.3s ease; }
.ln.on { stroke-dashoffset: 0; }
</style>
