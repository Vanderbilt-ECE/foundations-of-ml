<script setup lang="ts">
// t-SNE in one picture. Left: points in the original space, joined by their neighbor affinities p_ij
// (thicker = closer). Right: the 2D map. The map points start scrambled and slide into place; each link is drawn
// in the map too, red while it is stretched (q_ij too small for its p_ij), teal once it is matched.
// Loops while the slide is showing; the PDF export shows the finished map.
import { computed, ref } from 'vue'
import { rng, useActive, useLoop } from '../utils/plot'

const R = rng(21)
const centers = [[-1.1, 0.6], [1.0, 0.9], [0.1, -1.0]]
const COLS = ['#2dd4bf', '#fbbf24', '#a78bfa']
const lab = Array.from({ length: 18 }, (_, i) => i % 3)
const hi = lab.map(c => [centers[c][0] + 0.35 * R.n(), centers[c][1] + 0.35 * R.n()])
const target = hi.map(p => [p[0] * 1.05 + 0.1 * R.n(), p[1] * 1.05 + 0.1 * R.n()])
const start = hi.map(() => [1.6 * (R.u() - 0.5), 1.6 * (R.u() - 0.5)])
const links: { i: number, j: number, w: number }[] = []
hi.forEach((p, i) => hi.forEach((q, j) => {
  const d = Math.hypot(p[0] - q[0], p[1] - q[1])
  if (i < j && d < 0.9) links.push({ i, j, w: Math.exp(-d * d / 0.25) })
}))

const { isPrintMode } = useActive()
const u = ref(isPrintMode.value ? 1 : 0)
useLoop((_, t) => {
  const c = t % 7 // 1 s scrambled, 4 s settling, 2 s hold
  u.value = Math.min(1, Math.max(0, (c - 1) / 4))
}, () => { u.value = 0 })
const e = computed(() => 1 - (1 - u.value) ** 3)
const map = computed(() => start.map((s, i) => [s[0] + (target[i][0] - s[0]) * e.value, s[1] + (target[i][1] - s[1]) * e.value]))

const W = 300; const H = 260; const U = 82
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const stretch = (l: { i: number, j: number }) => {
  const a = map.value[l.i]; const b = map.value[l.j]
  const dm = Math.hypot(a[0] - b[0], a[1] - b[1])
  const dh = Math.hypot(target[l.i][0] - target[l.j][0], target[l.i][1] - target[l.j][1])
  return Math.min(1, Math.abs(dm - dh) / 0.6)
}
const mixC = (s: number) => `rgb(${Math.round(45 + (248 - 45) * s)},${Math.round(212 + (113 - 212) * s)},${Math.round(191 + (113 - 191) * s)})`
</script>

<template>
  <div class="grid grid-cols-[1fr_auto_1fr] gap-2 items-center">
    <div class="text-center">
      <div class="text-sm font-bold text-teal-300 mb-1">original space: pᵢⱼ</div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 260px" role="img" aria-label="Points in the original space joined by neighbor links">
        <rect x="2" y="2" :width="W - 4" :height="H - 4" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: 'rgba(255,255,255,0.08)' }" />
        <line v-for="(l, k) in links" :key="k" :x1="sx(hi[l.i][0])" :y1="sy(hi[l.i][1])" :x2="sx(hi[l.j][0])" :y2="sy(hi[l.j][1])" :style="{ stroke: '#cbd5e1', strokeOpacity: 0.2 + 0.5 * l.w, strokeWidth: 0.5 + 3 * l.w }" />
        <circle v-for="(p, i) in hi" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="6" :style="{ fill: COLS[lab[i]], stroke: '#0b1020', strokeWidth: 1.5 }" />
      </svg>
    </div>
    <div class="text-3xl opacity-60 px-1">⟶</div>
    <div class="text-center">
      <div class="text-sm font-bold text-amber-300 mb-1">2D map: qᵢⱼ</div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 260px" role="img" aria-label="Points in the 2D map moving until their links match">
        <rect x="2" y="2" :width="W - 4" :height="H - 4" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: 'rgba(255,255,255,0.08)' }" />
        <line v-for="(l, k) in links" :key="k" :x1="sx(map[l.i][0])" :y1="sy(map[l.i][1])" :x2="sx(map[l.j][0])" :y2="sy(map[l.j][1])" :style="{ stroke: mixC(stretch(l)), strokeOpacity: 0.3 + 0.5 * l.w, strokeWidth: 0.5 + 3 * l.w }" />
        <circle v-for="(p, i) in map" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="6" :style="{ fill: COLS[lab[i]], stroke: '#0b1020', strokeWidth: 1.5 }" />
      </svg>
    </div>
  </div>
</template>
