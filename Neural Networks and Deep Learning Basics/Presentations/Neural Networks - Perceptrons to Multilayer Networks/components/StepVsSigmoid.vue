<script setup lang="ts">
// Step and sigmoid overlaid on one small plot. Both cross the 0.5 line at z = 0,
// so thresholding the sigmoid at 0.5 gives exactly the step's yes/no answer. Static (prints as-is).
import { C, pathOf } from '../utils/plot'

const W = 360; const H = 210; const ZR = 6
const L = 34; const R = 12; const T = 14; const B = 30
const sx = (v: number) => L + (v + ZR) / (2 * ZR) * (W - L - R)
const sy = (v: number) => H - B - (v + 0.1) / 1.2 * (H - T - B)

const sig = (v: number) => 1 / (1 + Math.exp(-v))
const sigPath = pathOf(Array.from({ length: 161 }, (_, i) => { const v = -ZR + 2 * ZR * i / 160; return [sx(v), sy(sig(v))] }))
const stepPath = pathOf([[sx(-ZR), sy(0)], [sx(0), sy(0)], [sx(0), sy(1)], [sx(ZR), sy(1)]])
const ticksX = [-6, -3, 0, 3, 6]
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Step function and sigmoid plotted together; both switch from no to yes at z = 0">
    <!-- axes and grid -->
    <line :x1="sx(-ZR)" :x2="sx(ZR)" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: C.grid }" />
    <line :x1="sx(-ZR)" :x2="sx(ZR)" :y1="sy(1)" :y2="sy(1)" :style="{ stroke: C.grid, strokeDasharray: '2 4' }" />
    <line :x1="sx(0)" :x2="sx(0)" :y1="T - 4" :y2="H - B" :style="{ stroke: C.grid }" />
    <text v-for="t in ticksX" :key="t" :x="sx(t)" :y="H - B + 16" text-anchor="middle" style="font-size: 11px" :style="{ fill: C.muted }">{{ t }}</text>
    <text :x="sx(4.5)" :y="H - B + 16" text-anchor="middle" style="font-size: 12px" font-style="italic" :style="{ fill: C.muted }">z</text>
    <text :x="L - 6" :y="sy(0) + 4" text-anchor="end" style="font-size: 11px" :style="{ fill: C.muted }">0</text>
    <text :x="L - 6" :y="sy(0.5) + 4" text-anchor="end" style="font-size: 11px" :style="{ fill: C.amber }">0.5</text>
    <text :x="L - 6" :y="sy(1) + 4" text-anchor="end" style="font-size: 11px" :style="{ fill: C.muted }">1</text>

    <!-- the 0.5 decision threshold -->
    <line :x1="sx(-ZR)" :x2="sx(ZR)" :y1="sy(0.5)" :y2="sy(0.5)" :style="{ stroke: C.amber, strokeDasharray: '4 4', strokeOpacity: 0.6 }" />

    <!-- curves -->
    <path :d="stepPath" :style="{ fill: 'none', stroke: C.muted, strokeWidth: 2.6 }" />
    <path :d="sigPath" :style="{ fill: 'none', stroke: C.violet, strokeWidth: 2.8 }" />
    <circle :cx="sx(0)" :cy="sy(0.5)" r="5" :style="{ fill: C.amber }" />

    <!-- legend -->
    <g>
      <line :x1="L + 8" :x2="L + 26" :y1="T + 6" :y2="T + 6" :style="{ stroke: C.violet, strokeWidth: 2.8 }" />
      <text :x="L + 32" :y="T + 10" style="font-size: 12px" :style="{ fill: C.text }">sigmoid σ(z)</text>
      <line :x1="L + 8" :x2="L + 26" :y1="T + 24" :y2="T + 24" :style="{ stroke: C.muted, strokeWidth: 2.6 }" />
      <text :x="L + 32" :y="T + 28" style="font-size: 12px" :style="{ fill: C.text }">step</text>
    </g>
  </svg>
</template>
