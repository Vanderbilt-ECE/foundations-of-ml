<script setup lang="ts">
// Denoising with PCA (data/denoise.json). PCA was fit on 1497 clean training digits; 300 held-out digits got
// Gaussian pixel noise (sd 4). Each noisy digit is projected onto k components and mapped back.
// Rows: clean · noisy · rebuilt from k. Right: mean squared error against the clean digits, over all 300,
// for every k. Too few components blur the digit; too many let the noise back in.
import { computed, ref } from 'vue'
import d from '../data/denoise.json'

const k = ref(d.best)
const den = computed(() => d.noisy.slice(0, 8).map((x) => {
  const z = d.V.slice(0, k.value).map(v => v.reduce((s, vi, i) => s + vi * (x[i] - d.mean[i]), 0))
  return d.mean.map((m, i) => m + z.reduce((s, zj, j) => s + zj * d.V[j][i], 0))
}))
const W = 300; const H = 200; const L = 34; const B = 24
const mx = (j: number) => L + j / 64 * (W - L - 8)
const my = (v: number) => 10 + (1 - v / 20) * (H - B - 10)
const path = d.mse.map((v, j) => `${j ? 'L' : 'M'}${mx(j).toFixed(1)},${my(v).toFixed(1)}`).join('')
</script>

<template>
  <div class="grid grid-cols-[auto_1fr] gap-6 items-center">
    <div class="space-y-1.5">
      <div class="flex items-center gap-1.5"><span class="w-16 text-xs text-right opacity-70">clean</span><DigitImg v-for="(s, i) in d.clean" :key="i" :v="s" :size="44" /></div>
      <div class="flex items-center gap-1.5"><span class="w-16 text-xs text-right text-red-300">noisy</span><DigitImg v-for="i in 8" :key="i" :v="d.noisy[i - 1]" :size="44" /></div>
      <div class="flex items-center gap-1.5"><span class="w-16 text-xs text-right text-teal-300">k = {{ k }}</span><DigitImg v-for="(x, i) in den" :key="i" :v="x" :size="44" /></div>
      <div class="flex items-center gap-3 pt-2 text-sm font-mono">
        <input v-model.number="k" type="range" min="0" max="64" class="flex-1" style="accent-color: #2dd4bf">
      </div>
    </div>
    <div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 220px" role="img" aria-label="Reconstruction error against the clean digits as a function of k, U-shaped">
        <line :x1="L" :x2="W - 8" :y1="H - B" :y2="H - B" :style="{ stroke: '#64748b' }" />
        <line :x1="L" :x2="L" y1="10" :y2="H - B" :style="{ stroke: '#64748b' }" />
        <line :x1="L" :x2="W - 8" :y1="my(d.noisyMse)" :y2="my(d.noisyMse)" :style="{ stroke: '#f87171', strokeDasharray: '4 4' }" />
        <text :x="W - 10" :y="my(d.noisyMse) - 5" text-anchor="end" :style="{ fill: '#fca5a5', fontSize: '11px' }">noisy input</text>
        <path :d="path" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 2.5 }" />
        <circle :cx="mx(k)" :cy="my(d.mse[k])" r="5" :style="{ fill: '#2dd4bf', stroke: '#0b1020', strokeWidth: 2 }" />
        <text v-for="t in [0, 10, 20]" :key="t" :x="L - 5" :y="my(t) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ t }}</text>
        <text v-for="t in [0, 16, 32, 48, 64]" :key="`x${t}`" :x="mx(t)" :y="H - 8" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ t }}</text>
      </svg>
      <div class="font-mono text-sm">error <span class="text-teal-300">{{ d.mse[k].toFixed(2) }}</span> · <span class="opacity-70">noisy {{ d.noisyMse.toFixed(2) }} · best k = {{ d.best }}</span></div>
    </div>
  </div>
</template>
