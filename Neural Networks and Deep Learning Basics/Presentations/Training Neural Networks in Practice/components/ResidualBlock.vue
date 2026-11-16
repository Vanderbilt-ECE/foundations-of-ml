<script setup lang="ts">
// A plain block vs. a residual block.
//   step 0: plain: x → [Linear → ReLU → Linear] = F(x) → output. The layers must produce the whole output.
//   step 1: the skip connection draws in: y = ReLU(x + F(x)); signal pulses travel both paths.
//   step ≥ 2: F dims toward 0: the block passes x through almost unchanged ("doing nothing is easy").
import { computed, ref } from 'vue'
import { C, useActive, useLoop } from '../utils/plot'

const props = defineProps<{ step: number }>()
const { isPrintMode } = useActive()
const W = 900; const H = 300; const Y = 190
const BOXES = [
  { x: 210, label: 'Linear' }, { x: 340, label: 'ReLU' }, { x: 470, label: 'Linear' },
]
const BW = 96; const BH = 52
const PLUS = 640; const OUT = 830
const skip = computed(() => props.step >= 1)
const fZero = computed(() => props.step >= 2)
const skipPath = `M80,${Y} C80,60 ${PLUS},60 ${PLUS},${Y - 22}`
const SKIP_LEN = 760

const t = ref(0)
useLoop((dt) => { t.value = (t.value + dt / 2.2) % 1 })
const p = computed(() => (isPrintMode.value ? -1 : t.value))
const mainX = computed(() => 80 + (PLUS - 80) * p.value)
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="A residual block: the input skips around two layers and is added to their output">
      <!-- main path -->
      <line x1="60" :y1="Y" :x2="PLUS - 22" :y2="Y" :style="{ stroke: C.muted, strokeWidth: 3 }" />
      <line :x1="PLUS + 22" :y1="Y" :x2="OUT - 24" :y2="Y" :style="{ stroke: C.muted, strokeWidth: 3 }" />
      <g v-for="b in BOXES" :key="b.x" :style="{ opacity: fZero ? 0.35 : 1, transition: 'opacity .6s' }">
        <rect :x="b.x - BW / 2" :y="Y - BH / 2" :width="BW" :height="BH" rx="8" :style="{ fill: C.bg, stroke: C.blue, strokeWidth: 2.5 }" />
        <text :x="b.x" :y="Y + 6" text-anchor="middle" style="font-size: 17px" :style="{ fill: C.text }">{{ b.label }}</text>
      </g>
      <rect :x="BOXES[0].x - BW / 2 - 14" :y="Y - BH / 2 - 16" :width="BOXES[2].x - BOXES[0].x + BW + 28" :height="BH + 48" rx="12"
            :style="{ fill: 'none', stroke: C.blue, strokeDasharray: '6 5', strokeOpacity: fZero ? 0.3 : 0.8, transition: 'stroke-opacity .6s' }" />
      <text :x="BOXES[1].x" :y="Y + BH / 2 + 22" text-anchor="middle" style="font-size: 16px; font-weight: 700" :style="{ fill: C.blue, opacity: fZero ? 0.5 : 1 }">{{ fZero ? 'F(x) ≈ 0' : 'F(x)' }}</text>

      <!-- skip connection -->
      <path :d="skipPath" :style="{ fill: 'none', stroke: C.teal, strokeWidth: 4, strokeDasharray: SKIP_LEN, strokeDashoffset: skip ? 0 : SKIP_LEN, transition: 'stroke-dashoffset 1s ease' }" />
      <text x="360" y="58" text-anchor="middle" style="font-size: 17px; font-weight: 700" :style="{ fill: C.teal, opacity: skip ? 1 : 0, transition: 'opacity .5s .6s' }">skip connection: x</text>
      <g :style="{ opacity: skip ? 1 : 0, transition: 'opacity .5s .6s' }">
        <circle :cx="PLUS" :cy="Y" r="22" :style="{ fill: C.bg, stroke: C.teal, strokeWidth: 3 }" />
        <text :x="PLUS" :y="Y + 8" text-anchor="middle" style="font-size: 26px; font-weight: 700" :style="{ fill: C.teal }">+</text>
      </g>

      <!-- input / output -->
      <circle cx="60" :cy="Y" r="22" :style="{ fill: C.bg, stroke: C.violet, strokeWidth: 2.5 }" />
      <text x="60" :y="Y + 7" text-anchor="middle" style="font-size: 20px; font-style: italic" :style="{ fill: C.violet }">x</text>
      <circle :cx="OUT" :cy="Y" r="22" :style="{ fill: C.bg, stroke: C.violet, strokeWidth: 2.5 }" />
      <text :x="OUT" :y="Y + 7" text-anchor="middle" style="font-size: 20px; font-style: italic" :style="{ fill: C.violet }">y</text>
      <text :x="(PLUS + OUT) / 2" :y="Y - 16" text-anchor="middle" style="font-size: 14px" :style="{ fill: C.muted }">ReLU</text>

      <!-- pulses -->
      <circle v-if="p >= 0" :cx="mainX" :cy="Y" r="7" :style="{ fill: C.amber, opacity: fZero ? 0.35 : 1 }" />

      <!-- equation -->
      <text :x="W / 2" :y="H - 12" text-anchor="middle" style="font-size: 22px" :style="{ fill: C.text }">
        <tspan v-if="!skip">y = ReLU(F(x)): the layers must build the whole output</tspan>
        <tspan v-else-if="!fZero">y = ReLU(<tspan :style="{ fill: C.teal, fontWeight: 700 }">x</tspan> + F(x)): the layers learn only the change</tspan>
        <tspan v-else>F ≈ 0  ⟹  y ≈ x: <tspan :style="{ fill: C.teal, fontWeight: 700 }">doing nothing is easy</tspan></tspan>
      </text>
    </svg>
  </div>
</template>
