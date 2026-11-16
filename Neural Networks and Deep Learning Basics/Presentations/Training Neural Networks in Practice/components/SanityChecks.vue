<script setup lang="ts">
// Three quick checks, all measured (data/sanity.json, data/demo.json):
//   1 · the untrained MNIST classifier's loss vs. ln 10
//   2 (step ≥ 1) · overfitting a single batch of 32 images: the loss should go to ~0
//   3 (step ≥ 2) · test error against two baselines
import S from '../data/sanity.json'
import { C } from '../utils/plot'

defineProps<{ step: number }>()
const steps = S.one_batch.map((_, i) => i + 1)
</script>

<template>
  <div class="grid grid-cols-3 gap-4 mt-3 text-left">
    <div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
      <div class="font-bold text-blue-300 mb-2">1 · Check the starting loss</div>
      <div class="text-sm opacity-85 mb-3">Untrained, a K-class classifier should guess: loss ≈ ln K.</div>
      <div class="text-center">
        <div class="text-sm opacity-75">MNIST, 10 classes</div>
        <div class="text-3xl font-mono mt-1"><span class="text-blue-300">{{ S.init_loss.toFixed(3) }}</span></div>
        <div class="text-sm mt-1">vs. ln 10 = <span class="font-mono">{{ S.ln10.toFixed(3) }}</span> ✓</div>
      </div>
      <div class="text-xs opacity-75 mt-3">Much higher: confidently wrong from the start. Check scaling and initialization.</div>
    </div>

    <div class="reveal" :class="{ shown: step >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
      <div class="font-bold text-amber-300 mb-1">2 · Overfit one tiny batch</div>
      <div class="text-sm opacity-85">32 images, 100 steps. It must memorize them.</div>
      <LineChart
        :series="[{ x: steps, y: S.one_batch, color: C.amber, width: 3 }]" :width="300" :height="190" y-log
        :x-range="[1, 100]" :y-range="[1e-4, 10]" :x-ticks="[1, 50, 100]" :font="12" x-label="step" y-label="loss (log)"
        :y-ticks="[{ v: 1e-4, t: '10⁻⁴' }, { v: 1e-2, t: '10⁻²' }, { v: 1, t: '1' }]"
      />
      <div class="text-xs opacity-75">{{ S.one_batch[0].toFixed(2) }} → {{ S.one_batch.at(-1)!.toFixed(4) }}. If it can't, there's a bug.</div>
    </div>

    <div class="reveal" :class="{ shown: step >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
      <div class="font-bold text-teal-300 mb-1">3 · Beat a baseline</div>
      <div class="text-sm opacity-85 mb-2">California Housing, typical test error:</div>
      <BaselineBars :width="320" />
      <div class="text-xs opacity-75 mt-1">Can't beat linear regression? Look for a bug before tuning.</div>
    </div>
  </div>
</template>
