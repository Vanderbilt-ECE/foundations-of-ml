<script setup lang="ts">
// Why "maximize variance" and "minimize reconstruction error" are the same problem, for one point.
// x is fixed; the line through the origin turns. The right triangle O, projection, x has a fixed hypotenuse |x|,
// so the squares on its legs trade area: (vᵀx)² + |r|² = |x|² at every angle. The PDF export freezes at 25°.
import { computed, ref } from 'vue'
import { useLoop } from '../utils/plot'

const W = 460; const H = 410
const O = [130, 245]
const X = [270, 145] // the point, in SVG coordinates
const th = ref(-25 * Math.PI / 180) // SVG y points down, so this is 25 degrees up
useLoop((_, t) => { th.value = -(0.45 + 0.4 * Math.sin(0.5 * t)) })

const v = computed(() => [Math.cos(th.value), Math.sin(th.value)])
const t = computed(() => (X[0] - O[0]) * v.value[0] + (X[1] - O[1]) * v.value[1])
const P = computed(() => [O[0] + t.value * v.value[0], O[1] + t.value * v.value[1]])

// square on segment AB, built on the side away from C
function sq(A: number[], B: number[], C: number[]) {
  const dx = B[0] - A[0]; const dy = B[1] - A[1]
  let nx = -dy; let ny = dx
  if ((C[0] - A[0]) * nx + (C[1] - A[1]) * ny > 0) { nx = -nx; ny = -ny }
  const pts = [A, B, [B[0] + nx, B[1] + ny], [A[0] + nx, A[1] + ny]]
  return `M${pts.map(p => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('L')}Z`
}
const U = 50 // pixels per unit for the readout
const a2 = computed(() => (t.value / U) ** 2)
const c2 = ((X[0] - O[0]) ** 2 + (X[1] - O[1]) ** 2) / U ** 2
const b2 = computed(() => c2 - a2.value)
</script>

<template>
  <div class="grid grid-cols-[1.3fr_1fr] gap-4 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 340px" role="img" aria-label="A right triangle between the origin, a point, and its projection on a turning line, with squares on all three sides">
      <path :d="sq(O, X, P)" :style="{ fill: '#2dd4bf', fillOpacity: 0.06, stroke: '#2dd4bf', strokeWidth: 1.5, strokeDasharray: '5 4' }" />
      <path :d="sq(O, P, X)" :style="{ fill: '#fbbf24', fillOpacity: 0.22, stroke: '#fbbf24', strokeWidth: 1.5 }" />
      <path :d="sq(P, X, O)" :style="{ fill: '#f87171', fillOpacity: 0.25, stroke: '#f87171', strokeWidth: 1.5 }" />
      <line :x1="O[0] - 300 * v[0]" :y1="O[1] - 300 * v[1]" :x2="O[0] + 400 * v[0]" :y2="O[1] + 400 * v[1]" :style="{ stroke: '#fbbf24', strokeOpacity: 0.5 }" />
      <line :x1="O[0]" :y1="O[1]" :x2="X[0]" :y2="X[1]" :style="{ stroke: '#2dd4bf', strokeWidth: 2.5 }" />
      <line :x1="O[0]" :y1="O[1]" :x2="P[0]" :y2="P[1]" :style="{ stroke: '#fbbf24', strokeWidth: 3 }" />
      <line :x1="P[0]" :y1="P[1]" :x2="X[0]" :y2="X[1]" :style="{ stroke: '#f87171', strokeWidth: 3 }" />
      <circle :cx="O[0]" :cy="O[1]" r="4" :style="{ fill: '#e2e8f0' }" />
      <circle :cx="X[0]" :cy="X[1]" r="6" :style="{ fill: '#e2e8f0', stroke: '#0b1020', strokeWidth: 2 }" />
      <circle :cx="P[0]" :cy="P[1]" r="5" :style="{ fill: '#fbbf24' }" />
      <text :x="O[0] - 8" :y="O[1] + 20" :style="{ fill: '#cbd5e1', fontSize: '14px' }">0</text>
      <text :x="X[0] + 10" :y="X[1] - 6" :style="{ fill: '#e2e8f0', fontSize: '15px', fontWeight: 700 }">x</text>
    </svg>
    <div class="text-left font-mono space-y-2">
      <div class="text-teal-300">|x|² = {{ c2.toFixed(2) }} <span class="text-xs opacity-60 font-sans">fixed</span></div>
      <div class="text-amber-300">(vᵀx)² = {{ a2.toFixed(2) }} <span class="text-xs opacity-60 font-sans">kept</span></div>
      <div class="text-red-300">|r|² = {{ b2.toFixed(2) }} <span class="text-xs opacity-60 font-sans">lost</span></div>
      <div class="h-3 rounded-sm overflow-hidden flex mt-2" style="background: rgba(148,163,184,0.15)">
        <div :style="{ width: `${100 * a2 / c2}%`, background: '#fbbf24' }" />
        <div :style="{ width: `${100 * b2 / c2}%`, background: '#f87171' }" />
      </div>
    </div>
  </div>
</template>
