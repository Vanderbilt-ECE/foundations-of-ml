<script setup lang="ts">
// Regression, trained live: daily electricity use vs. outdoor temperature (synthetic, U-shaped: heating + cooling).
// Two models train side by side on the same data with the same loss (mean squared error):
//   a network with no hidden layer (= linear regression)  — dashed violet
//   a network with two hidden layers of 16 tanh units      — amber
// Training restarts a few seconds after it finishes; click the plot to restart sooner.
// Print mode shows both models fully trained.
import { reactive, ref } from 'vue'
import { MLP } from '../utils/mlp'
import { C, pathOf, useActive, useLoop } from '../utils/plot'
import { energy } from '../utils/rng'

const D = energy()
const nx = (t: number) => (t - 15) / 12
const X = D.map(d => [nx(d.t)]); const Y = D.map(d => [(d.kwh - 25) / 8])
const STEPS = 1200; const PER_FRAME = 3

let net: MLP; let lin: MLP
const st = reactive({ step: 0, rmse: 0, rmseLin: 0, curve: [] as number[][], line: [] as number[][], pause: 0 })
const TS = Array.from({ length: 81 }, (_, i) => -6 + 42 * i / 80)
function snapshot() {
  st.curve = TS.map(t => [t, 25 + 8 * net.predict([nx(t)])[0]])
  st.line = TS.map(t => [t, 25 + 8 * lin.predict([nx(t)])[0]])
  st.rmse = 8 * Math.sqrt(2 * net.meanLoss(X, Y)); st.rmseLin = 8 * Math.sqrt(2 * lin.meanLoss(X, Y))
}
function reset() {
  net = new MLP([1, 16, 16, 1], 'tanh', 'linear', 4)
  lin = new MLP([1, 1], 'tanh', 'linear', 4)
  st.step = 0; st.pause = 0.6
  snapshot()
}
const train = (k: number) => { for (let i = 0; i < k; i++) { net.step(X, Y, 0.004); lin.step(X, Y, 0.01) } st.step += k }
reset()

const { isPrintMode } = useActive()
if (isPrintMode.value) { train(STEPS); snapshot() }
useLoop((dt) => {
  if (st.pause > 0) { st.pause -= dt; if (st.pause <= 0 && st.step >= STEPS) reset(); return }
  train(PER_FRAME); snapshot()
  if (st.step >= STEPS) st.pause = 4
}, reset)
const hovering = ref(false)

const W = 620; const H = 330; const L = 52; const B = 40
const sx = (t: number) => L + (t + 6) / 42 * (W - L - 12)
const sy = (k: number) => H - B - (k - 10) / 45 * (H - B - 12)
const clipY = (P: number[][]) => P.map(p => [sx(p[0]), sy(Math.max(6, Math.min(57, p[1])))])
</script>

<template>
  <div class="grid grid-cols-[1.5fr_1fr] gap-6 items-center text-left">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full cursor-pointer" style="max-height: 340px" role="img" aria-label="Electricity use against temperature, with a straight line and a neural network curve being fit" @click="reset" @mouseenter="hovering = true" @mouseleave="hovering = false">
      <line v-for="k in [20, 30, 40, 50]" :key="k" :x1="L" :x2="W - 12" :y1="sy(k)" :y2="sy(k)" :style="{ stroke: C.grid, strokeDasharray: '3 5' }" />
      <text v-for="k in [20, 30, 40, 50]" :key="`t${k}`" :x="L - 8" :y="sy(k) + 4" text-anchor="end" :style="{ fill: C.muted, fontSize: '12px' }">{{ k }}</text>
      <text v-for="t in [0, 10, 20, 30]" :key="`x${t}`" :x="sx(t)" :y="H - B + 18" text-anchor="middle" :style="{ fill: C.muted, fontSize: '12px' }">{{ t }}°C</text>
      <text :x="(L + W) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: C.muted, fontSize: '13px' }">outdoor temperature</text>
      <text :x="14" :y="H / 2 - 10" text-anchor="middle" :transform="`rotate(-90 14 ${H / 2 - 10})`" :style="{ fill: C.muted, fontSize: '13px' }">electricity (kWh/day)</text>
      <circle v-for="(d, i) in D" :key="i" :cx="sx(d.t)" :cy="sy(d.kwh)" r="4" :style="{ fill: C.blue, fillOpacity: 0.75 }" />
      <path :d="pathOf(clipY(st.line))" :style="{ fill: 'none', stroke: C.violet, strokeWidth: 2.5, strokeDasharray: '8 6' }" />
      <path :d="pathOf(clipY(st.curve))" :style="{ fill: 'none', stroke: C.amber, strokeWidth: 3.2 }" />
      <text v-if="hovering" :x="W - 14" y="22" text-anchor="end" :style="{ fill: C.muted, fontSize: '11px' }">click to restart</text>
    </svg>
    <div>
      <div class="font-mono text-sm opacity-70 mb-3">training step {{ st.step }}</div>
      <div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2 mb-3>
        <div class="text-violet-300 font-bold">No hidden layer</div>
        <div class="text-xs opacity-75">1 → 1 (linear regression)</div>
        <div class="font-mono mt-1">typical error <span class="text-lg">{{ st.rmseLin.toFixed(1) }}</span> kWh</div>
      </div>
      <div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
        <div class="text-amber-300 font-bold">Two hidden layers</div>
        <div class="text-xs opacity-75">1 → 16 → 16 → 1, tanh</div>
        <div class="font-mono mt-1">typical error <span class="text-lg">{{ st.rmse.toFixed(1) }}</span> kWh</div>
      </div>
    </div>
  </div>
</template>
