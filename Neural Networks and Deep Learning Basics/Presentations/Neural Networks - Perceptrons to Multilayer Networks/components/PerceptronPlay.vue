<script setup lang="ts">
// Drag the perceptron's weights and bias; the decision line and the two predicted regions follow.
// The weight vector w (arrow) always points into the "+1" region, perpendicular to the line.
// Misclassified points get a red ring. Data: admitted (+1) or not (-1) from two standardized scores.
import { computed, ref } from 'vue'
import { halfPlane, lineInBox } from '../utils/geom'
import { arrow, C, pathOf } from '../utils/plot'
import { separable } from '../utils/rng'

const data = separable()
const w1 = ref(0.2); const w2 = ref(1.0); const b = ref(0.3)
const w = computed(() => [w1.value, w2.value])

const S = 300; const pad = 14
const box = [-1.15, 1.15, -1.15, 1.15]
const sx = (x: number) => pad + (x - box[0]) / (box[1] - box[0]) * (S - 2 * pad)
const sy = (y: number) => S - pad - (y - box[2]) / (box[3] - box[2]) * (S - 2 * pad)
const toS = (P: number[][]) => P.map(p => [sx(p[0]), sy(p[1])])

const pos = computed(() => pathOf(toS(halfPlane(w.value, b.value, box, 1))))
const neg = computed(() => pathOf(toS(halfPlane(w.value, b.value, box, -1))))
const seg = computed(() => toS(lineInBox(w.value, b.value, box)))
const pred = (x: number[]) => (w.value[0] * x[0] + w.value[1] * x[1] + b.value > 0 ? 1 : -1)
const errors = computed(() => data.filter(d => pred(d.x) !== d.y).length)
// arrow for w, starting at the point on the line closest to the origin
const wArrow = computed(() => {
  const n2 = w.value[0] ** 2 + w.value[1] ** 2
  if (n2 < 1e-6) return null
  const p = [-b.value * w.value[0] / n2, -b.value * w.value[1] / n2]
  const L = 0.45 / Math.sqrt(n2)
  return arrow(sx(p[0]), sy(p[1]), sx(p[0] + L * w.value[0]), sy(p[1] + L * w.value[1]), 10)
})
const sliders = [
  { label: 'w₁', v: w1, color: C.teal },
  { label: 'w₂', v: w2, color: C.teal },
  { label: 'b', v: b, color: C.amber },
]
</script>

<template>
  <div class="grid grid-cols-[1fr_1.05fr] gap-6 items-center text-left">
    <svg :viewBox="`0 0 ${S} ${S}`" class="w-full" style="max-height: 330px" role="img" aria-label="Two groups of points and a draggable linear decision boundary">
      <path :d="`${pos}Z`" :style="{ fill: C.teal, fillOpacity: 0.13 }" />
      <path :d="`${neg}Z`" :style="{ fill: C.violet, fillOpacity: 0.13 }" />
      <line :x1="sx(box[0])" :x2="sx(box[1])" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: C.grid }" />
      <line :x1="sx(0)" :x2="sx(0)" :y1="sy(box[2])" :y2="sy(box[3])" :style="{ stroke: C.grid }" />
      <line v-if="seg.length === 2" :x1="seg[0][0]" :y1="seg[0][1]" :x2="seg[1][0]" :y2="seg[1][1]" :style="{ stroke: C.text, strokeWidth: 2.5 }" />
      <g v-if="wArrow">
        <path :d="wArrow.line" :style="{ stroke: C.amber, strokeWidth: 2.5 }" />
        <path :d="wArrow.head" :style="{ stroke: C.amber, strokeWidth: 2.5, fill: 'none' }" />
      </g>
      <g v-for="(d, i) in data" :key="i">
        <circle v-if="pred(d.x) !== d.y" :cx="sx(d.x[0])" :cy="sy(d.x[1])" r="9" :style="{ fill: 'none', stroke: C.red, strokeWidth: 2 }" />
        <circle v-if="d.y > 0" :cx="sx(d.x[0])" :cy="sy(d.x[1])" r="5" :style="{ fill: C.teal }" />
        <rect v-else :x="sx(d.x[0]) - 4.5" :y="sy(d.x[1]) - 4.5" width="9" height="9" :style="{ fill: C.violet }" />
      </g>
      <text :x="S - pad" :y="sy(0) - 6" text-anchor="end" :style="{ fill: C.muted, fontSize: '11px' }">exam x₁</text>
      <text :x="sx(0) + 5" :y="pad + 8" :style="{ fill: C.muted, fontSize: '11px' }">interview x₂</text>
    </svg>
    <div>
      <div class="font-mono text-lg mb-3">
        ŷ = step(<span class="text-teal-300">{{ w1.toFixed(2) }}</span>·x₁ + <span class="text-teal-300">{{ w2.toFixed(2) }}</span>·x₂ + <span class="text-amber-300">{{ b.toFixed(2) }}</span>)
      </div>
      <div v-for="s in sliders" :key="s.label" class="flex items-center gap-3 my-2">
        <span class="font-mono w-8" :style="{ color: s.color }">{{ s.label }}</span>
        <input v-model.number="s.v.value" type="range" min="-1.5" max="1.5" step="0.01" class="flex-1" :style="{ accentColor: s.color }" :aria-label="`perceptron ${s.label}`">
        <span class="font-mono w-14 text-right">{{ s.v.value.toFixed(2) }}</span>
      </div>
      <div class="mt-4 text-lg">
        misclassified:
        <span class="font-mono text-2xl" :class="errors ? 'text-red-300' : 'text-teal-300'">{{ errors }}</span>
        <span class="opacity-60"> / {{ data.length }}</span>
      </div>
      <div class="text-sm opacity-75 mt-2">
        <span class="inline-block w-3 h-3 rounded-full bg-teal-400 align-middle" /> admitted (+1)
        <span class="inline-block w-3 h-3 bg-violet-400 align-middle ml-4" /> not admitted (−1)
        <span class="text-amber-300 ml-4">→</span> w
      </div>
    </div>
  </div>
</template>
