<script setup lang="ts">
// Two linear neurons in a chain, x → [w₁ = 2, b₁ = 1] → h → [w₂ = 3, b₂ = −4] → y, with no activation.
// Each bias is its own orange node feeding into the top of its neuron, and bias terms are orange
// everywhere (here and in the slide's equations), so students can follow +1 and −4 into the final −1.
//   step 1: neuron 1 and its bias light up; its output h = 2x + 1 appears
//   step 2: neuron 2 and its bias light up; its output y = 3h − 4 appears
//   step ≥ 3: the chain dims and a single equivalent neuron appears below it: w = 6, b = −1
// Static, so it prints as-is.
import { computed } from 'vue'
import { C } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const W = 860; const H = 236
const R = 28; const Y1 = 84; const Y2 = 206; const BIAS_GAP = 40
const X = { in: 60, n1: 300, n2: 560, out: 800, one: 430 }
const collapsed = computed(() => props.step >= 3)
const top = computed(() => (collapsed.value ? 0.4 : 1))

const right = (x: number, y: number) => `M${x - 11},${y - 6} L${x},${y} L${x - 11},${y + 6} Z`
const down = (x: number, y: number) => `M${x - 6},${y - 11} L${x},${y} L${x + 6},${y - 11} Z`
const NEURONS = [
  { x: X.n1, b: 'b₁ = 1', s: 1 },
  { x: X.n2, b: 'b₂ = −4', s: 2 },
]
const lit = (s: number) => props.step === s
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Two neurons without activation, each with its own bias feeding in from above, collapsing into one neuron with weight 6 and bias minus 1">
    <!-- the chain -->
    <g :style="{ opacity: top, transition: 'opacity .6s' }">
      <!-- weight edges -->
      <line :x1="X.in + 22" :y1="Y1" :x2="X.n1 - R - 2" :y2="Y1" :style="{ stroke: C.muted, strokeWidth: 2.5 }" />
      <path :d="right(X.n1 - R - 2, Y1)" :style="{ fill: C.muted }" />
      <line :x1="X.n1 + R" :y1="Y1" :x2="X.n2 - R - 2" :y2="Y1" :style="{ stroke: C.muted, strokeWidth: 2.5 }" />
      <path :d="right(X.n2 - R - 2, Y1)" :style="{ fill: C.muted }" />
      <line :x1="X.n2 + R" :y1="Y1" :x2="X.out - 24" :y2="Y1" :style="{ stroke: C.muted, strokeWidth: 2.5 }" />
      <path :d="right(X.out - 24, Y1)" :style="{ fill: C.muted }" />
      <text :x="(X.in + X.n1) / 2" :y="Y1 - 10" text-anchor="middle" style="font-size: 16px" :style="{ fill: C.text }">w₁ = 2</text>
      <text :x="(X.n1 + X.n2) / 2" :y="Y1 - 10" text-anchor="middle" style="font-size: 16px" :style="{ fill: C.text }">w₂ = 3</text>

      <!-- input and output -->
      <circle :cx="X.in" :cy="Y1" r="20" :style="{ fill: C.bg, stroke: C.blue, strokeWidth: 2.5 }" />
      <text :x="X.in" :y="Y1 + 6" text-anchor="middle" style="font-size: 18px; font-style: italic" :style="{ fill: C.blue }">x</text>
      <circle :cx="X.out" :cy="Y1" r="20" :style="{ fill: C.bg, stroke: C.violet, strokeWidth: 2.5 }" />
      <text :x="X.out" :y="Y1 + 6" text-anchor="middle" style="font-size: 18px; font-style: italic" :style="{ fill: C.violet }">y</text>

      <!-- neurons (Σ only, no activation), each with its bias feeding in from above -->
      <g v-for="n in NEURONS" :key="n.s">
        <rect :x="n.x - 40" :y="Y1 - BIAS_GAP - R - 14" width="80" height="26" rx="13" :style="{ fill: lit(n.s) ? 'rgba(251,146,60,0.25)' : C.bg, stroke: C.orange, strokeWidth: lit(n.s) ? 2.5 : 1.5, transition: 'all .4s' }" />
        <text :x="n.x" :y="Y1 - BIAS_GAP - R + 4" text-anchor="middle" style="font-size: 14px" :style="{ fill: C.orange }">{{ n.b }}</text>
        <line :x1="n.x" :y1="Y1 - BIAS_GAP - R + 12" :x2="n.x" :y2="Y1 - R - 2" :style="{ stroke: C.orange, strokeWidth: lit(n.s) ? 2.5 : 1.8, transition: 'all .4s' }" />
        <path :d="down(n.x, Y1 - R - 2)" :style="{ fill: C.orange }" />
        <circle :cx="n.x" :cy="Y1" :r="R" :style="{ fill: lit(n.s) ? 'rgba(226,232,240,0.12)' : C.bg, stroke: lit(n.s) ? C.text : C.muted, strokeWidth: lit(n.s) ? 3 : 2.5, transition: 'all .4s' }" />
        <text :x="n.x" :y="Y1 + 8" text-anchor="middle" style="font-size: 24px" :style="{ fill: C.text }">Σ</text>
      </g>

      <!-- each neuron's output: weight part in white, bias part in orange -->
      <text :x="(X.n1 + X.n2) / 2" :y="Y1 + 26" text-anchor="middle" style="font-size: 16px" :style="{ fill: C.text, opacity: step >= 1 ? 1 : 0, transition: 'opacity .5s' }">h = 2x <tspan :style="{ fill: C.orange }">+ 1</tspan></text>
      <text :x="(X.n2 + X.out) / 2" :y="Y1 + 26" text-anchor="middle" style="font-size: 16px" :style="{ fill: C.text, opacity: step >= 2 ? 1 : 0, transition: 'opacity .5s' }">y = 3h <tspan :style="{ fill: C.orange }">− 4</tspan></text>
    </g>

    <!-- the single equivalent neuron -->
    <g :style="{ opacity: collapsed ? 1 : 0, transition: 'opacity .6s .2s' }">
      <text :x="X.in - 40" :y="Y2 + 7" text-anchor="middle" style="font-size: 24px" :style="{ fill: C.teal }">=</text>
      <line :x1="X.in + 22" :y1="Y2" :x2="X.one - R - 2" :y2="Y2" :style="{ stroke: C.teal, strokeWidth: 2.5 }" />
      <path :d="right(X.one - R - 2, Y2)" :style="{ fill: C.teal }" />
      <line :x1="X.one + R" :y1="Y2" :x2="X.out - 24" :y2="Y2" :style="{ stroke: C.teal, strokeWidth: 2.5 }" />
      <path :d="right(X.out - 24, Y2)" :style="{ fill: C.teal }" />
      <text :x="(X.in + X.one) / 2" :y="Y2 - 10" text-anchor="middle" style="font-size: 16px" :style="{ fill: C.teal }">w = 3·2 = 6</text>

      <rect :x="X.one - 82" :y="Y2 - BIAS_GAP - R - 14" width="164" height="26" rx="13" :style="{ fill: 'rgba(251,146,60,0.2)', stroke: C.orange, strokeWidth: 2 }" />
      <text :x="X.one" :y="Y2 - BIAS_GAP - R + 4" text-anchor="middle" style="font-size: 14px" :style="{ fill: C.orange }">b = 3·1 − 4 = −1</text>
      <line :x1="X.one" :y1="Y2 - BIAS_GAP - R + 12" :x2="X.one" :y2="Y2 - R - 2" :style="{ stroke: C.orange, strokeWidth: 2.2 }" />
      <path :d="down(X.one, Y2 - R - 2)" :style="{ fill: C.orange }" />

      <circle :cx="X.in" :cy="Y2" r="20" :style="{ fill: C.bg, stroke: C.blue, strokeWidth: 2.5 }" />
      <text :x="X.in" :y="Y2 + 6" text-anchor="middle" style="font-size: 18px; font-style: italic" :style="{ fill: C.blue }">x</text>
      <circle :cx="X.one" :cy="Y2" :r="R" :style="{ fill: 'rgba(45,212,191,0.15)', stroke: C.teal, strokeWidth: 2.5 }" />
      <text :x="X.one" :y="Y2 + 8" text-anchor="middle" style="font-size: 24px" :style="{ fill: C.teal }">Σ</text>
      <circle :cx="X.out" :cy="Y2" r="20" :style="{ fill: C.bg, stroke: C.violet, strokeWidth: 2.5 }" />
      <text :x="X.out" :y="Y2 + 6" text-anchor="middle" style="font-size: 18px; font-style: italic" :style="{ fill: C.violet }">y</text>
    </g>
  </svg>
</template>
