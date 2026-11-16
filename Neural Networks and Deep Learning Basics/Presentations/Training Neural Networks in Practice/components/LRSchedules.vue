<script setup lang="ts">
// Learning-rate schedules over 90 epochs, as a fraction of the starting learning rate η₀.
//   step 0: constant · 1: + step decay (×0.1 at 30 and 60) · 2: + cosine · ≥ 3: + warmup (5 epochs) then cosine
import { computed } from 'vue'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const E = 90; const WARM = 5
const X = Array.from({ length: 451 }, (_, i) => i * E / 450)
const cosine = (e: number, start = 0) => 0.5 * (1 + Math.cos(Math.PI * (e - start) / (E - start)))
const series = [
  { x: X, y: X.map(() => 1), color: C.muted, width: 3 },
  { x: X, y: X.map(e => (e < 30 ? 1 : e < 60 ? 0.1 : 0.01)), color: C.amber, width: 3 },
  { x: X, y: X.map(e => cosine(e)), color: C.teal, width: 3 },
  { x: X, y: X.map(e => (e < WARM ? e / WARM : cosine(e, WARM))), color: C.violet, width: 3, dash: '7 4' },
]
const visible = computed(() => [true, props.step >= 1, props.step >= 2, props.step >= 3])
const legend = computed(() => [
  { color: C.muted, text: 'constant' },
  { color: C.amber, text: 'step decay: ×0.1 at epochs 30, 60 (StepLR)', show: props.step >= 1 },
  { color: C.teal, text: 'cosine annealing (CosineAnnealingLR)', show: props.step >= 2 },
  { color: C.violet, text: 'warmup, then cosine', dash: '7 4', show: props.step >= 3 },
])
</script>

<template>
  <LineChart
    :series="series" :visible="visible" :width="860" :height="300" :x-range="[0, E]" :y-range="[0, 1.08]"
    :x-ticks="[0, 15, 30, 45, 60, 75, 90]" :y-ticks="[0, 0.25, 0.5, 0.75, 1]" x-label="epoch" y-label="η / η₀"
    :legend="legend" legend-at="tr" :font="13"
  />
</template>
