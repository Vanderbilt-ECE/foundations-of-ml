<script setup lang="ts">
// The whole of PCA as motion, on the projection cloud (data/drag.json) placed off-center.
// step 0: raw data · 1: subtract the mean · 2: rotate so the eigenvectors become the axes (the scores Z)
// 3: keep k = 1: every point drops onto the PC1 axis · 4: map back and add the mean (the reconstruction X̂),
// with the residuals to the original points. One tweened phase drives every point, so the moves blend smoothly.
import { computed } from 'vue'
import d from '../data/drag.json'
import { eig2, useTween } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const phase = useTween(() => props.step, 1300)
const E = eig2(d.S)
const mu = d.offset
const raw = d.pts.map(p => [p[0] + mu[0], p[1] + mu[1]])
const W = 560; const H = 300; const U = 30
const sx = (x: number) => 150 + x * U
const sy = (y: number) => H / 2 + 20 - y * U
const rot = (p: number[], a: number) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)]
const clamp = (x: number) => Math.max(0, Math.min(1, x))

// where everything is at a given phase
function at(ph: number, p: number[]) {
  const c = clamp(ph); const r = clamp(ph - 1); const k = clamp(ph - 2); const b = clamp(ph - 3)
  let q = [p[0] - c * mu[0], p[1] - c * mu[1]] // centering
  q = rot(q, -r * E.ang) // rotate PC1 onto the x-axis
  q = [q[0], q[1] * (1 - k)] // drop PC2
  q = rot(q, b * E.ang) // back to the original axes
  return [q[0] + b * mu[0], q[1] + b * mu[1]]
}
const pts = computed(() => raw.map(p => at(phase.value, p)))
const origin = computed(() => at(phase.value, mu)) // the data mean, carried along
const axisAng = computed(() => E.ang * (1 - clamp(phase.value - 1)) + E.ang * clamp(phase.value - 3))
const pc = computed(() => [0, Math.PI / 2].map(o => [Math.cos(axisAng.value + o), Math.sin(axisAng.value + o)]))
const resid = computed(() => clamp(phase.value - 3.5) * 2)
const LABELS = ['raw data X', 'centered: X − μ', 'rotated: Z = (X − μ) Q', 'keep PC1: Z₁ = (X − μ) q₁', 'reconstruct: X̂ = μ + Z₁ q₁ᵀ']
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 320px" role="img" aria-label="A point cloud being centered, rotated onto its principal axes, flattened onto the first axis, and mapped back">
    <line :x1="sx(-4.5)" :x2="sx(12)" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#475569' }" />
    <line :x1="sx(0)" :x2="sx(0)" :y1="sy(-4.5)" :y2="sy(5.3)" :style="{ stroke: '#475569' }" />
    <text :x="sx(12)" :y="sy(0) - 6" text-anchor="end" :style="{ fill: '#64748b', fontSize: '12px' }">x₁</text>
    <text :x="sx(0) + 6" :y="sy(5.3) + 10" :style="{ fill: '#64748b', fontSize: '12px' }">x₂</text>
    <!-- principal axes, attached to the data mean -->
    <line
      v-for="(a, i) in pc" :key="i" :x1="sx(origin[0] - (i ? 1.6 : 4.4) * a[0])" :y1="sy(origin[1] - (i ? 1.6 : 4.4) * a[1])"
      :x2="sx(origin[0] + (i ? 1.6 : 4.4) * a[0])" :y2="sy(origin[1] + (i ? 1.6 : 4.4) * a[1])"
      :style="{ stroke: i ? '#a78bfa' : '#fbbf24', strokeWidth: 2.2, strokeOpacity: i ? Math.max(0.15, 0.8 - clamp(phase - 2) * 0.65) : 0.85 }"
    />
    <g v-if="resid > 0">
      <line v-for="(p, i) in pts" :key="`r${i}`" :x1="sx(p[0])" :y1="sy(p[1])" :x2="sx(raw[i][0])" :y2="sy(raw[i][1])" :style="{ stroke: '#f87171', strokeOpacity: 0.6 * resid, strokeWidth: 1.2 }" />
      <circle v-for="(p, i) in raw" :key="`o${i}`" :cx="sx(p[0])" :cy="sy(p[1])" r="2.6" :style="{ fill: '#cbd5e1', fillOpacity: 0.35 * resid }" />
    </g>
    <circle v-for="(p, i) in pts" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="3.4" :style="{ fill: phase > 2.5 ? '#fbbf24' : '#2dd4bf', fillOpacity: 0.9, transition: 'fill 0.6s' }" />
    <circle :cx="sx(origin[0])" :cy="sy(origin[1])" r="5" :style="{ fill: '#e2e8f0', stroke: '#0b1020', strokeWidth: 2 }" />
    <text :x="sx(origin[0]) + 8" :y="sy(origin[1]) + 18" :style="{ fill: '#e2e8f0', fontSize: '13px' }">μ</text>
    <text :x="W - 10" y="26" text-anchor="end" :style="{ fill: '#e2e8f0', fontSize: '17px' }" class="font-mono">{{ LABELS[Math.round(Math.min(4, Math.max(0, phase)))] }}</text>
  </svg>
</template>
