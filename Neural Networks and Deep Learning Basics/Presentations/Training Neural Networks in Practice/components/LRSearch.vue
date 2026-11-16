<script setup lang="ts">
// Left: the measured learning-rate range test (Adam, lr raised exponentially every mini-batch).
//   step 1: mark the minimum and the suggested lr (≈ minimum / 10) and shade the blow-up region
// Right (step ≥ 2): the measured 100-epoch sweep at four learning rates.
import { computed } from 'vue'
import demo from '../data/demo.json'
import R from '../data/lr_range.json'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const iMin = R.loss.indexOf(Math.min(...R.loss))
const lrMin = R.lr[iMin]
const suggested = 10 ** Math.round(Math.log10(lrMin / 10))
const fmt = (v: number) => (v >= 0.001 ? String(Number(v.toPrecision(2))) : v.toExponential(0))
const marks = computed(() => (props.step >= 1
  ? { points: [{ x: lrMin, y: R.loss[iMin], color: C.amber, label: `lowest: lr ≈ ${fmt(lrMin)}`, dy: -14, anchor: 'end' as const }],
      vlines: [{ x: suggested, color: C.teal, label: `pick ≈ ${fmt(suggested)}`, anchor: 'end' as const, dy: -6 }],
      bands: [{ x0: lrMin * 1.5, x1: 1, color: C.red, opacity: 0.14, label: 'blows up' }] }
  : { points: [], vlines: [], bands: [] }))

const SW = demo.lr
const sweep = [
  { y: SW['0.0001'], color: C.blue },
  { y: SW['0.001'], color: C.teal },
  { y: SW['0.01'], color: C.amber },
  { y: SW['0.1'], color: C.red },
]
const last = (a: number[]) => a.at(-1)!
const legend = [
  { color: C.blue, text: `10⁻⁴: still creeping → ${last(SW['0.0001']).toFixed(2)}` },
  { color: C.teal, text: `10⁻³ → ${last(SW['0.001']).toFixed(2)}` },
  { color: C.amber, text: `10⁻² → ${last(SW['0.01']).toFixed(2)}, fastest` },
  { color: C.red, text: `10⁻¹: dead ReLUs → ${last(SW['0.1']).toFixed(2)}` },
]
</script>

<template>
  <div class="grid grid-cols-2 gap-5 mt-2">
    <div>
      <div class="text-sm font-bold mb-1">Range test: raise lr every mini-batch</div>
      <LineChart
        :series="[{ x: R.lr, y: R.loss, color: C.violet, width: 3 }]" :width="440" :height="300" x-log
        :x-range="[1e-6, 1]" :y-range="[0, 6]" :y-ticks="[0, 2, 4, 6]" x-label="learning rate (log)" y-label="training loss (smoothed)"
        :x-ticks="[{ v: 1e-6, t: '10⁻⁶' }, { v: 1e-4, t: '10⁻⁴' }, { v: 1e-2, t: '10⁻²' }, { v: 1, t: '1' }]" :font="13"
        :points="marks.points" :vlines="marks.vlines" :bands="marks.bands"
      />
      <div class="text-xs opacity-70 text-center">{{ R.lr.length }} mini-batches (under one epoch), stopped once the loss blew up</div>
    </div>
    <div class="reveal" :class="{ shown: step >= 2 }">
      <div class="text-sm font-bold mb-1">Sweep: train fully at each lr (Adam, 100 epochs)</div>
      <LineChart
        :series="sweep" :width="440" :height="300" :x-range="[1, 100]" :y-range="[0.45, 1.25]" :y-ticks="[0.5, 0.75, 1, 1.25]"
        :x-ticks="[1, 25, 50, 75, 100]" x-label="epoch" y-label="validation RMSE" :font="13" :legend="legend" legend-at="tr"
      />
    </div>
  </div>
</template>
