<script setup lang="ts">
// One full K-sweep curve on blobs6 (data/blobs6.json → sweep), K = 1..8, with the best K marked.
//   which = 'J'   elbow of the within-cluster sum of squares
//   which = 'sil' mean silhouette
import { computed } from 'vue'
import d from '../data/blobs6.json'

const props = withDefaults(defineProps<{ which?: 'J' | 'sil', best?: number }>(), { which: 'J', best: 6 })
const W = 300; const H = 116; const L = 40; const R = 288; const T = 8; const B = 88
const isJ = computed(() => props.which === 'J')
const color = computed(() => (isJ.value ? '#fbbf24' : '#2dd4bf'))
const lo = computed(() => (isJ.value ? 0 : 0.3))
const hi = computed(() => (isJ.value ? d.sweep[0].J : 0.75))
const fmt = (v: number) => (isJ.value ? `${Math.round(v / 1000)}k` : v.toFixed(2))
const sx = (k: number) => L + (k - 1) / 7 * (R - L)
const sy = (v: number) => B - (v - lo.value) / (hi.value - lo.value) * (B - T)
const rows = computed(() => d.sweep.filter(s => (s as any)[props.which] != null))
const val = (s: any) => s[props.which] as number
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="isJ ? 'Within-cluster sum of squares for K from 1 to 8; the elbow is at K = 6' : 'Mean silhouette for K from 1 to 8; the peak is at K = 6'">
    <line :x1="L" :x2="R" :y1="B" :y2="B" :style="{ stroke: '#475569' }" />
    <line :x1="L" :x2="L" :y1="T" :y2="B" :style="{ stroke: '#475569' }" />
    <text :x="L - 6" :y="T + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ fmt(hi) }}</text>
    <text :x="L - 6" :y="B + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ fmt(lo) }}</text>
    <text v-for="k in 8" :key="k" :x="sx(k)" :y="B + 14" text-anchor="middle" :style="{ fill: k === best ? '#fff' : '#94a3b8', fontSize: '10px', fontWeight: k === best ? 700 : 400 }">{{ k }}</text>
    <polyline :points="rows.map(s => `${sx(s.k)},${sy(val(s))}`).join(' ')" :style="{ fill: 'none', stroke: color, strokeWidth: 2.5 }" />
    <circle v-for="s in rows" :key="s.k" :cx="sx(s.k)" :cy="sy(val(s))" :r="s.k === best ? 6 : 3.5" :style="{ fill: s.k === best ? '#fff' : color, stroke: color, strokeWidth: 2 }" />
    <text :x="sx(best) + 9" :y="sy(val(rows.find(s => s.k === best)))- 8" :style="{ fill: '#fff', fontSize: '11px', fontWeight: 700 }">{{ isJ ? 'elbow' : 'peak' }}</text>
    <text :x="(L + R) / 2" :y="H - 2" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">number of clusters K</text>
  </svg>
</template>
