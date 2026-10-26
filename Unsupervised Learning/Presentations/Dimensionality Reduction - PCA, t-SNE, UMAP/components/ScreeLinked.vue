<script setup lang="ts">
// Scree plot for digits (data/digits.json): bars = share of variance per component, line = cumulative share.
// Hover or click on the chart to choose k; the row below shows eight digits rebuilt from k components.
// Dashed lines: the k needed for 80 / 90 / 95% (what PCA(n_components=0.95) would pick).
import { computed, ref } from 'vue'
import d from '../data/digits.json'
import { decode, toLocal } from '../utils/plot'

const N = 45
const W = 560; const H = 230; const L = 40; const B = 26
const bw = (W - L - 10) / N
const bx = (j: number) => L + j * bw // j = 0-based component
const yv = (v: number) => H - B - v * (H - B - 12)
const k = ref(d.kAt['0.9'])
const cumPath = d.cum.slice(0, N).map((c, j) => `${j ? 'L' : 'M'}${(bx(j) + bw / 2).toFixed(1)},${yv(c).toFixed(1)}`).join('')
const scale = 1 / 0.16 // bars: 16% = full height
const TH = [['0.8', '#a78bfa'], ['0.9', '#60a5fa'], ['0.95', '#2dd4bf']] as const

function pick(e: PointerEvent) {
  const [x] = toLocal(e, e.currentTarget as Element, W, H)
  k.value = Math.max(1, Math.min(N, Math.floor((x - L) / bw) + 1))
}
const show = [0, 1, 2, 3, 4, 5, 6, 7].map(c => d.y.indexOf(c, d.y.indexOf(c) + 1)) // the second example of each digit 0-7
const imgs = show.map(i => decode(d.img[i]))
const recon = computed(() => imgs.map((x) => {
  const z = d.V.slice(0, k.value).map(v => v.reduce((s, vi, i) => s + vi * (x[i] - d.mean[i]), 0))
  return d.mean.map((m, i) => m + z.reduce((s, zj, j) => s + zj * d.V[j][i], 0))
}))
</script>

<template>
  <div>
    <svg
      :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 250px; cursor: col-resize" role="img"
      aria-label="Scree plot: variance per component as bars and cumulative variance as a line"
      @pointermove="pick" @pointerdown="pick"
    >
      <line :x1="L" :x2="W - 10" :y1="H - B" :y2="H - B" :style="{ stroke: '#64748b' }" />
      <text v-for="t in [0, 0.5, 1]" :key="t" :x="L - 6" :y="yv(t) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ t * 100 }}%</text>
      <rect v-for="j in N" :key="j" :x="bx(j - 1) + 1" :y="yv(Math.min(1, d.evr[j - 1] * scale))" :width="bw - 2" :height="H - B - yv(Math.min(1, d.evr[j - 1] * scale))" :style="{ fill: j <= k ? '#fb923c' : '#475569', transition: 'fill 0.2s' }" />
      <line v-for="[t, c] in TH" :key="t" :x1="bx(d.kAt[t] - 1) + bw / 2" :x2="bx(d.kAt[t] - 1) + bw / 2" :y1="yv(+t)" :y2="H - B" :style="{ stroke: c, strokeDasharray: '3 3', strokeOpacity: 0.7 }" />
      <text v-for="([t, c], i) in TH" :key="`l${t}`" :x="bx(d.kAt[t] - 1) + bw / 2 + 4" :y="H - B - 52 + 16 * i" :style="{ fill: c, fontSize: '11px' }">{{ +t * 100 }}%: k = {{ d.kAt[t] }}</text>
      <path :d="cumPath" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 2.5 }" />
      <circle :cx="bx(k - 1) + bw / 2" :cy="yv(d.cum[k - 1])" r="5" :style="{ fill: '#2dd4bf', stroke: '#0b1020', strokeWidth: 2 }" />
      <text v-for="j in [1, 10, 20, 30, 40]" :key="`x${j}`" :x="bx(j - 1) + bw / 2" :y="H - 8" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ j }}</text>
    </svg>
    <div class="flex justify-center gap-5 text-sm font-mono">
      <span class="text-amber-300">k = {{ k }} · {{ (100 * d.cum[k - 1]).toFixed(1) }}% kept</span>
      <span class="text-orange-300">bars: each component (16% = full height)</span>
      <span class="text-teal-300">line: cumulative</span>
    </div>
    <div class="flex justify-center gap-3 mt-2">
      <DigitImg v-for="(r, i) in recon" :key="i" :v="r" :size="54" />
    </div>
  </div>
</template>
