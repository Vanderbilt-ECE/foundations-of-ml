<script setup lang="ts">
// Three activations side by side (ReLU, Leaky ReLU, GELU), then (step 1) the demo's measured
// dying-ReLU evidence: at lr = 0.1 every unit in layer 2 is dead and the prediction is a constant.
import demo from '../data/demo.json'
import { C } from '../utils/plot'

defineProps<{ step: number }>()
const ZS = Array.from({ length: 81 }, (_, i) => -4 + i * 0.1)
const gelu = (z: number) => 0.5 * z * (1 + Math.tanh(Math.sqrt(2 / Math.PI) * (z + 0.044715 * z ** 3)))
const FNS = [
  { name: 'ReLU', code: 'nn.ReLU()', color: C.teal, f: (z: number) => Math.max(0, z), note: 'slope 0 for z < 0: a unit stuck there never recovers' },
  { name: 'Leaky ReLU', code: 'nn.LeakyReLU()', color: C.blue, f: (z: number) => (z > 0 ? z : 0.1 * z), note: 'small slope below 0 (drawn as 0.1 to be visible)' },
  { name: 'GELU', code: 'nn.GELU()', color: C.violet, f: gelu, note: 'smooth, dips slightly below 0; the transformer default' },
]
const dead = demo.dead
const usd = (v: number) => `$${Math.round(v * 1e5).toLocaleString('en-US')}`
</script>

<template>
  <div class="mt-2">
    <div class="grid grid-cols-3 gap-4 text-left">
      <div v-for="fn in FNS" :key="fn.name" border="2 solid white/5" bg="white/5" rounded-lg p-2>
        <div class="flex justify-between items-baseline px-1">
          <b :style="{ color: fn.color }">{{ fn.name }}</b>
          <code class="text-xs opacity-80">{{ fn.code }}</code>
        </div>
        <LineChart
          :series="[{ x: ZS, y: ZS.map(fn.f), color: fn.color, width: 3 }]" :width="300" :height="170"
          :x-range="[-4, 4]" :y-range="[-1, 4]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[0, 2, 4]" :font="12"
          :hlines="[{ y: 0, color: C.dim, dash: '0' }]"
        />
        <div class="text-xs opacity-80 px-1 leading-snug">{{ fn.note }}</div>
      </div>
    </div>

    <div class="reveal mt-4 grid grid-cols-2 gap-4 text-sm text-left" :class="{ shown: step >= 1 }">
      <div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2>
        <b class="text-red-300">Measured in the demo, lr = 0.1:</b> <b>{{ Math.round(dead['0.1'].layer2_dead * 100) }}%</b> of hidden layer 2 is dead.
        Every district gets the same prediction, <b>{{ usd(dead['0.1'].pred_mean) }}</b>: the network collapsed to a constant.
      </div>
      <div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
        <b class="text-teal-300">Same network, lr = 0.001:</b> only <b>{{ Math.round(dead['0.001'].layer2_dead * 100) }}%</b> dead, and the rest carry the model.
        The usual cure is a sensible learning rate; Leaky ReLU or GELU if many units still die.
      </div>
    </div>
  </div>
</template>
