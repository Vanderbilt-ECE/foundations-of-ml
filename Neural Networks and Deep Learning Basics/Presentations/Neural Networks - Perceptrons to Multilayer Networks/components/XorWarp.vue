<script setup lang="ts">
// How one hidden layer solves XOR, as motion.
// step 0: the four XOR points in input space
// 1: two hidden perceptrons draw two lines — h₁ = step(x₁ + x₂ − 0.5) ("OR"), h₂ = step(x₁ + x₂ − 1.5) ("AND")
// 2: every point moves to its hidden coordinates (h₁, h₂): (0,1) and (1,0) both land on (1,0)
// 3: in the new space one line separates the classes: ŷ = step(h₁ − h₂ − 0.5)
// 4: back in input space, the network's decision region is the band between the two hidden lines
import { computed } from 'vue'
import { boxPoly, clip, halfPlane, lineInBox } from '../utils/geom'
import { C, clamp, pathOf, useTween } from '../utils/plot'
import { XOR } from '../utils/rng'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const p = useTween(() => props.step, 1100)

const box = [-0.45, 1.45, -0.45, 1.45]
const S = 320; const pad = 16
const sx = (x: number) => pad + (x - box[0]) / (box[1] - box[0]) * (S - 2 * pad)
const sy = (y: number) => S - pad - (y - box[2]) / (box[3] - box[2]) * (S - 2 * pad)
const toS = (P: number[][]) => P.map(q => [sx(q[0]), sy(q[1])])
const segS = (w: number[], b: number) => toS(lineInBox(w, b, box))

const H = XOR.map(d => [d.x[0] + d.x[1] > 0.5 ? 1 : 0, d.x[0] + d.x[1] > 1.5 ? 1 : 0])
// the two points that collide at (1, 0) are nudged apart so both stay visible
const Hshow = H.map((h, i) => (i === 1 ? [h[0] - 0.06, h[1] + 0.06] : i === 2 ? [h[0] + 0.06, h[1] - 0.06] : h))

const lines = computed(() => clamp(p.value) * (1 - clamp(p.value - 1)) + clamp(p.value - 3))
const move = computed(() => clamp(p.value - 1) * (1 - clamp(p.value - 3)))
const outLine = computed(() => clamp(p.value - 2) * (1 - clamp(p.value - 3)))
const band = computed(() => clamp(p.value - 3))
const inHidden = computed(() => move.value > 0.5)

const pts = computed(() => XOR.map((d, i) => [d.x[0] + (Hshow[i][0] - d.x[0]) * move.value, d.x[1] + (Hshow[i][1] - d.x[1]) * move.value]))
const h1 = segS([1, 1], -0.5); const h2 = segS([1, 1], -1.5); const out = segS([1, -1], -0.5)
const outPos = pathOf(toS(halfPlane([1, -1], -0.5, box, 1)))
const bandPoly = pathOf(toS(clip(clip(boxPoly(box), [1, 1], -0.5, 1), [1, 1], -1.5, -1)))
const caption = computed(() => [
  'XOR: output 1 when exactly one input is 1',
  'Hidden layer: two perceptrons, two lines',
  'Each point moves to its hidden values (h₁, h₂)',
  'Now one line separates them',
  'Back in input space: a band, not a line',
][Math.round(clamp(p.value, 0, 4))])
</script>

<template>
  <svg :viewBox="`0 0 ${S + 200} ${S}`" class="w-full" style="max-height: 340px" role="img" aria-label="The four XOR points are moved by a hidden layer into a space where a single line separates them">
    <!-- band (step 4) and output half-plane (step 3) -->
    <path :d="`${bandPoly}Z`" :style="{ fill: C.teal, fillOpacity: 0.16 * band }" />
    <path :d="`${outPos}Z`" :style="{ fill: C.teal, fillOpacity: 0.16 * outLine }" />
    <!-- axes -->
    <line :x1="sx(box[0])" :x2="sx(box[1])" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: C.grid }" />
    <line :x1="sx(0)" :x2="sx(0)" :y1="sy(box[2])" :y2="sy(box[3])" :style="{ stroke: C.grid }" />
    <text :x="sx(box[1]) - 4" :y="sy(0) + 18" text-anchor="end" :style="{ fill: inHidden ? C.amber : C.muted, fontSize: '14px' }">{{ inHidden ? 'h₁' : 'x₁' }}</text>
    <text :x="sx(0) - 8" :y="sy(box[3]) + 12" text-anchor="end" :style="{ fill: inHidden ? C.amber : C.muted, fontSize: '14px' }">{{ inHidden ? 'h₂' : 'x₂' }}</text>
    <!-- hidden lines -->
    <g :style="{ opacity: lines }">
      <line :x1="h1[0][0]" :y1="h1[0][1]" :x2="h1[1][0]" :y2="h1[1][1]" :style="{ stroke: C.blue, strokeWidth: 2.5, strokeDasharray: '7 5' }" />
      <line :x1="h2[0][0]" :y1="h2[0][1]" :x2="h2[1][0]" :y2="h2[1][1]" :style="{ stroke: C.orange, strokeWidth: 2.5, strokeDasharray: '7 5' }" />
      <text :x="sx(-0.38)" :y="sy(0.95) - 6" :style="{ fill: C.blue, fontSize: '13px' }">h₁ (OR)</text>
      <text :x="sx(0.62)" :y="sy(1.32)" :style="{ fill: C.orange, fontSize: '13px' }">h₂ (AND)</text>
    </g>
    <!-- output line in hidden space -->
    <line :x1="out[0][0]" :y1="out[0][1]" :x2="out[1][0]" :y2="out[1][1]" :style="{ stroke: C.text, strokeWidth: 2.8, opacity: outLine }" />
    <!-- points -->
    <g v-for="(d, i) in XOR" :key="i">
      <circle v-if="d.y > 0" :cx="sx(pts[i][0])" :cy="sy(pts[i][1])" r="11" :style="{ fill: C.teal }" />
      <rect v-else :x="sx(pts[i][0]) - 10" :y="sy(pts[i][1]) - 10" width="20" height="20" :style="{ fill: C.violet }" />
    </g>
    <!-- right-hand readout -->
    <text :x="S + 14" y="30" :style="{ fill: C.text, fontSize: '15px', fontWeight: 700 }">{{ caption }}</text>
    <g :style="{ fontFamily: 'monospace', fontSize: '13px' }">
      <text :x="S + 14" y="70" :style="{ fill: C.muted }">x₁ x₂ → h₁ h₂ → ŷ</text>
      <text v-for="(d, i) in XOR" :key="`r${i}`" :x="S + 14" :y="96 + i * 24" :style="{ fill: d.y > 0 ? C.teal : C.violet }">
        {{ d.x[0] }}  {{ d.x[1] }}  →  {{ p > 0.5 ? H[i][0] : '·' }}  {{ p > 0.5 ? H[i][1] : '·' }}  →  {{ p > 2.5 ? (d.y > 0 ? 1 : 0) : '·' }}
      </text>
    </g>
    <text :x="S + 14" y="216" :style="{ fill: C.muted, fontSize: '12px', opacity: clamp(p - 1) }">(0,1) and (1,0) land on</text>
    <text :x="S + 14" y="232" :style="{ fill: C.muted, fontSize: '12px', opacity: clamp(p - 1) }">the same hidden point (1,0)</text>
  </svg>
</template>
