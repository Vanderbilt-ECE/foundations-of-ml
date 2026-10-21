<script setup lang="ts">
// Wholesale customers: elbow (J) and mean silhouette for K = 2..8 (data/wholesale.json → sweep).
// The honest picture for real data: no sharp elbow, and silhouettes well below the toy example's.
import toy from '../data/blobs3.json'
import d from '../data/wholesale.json'

const W = 300; const L = 46; const R = 288
const ks = d.sweep.map(s => s.k)
const sx = (k: number) => L + (k - ks[0]) / (ks[ks.length - 1] - ks[0]) * (R - L)
const charts = [
  { key: 'J', title: 'Within-cluster SS  J', color: '#fbbf24', T: 24, B: 140, lo: 900, hi: 1900, fmt: (v: number) => `${v}` },
  { key: 'sil', title: 'Mean silhouette', color: '#2dd4bf', T: 190, B: 306, lo: 0, hi: 0.7, fmt: (v: number) => v.toFixed(1) },
] as const
const sy = (c: typeof charts[number], v: number) => c.B - (v - c.lo) / (c.hi - c.lo) * (c.B - c.T)
</script>

<template>
  <svg :viewBox="`0 0 ${W} 335`" class="w-full" role="img" :aria-label="`Wholesale customers: J falls smoothly with no clear elbow; mean silhouette is highest at K = 2 (${d.sweep[0].sil})`">
    <g v-for="c in charts" :key="c.key">
      <text :x="L - 40" :y="c.T - 10" :style="{ fill: c.color, fontSize: '12px', fontWeight: 700 }">{{ c.title }}</text>
      <line :x1="L" :x2="R" :y1="c.B" :y2="c.B" :style="{ stroke: '#475569' }" />
      <line :x1="L" :x2="L" :y1="c.T" :y2="c.B" :style="{ stroke: '#475569' }" />
      <text :x="L - 6" :y="c.T + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ c.fmt(c.hi) }}</text>
      <text :x="L - 6" :y="c.B + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ c.fmt(c.lo) }}</text>
      <text v-for="k in ks" :key="k" :x="sx(k)" :y="c.B + 14" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ k }}</text>
      <polyline :points="d.sweep.map(s => `${sx(s.k)},${sy(c, s[c.key])}`).join(' ')" :style="{ fill: 'none', stroke: c.color, strokeWidth: 2.5 }" />
      <g v-for="s in d.sweep" :key="s.k">
        <circle :cx="sx(s.k)" :cy="sy(c, s[c.key])" r="3.5" :style="{ fill: c.color }" />
        <text v-if="c.key === 'sil'" :x="sx(s.k)" :y="sy(c, s.sil) - 8" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '9.5px' }">{{ s.sil.toFixed(2) }}</text>
      </g>
    </g>
    <line :x1="L" :x2="R" :y1="sy(charts[1], toy.sil)" :y2="sy(charts[1], toy.sil)" :style="{ stroke: '#5eead4', strokeDasharray: '4 4', opacity: 0.5 }" />
    <text :x="R" :y="sy(charts[1], toy.sil) - 5" text-anchor="end" :style="{ fill: '#5eead4', fontSize: '9.5px', opacity: 0.8 }">three-blob toy example, K = 3</text>
    <text :x="(L + R) / 2" y="333" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">number of clusters K</text>
  </svg>
</template>
