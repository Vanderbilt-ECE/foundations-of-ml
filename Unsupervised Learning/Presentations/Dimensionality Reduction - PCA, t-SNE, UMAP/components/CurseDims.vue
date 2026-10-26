<script setup lang="ts">
// Distance concentration. 150 random points, uniform in the unit cube [0,1]^d. Left: histogram of all
// pairwise distances, divided by their mean. As d grows the histogram collapses onto 1: every point is
// about equally far from every other. Readout: (farthest - nearest) / nearest, over all pairs.
// Right: the fraction of the cube's volume inside its inscribed ball, on a log scale.
// Drag the slider, or press play to sweep d. The PDF export shows d = 2 and d = 1000 side by side.
import { computed, onBeforeUnmount, ref } from 'vue'
import { rng, useActive, useTween } from '../utils/plot'

const DS = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]
const N = 150; const BINS = 36; const MAX = 2
const { isPrintMode } = useActive()
const di = ref(1)

// One fixed pool of random numbers, so increasing d adds coordinates to the same points.
const R = rng(42)
const pool = Array.from({ length: N }, () => Float64Array.from({ length: 1000 }, () => R.u()))
function stats(d: number) {
  const dist: number[] = []
  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      let s = 0
      for (let k = 0; k < d; k++) s += (pool[i][k] - pool[j][k]) ** 2
      dist.push(Math.sqrt(s))
    }
  }
  const mean = dist.reduce((a, b) => a + b, 0) / dist.length
  const h = Array.from({ length: BINS }, () => 0)
  for (const x of dist) h[Math.min(BINS - 1, Math.floor((x / mean) / MAX * BINS))]++
  const lo = Math.min(...dist); const hi = Math.max(...dist)
  return { h: h.map(c => c / dist.length), contrast: (hi - lo) / lo }
}
const cache = new Map<number, ReturnType<typeof stats>>()
const at = (d: number) => cache.get(d) ?? (cache.set(d, stats(d)), cache.get(d)!)
const cur = computed(() => at(DS[di.value]))
const bars = useTween(() => cur.value.h, 500)

// volume of the radius-1/2 ball in d dimensions: pi^(d/2) (1/2)^d / Gamma(d/2 + 1)
function lgammaHalf(x: number) { // log Gamma(x) for x a positive multiple of 1/2
  let s = 0; let y = x
  while (y > 1.01) { y -= 1; s += Math.log(y) }
  return s + (Math.abs(y - 0.5) < 1e-9 ? 0.5 * Math.log(Math.PI) : 0)
}
const ballFrac = (d: number) => Math.exp((d / 2) * Math.log(Math.PI) - d * Math.log(2) - lgammaHalf(d / 2 + 1))

const W = 420; const H = 230; const PB = 28
const bw = (W - 20) / BINS
const by = (p: number) => H - PB - Math.min(1, p / 0.25) * (H - PB - 12)
const VW = 300; const VH = 230
const vx = (i: number) => 36 + i * (VW - 50) / (DS.length - 1)
const vy = (f: number) => 14 + (-Math.log10(f) / 13) * (VH - 50) // 1 down to 1e-13
const vpath = DS.map((d, i) => `${i ? 'L' : 'M'}${vx(i).toFixed(1)},${vy(Math.max(ballFrac(d), 1e-13)).toFixed(1)}`).join('')

let timer: ReturnType<typeof setInterval> | undefined
const playing = ref(false)
function play() {
  clearInterval(timer)
  playing.value = true
  di.value = 0
  timer = setInterval(() => {
    if (di.value >= DS.length - 1) { clearInterval(timer); playing.value = false; return }
    di.value++
  }, 900)
}
onBeforeUnmount(() => clearInterval(timer))
const sup = (e: number) => [...String(e)].map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹'[+c]).join('')
const fracTxt = (f: number) => {
  if (f > 0.01) return `${(100 * f).toFixed(1)}%`
  const e = Math.floor(Math.log10(f))
  return `${(f / 10 ** e).toFixed(1)} × 10⁻${sup(-e)}`
}
</script>

<template>
  <div v-if="isPrintMode" class="grid grid-cols-2 gap-4">
    <div v-for="d in [2, 1000]" :key="d" class="text-center">
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 220px" role="img" :aria-label="`Histogram of pairwise distances in ${d} dimensions`">
        <rect v-for="(p, i) in at(d).h" :key="i" :x="10 + i * bw" :y="by(p)" :width="bw - 1.5" :height="H - PB - by(p)" :style="{ fill: '#2dd4bf', fillOpacity: 0.8 }" />
        <line :x1="10" :x2="W - 10" :y1="H - PB" :y2="H - PB" :style="{ stroke: '#64748b' }" />
      </svg>
      <div class="text-sm font-mono">d = {{ d }} · (max − min) / min = {{ at(d).contrast.toFixed(2) }}</div>
    </div>
  </div>
  <div v-else class="grid grid-cols-[1.4fr_1fr] gap-6 items-start">
    <div>
      <div class="flex items-center gap-3 text-sm">
        <span class="font-mono w-20 text-amber-300 text-lg">d = {{ DS[di] }}</span>
        <input v-model.number="di" type="range" min="0" :max="DS.length - 1" step="1" class="flex-1" style="accent-color: #fbbf24">
        <button class="px-2 py-0.5 rounded border-2 border-white/10 bg-white/5 hover:bg-white/10" @click="play">{{ playing ? '…' : '▶ sweep' }}</button>
      </div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full mt-1" style="max-height: 240px" role="img" aria-label="Histogram of pairwise distances divided by their mean">
        <rect v-for="(p, i) in bars" :key="i" :x="10 + i * bw" :y="by(p)" :width="bw - 1.5" :height="Math.max(0, H - PB - by(p))" :style="{ fill: '#2dd4bf', fillOpacity: 0.8 }" />
        <line :x1="10" :x2="W - 10" :y1="H - PB" :y2="H - PB" :style="{ stroke: '#64748b' }" />
        <line :x1="10 + (W - 20) / 2" :x2="10 + (W - 20) / 2" :y1="10" :y2="H - PB" :style="{ stroke: '#fbbf24', strokeDasharray: '4 4', strokeOpacity: 0.6 }" />
        <text v-for="t in [0, 0.5, 1, 1.5, 2]" :key="t" :x="10 + t / MAX * (W - 20)" :y="H - 8" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">{{ t }}</text>
        <text :x="W - 12" :y="20" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">distance ÷ mean distance</text>
      </svg>
      <div class="text-sm font-mono mt-1">
        nearest vs farthest pair: <span class="text-amber-300">(max − min) / min = {{ cur.contrast.toFixed(2) }}</span>
      </div>
    </div>
    <div>
      <div class="text-sm opacity-80 mb-1">Volume of the cube inside its inscribed ball</div>
      <svg :viewBox="`0 0 ${VW} ${VH}`" class="w-full" style="max-height: 240px" role="img" aria-label="Fraction of the cube's volume inside the inscribed ball, falling toward zero as d grows">
        <line x1="36" :x2="VW - 10" :y1="VH - 36" :y2="VH - 36" :style="{ stroke: '#64748b' }" />
        <line x1="36" x2="36" y1="10" :y2="VH - 36" :style="{ stroke: '#64748b' }" />
        <text v-for="e in [0, 4, 8, 12]" :key="e" x="30" :y="vy(10 ** -e) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">10{{ e ? `⁻${sup(e)}` : '⁰' }}</text>
        <path :d="vpath" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 2.5 }" />
        <circle :cx="vx(Math.min(di, DS.length - 1))" :cy="vy(Math.max(ballFrac(DS[di]), 1e-13))" r="6" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2, transition: 'cx 0.4s, cy 0.4s' }" />
        <text v-for="(d, i) in DS" :key="d" :x="vx(i)" :y="VH - 20" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ d }}</text>
        <text :x="VW / 2 + 10" :y="VH - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">d</text>
      </svg>
      <div class="text-sm font-mono text-violet-300">ball / cube = {{ fracTxt(ballFrac(DS[di])) }}</div>
    </div>
  </div>
</template>
