<script setup lang="ts">
// A 1D mixture built up in steps (data/mix1d.json: weights .3/.5/.2 and 600 samples from it).
//   step 0: the three component densities, each with area 1
//   step 1: each scaled by its weight pi_k (the curves shrink)
//   step 2: their sum, the mixture density p(x) (drawn on)
//   step 3: a histogram of 600 samples, which follows p(x)
import { computed } from 'vue'
import d from '../data/mix1d.json'
import { color, useTween } from '../utils/clusters'
import { pdf1 } from '../utils/gmm'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const W = 640; const H = 300; const X0 = -5; const X1 = 8; const YMAX = 0.7
const sx = (x: number) => 30 + (x - X0) / (X1 - X0) * (W - 50)
const sy = (y: number) => H - 30 - y / YMAX * (H - 50)
const wts = useTween(() => (props.step >= 1 ? d.w : [1, 1, 1]), 900)
const xs = Array.from({ length: 261 }, (_, i) => X0 + (X1 - X0) * i / 260)
const path = (f: (x: number) => number) => xs.map((x, i) => `${i ? 'L' : 'M'}${sx(x).toFixed(1)},${sy(f(x)).toFixed(1)}`).join('')
const comps = computed(() => d.mu.map((m, k) => path(x => wts.value[k] * pdf1(x, m, d.sd[k]))))
const total = path(x => d.w.reduce((s, w, k) => s + w * pdf1(x, d.mu[k], d.sd[k]), 0))
const BW = 0.4
const bins = (() => {
  const n = Math.round((X1 - X0) / BW)
  const c = Array.from({ length: n }, () => 0)
  d.x.forEach((v) => { const i = Math.floor((v - X0) / BW); if (i >= 0 && i < n) c[i]++ })
  return c.map((v, i) => ({ x: X0 + i * BW, h: v / (d.x.length * BW) }))
})()
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Three bell curves, scaled by their weights and summed into a three-peaked density; a histogram of samples follows it">
    <line :x1="sx(X0)" :x2="sx(X1)" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#475569', strokeWidth: 1.5 }" />
    <g :style="{ opacity: step >= 3 ? 1 : 0, transition: 'opacity 0.5s' }">
      <rect
        v-for="(b, i) in bins" :key="i" :x="sx(b.x) + 1" :width="sx(b.x + BW) - sx(b.x) - 2" :y="sy(step >= 3 ? b.h : 0)" :height="sy(0) - sy(step >= 3 ? b.h : 0)" class="bar"
        :style="{ fill: '#94a3b8', fillOpacity: 0.28, transitionDelay: `${i * 18}ms` }"
      />
    </g>
    <path v-for="(p, k) in comps" :key="k" :d="p" :style="{ fill: color(k), fillOpacity: 0.12, stroke: color(k), strokeWidth: 2.4, strokeDasharray: step >= 2 ? '6 4' : 'none' }" />
    <text v-for="(m, k) in d.mu" :key="`l${k}`" :x="sx(m)" :y="sy(wts[k] * pdf1(m, m, d.sd[k])) - 8" text-anchor="middle" :style="{ fill: color(k), fontSize: '13px', fontWeight: 700 }">{{ step >= 1 ? `π=${d.w[k]}` : `N(μ=${m}, σ=${d.sd[k]})` }}</text>
    <path :d="total" pathLength="1" class="total" :class="{ on: step >= 2 }" :style="{ fill: 'none', stroke: '#f8fafc', strokeWidth: 3.5 }" />
    <text v-if="step >= 2" :x="sx(3.3)" :y="sy(0.2)" :style="{ fill: '#f8fafc', fontSize: '14px', fontWeight: 700 }">p(x)</text>
  </svg>
</template>

<style scoped>
.total { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 1.6s ease; }
.total.on { stroke-dashoffset: 0; }
.bar { transition: y 0.6s ease, height 0.6s ease; }
</style>
