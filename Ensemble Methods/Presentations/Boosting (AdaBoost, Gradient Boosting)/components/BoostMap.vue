<script setup lang="ts">
// AdaBoost with stumps on two moons (data/moons.json, the same 300 training points as the bagging deck).
// Shaded by the normalized vote Σαh / Σα: amber where it says class 1, blue where it says class 0,
// stronger color where the vote is more lopsided. Accuracy is on 5,000 fresh test points.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/moons.json'

const props = defineProps<{ m: '1' | '10' | '400' }>()

const P: number[][] = (d.stages as Record<string, number[][]>)[props.m]
const acc = d.acc[Number(props.m) - 1]
const title = props.m === '1' ? '1 stump' : `${props.m} stumps`

const W = 300
const H = 222
const T = 26
const nx = d.xs.length
const ny = d.ys.length
const cw = W / nx
const ch = (H - T) / ny
const x0 = d.xs[0]
const x1 = d.xs[nx - 1]
const y0 = d.ys[0]
const y1 = d.ys[ny - 1]
const sx = (x: number) => (x - x0) / (x1 - x0) * (W - cw) + cw / 2
const sy = (y: number) => T + (y1 - y) / (y1 - y0) * (H - T - ch) + ch / 2
// blend over the slide background so overlapping cells don't leave seams
const bg = [15, 23, 42]
const amber = [245, 158, 11]
const blue = [59, 130, 246]
const mix = (c: number[], t: number) => `rgb(${c.map((v, k) => Math.round(bg[k] + (v - bg[k]) * t)).join(',')})`
const cells = P.flatMap((row, j) => row.map((v, i) => ({
  key: `${i}-${j}`,
  x: i * cw,
  y: T + (ny - 1 - j) * ch,
  style: { fill: mix(v > 0 ? amber : blue, 0.1 + 0.5 * Math.min(1, Math.abs(v) * 2)) },
})))
const pts = d.X.map((p, i) => ({ key: i, cx: sx(p[0]), cy: sy(p[1]), c: d.y[i] }))
</script>

<template>
  <svg role="img" :aria-label="`AdaBoost with ${title} on two moons; test accuracy ${(acc * 100).toFixed(1)} percent`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <text x="0" y="17" :style="{ fill: '#c4b5fd', fontSize: '15px', fontWeight: 700 }">{{ title }}</text>
    <text :x="W" y="17" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '13px' }">test accuracy {{ (acc * 100).toFixed(1) }}%</text>
    <rect v-for="c in cells" :key="c.key" :x="c.x" :y="c.y" :width="cw + 0.5" :height="ch + 0.5" :style="c.style" />
    <circle v-for="p in pts" :key="p.key" :cx="p.cx" :cy="p.cy" r="2.3"
      :style="{ fill: p.c ? '#fde68a' : '#bfdbfe', stroke: '#0f172a', strokeWidth: 0.6 }" />
    <rect x="0.5" :y="T + 0.5" :width="W - 1" :height="H - T - 1" rx="4" :style="{ fill: 'none', stroke: '#475569', strokeWidth: 1 }" />
  </svg>
</template>
