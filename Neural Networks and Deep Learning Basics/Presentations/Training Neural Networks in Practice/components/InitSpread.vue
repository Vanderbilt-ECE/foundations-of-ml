<script setup lang="ts">
// Measured in PyTorch (scripts/make_data.py): std of the activations after each of 10 ReLU layers
// of width 256, for four weight initializations. Log scale.
//   step 0: small (std 0.01) · step 1: + large (0.15) · step 2: + He · step ≥ 3: + PyTorch's default
import { computed } from 'vue'
import init from '../data/init.json'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const S = init.spread
const X = S.he.map((_, i) => i)
const floor = (a: (number | null)[]) => a.map(v => (v != null && v > 0 ? v : null))
const series = [
  { x: X, y: floor(S.small), color: C.blue, width: 3 },
  { x: X, y: floor(S.large), color: C.red, width: 3 },
  { x: X, y: floor(S.he), color: C.teal, width: 3.5 },
  { x: X, y: floor(S.default), color: C.violet, width: 3, dash: '7 5' },
]
const visible = computed(() => [true, props.step >= 1, props.step >= 2, props.step >= 3])
const end = (a: number[]) => a.at(-1)!
const legend = computed(() => [
  { color: C.blue, text: `too small, std 0.01 → ${end(S.small).toExponential(0).replace('e-', '×10⁻').replace(/\d+$/, d => [...d].map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹'[+c]).join(''))}` },
  { color: C.red, text: `too large, std 0.15 → ${end(S.large).toFixed(0)}`, show: props.step >= 1 },
  { color: C.teal, text: `He, std √(2/256) = ${init.he_std.toFixed(3)} → ${end(S.he).toFixed(2)}`, show: props.step >= 2 },
  { color: C.violet, text: `PyTorch default, std ${init.default_weight_std.toFixed(3)} → ${end(S.default).toFixed(3)}`, dash: '7 5', show: props.step >= 3 },
])
</script>

<template>
  <div class="mt-1">
    <LineChart
      :series="series" :visible="visible" :width="860" :height="350" :x-range="[0, 10]" :y-range="[1e-11, 1e5]" y-log
      :y-ticks="[{ v: 1e-10, t: '10⁻¹⁰' }, { v: 1e-7, t: '10⁻⁷' }, { v: 1e-4, t: '10⁻⁴' }, { v: 0.1, t: '0.1' }, { v: 100, t: '100' }]"
      :x-ticks="[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]" x-label="layer (0 = input)" y-label="std of activations (log)"
      :legend="legend" legend-at="bl" :font="13"
    />
  </div>
</template>
