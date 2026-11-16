<script setup lang="ts">
// Mini-batch gradient estimates (colored arrows) around the true gradient (white arrow),
// for batch sizes 1, 16 and 256. Each estimate = true gradient + noise with spread σ/√B.
// New batches are drawn continuously; seeded, so print shows a fixed, representative frame.
import { computed, ref } from 'vue'
import { C, rng, useLoop } from '../utils/plot'

const SIZES = [1, 16, 256]
const COLORS = [C.red, C.amber, C.teal]
const N_ARROWS = 14
const G = [70, -22]              // the true gradient, in pixels
const SIGMA = 62                 // per-example noise, in pixels
const PW = 270; const PH = 240; const GAP = 25

const frame = ref(0)
let acc = 0
useLoop((dt) => { acc += dt; if (acc > 0.45) { acc = 0; frame.value++ } })
const arrows = computed(() => SIZES.map((B, k) => {
  const R = rng(1000 * k + frame.value * 7 + 11)
  return Array.from({ length: N_ARROWS }, () => [G[0] + R.n() * SIGMA / Math.sqrt(B), G[1] + R.n() * SIGMA / Math.sqrt(B)])
}))
const head = (x: number, y: number, dx: number, dy: number) => {
  const a = Math.atan2(dy, dx); const L = 9
  return `M${x},${y} L${x - L * Math.cos(a - 0.4)},${y - L * Math.sin(a - 0.4)} M${x},${y} L${x - L * Math.cos(a + 0.4)},${y - L * Math.sin(a + 0.4)}`
}
</script>

<template>
  <div class="mt-3">
    <svg :viewBox="`0 0 ${3 * PW + 2 * GAP} ${PH + 40}`" class="w-full" role="img" aria-label="Gradient estimates from mini-batches of 1, 16 and 256 examples: widely scattered, clustered, and almost exactly the true gradient">
      <g v-for="(B, k) in SIZES" :key="B" :transform="`translate(${k * (PW + GAP)} 0)`">
        <rect x="0" y="0" :width="PW" :height="PH" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: C.grid }" />
        <text x="14" y="26" style="font-size: 17px; font-weight: 700" :style="{ fill: COLORS[k] }">batch size {{ B }}</text>
        <g :transform="`translate(${PW / 2 - 40} ${PH / 2 + 10})`">
          <g v-for="(a, i) in arrows[k]" :key="i">
            <line x1="0" y1="0" :x2="a[0]" :y2="a[1]" :style="{ stroke: COLORS[k], strokeWidth: 2, strokeOpacity: 0.7 }" />
            <path :d="head(a[0], a[1], a[0], a[1])" :style="{ fill: 'none', stroke: COLORS[k], strokeWidth: 2, strokeOpacity: 0.7 }" />
          </g>
          <line x1="0" y1="0" :x2="G[0]" :y2="G[1]" :style="{ stroke: C.text, strokeWidth: 3.5 }" />
          <path :d="head(G[0], G[1], G[0], G[1])" :style="{ fill: 'none', stroke: C.text, strokeWidth: 3.5 }" />
          <circle cx="0" cy="0" r="4" :style="{ fill: C.text }" />
        </g>
        <text :x="PW / 2" :y="PH + 26" text-anchor="middle" style="font-size: 15px" :style="{ fill: C.text }">
          spread ∝ 1/√{{ B }} = <tspan :style="{ fill: COLORS[k], fontWeight: 700 }">{{ (1 / Math.sqrt(B)).toFixed(B === 1 ? 0 : 2) }}</tspan>
        </text>
      </g>
    </svg>
    <div class="grid grid-cols-3 gap-4 mt-3 text-sm text-left">
      <div border="2 solid white/10" bg="white/5" rounded-lg px-3 py-1.5>White: the true gradient over all training data. Colored: one estimate per mini-batch.</div>
      <div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-1.5><b class="text-amber-300">16× the batch</b> is only 4× less noisy, at 16× the cost per step.</div>
      <div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-1.5><b class="text-teal-300">Default: 32–256.</b> A bigger batch can usually take a bigger learning rate.</div>
    </div>
  </div>
</template>
