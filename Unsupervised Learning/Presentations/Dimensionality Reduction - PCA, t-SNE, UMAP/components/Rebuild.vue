<script setup lang="ts">
// Rebuilding one digit from k principal components: x̂ = μ + z₁ v₁ + … + z_k v_k, with z_j = v_jᵀ (x − μ).
// Click a digit to pick it; drag the slider, or press play to add components one at a time.
// The strip shows the first terms of the sum with this digit's coefficients; the bars are all |z_j|.
import { computed, onBeforeUnmount, ref } from 'vue'
import d from '../data/digits.json'
import { decode } from '../utils/plot'

const which = ref(2)
const k = ref(5)
const x = computed(() => decode(d.img[d.picks[which.value]]))
const z = computed(() => d.V.map(v => v.reduce((s, vi, i) => s + vi * (x.value[i] - d.mean[i]), 0)))
const xhat = computed(() => d.mean.map((m, i) => m + z.value.slice(0, k.value).reduce((s, zj, j) => s + zj * d.V[j][i], 0)))
const err = computed(() => x.value.reduce((s, xi, i) => s + (xi - xhat.value[i]) ** 2, 0) / 64)
const zmax = computed(() => Math.max(...z.value.map(Math.abs)))

let timer: ReturnType<typeof setInterval> | undefined
const playing = ref(false)
function play() {
  clearInterval(timer)
  playing.value = true
  k.value = 0
  timer = setInterval(() => {
    if (k.value >= 40) { clearInterval(timer); playing.value = false; return }
    k.value++
  }, 260)
}
onBeforeUnmount(() => clearInterval(timer))
const BW = 380; const BH = 70; const NB = 40
</script>

<template>
  <div class="grid grid-cols-[auto_1fr] gap-8 items-start">
    <div class="text-center">
      <div class="flex gap-1.5 justify-center mb-3">
        <div v-for="(p, i) in d.picks" :key="p" class="cursor-pointer rounded" :style="{ outline: which === i ? '2px solid #2dd4bf' : 'none', opacity: which === i ? 1 : 0.6 }" @click="which = i">
          <DigitImg :v="d.img[p]" :size="36" />
        </div>
      </div>
      <div class="flex gap-4 justify-center">
        <div><DigitImg :v="xhat" :size="150" /><div class="text-xs mt-1">x̂ with k = {{ k }}</div></div>
        <div class="opacity-70"><DigitImg :v="x" :size="76" /><div class="text-xs mt-1">original</div></div>
      </div>
    </div>
    <div class="text-left space-y-3">
      <div class="flex items-center gap-3 text-sm font-mono">
        <span class="text-amber-300 w-14 text-lg">k = {{ k }}</span>
        <input v-model.number="k" type="range" min="0" max="64" class="flex-1" style="accent-color: #fbbf24">
        <button class="px-2 py-0.5 rounded border-2 border-white/10 bg-white/5 hover:bg-white/10" @click="play">{{ playing ? '…' : '▶ build' }}</button>
      </div>
      <div class="flex items-center gap-1.5 text-sm font-mono">
        <DigitImg :v="d.mean" :size="40" />
        <template v-for="j in 4" :key="j">
          <span class="transition-opacity" :style="{ opacity: j <= k ? 1 : 0.25 }">{{ z[j - 1] >= 0 ? '+' : '−' }}{{ Math.abs(z[j - 1]).toFixed(1) }}×</span>
          <DigitImg :v="d.V[j - 1]" div :size="40" class="transition-opacity" :style="{ opacity: j <= k ? 1 : 0.25 }" />
        </template>
        <span :style="{ opacity: k > 4 ? 1 : 0.25 }">+ …</span>
      </div>
      <svg :viewBox="`0 0 ${BW} ${BH + 16}`" class="w-full" role="img" aria-label="Size of each principal-component coefficient for this digit">
        <rect v-for="j in NB" :key="j" :x="(j - 1) * BW / NB + 1" :y="BH - BH * Math.abs(z[j - 1]) / zmax" :width="BW / NB - 2" :height="BH * Math.abs(z[j - 1]) / zmax" :style="{ fill: j <= k ? '#fbbf24' : '#475569', transition: 'fill 0.25s, y 0.4s, height 0.4s' }" />
        <text x="0" :y="BH + 13" :style="{ fill: '#94a3b8', fontSize: '10px' }">|z₁|</text>
        <text :x="BW" :y="BH + 13" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">|z₄₀|</text>
      </svg>
      <div class="font-mono text-sm space-y-0.5">
        <div>variance kept (all digits): <span class="text-amber-300">{{ k ? (100 * d.cum[k - 1]).toFixed(1) : '0.0' }}%</span></div>
        <div>this digit's error ‖x − x̂‖²/64: <span class="text-red-300">{{ err.toFixed(2) }}</span></div>
      </div>
    </div>
  </div>
</template>
