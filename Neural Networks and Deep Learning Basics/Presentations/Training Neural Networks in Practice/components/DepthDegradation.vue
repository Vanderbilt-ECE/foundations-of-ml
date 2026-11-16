<script setup lang="ts">
// Measured training error (RMSE on the training set, every epoch) on California Housing,
// SGD with momentum, lr 0.01 (scripts/make_data.py, section 5).
//   step 0: plain 4-layer · step 1: + plain 22-layer (stuck at the "predict the average" error)
//   step ≥ 2: + residual 22-layer
import { computed } from 'vue'
import D from '../data/depth.json'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const last = (a: number[]) => a.at(-1)!
const series = [
  { y: D.plain_2.train_rmse, color: C.blue, width: 3 },
  { y: D.plain_20.train_rmse, color: C.red, width: 3 },
  { y: D.res_20.train_rmse, color: C.teal, width: 3.5 },
]
const visible = computed(() => [true, props.step >= 1, props.step >= 2])
const legend = computed(() => [
  { color: C.blue, text: `plain, 4 layers → ${last(D.plain_2.train_rmse).toFixed(2)}` },
  { color: C.red, text: `plain, 22 layers → ${last(D.plain_20.train_rmse).toFixed(2)}`, show: props.step >= 1 },
  { color: C.teal, text: `residual, 22 layers → ${last(D.res_20.train_rmse).toFixed(2)}`, show: props.step >= 2 },
])
</script>

<template>
  <div class="grid grid-cols-[1.8fr_1fr] gap-5 items-center mt-2 text-left">
    <LineChart
      :series="series" :visible="visible" :width="620" :height="350" :x-range="[1, 40]" :y-range="[0.15, 1.3]"
      :x-ticks="[1, 10, 20, 30, 40]" :y-ticks="[0.5, 0.75, 1, 1.25]" x-label="epoch" y-label="training RMSE ($100k)" :font="13"
      :hlines="[{ y: D.mean_baseline_train, color: C.muted, label: 'always predict the average' }]"
      :legend="legend" legend-at="bl"
    />
    <div class="flex flex-col gap-3 text-sm">
      <div border="2 solid white/10" bg="white/5" rounded-lg px-3 py-2>
        <b>Training error</b>, not validation: this isn't overfitting.
      </div>
      <div class="reveal" :class="{ shown: step >= 1 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-2>
        <b class="text-red-300">22 plain layers learn nothing:</b> {{ last(D.plain_20.train_rmse).toFixed(4) }}, exactly the error of always predicting the average ({{ D.mean_baseline_train.toFixed(4) }}).
      </div>
      <div class="reveal" :class="{ shown: step >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
        <b class="text-teal-300">Same 22 layers, with residual connections:</b> the best of the three.
      </div>
    </div>
  </div>
</template>
