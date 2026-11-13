<script setup lang="ts">
// The ball inside the cube. Left: a square with its inscribed circle, and 600 points drawn uniformly from the
// unit cube [0,1]^d, plotted by their first two coordinates. A dot is violet if it lies within 0.5 of the
// center using ALL d coordinates, i.e. inside the inscribed d-dimensional ball; gray otherwise. As d grows the
// dots go gray even near the center of the picture, because the other coordinates carry them away.
// Right: the exact fraction of the cube's volume inside the ball, pi^(d/2) (1/2)^d / Gamma(d/2 + 1), log scale.
// Drag the slider, or press play to sweep d. The PDF export shows d = 2 and d = 10.
import { computed, onBeforeUnmount, ref } from 'vue'
import { rng, useActive } from '../utils/plot'

const DS = [2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]
const N = 600
const { isPrintMode } = useActive()
const di = ref(0)
const d = computed(() => DS[di.value])

// Fixed uniform points, so increasing d adds coordinates to the same points.
const R = rng(7)
const pool = Array.from({ length: N }, () => Float64Array.from({ length: 1000 }, () => R.u()))
// inside[d][i]: is point i within 0.5 of the center using its first d coordinates?
const inside = new Map<number, boolean[]>()
{
  const s = new Float64Array(N)
  let k = 0
  for (const dd of DS) {
    for (; k < dd; k++) for (let i = 0; i < N; i++) s[i] += (pool[i][k] - 0.5) ** 2
    inside.set(dd, Array.from(s, v => v <= 0.25))
  }
}
const inNow = computed(() => inside.get(d.value)!)
const countIn = computed(() => inNow.value.filter(Boolean).length)

// --- square ---
const SQ = 200; const SP = 6
const sx = (v: number) => SP + v * (SQ - 2 * SP)
const sy = (v: number) => SQ - SP - v * (SQ - 2 * SP)

// --- exact volume fraction, kept in log10 so d = 1000 (about 10^-1187) does not underflow ---
function lgammaHalf(x: number) { // log Gamma(x) for x a positive multiple of 1/2
  let s = 0; let y = x
  while (y > 1.01) { y -= 1; s += Math.log(y) }
  return s + (Math.abs(y - 0.5) < 1e-9 ? 0.5 * Math.log(Math.PI) : 0)
}
const ballLog10 = (d: number) => ((d / 2) * Math.log(Math.PI) - d * Math.log(2) - lgammaHalf(d / 2 + 1)) / Math.LN10
const FLOOR = -13
const VW = 400; const VH = 200; const VL = 56; const VB = 36
const vx = (i: number) => VL + i * (VW - VL - 16) / (DS.length - 1)
const vy = (L: number) => 10 + (-Math.max(L, FLOOR) / -FLOOR) * (VH - VB - 10)
const lastOn = DS.findLastIndex(dd => ballLog10(dd) >= FLOOR) // last d still on the chart (d = 20)
const vpath = DS.slice(0, lastOn + 1).map((dd, i) => `${i ? 'L' : 'M'}${vx(i).toFixed(1)},${vy(ballLog10(dd)).toFixed(1)}`).join('')
const offScale = computed(() => ballLog10(d.value) < FLOOR)

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
const fracTxt = (L: number) => {
  if (L > -2) return `${(100 * 10 ** L).toFixed(1)}%`
  const e = Math.floor(L)
  return `${(10 ** (L - e)).toFixed(1)} × 10⁻${sup(-e)}`
}
</script>

<template>
  <!-- PDF export: the square at d = 2 and d = 10 -->
  <div v-if="isPrintMode" class="grid grid-cols-2 gap-8 mt-2 text-center">
    <div v-for="dd in [2, 10]" :key="dd">
      <svg :viewBox="`0 0 ${SQ} ${SQ}`" class="mx-auto" style="height: 200px" :aria-label="`Uniform points in the cube, colored by whether they are inside the ball, at d = ${dd}`" role="img">
        <rect :x="SP" :y="SP" :width="SQ - 2 * SP" :height="SQ - 2 * SP" :style="{ fill: 'none', stroke: '#64748b' }" />
        <circle :cx="SQ / 2" :cy="SQ / 2" :r="(SQ - 2 * SP) / 2" :style="{ fill: '#a78bfa', fillOpacity: 0.08, stroke: '#a78bfa', strokeOpacity: 0.6 }" />
        <circle v-for="(p, i) in pool" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="2" :style="{ fill: inside.get(dd)![i] ? '#a78bfa' : '#64748b' }" />
      </svg>
      <div class="text-sm font-mono">d = {{ dd }} · inside the ball: {{ inside.get(dd)!.filter(Boolean).length }} of {{ N }} · exact {{ fracTxt(ballLog10(dd)) }}</div>
    </div>
  </div>

  <div v-else>
    <div class="flex items-center gap-4 text-sm">
      <span class="font-mono text-amber-300 text-xl w-28 shrink-0">d = {{ d }}</span>
      <input v-model.number="di" type="range" min="0" :max="DS.length - 1" step="1" class="flex-1" style="accent-color: #fbbf24" aria-label="Number of dimensions">
      <button class="px-3 py-0.5 rounded border-2 border-white/10 bg-white/5 hover:bg-white/10 w-24" @click="play">{{ playing ? '…' : '▶ sweep' }}</button>
    </div>

    <div class="grid grid-cols-[0.85fr_1.15fr] gap-6 mt-4 items-start text-left">
      <!-- 1 · the picture -->
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
        <div class="text-sm font-bold text-violet-300">1 · 600 uniform points in the cube</div>
        <svg :viewBox="`0 0 ${SQ} ${SQ}`" class="block mx-auto mt-2" style="width: 190px; height: 190px" role="img" aria-label="A square with its inscribed circle; random points inside the d-dimensional ball are violet, the rest gray">
          <rect :x="SP" :y="SP" :width="SQ - 2 * SP" :height="SQ - 2 * SP" :style="{ fill: '#ffffff', fillOpacity: 0.02, stroke: '#64748b', strokeWidth: 1.2 }" />
          <circle :cx="SQ / 2" :cy="SQ / 2" :r="(SQ - 2 * SP) / 2" :style="{ fill: '#a78bfa', fillOpacity: 0.08, stroke: '#a78bfa', strokeOpacity: 0.7, strokeWidth: 1.5 }" />
          <circle v-for="(p, i) in pool" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="2.1" :style="{ fill: inNow[i] ? '#a78bfa' : '#64748b', fillOpacity: inNow[i] ? 1 : 0.6, transition: 'fill 0.4s' }" />
        </svg>
        <div class="text-xs opacity-75 mt-2">
          Drawn at their first two coordinates. <span class="text-violet-300">Violet</span> = within 0.5 of the center using <b>all {{ d }}</b> coordinates.
        </div>
        <div class="text-sm font-mono mt-1">inside the ball: <span class="text-violet-300 text-base">{{ countIn }}</span> of {{ N }}</div>
      </div>

      <!-- 2 · the exact fraction -->
      <div>
        <div class="text-sm font-bold text-violet-300">2 · Fraction of the cube inside the ball</div>
        <svg :viewBox="`0 0 ${VW} ${VH}`" class="w-full mt-1" role="img" aria-label="Fraction of the cube's volume inside the inscribed ball, on a log scale, falling below 10 to the minus 13 by d = 50">
          <line :x1="VL" :x2="VW - 8" :y1="VH - VB" :y2="VH - VB" :style="{ stroke: '#64748b' }" />
          <line :x1="VL" :x2="VL" y1="10" :y2="VH - VB" :style="{ stroke: '#64748b' }" />
          <text x="14" :y="(VH - VB) / 2 + 5" :transform="`rotate(-90 14 ${(VH - VB) / 2 + 5})`" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">log scale</text>
          <text v-for="e in [0, 4, 8, 12]" :key="e" :x="VL - 6" :y="vy(-e) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">10{{ e ? `⁻${sup(e)}` : '⁰' }}</text>
          <path :d="vpath" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 2.5 }" />
          <!-- past d = 20 the value leaves the chart: show that instead of a fake flat line -->
          <line :x1="vx(lastOn)" :y1="vy(ballLog10(DS[lastOn]))" :x2="vx(lastOn + 1)" :y2="vy(FLOOR)" :style="{ stroke: '#a78bfa', strokeWidth: 2, strokeDasharray: '3 4' }" />
          <text :x="vx(lastOn + 1) + 8" :y="vy(FLOOR) - 8" :style="{ fill: '#a78bfa', fontSize: '12px' }">off scale ↓</text>
          <circle :cx="vx(di)" :cy="vy(ballLog10(d))" r="6" :style="{ fill: offScale ? 'none' : '#fbbf24', stroke: offScale ? '#fbbf24' : '#0b1020', strokeWidth: 2, transition: 'cx 0.4s, cy 0.4s' }" />
          <text v-for="(dd, i) in DS" :key="dd" :x="vx(i)" :y="VH - VB + 16" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ dd }}</text>
          <text :x="(VL + VW) / 2" :y="VH - 2" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">d</text>
        </svg>
        <div class="text-sm font-mono mt-1">ball / cube = <span class="text-violet-300 text-base">{{ fracTxt(ballLog10(d)) }}</span></div>
      </div>
    </div>
  </div>
</template>
