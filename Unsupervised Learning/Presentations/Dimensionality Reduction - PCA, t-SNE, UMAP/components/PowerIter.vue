<script setup lang="ts">
// Power iteration: v <- Σv / |Σv|, repeated. Each step stretches v toward the top eigenvector; the error
// angle shrinks by a factor of about λ₂/λ₁ per step. Two matrices with the same eigenvectors:
// the projection cloud's (λ₂/λ₁ = 0.10, done in three steps) and one with close eigenvalues (0.85, slow).
// Plays on a loop; the PDF export shows the finished run for the slow matrix.
import { computed, ref } from 'vue'
import d from '../data/drag.json'
import { arrow, eig2, useActive, useLoop } from '../utils/plot'

const E = eig2(d.S)
const build = (l1: number, l2: number) => [0, 1].map(i => [0, 1].map(j => l1 * E.v1[i] * E.v1[j] + l2 * E.v2[i] * E.v2[j]))
const MATS = [
  { name: 'our cloud', S: d.S, ratio: d.lam[1] / d.lam[0] },
  { name: 'close eigenvalues', S: build(1, 0.85), ratio: 0.85 },
]
const which = ref(1)
const START = E.ang + Math.PI / 2 - 0.12 // almost perpendicular to v₁: a bad start
const STEPS = 24
const { isPrintMode } = useActive()

function run(S: number[][]) {
  const vs: number[][] = [[Math.cos(START), Math.sin(START)]]
  for (let k = 0; k < STEPS; k++) {
    const v = vs[k]
    const w = [S[0][0] * v[0] + S[0][1] * v[1], S[1][0] * v[0] + S[1][1] * v[1]]
    const n = Math.hypot(w[0], w[1])
    vs.push([w[0] / n, w[1] / n])
  }
  return vs
}
const path = computed(() => run(MATS[which.value].S))
const err = (v: number[]) => Math.acos(Math.min(1, Math.abs(v[0] * E.v1[0] + v[1] * E.v1[1]))) * 180 / Math.PI
const k = ref(isPrintMode.value ? STEPS : 0)
let acc = 0
useLoop((dt) => {
  acc += dt
  if (acc < 0.7) return
  acc = 0
  k.value = k.value >= STEPS + 3 ? 0 : k.value + 1 // hold the result for a few beats, then restart
}, () => { k.value = 0; acc = 0 })
const shown = computed(() => Math.min(k.value, STEPS))
function pick(i: number) { which.value = i; k.value = 0; acc = 0 }

const W = 330; const H = 300; const U = 120
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const errs = computed(() => path.value.slice(0, shown.value + 1).map(err))
const CW = 300; const CH = 170
const ex = (i: number) => 30 + i * (CW - 40) / STEPS
const ey = (e: number) => 12 + (2 - Math.log10(Math.max(e, 1e-3))) / 5 * (CH - 40) // log scale, 100° down to 0.001°
</script>

<template>
  <div class="grid grid-cols-2 gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 300px" role="img" aria-label="Successive power-iteration vectors on the unit circle, turning toward the top eigenvector">
      <circle :cx="sx(0)" :cy="sy(0)" :r="U" :style="{ fill: 'none', stroke: '#475569' }" />
      <line v-for="s in [-1, 1]" :key="s" :x1="sx(0)" :y1="sy(0)" :x2="sx(s * 1.15 * E.v1[0])" :y2="sy(s * 1.15 * E.v1[1])" :style="{ stroke: '#fbbf24', strokeOpacity: 0.45, strokeDasharray: '3 4', strokeWidth: 2 }" />
      <text :x="sx(1.2 * E.v1[0])" :y="sy(1.2 * E.v1[1])" :style="{ fill: '#fcd34d', fontSize: '13px' }">v₁</text>
      <g v-for="(v, i) in path.slice(0, shown + 1)" :key="i" :style="{ stroke: i === shown ? '#2dd4bf' : '#94a3b8', strokeOpacity: i === shown ? 1 : 0.25 + 0.5 * i / (shown + 1), strokeWidth: i === shown ? 3.5 : 1.5, fill: 'none' }">
        <path :d="arrow(sx(0), sy(0), sx(v[0]), sy(v[1]), i === shown ? 10 : 6).line" />
        <path :d="arrow(sx(0), sy(0), sx(v[0]), sy(v[1]), i === shown ? 10 : 6).head" />
      </g>
      <text :x="12" :y="22" :style="{ fill: '#5eead4', fontSize: '15px' }" class="font-mono">step {{ shown }}</text>
    </svg>
    <div class="text-left space-y-3">
      <div class="flex gap-2">
        <button
          v-for="(m, i) in MATS" :key="m.name" class="px-2 py-1 rounded-md text-xs transition-all"
          :style="{ border: `2px solid ${which === i ? '#2dd4bf' : 'rgba(255,255,255,0.08)'}`, background: which === i ? 'rgba(45,212,191,0.15)' : 'rgba(255,255,255,0.03)' }"
          @click="pick(i)"
        >
          {{ m.name }} · λ₂/λ₁ = {{ m.ratio.toFixed(2) }}
        </button>
      </div>
      <svg :viewBox="`0 0 ${CW} ${CH}`" class="w-full" role="img" aria-label="Angle error against v1 per step, log scale">
        <line x1="30" :x2="CW - 10" :y1="CH - 22" :y2="CH - 22" :style="{ stroke: '#64748b' }" />
        <text v-for="e in [100, 1, 0.01]" :key="e" x="26" :y="ey(e) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ e }}°</text>
        <path :d="errs.map((e, i) => `${i ? 'L' : 'M'}${ex(i).toFixed(1)},${ey(e).toFixed(1)}`).join('')" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 2 }" />
        <circle v-for="(e, i) in errs" :key="i" :cx="ex(i)" :cy="ey(e)" r="2.5" :style="{ fill: '#2dd4bf' }" />
        <text :x="CW / 2" :y="CH - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">step</text>
      </svg>
      <div class="font-mono text-sm">angle to v₁: <span class="text-teal-300">{{ err(path[shown]).toFixed(err(path[shown]) < 0.1 ? 4 : 1) }}°</span></div>
    </div>
  </div>
</template>
