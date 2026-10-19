<script setup lang="ts">
// The weighted exponential loss of one round as a function of the stump weight α,
// L(α) = (1 − ε) e^(−α) + ε e^(α), drawn for round 1 of the 12-point example (data/ada.json).
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/ada.json'

const eps = d.rounds[0].e
const aStar = 0.5 * Math.log((1 - eps) / eps)
const W = 460
const H = 280
const L = 42
const R = 444
const T = 12
const Bot = 238
const aLo = -0.5
const aHi = 2
const yLo = 0
const yHi = 2.2
const sx = (a: number) => L + (a - aLo) / (aHi - aLo) * (R - L)
const sy = (v: number) => Bot - (Math.max(yLo, Math.min(yHi, v)) - yLo) / (yHi - yLo) * (Bot - T)
const as = Array.from({ length: 120 }, (_, i) => aLo + i * (aHi - aLo) / 119)
const path = (f: (a: number) => number) => as.map(a => `${sx(a).toFixed(1)},${sy(f(a)).toFixed(1)}`).join(' ')
const right = (a: number) => (1 - eps) * Math.exp(-a)
const wrong = (a: number) => eps * Math.exp(a)
const total = (a: number) => right(a) + wrong(a)
const xt = [-0.5, 0, 0.5, 1, 1.5, 2]
const yt = [0, 0.5, 1, 1.5, 2]
</script>

<template>
  <svg role="img" :aria-label="`Loss as a function of alpha for epsilon ${eps}: minimum at alpha ${aStar.toFixed(2)}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in xt" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="Bot" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="Bot" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="L" :y1="T" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <polyline :points="path(right)" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 2.2, strokeDasharray: '6 5' }" />
    <polyline :points="path(wrong)" :style="{ fill: 'none', stroke: '#f87171', strokeWidth: 2.2, strokeDasharray: '6 5' }" />
    <polyline :points="path(total)" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 3.5 }" />
    <line :x1="sx(aStar)" :x2="sx(aStar)" :y1="sy(total(aStar))" :y2="Bot" :style="{ stroke: '#c4b5fd', strokeWidth: 1.5, strokeDasharray: '3 4' }" />
    <circle :cx="sx(aStar)" :cy="sy(total(aStar))" r="5.5" :style="{ fill: '#a78bfa', stroke: '#0f172a', strokeWidth: 2 }" />
    <text :x="sx(aStar)" :y="sy(total(aStar)) - 14" text-anchor="middle" :style="{ fill: '#c4b5fd', fontSize: '12px', fontWeight: 700 }">minimum at <tspan class="greek">α</tspan> = {{ aStar.toFixed(2) }}</text>
    <text :x="sx(-0.45)" :y="sy(1.95)" :style="{ fill: '#5eead4', fontSize: '12px' }">correct: (1 − ε) e⁻ᵅ</text>
    <text :x="sx(1.12)" :y="sy(1.95)" :style="{ fill: '#fca5a5', fontSize: '12px' }">mistakes: ε eᵅ</text>
    <text :x="sx(-0.12)" :y="sy(1.28)" :style="{ fill: '#c4b5fd', fontSize: '12px', fontWeight: 700 }">total L(<tspan class="greek">α</tspan>)</text>
    <text v-for="t in xt" :key="`x${t}`" :x="sx(t)" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text v-for="t in yt" :key="`y${t}`" :x="L - 8" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text :x="(L + R) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">stump weight <tspan class="greek">α</tspan>   (round 1: ε = {{ eps.toFixed(2) }})</text>
  </svg>
</template>
