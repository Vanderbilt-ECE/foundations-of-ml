<script setup lang="ts">
// One round of gradient boosting by hand (data/oned.json → rounds[t]), learning rate 1.
//   top:    the data and the running fit F (violet)
//   bottom: the residuals y − F (red stems) and the stump fit to them (amber)
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/oned.json'

const props = defineProps<{ t: number }>()

const r = d.rounds[props.t]
const W = 300
const top = { y: 26, h: 128 }
const bot = { y: 186, h: 118 }
const H = bot.y + bot.h + 8
const L = 8
const R = W - 8
const sx = (x: number) => L + x * (R - L)
const syTop = (y: number) => top.y + (1.8 - Math.max(-2.1, Math.min(1.8, y))) / 3.9 * top.h
const syBot = (y: number) => bot.y + (1.6 - Math.max(-2.3, Math.min(1.6, y))) / 3.9 * bot.h
const line = (ys: number[], sy: (v: number) => number) => ys.map((y, i) => `${sx(d.grid[i]).toFixed(1)},${sy(y).toFixed(1)}`).join(' ')
const pts = d.x.map((x, i) => ({ key: i, cx: sx(x), cy: syTop(d.y[i]) }))
const stems = d.x.map((x, i) => ({ key: i, x: sx(x), y: syBot(r.res[i]) }))
const mse = (r.res as number[]).reduce((s, v) => s + v * v, 0) / r.res.length
const label = props.t === 0 ? 'F₀ = mean of y' : `F${'₀₁₂₃'[props.t]} after ${props.t} stump${props.t > 1 ? 's' : ''}`
</script>

<template>
  <svg role="img" :aria-label="`Round ${t + 1}: current fit with training MSE ${mse.toFixed(3)}, residuals, and stump ${t + 1} splitting at x = ${r.thr}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <text :x="L" y="16" :style="{ fill: '#c4b5fd', fontSize: '14px', fontWeight: 700 }">{{ label }}</text>
    <text :x="R" y="16" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">train MSE {{ mse.toFixed(3) }}</text>
    <rect :x="L" :y="top.y" :width="R - L" :height="top.h" rx="4" :style="{ fill: '#ffffff', fillOpacity: 0.025, stroke: '#334155', strokeWidth: 1 }" />
    <circle v-for="p in pts" :key="p.key" :cx="p.cx" :cy="p.cy" r="2.6" :style="{ fill: '#cbd5e1', fillOpacity: 0.6 }" />
    <polyline :points="line(r.Fg, syTop)" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 3, strokeLinejoin: 'round' }" />

    <text :x="L" :y="bot.y - 8" :style="{ fill: '#fca5a5', fontSize: '13px', fontWeight: 700 }">residuals y − F</text>
    <text :x="R" :y="bot.y - 8" text-anchor="end" :style="{ fill: '#fbbf24', fontSize: '12px', fontWeight: 700 }">stump {{ t + 1 }}: split at x = {{ r.thr.toFixed(2) }}</text>
    <rect :x="L" :y="bot.y" :width="R - L" :height="bot.h" rx="4" :style="{ fill: '#ffffff', fillOpacity: 0.025, stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="syBot(0)" :y2="syBot(0)" :style="{ stroke: '#64748b', strokeWidth: 1 }" />
    <line v-for="s in stems" :key="s.key" :x1="s.x" :x2="s.x" :y1="syBot(0)" :y2="s.y" :style="{ stroke: '#f87171', strokeWidth: 1.6, opacity: 0.75 }" />
    <circle v-for="s in stems" :key="`c${s.key}`" :cx="s.x" :cy="s.y" r="2" :style="{ fill: '#f87171' }" />
    <polyline :points="line(r.h, syBot)" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 3, strokeLinejoin: 'round' }" />
  </svg>
</template>
