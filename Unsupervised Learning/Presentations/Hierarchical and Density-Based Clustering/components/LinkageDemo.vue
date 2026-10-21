<script setup lang="ts">
// Two small groups (data/linkdemo.json) and what each linkage measures between them.
// mode 0 single: closest pair · 1 complete: farthest pair · 2 average: all pairs · 3 Ward: centroids.
import { computed } from 'vue'
import d from '../data/linkdemo.json'
import { domainOf, equalScale } from '../utils/clusters'

const props = withDefaults(defineProps<{ mode?: number }>(), { mode: 0 })
const W = 470; const H = 270
const S = equalScale(domainOf([...d.A, ...d.B], 0.18), W, H)
const P = (p: number[]) => [S.sx(p[0]), S.sy(p[1])]
const merged = [(d.mA[0] * d.A.length + d.mB[0] * d.B.length) / (d.A.length + d.B.length), (d.mA[1] * d.A.length + d.mB[1] * d.B.length) / (d.A.length + d.B.length)]
const pairs = d.A.flatMap(a => d.B.map(b => [P(a), P(b)]))
const m = computed(() => Math.max(0, Math.min(3, props.mode)))
const caption = computed(() => [
  ['Single', `closest pair: ${d.dSingle.toFixed(2)}`],
  ['Complete', `farthest pair: ${d.dComplete.toFixed(2)}`],
  ['Average', `mean of all ${d.A.length * d.B.length} pair distances: ${d.dAverage.toFixed(2)}`],
  ['Ward', `increase in within-cluster squared error: ${d.dWard.toFixed(1)}`],
][m.value])
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`Two groups of points; ${caption[0]} linkage highlighted`">
      <g :style="{ opacity: m === 2 ? 1 : 0 }" class="fade">
        <line v-for="(p, i) in pairs" :key="i" :x1="p[0][0]" :y1="p[0][1]" :x2="p[1][0]" :y2="p[1][1]" :style="{ stroke: '#fbbf24', strokeOpacity: 0.22, strokeWidth: 1 }" />
      </g>
      <line class="fade" :style="{ opacity: m === 0 ? 1 : 0, stroke: '#fbbf24', strokeWidth: 3 }" :x1="P(d.A[d.single[0]])[0]" :y1="P(d.A[d.single[0]])[1]" :x2="P(d.B[d.single[1]])[0]" :y2="P(d.B[d.single[1]])[1]" />
      <line class="fade" :style="{ opacity: m === 1 ? 1 : 0, stroke: '#fbbf24', strokeWidth: 3 }" :x1="P(d.A[d.complete[0]])[0]" :y1="P(d.A[d.complete[0]])[1]" :x2="P(d.B[d.complete[1]])[0]" :y2="P(d.B[d.complete[1]])[1]" />
      <g class="fade" :style="{ opacity: m === 3 ? 1 : 0 }">
        <line v-for="(p, i) in [...d.A, ...d.B]" :key="`w${i}`" :x1="P(p)[0]" :y1="P(p)[1]" :x2="P(merged)[0]" :y2="P(merged)[1]" :style="{ stroke: '#a78bfa', strokeOpacity: 0.35, strokeWidth: 1 }" />
        <circle :cx="P(merged)[0]" :cy="P(merged)[1]" r="8" :style="{ fill: '#a78bfa', stroke: '#0b1020', strokeWidth: 2 }" />
        <g v-for="(c, k) in [d.mA, d.mB]" :key="`m${k}`" :transform="`translate(${P(c)[0]},${P(c)[1]})`">
          <path d="M-7,-7L7,7M-7,7L7,-7" :style="{ stroke: k ? '#60a5fa' : '#2dd4bf', strokeWidth: 3 }" />
        </g>
      </g>
      <circle v-for="(p, i) in d.A" :key="`a${i}`" :cx="P(p)[0]" :cy="P(p)[1]" r="7" :style="{ fill: '#2dd4bf', stroke: '#0b1020', strokeWidth: 2 }" />
      <circle v-for="(p, i) in d.B" :key="`b${i}`" :cx="P(p)[0]" :cy="P(p)[1]" r="7" :style="{ fill: '#60a5fa', stroke: '#0b1020', strokeWidth: 2 }" />
    </svg>
    <div class="text-center text-sm mt-1" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
      <b class="text-amber-300">{{ caption[0] }}</b> · {{ caption[1] }}
    </div>
  </div>
</template>

<style scoped>
.fade { transition: opacity 0.5s ease; }
</style>
