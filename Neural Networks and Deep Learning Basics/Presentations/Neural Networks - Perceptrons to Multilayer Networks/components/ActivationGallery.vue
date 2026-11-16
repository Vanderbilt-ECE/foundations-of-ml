<script setup lang="ts">
// Four activation functions, side by side, with one input z sweeping back and forth through all of them.
// Each card shows the curve, where the current z lands, and the output f(z). Print mode freezes z = 1.
import { ref } from 'vue'
import { C, pathOf, useLoop } from '../utils/plot'

const z = ref(1)
useLoop((_, t) => { z.value = 3.6 * Math.sin(t * 0.9) })

const FNS = [
  { name: 'Step', f: (v: number) => (v > 0 ? 1 : 0), eq: 'z > 0 ? 1 : 0', range: '{0, 1}', note: 'the original perceptron; flat almost everywhere, so no gradient to learn from', col: C.dim, lo: -0.2, hi: 1.2 },
  { name: 'Sigmoid', f: (v: number) => 1 / (1 + Math.exp(-v)), eq: '1 / (1 + e⁻ᶻ)', range: '(0, 1)', note: 'a smooth step; reads as a probability', col: C.blue, lo: -0.2, hi: 1.2 },
  { name: 'Tanh', f: Math.tanh, eq: '(eᶻ − e⁻ᶻ) / (eᶻ + e⁻ᶻ)', range: '(−1, 1)', note: 'a sigmoid centered at zero', col: C.violet, lo: -1.3, hi: 1.3 },
  { name: 'ReLU', f: (v: number) => Math.max(0, v), eq: 'max(0, z)', range: '[0, ∞)', note: 'the modern default for hidden layers: cheap, and it doesn’t flatten out for large z', col: C.teal, lo: -0.6, hi: 4 },
]
const W = 200; const H = 130; const ZR = 4
const sx = (v: number) => 10 + (v + ZR) / (2 * ZR) * (W - 20)
const sy = (fn: typeof FNS[number], v: number) => H - 12 - (v - fn.lo) / (fn.hi - fn.lo) * (H - 24)
const curve = (fn: typeof FNS[number]) => {
  const P: number[][] = []
  for (let i = 0; i <= 160; i++) {
    const v = -ZR + 2 * ZR * i / 160
    // draw the step's jump as a vertical segment
    if (fn.name === 'Step' && i > 0 && (-ZR + 2 * ZR * (i - 1) / 160) <= 0 && v > 0) P.push([sx(0), sy(fn, 0)], [sx(0), sy(fn, 1)])
    P.push([sx(v), sy(fn, fn.f(v))])
  }
  return pathOf(P)
}
const paths = FNS.map(curve)
</script>

<template>
  <div class="grid grid-cols-4 gap-3 text-left">
    <div v-for="(fn, k) in FNS" :key="fn.name" border="2 solid white/5" bg="white/5" rounded-lg p-3>
      <div class="flex justify-between items-baseline">
        <span class="font-bold" :style="{ color: fn.col === C.dim ? C.muted : fn.col }">{{ fn.name }}</span>
        <span class="font-mono text-xs opacity-70">{{ fn.range }}</span>
      </div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full my-1" role="img" :aria-label="`${fn.name} activation curve`">
        <line :x1="sx(-ZR)" :x2="sx(ZR)" :y1="sy(fn, 0)" :y2="sy(fn, 0)" :style="{ stroke: C.grid }" />
        <line :x1="sx(0)" :x2="sx(0)" y1="6" :y2="H - 6" :style="{ stroke: C.grid }" />
        <path :d="paths[k]" :style="{ fill: 'none', stroke: fn.col === C.dim ? C.muted : fn.col, strokeWidth: 2.6 }" />
        <line :x1="sx(z)" :x2="sx(z)" :y1="sy(fn, 0)" :y2="sy(fn, fn.f(z))" :style="{ stroke: C.amber, strokeDasharray: '3 3', strokeOpacity: 0.7 }" />
        <circle :cx="sx(z)" :cy="sy(fn, fn.f(z))" r="5" :style="{ fill: C.amber }" />
      </svg>
      <div class="font-mono text-xs opacity-80">{{ fn.eq }}</div>
      <div class="font-mono text-sm mt-1">f(<span class="text-amber-300">{{ z.toFixed(1) }}</span>) = <span class="text-amber-300">{{ fn.f(z).toFixed(2) }}</span></div>
      <div class="text-xs opacity-70 mt-1 leading-snug">{{ fn.note }}</div>
    </div>
  </div>
</template>
