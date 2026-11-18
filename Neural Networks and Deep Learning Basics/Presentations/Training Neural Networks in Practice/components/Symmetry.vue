<script setup lang="ts">
// The symmetry problem. Two inputs → two hidden units → one output.
//   step 0: both hidden units start with identical weights, so they compute identical outputs
//   step 1: backward pulses: identical gradients, identical updates, still twins ("forever")
//   step ≥ 2: random initialization (input AND output weights): different outputs, different gradients
// Pulse sizes and the ∂L/∂w labels are the real backprop values for ∂L/∂ŷ = 1.
// Pulses travel forward then backward along the edges on a loop; print shows a still frame.
import { computed, ref } from 'vue'
import { C, useActive, useLoop } from '../utils/plot'

const props = defineProps<{ step: number }>()
const { isPrintMode } = useActive()
const W = 640; const H = 300
const IN = [[90, 80], [90, 220]]; const HID = [[330, 80], [330, 220]]; const OUT = [540, 150]
const random = computed(() => props.step >= 2)
// weights into hidden unit k from input j
const Wt = computed(() => (random.value ? [[0.8, -0.3], [-0.4, 0.6]] : [[0.5, 0.5], [0.5, 0.5]]))
// weights from hidden unit k to the output (randomized too in step ≥ 2)
const V = computed(() => (random.value ? [0.9, -0.4] : [0.5, 0.5]))
const x = [1.0, 2.0]
// Backprop with ∂L/∂ŷ = 1 (both hidden units are active, so ReLU' = 1):
//   ∂L/∂h_k = v_k,   ∂L/∂W_kj = v_k · x_j
const gH = computed(() => V.value)
const gW = computed(() => V.value.map(v => x.map(xj => v * xj)))
const gR = (g: number) => 1.5 + 7 * Math.abs(g)
const fmt = (g: number) => (Number.isInteger(g) ? g.toFixed(1) : String(+g.toFixed(2)))
const h = computed(() => Wt.value.map(w => Math.max(0, w[0] * x[0] + w[1] * x[1])))
const HC = computed(() => (random.value ? [C.teal, C.violet] : [C.amber, C.amber]))

const t = ref(0)
useLoop((dt) => { t.value = (t.value + dt / 4.5) % 1 })
const phase = computed(() => (isPrintMode.value ? -1 : t.value))
// forward pulses during the first half, backward (gradient) pulses during the second half once step ≥ 1
const pulse = (a: number[], b: number[], from: number, to: number) => {
  const p = phase.value
  if (p < from || p > to) return null
  const u = (p - from) / (to - from)
  return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]
}
const edgeW = (w: number) => 1.5 + Math.abs(w) * 4
</script>

<template>
  <div class="grid grid-cols-[1.5fr_1fr] gap-6 items-center mt-4">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Two hidden units with identical weights compute the same thing and get the same gradient forever; random weights make them different">
      <!-- input → hidden edges -->
      <g v-for="(hp, k) in HID" :key="`hk${k}`">
        <g v-for="(ip, j) in IN" :key="`e${k}${j}`">
          <line :x1="ip[0] + 26" :y1="ip[1]" :x2="hp[0] - 30" :y2="hp[1]" :style="{ stroke: Wt[k][j] >= 0 ? C.blue : C.violet, strokeWidth: edgeW(Wt[k][j]), strokeOpacity: 0.7, transition: 'all .6s' }" />
          <text :x="ip[0] + 50 + (hp[0] - ip[0]) * 0.12" :y="ip[1] + (hp[1] - ip[1]) * 0.22 - 9" text-anchor="middle" style="font-size: 16px; font-weight: 700" :style="{ fill: C.text }">{{ Wt[k][j] }}</text>
        </g>
      </g>
      <!-- hidden → output -->
      <g v-for="(hp, k) in HID" :key="`ho${k}`">
        <line :x1="hp[0] + 30" :y1="hp[1]" :x2="OUT[0] - 28" :y2="OUT[1]" :style="{ stroke: V[k] >= 0 ? C.blue : C.violet, strokeWidth: edgeW(V[k]), strokeOpacity: 0.7, transition: 'all .6s' }" />
        <text :x="hp[0] + 100" :y="hp[1] + (OUT[1] - hp[1]) * 0.45 + (k ? 22 : -10)" text-anchor="middle" style="font-size: 16px; font-weight: 700" :style="{ fill: C.text }">{{ V[k] }}</text>
      </g>

      <!-- forward pulses -->
      <template v-for="(hp, k) in HID" :key="`fp${k}`">
        <template v-for="(ip, j) in IN" :key="`fpp${k}${j}`">
          <circle v-if="pulse(ip, hp, 0, 0.35)" :cx="pulse(ip, hp, 0, 0.35)![0]" :cy="pulse(ip, hp, 0, 0.35)![1]" r="6" :style="{ fill: C.amber }" />
        </template>
        <circle v-if="pulse(hp, OUT, 0.35, 0.5)" :cx="pulse(hp, OUT, 0.35, 0.5)![0]" :cy="pulse(hp, OUT, 0.35, 0.5)![1]" r="6" :style="{ fill: C.amber }" />
      </template>
      <!-- backward (gradient) pulses -->
      <template v-if="step >= 1">
        <template v-for="(hp, k) in HID" :key="`bp${k}`">
          <circle v-if="pulse(OUT, hp, 0.55, 0.72)" :cx="pulse(OUT, hp, 0.55, 0.72)![0]" :cy="pulse(OUT, hp, 0.55, 0.72)![1]" :r="gR(gH[k])" :style="{ fill: C.red }" />
          <template v-for="(ip, j) in IN" :key="`bpp${k}${j}`">
            <circle v-if="pulse(hp, ip, 0.72, 0.95)" :cx="pulse(hp, ip, 0.72, 0.95)![0]" :cy="pulse(hp, ip, 0.72, 0.95)![1]" :r="gR(gW[k][j])" :style="{ fill: C.red }" />
          </template>
        </template>
      </template>

      <!-- nodes -->
      <g v-for="(ip, j) in IN" :key="`in${j}`">
        <circle :cx="ip[0]" :cy="ip[1]" r="26" :style="{ fill: C.bg, stroke: C.blue, strokeWidth: 2.5 }" />
        <text :x="ip[0]" :y="ip[1] + 6" text-anchor="middle" style="font-size: 17px" :style="{ fill: C.blue }">x{{ j ? '₂' : '₁' }}</text>
        <text :x="ip[0] - 34" :y="ip[1] + 6" text-anchor="end" style="font-size: 16px" :style="{ fill: C.muted }">{{ x[j] }}</text>
      </g>
      <g v-for="(hp, k) in HID" :key="`h${k}`">
        <circle :cx="hp[0]" :cy="hp[1]" r="30" :style="{ fill: C.bg, stroke: HC[k], strokeWidth: 3, transition: 'stroke .6s' }" />
        <text :x="hp[0]" :y="hp[1] + 6" text-anchor="middle" style="font-size: 17px" :style="{ fill: HC[k], transition: 'fill .6s' }">h{{ k ? '₂' : '₁' }}</text>
        <text :x="hp[0] + 36" :y="hp[1] + (k ? 40 : -28)" style="font-size: 17px; font-weight: 700" :style="{ fill: HC[k] }">= {{ h[k].toFixed(1) }}</text>
        <text v-if="step >= 1" :x="hp[0] - 40" :y="hp[1] + (k ? 62 : -48)" text-anchor="middle" style="font-size: 15px" :style="{ fill: C.red }">∂L/∂w = ({{ fmt(gW[k][0]) }}, {{ fmt(gW[k][1]) }})</text>
      </g>
      <circle :cx="OUT[0]" :cy="OUT[1]" r="28" :style="{ fill: C.bg, stroke: C.violet, strokeWidth: 2.5 }" />
      <text :x="OUT[0]" :y="OUT[1] + 6" text-anchor="middle" style="font-size: 17px; font-style: italic" :style="{ fill: C.violet }">ŷ</text>
      <text v-if="step >= 1" :x="OUT[0]" :y="OUT[1] + 52" text-anchor="middle" style="font-size: 15px" :style="{ fill: C.red }">gradients flow back</text>
    </svg>

    <div class="flex flex-col gap-3 text-sm text-left">
      <div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
        <b class="text-amber-300">Same weights:</b> h₁ and h₂ compute the same number for every input.
      </div>
      <div class="reveal" :class="{ shown: step >= 1 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-2>
        <b class="text-red-300">Same gradients, same updates:</b> they stay twins forever. 100 hidden units act like 1.
      </div>
      <div class="reveal" :class="{ shown: step >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
        <b class="text-teal-300">Random weights</b> break the tie: different outputs, different gradients, different features. Biases can start at 0.
      </div>
    </div>
  </div>
</template>
