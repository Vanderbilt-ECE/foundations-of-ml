<script setup lang="ts">
// Distance concentration. 150 random points, uniform in the unit cube [0,1]^d.
// Left: the same points at d = 2 (their first two coordinates), with the nearest and farthest pair marked,
//   plus two bars comparing the nearest and farthest pair distance at the current d.
// Right: histogram of all 11,175 pairwise distances, divided by their mean. As d grows it collapses onto 1.
// Drag the slider, or press play to sweep d. The PDF export shows the 2D picture and the d = 2 / d = 1000 histograms.
// The ball-in-cube volume lives on the next slide (BallCube.vue).
import { computed, onBeforeUnmount, ref } from 'vue'
import { rng, useActive, useTween } from '../utils/plot'

const DS = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]
const N = 150; const BINS = 36; const MAX = 2
const { isPrintMode } = useActive()
const di = ref(1)
const d = computed(() => DS[di.value])

// One fixed pool of random numbers, so increasing d adds coordinates to the same points.
const R = rng(42)
const pool = Array.from({ length: N }, () => Float64Array.from({ length: 1000 }, () => R.u()))

function stats(d: number) {
  const dist: number[] = []
  let lo = Infinity; let hi = 0; let loPair = [0, 0]; let hiPair = [0, 0]
  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      let s = 0
      for (let k = 0; k < d; k++) s += (pool[i][k] - pool[j][k]) ** 2
      const r = Math.sqrt(s)
      dist.push(r)
      if (r < lo) { lo = r; loPair = [i, j] }
      if (r > hi) { hi = r; hiPair = [i, j] }
    }
  }
  const mean = dist.reduce((a, b) => a + b, 0) / dist.length
  const h = Array.from({ length: BINS }, () => 0)
  for (const x of dist) h[Math.min(BINS - 1, Math.floor((x / mean) / MAX * BINS))]++
  return { h: h.map(c => c / dist.length), lo, hi, mean, loPair, hiPair, contrast: (hi - lo) / lo }
}
const cache = new Map<number, ReturnType<typeof stats>>()
const at = (d: number) => cache.get(d) ?? (cache.set(d, stats(d)), cache.get(d)!)
const cur = computed(() => at(d.value))
const bars = useTween(() => cur.value.h, 500)
const nearFar = useTween(() => [cur.value.lo / cur.value.hi, 1], 500)

// --- 2D square: all 150 points by their first two coordinates; nearest + farthest pair at d = 2 ---
const two = at(2)
const SQ = 170; const SP = 8
const sx = (v: number) => SP + v * (SQ - 2 * SP)
const sy = (v: number) => SQ - SP - v * (SQ - 2 * SP)
const P = (i: number) => [sx(pool[i][0]), sy(pool[i][1])]

// --- histogram ---
const W = 460; const H = 230; const PB = 24; const YCAP = 0.12
const bw = (W - 20) / BINS
const by = (p: number) => H - PB - Math.min(1, p / YCAP) * (H - PB - 10)

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
</script>

<template>
  <!-- PDF export: the 2D picture, then the histogram at d = 2 and d = 1000 -->
  <div v-if="isPrintMode" class="grid grid-cols-[0.8fr_1fr_1fr] gap-5 items-end mt-2">
    <div class="text-center">
      <svg :viewBox="`0 0 ${SQ} ${SQ}`" class="w-full" style="max-height: 200px" role="img" aria-label="150 random points in the unit square with the nearest and farthest pair marked">
        <rect :x="SP" :y="SP" :width="SQ - 2 * SP" :height="SQ - 2 * SP" :style="{ fill: 'none', stroke: '#64748b' }" />
        <circle v-for="i in N" :key="i" :cx="P(i - 1)[0]" :cy="P(i - 1)[1]" r="2" :style="{ fill: '#cbd5e1', fillOpacity: 0.7 }" />
        <line :x1="P(two.hiPair[0])[0]" :y1="P(two.hiPair[0])[1]" :x2="P(two.hiPair[1])[0]" :y2="P(two.hiPair[1])[1]" :style="{ stroke: '#a78bfa', strokeWidth: 2 }" />
        <circle v-for="k in two.loPair" :key="k" :cx="P(k)[0]" :cy="P(k)[1]" r="7" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 2 }" />
      </svg>
      <div class="text-sm font-mono">the points at d = 2</div>
    </div>
    <div v-for="dd in [2, 1000]" :key="dd" class="text-center">
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 200px" role="img" :aria-label="`Histogram of pairwise distances in ${dd} dimensions`">
        <rect v-for="(p, i) in at(dd).h" :key="i" :x="10 + i * bw" :y="by(p)" :width="bw - 1.5" :height="H - PB - by(p)" :style="{ fill: '#2dd4bf', fillOpacity: 0.8 }" />
        <line :x1="10" :x2="W - 10" :y1="H - PB" :y2="H - PB" :style="{ stroke: '#64748b' }" />
      </svg>
      <div class="text-sm font-mono">d = {{ dd }} · (max − min) / min = {{ at(dd).contrast.toFixed(2) }}</div>
    </div>
  </div>

  <div v-else>
    <!-- one slider drives both panels -->
    <div class="flex items-center gap-4 text-sm">
      <span class="font-mono text-amber-300 text-xl w-28 shrink-0">d = {{ d }}</span>
      <input v-model.number="di" type="range" min="0" :max="DS.length - 1" step="1" class="flex-1" style="accent-color: #fbbf24" aria-label="Number of dimensions">
      <button class="px-3 py-0.5 rounded border-2 border-white/10 bg-white/5 hover:bg-white/10 w-24" @click="play">{{ playing ? '…' : '▶ sweep' }}</button>
    </div>

    <div class="grid grid-cols-[0.75fr_1.25fr] gap-6 mt-4 items-start text-left">
      <!-- 1 · what is being measured -->
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
        <div class="text-sm font-bold text-teal-300">1 · 150 random points</div>
        <svg :viewBox="`0 0 ${SQ} ${SQ}`" class="block mx-auto mt-1" style="width: 170px; height: 170px" role="img" aria-label="The 150 random points by their first two coordinates; the nearest pair is ringed in amber and the farthest pair joined in violet">
          <rect :x="SP" :y="SP" :width="SQ - 2 * SP" :height="SQ - 2 * SP" :style="{ fill: '#2dd4bf', fillOpacity: 0.04, stroke: '#64748b' }" />
          <circle v-for="i in N" :key="i" :cx="P(i - 1)[0]" :cy="P(i - 1)[1]" r="2.2" :style="{ fill: '#cbd5e1', fillOpacity: 0.65 }" />
          <line :x1="P(two.hiPair[0])[0]" :y1="P(two.hiPair[0])[1]" :x2="P(two.hiPair[1])[0]" :y2="P(two.hiPair[1])[1]" :style="{ stroke: '#a78bfa', strokeWidth: 2.2 }" />
          <circle v-for="k in two.hiPair" :key="`h${k}`" :cx="P(k)[0]" :cy="P(k)[1]" r="3.5" :style="{ fill: '#a78bfa' }" />
          <circle v-for="k in two.loPair" :key="`l${k}`" :cx="P(k)[0]" :cy="P(k)[1]" r="3" :style="{ fill: '#fbbf24' }" />
          <circle :cx="(P(two.loPair[0])[0] + P(two.loPair[1])[0]) / 2" :cy="(P(two.loPair[0])[1] + P(two.loPair[1])[1]) / 2" r="9" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 2 }" />
        </svg>
        <div class="text-xs opacity-70 text-center">the d = 2 view (x₁, x₂)</div>
        <!-- nearest vs farthest pair at the current d, as bars on a common scale -->
        <div class="mt-2 space-y-1 text-xs font-mono">
          <div class="flex items-center gap-2">
            <span class="w-16 text-amber-300">nearest</span>
            <div class="flex-1 h-2.5 rounded-sm bg-white/5"><div class="h-full rounded-sm" :style="{ width: `${100 * nearFar[0]}%`, background: '#fbbf24' }" /></div>
            <span class="w-10 text-right">{{ cur.lo.toFixed(cur.lo < 0.1 ? 3 : 2) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-16 text-violet-300">farthest</span>
            <div class="flex-1 h-2.5 rounded-sm bg-white/5"><div class="h-full rounded-sm" :style="{ width: `${100 * nearFar[1]}%`, background: '#a78bfa' }" /></div>
            <span class="w-10 text-right">{{ cur.hi.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- 2 · all pairwise distances -->
      <div>
        <div class="text-sm font-bold text-teal-300">2 · All 11,175 pair distances ÷ their mean</div>
        <svg :viewBox="`0 0 ${W} ${H}`" class="w-full mt-1" role="img" aria-label="Histogram of pairwise distances divided by their mean">
          <rect v-for="(p, i) in bars" :key="i" :x="10 + i * bw" :y="by(p)" :width="bw - 1.5" :height="Math.max(0, H - PB - by(p))" :style="{ fill: '#2dd4bf', fillOpacity: 0.8 }" />
          <line :x1="10" :x2="W - 10" :y1="H - PB" :y2="H - PB" :style="{ stroke: '#64748b' }" />
          <line :x1="10 + (W - 20) / 2" :x2="10 + (W - 20) / 2" :y1="10" :y2="H - PB" :style="{ stroke: '#fbbf24', strokeDasharray: '4 4', strokeOpacity: 0.6 }" />
          <text v-for="t in [0, 0.5, 1, 1.5, 2]" :key="t" :x="10 + t / MAX * (W - 20)" :y="H - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">{{ t === 2 ? '2+' : t }}</text>
        </svg>
        <div class="text-sm font-mono mt-1 flex gap-6">
          <span>mean distance = <span class="text-teal-300 text-base">{{ cur.mean.toFixed(2) }}</span></span>
          <span>(max − min) / min = <span class="text-amber-300 text-base">{{ cur.contrast.toFixed(2) }}</span></span>
        </div>
      </div>
    </div>
  </div>
</template>
