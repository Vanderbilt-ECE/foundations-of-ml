<script setup lang="ts">
// Gradient descent on a loss surface over two weights, seen from above (contour lines = equal loss).
// The arrow at the current point is the negative gradient: the steepest way down from here.
// Each step: w ← w − η ∇L(w). The walk restarts from a new starting point after it settles.
// The surface is a tilted quadratic bowl L(w) = ½ (w − w*)ᵀ A (w − w*), with one steep and one shallow direction.
// Print mode shows one full path.
import { computed, reactive } from 'vue'
import { arrow, C, pathOf, useActive, useLoop } from '../utils/plot'

const TH = Math.PI / 6
const ev = [0.8, 5]
const Q = [[Math.cos(TH), -Math.sin(TH)], [Math.sin(TH), Math.cos(TH)]]
const A = [0, 1].map(i => [0, 1].map(j => Q[i][0] * ev[0] * Q[j][0] + Q[i][1] * ev[1] * Q[j][1]))
const WS = [0.4, -0.2]
const ETA = 0.14
const grad = (w: number[]) => { const d = [w[0] - WS[0], w[1] - WS[1]]; return [A[0][0] * d[0] + A[0][1] * d[1], A[1][0] * d[0] + A[1][1] * d[1]] }
const loss = (w: number[]) => { const g = grad(w); return 0.5 * ((w[0] - WS[0]) * g[0] + (w[1] - WS[1]) * g[1]) }
const STARTS = [[-2.2, 1.6], [2.4, 1.4], [-1.6, -2.1]]
const STEPS = 22

const st = reactive({ run: 0, path: [STARTS[0]] as number[][], timer: 0.6 })
function restart(run: number) { st.run = run % STARTS.length; st.path = [STARTS[st.run]]; st.timer = 0.8 }
const stepOnce = () => { const w = st.path.at(-1)!; const g = grad(w); st.path = [...st.path, [w[0] - ETA * g[0], w[1] - ETA * g[1]]] }
const { isPrintMode } = useActive()
if (isPrintMode.value) for (let i = 0; i < 12; i++) stepOnce()
useLoop((dt) => {
  st.timer -= dt
  if (st.timer > 0) return
  if (st.path.length > STEPS) { restart(st.run + 1); return }
  stepOnce(); st.timer = st.path.length > STEPS ? 2.2 : 0.42
}, () => restart(0))

const S = 340; const RNG = 3
const sx = (x: number) => S / 2 + x / RNG * (S / 2 - 8)
const sy = (y: number) => S / 2 - y / RNG * (S / 2 - 8)
// contour ellipses: level c ⇒ semi-axes sqrt(2c/λ) along the eigenvectors
const contours = [0.1, 0.4, 1, 2, 3.5, 5.5, 8, 11].map((c) => {
  const P: number[][] = []
  for (let i = 0; i <= 90; i++) {
    const t = i / 90 * 2 * Math.PI
    const u = Math.sqrt(2 * c / ev[0]) * Math.cos(t); const v = Math.sqrt(2 * c / ev[1]) * Math.sin(t)
    P.push([sx(WS[0] + Q[0][0] * u + Q[0][1] * v), sy(WS[1] + Q[1][0] * u + Q[1][1] * v)])
  }
  return pathOf(P)
})
const cur = computed(() => st.path.at(-1)!)
const gArrow = computed(() => {
  const g = grad(cur.value); const n = Math.hypot(g[0], g[1])
  if (n < 0.05) return null
  const L = Math.min(1.1, 0.25 * n) / n
  return arrow(sx(cur.value[0]), sy(cur.value[1]), sx(cur.value[0] - L * g[0]), sy(cur.value[1] - L * g[1]), 10)
})
const LW = 260; const LH = 200
const lx = (k: number) => 30 + k / STEPS * (LW - 40)
const L0 = computed(() => loss(st.path[0]))
const ly = (l: number) => LH - 26 - l / Math.max(L0.value, 1e-9) * (LH - 46)
</script>

<template>
  <div class="grid grid-cols-[1.2fr_1fr] gap-6 items-center text-left">
    <svg :viewBox="`0 0 ${S} ${S}`" class="w-full" style="max-height: 330px" role="img" aria-label="A point stepping downhill across the contour lines of a loss surface">
      <path v-for="(d, i) in contours" :key="i" :d="`${d}Z`" :style="{ fill: C.blue, fillOpacity: 0.035, stroke: C.blue, strokeOpacity: 0.25 + 0.05 * (8 - i), strokeWidth: 1.3 }" />
      <circle :cx="sx(WS[0])" :cy="sy(WS[1])" r="4" :style="{ fill: C.teal }" />
      <text :x="sx(WS[0]) + 8" :y="sy(WS[1]) + 18" :style="{ fill: C.teal, fontSize: '12px' }">minimum</text>
      <path :d="pathOf(st.path.map(w => [sx(w[0]), sy(w[1])]))" :style="{ fill: 'none', stroke: C.amber, strokeWidth: 2, strokeOpacity: 0.8 }" />
      <circle v-for="(w, i) in st.path" :key="i" :cx="sx(w[0])" :cy="sy(w[1])" r="3" :style="{ fill: C.amber, fillOpacity: 0.6 }" />
      <g v-if="gArrow">
        <path :d="gArrow.line" :style="{ stroke: C.red, strokeWidth: 2.5 }" />
        <path :d="gArrow.head" :style="{ stroke: C.red, strokeWidth: 2.5, fill: 'none' }" />
      </g>
      <circle :cx="sx(cur[0])" :cy="sy(cur[1])" r="7" :style="{ fill: C.amber, stroke: '#0b1020', strokeWidth: 2 }" />
      <text :x="S - 6" :y="S - 8" text-anchor="end" :style="{ fill: C.muted, fontSize: '12px' }">weight w₁ →</text>
      <text x="8" y="16" :style="{ fill: C.muted, fontSize: '12px' }">↑ weight w₂</text>
    </svg>
    <div>
      <div class="font-mono text-lg mb-2">w ← w − η ∇L(w)</div>
      <div class="text-sm opacity-80 mb-3"><span class="text-red-300">→</span> −∇L: steepest way down from where we stand</div>
      <svg :viewBox="`0 0 ${LW} ${LH}`" class="w-full" role="img" aria-label="Loss after each step">
        <line x1="30" :x2="LW - 10" :y1="ly(0)" :y2="ly(0)" :style="{ stroke: C.grid }" />
        <text x="34" y="14" :style="{ fill: C.red, fontSize: '12px' }">loss</text>
        <rect v-for="(w, i) in st.path" :key="i" :x="lx(i) - 3" :y="ly(loss(w))" width="6" :height="Math.max(1, ly(0) - ly(loss(w)))" :style="{ fill: C.red, fillOpacity: 0.75 }" />
        <text :x="(LW + 30) / 2" :y="LH - 6" text-anchor="middle" :style="{ fill: C.muted, fontSize: '11px' }">step {{ st.path.length - 1 }}</text>
      </svg>
    </div>
  </div>
</template>
