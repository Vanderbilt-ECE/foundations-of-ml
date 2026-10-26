<script setup lang="ts">
// The worked example's 10 points (data/worked.json), drawn to scale. step 1: mean and the 1- and 2-standard-
// deviation ellipses of Σ · 2: the principal axes, √λ long · 3: each point's projection onto PC1 (its score z).
// Hover a point to see its coordinates and score.
import { ref } from 'vue'
import d from '../data/worked.json'
import { ellipsePath } from '../utils/plot'

withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const W = 340; const H = 300; const U = 82
const sx = (x: number) => 30 + (x - 0.2) * U
const sy = (y: number) => H - 26 - (y - 0.4) * U
const mu = d.mean
const ax = (j: number, s: number) => [mu[0] + s * Math.sqrt(d.lam[j]) * 2 * d.V[j][0], mu[1] + s * Math.sqrt(d.lam[j]) * 2 * d.V[j][1]]
const q = d.z.map(z => [mu[0] + z * d.V[0][0], mu[1] + z * d.V[0][1]])
const hot = ref<number | null>(null)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 300px" role="img" aria-label="Ten points, their covariance ellipse and first principal axis">
    <line :x1="sx(0.2)" :x2="sx(3.9)" :y1="sy(0.4)" :y2="sy(0.4)" :style="{ stroke: '#475569' }" />
    <line :x1="sx(0.2)" :x2="sx(0.2)" :y1="sy(0.4)" :y2="sy(3.5)" :style="{ stroke: '#475569' }" />
    <text v-for="t in [1, 2, 3]" :key="`x${t}`" :x="sx(t)" :y="sy(0.4) + 15" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ t }}</text>
    <text v-for="t in [1, 2, 3]" :key="`y${t}`" :x="sx(0.2) - 6" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ t }}</text>
    <g class="reveal" :class="{ shown: step >= 1 }">
      <path v-for="s in [2, 1]" :key="s" :d="ellipsePath(mu, d.S, s, sx, sy)" :style="{ fill: '#2dd4bf', fillOpacity: 0.07, stroke: '#2dd4bf', strokeOpacity: 0.6, strokeDasharray: s === 2 ? '5 4' : 'none' }" />
      <circle :cx="sx(mu[0])" :cy="sy(mu[1])" r="5" :style="{ fill: '#e2e8f0' }" />
    </g>
    <g class="reveal" :class="{ shown: step >= 2 }">
      <line v-for="j in [0, 1]" :key="j" :x1="sx(ax(j, -1)[0])" :y1="sy(ax(j, -1)[1])" :x2="sx(ax(j, 1)[0])" :y2="sy(ax(j, 1)[1])" :style="{ stroke: j ? '#a78bfa' : '#fbbf24', strokeWidth: 3 }" />
      <text :x="sx(ax(0, 1)[0]) + 6" :y="sy(ax(0, 1)[1])" :style="{ fill: '#fcd34d', fontSize: '13px', fontWeight: 700 }">PC1</text>
    </g>
    <g class="reveal" :class="{ shown: step >= 3 }">
      <line v-for="(p, i) in d.pts" :key="`r${i}`" :x1="sx(p[0])" :y1="sy(p[1])" :x2="sx(q[i][0])" :y2="sy(q[i][1])" :style="{ stroke: '#f87171', strokeOpacity: 0.7 }" />
      <circle v-for="(p, i) in q" :key="`q${i}`" :cx="sx(p[0])" :cy="sy(p[1])" r="3" :style="{ fill: '#fbbf24' }" />
    </g>
    <circle
      v-for="(p, i) in d.pts" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" :r="hot === i ? 7 : 5" :style="{ fill: '#cbd5e1', stroke: '#0b1020', strokeWidth: 1.5, cursor: 'pointer' }"
      @pointerenter="hot = i" @pointerleave="hot = null"
    />
    <text v-if="hot != null" :x="W - 6" y="16" text-anchor="end" :style="{ fill: '#fcd34d', fontSize: '13px' }" class="font-mono">x = ({{ d.pts[hot][0] }}, {{ d.pts[hot][1] }}) · z = {{ d.z[hot].toFixed(2) }}</text>
  </svg>
</template>
