<script setup lang="ts">
// Covariance as geometry. Sigma = V diag(l1, l2) V^T, with the eigenvectors V rotating and l1 breathing.
// 200 fixed standard-normal draws z are mapped to x = V sqrt(L) z, so the cloud turns and stretches with Sigma.
// Arrows: the eigenvectors scaled by sqrt(eigenvalue) = the ellipse's semi-axes. Readout: the matrix entries live.
// The PDF export freezes at a 30 degree tilt.
import { computed, ref } from 'vue'
import { ellipsePath, rng, useLoop } from '../utils/gmm'

const W = 380; const H = 300; const U = 30 // pixels per unit
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const th = ref(Math.PI / 6); const l1 = ref(3); const l2 = ref(0.35)
useLoop((dt, t) => {
  th.value += dt * 0.35
  l1.value = 2.6 + 1.2 * Math.sin(0.6 * t)
  l2.value = 0.32 + 0.18 * Math.sin(0.9 * t + 1)
}, () => { th.value = Math.PI / 6 })

const R = rng(4)
const Z = Array.from({ length: 200 }, () => [R.n(), R.n()])
const v1 = computed(() => [Math.cos(th.value), Math.sin(th.value)])
const v2 = computed(() => [-Math.sin(th.value), Math.cos(th.value)])
const S = computed(() => {
  const [a, b] = v1.value; const [c, d] = v2.value
  return [[l1.value * a * a + l2.value * c * c, l1.value * a * b + l2.value * c * d], [l1.value * a * b + l2.value * c * d, l1.value * b * b + l2.value * d * d]]
})
const pts = computed(() => Z.map(([p, q]) => {
  const a = Math.sqrt(l1.value) * p; const b = Math.sqrt(l2.value) * q
  return [a * v1.value[0] + b * v2.value[0], a * v1.value[1] + b * v2.value[1]]
}))
const rho = computed(() => S.value[0][1] / Math.sqrt(S.value[0][0] * S.value[1][1]))
const deg = computed(() => ((th.value * 180 / Math.PI) % 180 + 180) % 180)
const f = (v: number) => (v >= 0 ? ' ' : '') + v.toFixed(2)
const arrow = (v: number[], s: number) => {
  const x2 = sx(v[0] * s); const y2 = sy(v[1] * s)
  const a = Math.atan2(y2 - H / 2, x2 - W / 2)
  const h = (o: number) => `${(x2 - 9 * Math.cos(a + o)).toFixed(1)},${(y2 - 9 * Math.sin(a + o)).toFixed(1)}`
  return { line: `M${W / 2},${H / 2}L${x2.toFixed(1)},${y2.toFixed(1)}`, head: `M${h(0.45)}L${x2.toFixed(1)},${y2.toFixed(1)}L${h(-0.45)}`, x: x2, y: y2 }
}
const a1 = computed(() => arrow(v1.value, Math.sqrt(l1.value)))
const a2 = computed(() => arrow(v2.value, Math.sqrt(l2.value)))
</script>

<template>
  <div class="grid grid-cols-[1.25fr_1fr] gap-4 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 330px" role="img" aria-label="A tilted ellipse of points rotating and stretching, with its two principal axes drawn as arrows">
      <line :x1="0" :x2="W" :y1="H / 2" :y2="H / 2" :style="{ stroke: '#334155' }" />
      <line :x1="W / 2" :x2="W / 2" :y1="0" :y2="H" :style="{ stroke: '#334155' }" />
      <circle v-for="(p, i) in pts" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="2.3" :style="{ fill: '#94a3b8', fillOpacity: 0.55 }" />
      <path :d="ellipsePath([0, 0], S, 2, sx, sy)" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 1.4, strokeDasharray: '5 4' }" />
      <path :d="ellipsePath([0, 0], S, 1, sx, sy)" :style="{ fill: '#2dd4bf', fillOpacity: 0.1, stroke: '#2dd4bf', strokeWidth: 2.4 }" />
      <path :d="a1.line" :style="{ stroke: '#fbbf24', strokeWidth: 3 }" /><path :d="a1.head" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 3 }" />
      <path :d="a2.line" :style="{ stroke: '#a78bfa', strokeWidth: 3 }" /><path :d="a2.head" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 3 }" />
      <text :x="a1.x + 10 * Math.cos(th)" :y="a1.y - 10 * Math.sin(th) - 4" :style="{ fill: '#fcd34d', fontSize: '13px', fontWeight: 700 }">√λ₁ v₁</text>
      <text :x="a2.x - 14 * Math.sin(th)" :y="a2.y - 14 * Math.cos(th)" :style="{ fill: '#c4b5fd', fontSize: '13px', fontWeight: 700 }">√λ₂ v₂</text>
    </svg>
    <div class="text-left space-y-3">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
        <div class="text-xs opacity-60 uppercase tracking-wide mb-1">Σ (live)</div>
        <div class="flex items-center gap-2 font-mono text-lg">
          <span class="text-3xl opacity-60">[</span>
          <div class="grid grid-cols-2 gap-x-5">
            <span>{{ f(S[0][0]) }}</span><span class="text-teal-300">{{ f(S[0][1]) }}</span>
            <span class="text-teal-300">{{ f(S[1][0]) }}</span><span>{{ f(S[1][1]) }}</span>
          </div>
          <span class="text-3xl opacity-60">]</span>
        </div>
      </div>
      <div class="font-mono text-sm space-y-1 px-1">
        <div><span class="text-amber-300">λ₁ = {{ l1.toFixed(2) }}</span> · <span class="text-violet-300">λ₂ = {{ l2.toFixed(2) }}</span></div>
        <div>tilt = {{ deg.toFixed(0) }}° · corr ρ = {{ rho.toFixed(2) }}</div>
      </div>
      <div class="text-xs opacity-75 px-1">Diagonal entries: spread along each axis. Off-diagonal: tilt (correlation). Eigenvectors: the ellipse's axes; √eigenvalues: its radii.</div>
    </div>
  </div>
</template>
