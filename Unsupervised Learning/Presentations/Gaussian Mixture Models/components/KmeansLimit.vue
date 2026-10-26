<script setup lang="ts">
// k-means as a limit of GMM (data/blobs3.json, the k-Means deck's three blobs). Fix equal weights and one shared
// spherical covariance sigma^2 I at the k-means centroids, then shrink sigma^2. Responsibilities sharpen from soft
// blends into hard 0/1 labels: the k-means assignment. Right: gamma along the segment between two centroids,
// a smooth S-curve that becomes a step. Loops while the slide is showing; the PDF export shows a small sigma^2.
import { computed, ref } from 'vue'
import d from '../data/blobs3.json'
import type { Mix } from '../utils/gmm'
import { entropy, resp, useLoop } from '../utils/gmm'

const v = ref(0.05)
useLoop((_, t) => {
  const u = (t % 9) / 7 // 7 s down, 2 s hold
  v.value = 8 * (0.006 / 8) ** Math.min(1, u)
}, () => { v.value = 8 })
const mix = computed<Mix>(() => ({ w: [1 / 3, 1 / 3, 1 / 3], mu: d.C, cov: d.C.map(() => [[v.value, 0], [0, v.value]]) }))
const R = computed(() => d.pts.map(p => resp(p, mix.value)))
const unsure = computed(() => R.value.filter(g => Math.max(...g) < 0.99).length)
const H = computed(() => R.value.reduce((s, g) => s + entropy(g), 0) / R.value.length)

// the two centroids closest to each other: their bisector is the most contested border
const pair = (() => {
  let best = [0, 1]; let bd = Infinity
  for (let i = 0; i < 3; i++) for (let j = i + 1; j < 3; j++) {
    const dd = Math.hypot(d.C[i][0] - d.C[j][0], d.C[i][1] - d.C[j][1])
    if (dd < bd) { bd = dd; best = [i, j] }
  }
  return best
})()
const PW = 260; const PH = 150
const prof = computed(() => {
  const [a, b] = pair
  const A = d.C[a]; const B = d.C[b]
  return Array.from({ length: 121 }, (_, i) => {
    const t = -0.25 + 1.5 * i / 120
    const p = [A[0] + t * (B[0] - A[0]), A[1] + t * (B[1] - A[1])]
    const g = resp(p, mix.value)
    return `${i ? 'L' : 'M'}${(20 + i / 120 * (PW - 30)).toFixed(1)},${(PH - 30 - g[a] * (PH - 50)).toFixed(1)}`
  }).join('')
})
const tx = (t: number) => 20 + (t + 0.25) / 1.5 * (PW - 30)
</script>

<template>
  <div class="grid grid-cols-[1.45fr_1fr] gap-5 items-center">
    <GmmPlot :pts="d.pts" :mix="mix" mode="soft" :levels="[1]" field="argmax" :fieldRes="56" :w="500" :h="320" :r="3" :ms="0" frame label="Three blobs; circles shrink and point colors sharpen from blends into solid labels" />
    <div class="text-left space-y-3">
      <div class="font-mono text-sm">σ² = <span class="text-teal-300 text-lg font-bold">{{ v < 0.1 ? v.toFixed(3) : v.toFixed(2) }}</span></div>
      <svg :viewBox="`0 0 ${PW} ${PH}`" class="w-full" role="img" aria-label="Responsibility along the line between two centroids, an S-curve that sharpens into a step">
        <line :x1="20" :x2="PW - 10" :y1="PH - 30" :y2="PH - 30" :style="{ stroke: '#475569' }" />
        <line :x1="20" :x2="PW - 10" :y1="20" :y2="20" :style="{ stroke: '#334155', strokeDasharray: '2 4' }" />
        <line :x1="tx(0.5)" :x2="tx(0.5)" :y1="16" :y2="PH - 30" :style="{ stroke: '#64748b', strokeDasharray: '3 3' }" />
        <path :d="prof" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 3 }" />
        <text :x="tx(0)" :y="PH - 12" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">μ_a</text>
        <text :x="tx(1)" :y="PH - 12" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">μ_b</text>
        <text :x="tx(0.5)" :y="12" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">midpoint</text>
        <text x="22" y="34" :style="{ fill: '#5eead4', fontSize: '11px' }">γ_a = 1</text>
      </svg>
      <div class="font-mono text-sm space-y-1">
        <div>points with max γ &lt; 0.99: <b>{{ unsure }}</b></div>
        <div>mean entropy: <b>{{ H.toFixed(3) }}</b></div>
      </div>
    </div>
  </div>
</template>
