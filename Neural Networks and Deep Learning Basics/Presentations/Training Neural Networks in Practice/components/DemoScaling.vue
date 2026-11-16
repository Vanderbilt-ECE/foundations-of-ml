<script setup lang="ts">
// Real validation curves from the demo: 2 optimizers × raw/standardized inputs.
//   step 0: SGD (standardized trains; raw diverged to NaN in epoch 1, so there is nothing to draw)
//   step 1: Adam added
//   step ≥ 2: the takeaway card
import { computed } from 'vue'
import demo from '../data/demo.json'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const S = demo.scale
const last = (a: (number | null)[]) => a.filter((v): v is number => v != null).at(-1)!
const series = [
  { y: S.sgd_std, color: C.blue },
  { y: S.adam_raw, color: C.orange, dash: '6 4', width: 2 },
  { y: S.adam_std, color: C.teal },
]
const visible = computed(() => [true, props.step >= 1, props.step >= 1])
const legend = computed(() => [
  { color: C.red, text: 'SGD, raw inputs: NaN in epoch 1 (nothing to draw)', dash: '2 3' },
  { color: C.blue, text: `SGD, standardized → ${last(S.sgd_std).toFixed(2)}` },
  { color: C.orange, text: `Adam, raw inputs → ${last(S.adam_raw).toFixed(2)}`, dash: '6 4', show: props.step >= 1 },
  { color: C.teal, text: `Adam, standardized → ${last(S.adam_std).toFixed(2)}`, show: props.step >= 1 },
])
</script>

<template>
  <div class="grid grid-cols-[1.7fr_1fr] gap-5 items-center text-left mt-2">
    <LineChart
      :series="series" :visible="visible" :width="640" :height="380" :y-range="[0.45, 1.6]" :x-range="[1, 100]"
      :x-ticks="[1, 20, 40, 60, 80, 100]" :y-ticks="[0.5, 0.75, 1, 1.25, 1.5]" x-label="epoch" y-label="validation RMSE ($100k)"
      :legend="legend" legend-at="tr" :font="13"
    />
    <div class="flex flex-col gap-3 text-sm">
      <div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-2>
        <b class="text-blue-300">Plain SGD</b> (lr 0.01): trains on standardized inputs. On raw inputs the first steps are huge and every weight becomes <b class="text-red-300">NaN</b>.
      </div>
      <div class="reveal" :class="{ shown: step >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
        <b class="text-teal-300">Adam</b> (lr 0.001) rescales each weight's step, so raw inputs still train, but noisily and much worse.
      </div>
      <div class="reveal" :class="{ shown: step >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
        <b class="text-amber-300">A smarter optimizer survives bad scaling. It doesn't fix it.</b> Always standardize.
      </div>
    </div>
  </div>
</template>
