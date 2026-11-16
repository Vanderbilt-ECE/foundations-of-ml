<script setup lang="ts">
// Interactive: gradient descent on L = ½(w₁² + 4 w₂²) from a fixed start, 40 steps, with a learning-rate
// slider and three presets. Divergence threshold is η = 2/4 = 0.5 (the steep direction).
//   left: the path on the contours · right: loss per step (log scale)
import { computed, ref } from 'vue'
import { contours, loss, run } from '../utils/quad'
import { C, pathOf } from '../utils/plot'

const B = { a: 1, b: 4 }; const W0 = [-2.4, 1.2]; const STEPS = 40
const lr = ref(0.3)
const PRESETS = [
  { name: 'too small', v: 0.02, color: C.blue },
  { name: 'just right', v: 0.3, color: C.teal },
  { name: 'too big', v: 0.55, color: C.red },
]
const path = computed(() => run(B, 'sgd', W0, STEPS, lr.value))
const losses = computed(() => path.value.map(w => loss(B, w)))
const L0 = loss(B, W0)
const onePct = computed(() => losses.value.findIndex(v => v < 0.01 * L0))
const diverged = computed(() => losses.value.at(-1)! > L0)
const status = computed(() => diverged.value
  ? { text: 'diverging: every step overshoots', color: C.red }
  : onePct.value < 0
    ? { text: `still far from the bottom after ${STEPS} steps`, color: C.blue }
    : { text: `loss under 1% of its start after ${onePct.value} steps`, color: C.teal })

const PW = 460; const PH = 300; const U = 78
const map = (x: number, y: number) => [PW / 2 + 40 + x * U, PH / 2 - y * U]
const rings = contours(B, [0.05, 0.25, 0.6, 1.2, 2.2, 3.6, 5.5, 8], map)
const trail = computed(() => pathOf(path.value.map(w => map(Math.max(-9, Math.min(9, w[0])), Math.max(-9, Math.min(9, w[1]))))))
const lossSeries = computed(() => [{ x: losses.value.map((_, i) => i), y: losses.value.map(v => Math.max(v, 1e-9)), color: status.value.color, width: 3 }])
</script>

<template>
  <div class="mt-1">
    <div class="flex items-center gap-4 mb-2 text-sm">
      <span>learning rate η = <b class="font-mono text-amber-300 text-base">{{ lr.toFixed(2) }}</b></span>
      <input v-model.number="lr" type="range" min="0.01" max="0.6" step="0.01" class="w-64 accent-amber-400">
      <button
        v-for="p in PRESETS" :key="p.name" class="px-2 py-0.5 rounded border-2 text-xs font-bold"
        :style="{ borderColor: p.color, color: p.color, background: Math.abs(lr - p.v) < 1e-9 ? `${p.color}33` : 'transparent' }"
        @click="lr = p.v"
      >
        {{ p.name }} ({{ p.v }})
      </button>
    </div>
    <div class="grid grid-cols-[1.05fr_1fr] gap-4 items-center">
      <svg :viewBox="`0 0 ${PW + 40} ${PH}`" class="w-full" role="img" aria-label="Gradient descent path on a loss surface for the chosen learning rate">
        <defs><clipPath id="lrplay-clip"><rect x="0" y="0" :width="PW + 40" :height="PH" rx="10" /></clipPath></defs>
        <rect x="0" y="0" :width="PW + 40" :height="PH" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: C.grid }" />
        <g clip-path="url(#lrplay-clip)">
          <path v-for="(r, i) in rings" :key="i" :d="r" :style="{ fill: 'none', stroke: C.blue, strokeOpacity: 0.25 + 0.05 * i, strokeWidth: 1.3 }" />
          <path :d="trail" :style="{ fill: 'none', stroke: status.color, strokeWidth: 2.2, strokeLinejoin: 'round' }" />
          <circle v-for="(w, i) in path" :key="i" :cx="map(w[0], w[1])[0]" :cy="map(w[0], w[1])[1]" r="3" :style="{ fill: status.color }" />
        </g>
        <circle :cx="map(0, 0)[0]" :cy="map(0, 0)[1]" r="5" :style="{ fill: 'none', stroke: C.text, strokeWidth: 1.5 }" />
        <circle :cx="map(W0[0], W0[1])[0]" :cy="map(W0[0], W0[1])[1]" r="6" :style="{ fill: C.amber }" />
        <text x="12" y="22" style="font-size: 14px" :style="{ fill: C.muted }">loss contours, minimum at the ring</text>
      </svg>
      <div>
        <LineChart
          :series="lossSeries" :width="440" :height="270" :x-range="[0, STEPS]" :y-range="[1e-8, 1e6]" y-log
          :y-ticks="[{ v: 1e-8, t: '10⁻⁸' }, { v: 1e-4, t: '10⁻⁴' }, { v: 1, t: '1' }, { v: 1e4, t: '10⁴' }]"
          :x-ticks="[0, 10, 20, 30, 40]" x-label="step" y-label="loss (log)" :font="13"
          :hlines="[{ y: L0, color: C.muted, label: 'starting loss' }]"
        />
        <div class="text-center text-base font-bold" :style="{ color: status.color }">{{ status.text }}</div>
      </div>
    </div>
  </div>
</template>
