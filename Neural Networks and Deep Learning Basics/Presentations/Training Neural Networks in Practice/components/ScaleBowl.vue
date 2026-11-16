<script setup lang="ts">
// Gradient descent, same start and same learning rate (η = 0.09), on two loss bowls:
//   left: a narrow valley L = ½(w₁² + 20 w₂²), what badly scaled inputs produce
//   right: a round bowl L = ½(5 w₁² + 5 w₂²), what standardized inputs produce
//   step 0: contours and the start; step 1: the paths animate (loop); step ≥ 2: the takeaway banner.
// The step counts shown are computed from the same paths.
import { computed, ref } from 'vue'
import { contours, loss, run } from '../utils/quad'
import { C, pathOf, useActive, useLoop } from '../utils/plot'

const props = defineProps<{ step: number }>()
const { isPrintMode } = useActive()
const LR = 0.09; const STEPS = 30; const W0 = [-2.6, 1.0]
const PANELS = [
  { B: { a: 1, b: 20 }, title: 'Raw inputs: a narrow valley', color: C.red, x0: 0 },
  { B: { a: 5, b: 5 }, title: 'Standardized: a round bowl', color: C.teal, x0: 450 },
]
const PW = 430; const PH = 250; const U = 68 // pixels per unit
const map = (x0: number) => (x: number, y: number) => [x0 + PW / 2 + x * U, 30 + PH / 2 - y * U]
const LEVELS = [0.05, 0.2, 0.5, 1, 2, 4, 7, 11]

const data = PANELS.map((p) => {
  const path = run(p.B, 'sgd', W0, STEPS, LR)
  const L = path.map(w => loss(p.B, w))
  const k = L.findIndex(v => v < 0.01 * L[0])
  return { ...p, rings: contours(p.B, LEVELS, map(p.x0)), path, toOnePct: k, m: map(p.x0) }
})

const t = ref(0)
useLoop((dt) => { if (props.step >= 1) t.value = (t.value + dt * 6) % (STEPS + 8) }, () => { t.value = 0 })
const shown = computed(() => (isPrintMode.value || props.step >= 2 ? STEPS : props.step >= 1 ? Math.min(STEPS, Math.floor(t.value)) : 0))
const trail = (d: typeof data[number]) => pathOf(d.path.slice(0, shown.value + 1).map(w => d.m(w[0], w[1])))
const head = (d: typeof data[number]) => d.m(d.path[shown.value][0], d.path[shown.value][1])
</script>

<template>
  <div>
    <svg viewBox="0 0 880 300" class="w-full" role="img" aria-label="Gradient descent zigzags slowly down a narrow valley but goes almost straight to the minimum of a round bowl, with the same learning rate">
      <defs>
        <clipPath v-for="d in data" :id="`bowl${d.x0}`" :key="d.x0"><rect :x="d.x0" y="30" :width="PW" :height="PH" rx="10" /></clipPath>
      </defs>
      <g v-for="d in data" :key="d.title">
        <rect :x="d.x0" y="30" :width="PW" :height="PH" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: C.grid }" />
        <text :x="d.x0 + 8" y="20" style="font-size: 15px; font-weight: 700" :style="{ fill: d.color }">{{ d.title }}</text>
        <g :clip-path="`url(#bowl${d.x0})`">
          <path v-for="(r, i) in d.rings" :key="i" :d="r" :style="{ fill: 'none', stroke: C.blue, strokeOpacity: 0.25 + 0.05 * i, strokeWidth: 1.3 }" />
          <path :d="trail(d)" :style="{ fill: 'none', stroke: d.color, strokeWidth: 2.4, strokeLinejoin: 'round' }" />
          <circle v-for="(w, i) in d.path.slice(0, shown + 1)" :key="i" :cx="d.m(w[0], w[1])[0]" :cy="d.m(w[0], w[1])[1]" r="2.6" :style="{ fill: d.color }" />
        </g>
        <circle :cx="d.m(0, 0)[0]" :cy="d.m(0, 0)[1]" r="5" :style="{ fill: 'none', stroke: C.text, strokeWidth: 1.5 }" />
        <circle :cx="head(d)[0]" :cy="head(d)[1]" r="6.5" :style="{ fill: C.amber }" />
        <text :x="d.x0 + PW - 10" y="270" text-anchor="end" style="font-size: 13px" :style="{ fill: C.text, opacity: step >= 1 ? 1 : 0, transition: 'opacity .4s' }">
          step {{ shown }}{{ shown >= d.toOnePct ? ` · loss under 1% after ${d.toOnePct} steps` : '' }}
        </text>
      </g>
      <text x="880" y="20" text-anchor="end" style="font-size: 13px" :style="{ fill: C.muted }">same start, same η = {{ LR }}</text>
    </svg>
    <div class="reveal mt-2 text-base text-center" :class="{ shown: step >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-1.5>
      One learning rate has to suit every direction. <b class="text-amber-300">Scaling makes the directions comparable, so one learning rate can.</b>
    </div>
  </div>
</template>
