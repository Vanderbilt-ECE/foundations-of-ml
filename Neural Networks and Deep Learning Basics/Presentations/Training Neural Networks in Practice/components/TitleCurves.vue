<script setup lang="ts">
// Title figure: the demo's real early-stopping run (train and validation RMSE per epoch),
// shown as a static, finished picture.
import demo from '../data/demo.json'
import { C } from '../utils/plot'

const E = demo.early
const series = [
  { y: E.train, color: C.blue, label: 'training', width: 3 },
  { y: E.val, color: C.amber, label: 'validation', width: 3 },
]
const points = [{ x: E.best_epoch, y: E.best_val, color: C.teal, label: 'best', r: 5 }]
</script>

<template>
  <LineChart
    :series="series" :width="640" :height="210" :draw="1" :y-range="[0.45, 0.76]" :x-range="[1, 48]"
    :y-ticks="[0.5, 0.6, 0.7]" :x-ticks="[1, 10, 20, 30, 40]" x-label="epoch" y-label="error (RMSE)"
    :points="points"
  />
</template>
