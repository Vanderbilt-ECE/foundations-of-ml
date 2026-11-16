<script setup lang="ts">
// Four illustrative learning-curve shapes (training vs. validation loss), each with its diagnosis and fix.
// The curves are visible (dimmed) from the start; click k (1–4) brightens panel k and reveals its diagnosis.
import { C, rng } from '../utils/plot'

defineProps<{ step: number }>()
const E = Array.from({ length: 50 }, (_, i) => i + 1)
const ex = (e: number, tau: number) => Math.exp(-e / tau)
const R = rng(7)
const jitter = E.map(() => R.n())
const spikes = E.map((e, i) => (i % 9 === 4 ? 0.35 : 0) + 0.08 * jitter[i])
const PANELS = [
  {
    name: 'Underfitting', color: C.blue, fix: 'bigger model, train longer, higher lr',
    sign: 'both high, close together',
    train: E.map(e => 0.82 + 0.3 * ex(e, 6)), val: E.map(e => 0.88 + 0.3 * ex(e, 6)),
  },
  {
    name: 'Overfitting', color: C.red, fix: 'early stopping, weight decay, dropout, more data',
    sign: 'train keeps falling, validation turns up',
    train: E.map(e => 0.12 + 0.85 * ex(e, 9)), val: E.map(e => 0.42 + 0.6 * ex(e, 7) + 0.009 * Math.max(0, e - 14)),
  },
  {
    name: 'LR too high', color: C.amber, fix: 'lower lr by 3–10×',
    sign: 'jagged, jumping, or shooting to NaN',
    train: E.map((e, i) => 0.55 + 0.35 * ex(e, 5) + spikes[i]), val: E.map((e, i) => 0.62 + 0.35 * ex(e, 5) + spikes[i] * 1.2 + 0.03),
  },
  {
    name: 'Good fit', color: C.teal, fix: 'stop where validation levels off',
    sign: 'both fall and level off, small gap',
    train: E.map(e => 0.26 + 0.75 * ex(e, 8)), val: E.map(e => 0.33 + 0.72 * ex(e, 8)),
  },
]
</script>

<template>
  <div class="mt-1">
    <div class="flex gap-6 justify-center text-sm mb-1">
      <span><span class="inline-block w-5 h-1 align-middle mr-1" :style="{ background: C.blue }" />training loss</span>
      <span><span class="inline-block w-5 h-1 align-middle mr-1" :style="{ background: C.amber }" />validation loss</span>
      <span class="opacity-60">(illustrative shapes)</span>
    </div>
    <div class="grid grid-cols-2 gap-x-5 gap-y-2">
      <div
        v-for="(p, k) in PANELS" :key="p.name" border="2 solid white/5" bg="white/5" rounded-lg px-2 pt-1
        :style="{ opacity: step >= k + 1 ? 1 : 0.35, transition: 'opacity .5s', borderColor: step >= k + 1 ? p.color : undefined }"
      >
        <div class="flex justify-between items-baseline px-1 text-left">
          <b :style="{ color: p.color }">{{ k + 1 }} · {{ p.name }}</b>
          <span class="text-xs opacity-75">{{ p.sign }}</span>
        </div>
        <LineChart
          :series="[{ x: E, y: p.train, color: C.blue, width: 2.5 }, { x: E, y: p.val, color: C.amber, width: 2.5 }]"
          :width="440" :height="118" :x-range="[1, 50]" :y-range="[0, 1.3]" :x-ticks="[]" :y-ticks="[]" :font="11"
        />
        <div class="text-xs text-left px-1 pb-1 reveal" :class="{ shown: step >= k + 1 }"><b>Fix:</b> {{ p.fix }}</div>
      </div>
    </div>
  </div>
</template>
