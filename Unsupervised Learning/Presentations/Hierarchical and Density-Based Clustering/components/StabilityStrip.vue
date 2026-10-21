<script setup lang="ts">
// Stability (data/compare.json → stab): each method refit on 30 random 80% subsamples; each dot is the
// ARI between the subsample's clustering and the full-data clustering on the shared points (1 = same answer).
// The bar marks the median. The diamond is the ARI against the true groups, shown once `truth` is on:
// stable is not the same as right.
import d from '../data/compare.json'

withDefaults(defineProps<{ truth?: boolean }>(), { truth: false })
const st = d.stab
const W = 400; const H = 230; const L = 78; const R = 388; const T = 26; const B = 200
const X = (a: number) => L + (Math.max(-0.1, a) + 0.1) / 1.1 * (R - L)
const rowY = (j: number) => T + (j + 0.5) * (B - T) / st.methods.length
const jitter = (b: number) => ((b * 37) % 11 - 5) * 1.6
const median = (v: number[]) => [...v].sort((a, b) => a - b)[Math.floor(v.length / 2)]
const truthAri = (i: number, j: number) => d.table.ari[d.table.datasets.indexOf(st.datasets[i])][j]
const titles: Record<string, string> = { blobs3: 'Three blobs', moons: 'Two moons' }
</script>

<template>
  <div class="grid grid-cols-2 gap-6">
    <svg v-for="(ds, i) in st.datasets" :key="ds" :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`Stability of each method on ${ds}`">
      <text :x="L" y="14" :style="{ fill: '#e2e8f0', fontSize: '14px', fontWeight: 700 }">{{ titles[ds] }}</text>
      <line :x1="L" :x2="R" :y1="B" :y2="B" :style="{ stroke: '#475569' }" />
      <g v-for="v in [0, 0.5, 1]" :key="v">
        <line :x1="X(v)" :x2="X(v)" :y1="T" :y2="B" :style="{ stroke: '#1e293b' }" />
        <text :x="X(v)" :y="B + 15" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v }}</text>
      </g>
      <text :x="(L + R) / 2" :y="H - 1" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">ARI, subsample vs. full data</text>
      <g v-for="(m, j) in st.methods" :key="m">
        <text :x="L - 8" :y="rowY(j) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ m }}</text>
        <circle v-for="(a, b) in st.ari[i][j]" :key="b" :cx="X(a)" :cy="rowY(j) + jitter(b)" r="2.6" :style="{ fill: '#60a5fa', fillOpacity: 0.6 }" />
        <line :x1="X(median(st.ari[i][j]))" :x2="X(median(st.ari[i][j]))" :y1="rowY(j) - 11" :y2="rowY(j) + 11" :style="{ stroke: '#e2e8f0', strokeWidth: 2.5 }" />
        <path
          class="fade" :style="{ opacity: truth ? 1 : 0, fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 1.5 }"
          :d="`M${X(truthAri(i, j))},${rowY(j) - 8}l7,8l-7,8l-7,-8Z`"
        />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.fade { transition: opacity 0.6s ease; }
</style>
