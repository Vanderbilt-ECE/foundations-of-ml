<script setup lang="ts">
// The chicken-and-egg problem behind EM, on the running example (data/em.json).
// Left: if we knew each point's component, fitting is easy: per-group fraction, mean and covariance.
// Right: if we knew the Gaussians, labeling is easy: Bayes' rule gives the responsibilities.
// step 0: left · step 1: right · step 2: the circular arrows (guess one side, then alternate) start flowing.
import d from '../data/em.json'
import type { Mix } from '../utils/gmm'

withDefaults(defineProps<{ step?: number }>(), { step: 0 })
// sample statistics per true component
const known: Mix = (() => {
  const w: number[] = []; const mu: number[][] = []; const cov: number[][][] = []
  for (let k = 0; k < 3; k++) {
    const P = d.pts.filter((_, i) => d.truth[i] === k)
    const m = [P.reduce((s, p) => s + p[0], 0) / P.length, P.reduce((s, p) => s + p[1], 0) / P.length]
    let a = 0; let b = 0; let c = 0
    P.forEach((p) => { a += (p[0] - m[0]) ** 2; b += (p[0] - m[0]) * (p[1] - m[1]); c += (p[1] - m[1]) ** 2 })
    w.push(P.length / d.pts.length); mu.push(m); cov.push([[a / P.length, b / P.length], [b / P.length, c / P.length]])
  }
  return { w, mu, cov }
})()
</script>

<template>
  <div class="grid grid-cols-[1fr_auto_1fr] gap-3 items-center">
    <div class="text-left" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
      <div class="font-bold text-teal-300">If we knew the labels…</div>
      <div class="text-xs opacity-80 mb-1">…each Gaussian is just its group's fraction, mean and covariance.</div>
      <GmmPlot :pts="d.pts" :mix="known" mode="lab" :lab="d.truth" :levels="[1, 2]" :w="330" :h="230" :r="2" label="Points colored by their true component, with each group's fitted ellipse" />
    </div>
    <svg viewBox="0 0 90 200" class="w-22" role="img" aria-label="Two arrows forming a loop between the panels">
      <path d="M10,70 C40,20 50,20 80,70" class="flow" :class="{ on: step >= 2 }" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 3 }" />
      <path d="M72,62 L80,70 L70,74" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 3, opacity: step >= 2 ? 1 : 0.25 }" />
      <path d="M80,130 C50,180 40,180 10,130" class="flow" :class="{ on: step >= 2 }" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 3 }" />
      <path d="M18,138 L10,130 L20,126" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 3, opacity: step >= 2 ? 1 : 0.25 }" />
      <text x="45" y="104" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '13px', fontWeight: 700, opacity: step >= 2 ? 1 : 0 }">EM</text>
    </svg>
    <div class="text-left reveal" :class="{ shown: step >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
      <div class="font-bold text-amber-300">If we knew the Gaussians…</div>
      <div class="text-xs opacity-80 mb-1">…each point's membership is Bayes' rule: the responsibilities.</div>
      <GmmPlot :pts="d.pts" :mix="d.true" mode="soft" :levels="[1, 2]" :w="330" :h="230" :r="2" label="True Gaussians drawn, points colored by responsibility" />
    </div>
  </div>
</template>

<style scoped>
.flow { stroke-dasharray: 8 6; opacity: 0.25; }
.flow.on { opacity: 1; animation: flow 0.9s linear infinite; }
@keyframes flow { to { stroke-dashoffset: -14; } }
</style>
