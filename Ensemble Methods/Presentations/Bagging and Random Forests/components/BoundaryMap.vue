<script setup lang="ts">
// Two-moons decision regions (data/moons.json): predicted P(class 1) on a grid, shaded from
// blue (class 0) to amber (class 1), with the 300 training points on top.
// model='data' draws only the points; hard thresholds the probability at 0.5 (solid colors).
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/moons.json'

const props = withDefaults(defineProps<{ model: 'data' | 'tree' | 'bag'; hard?: boolean }>(), { hard: false })

const isData = props.model === 'data'
const P: number[][] = isData ? [] : d[props.model]
const acc = props.model === 'tree' ? d.treeAcc : d.bagAcc
const title = isData ? 'Training data' : props.model === 'tree' ? 'One deep tree' : props.hard ? 'Bagged, thresholded at 0.5' : 'Bagged, 300 trees'
const color = isData ? '#cbd5e1' : props.model === 'tree' ? '#fbbf24' : '#60a5fa'

const W = 420
const H = 300
const T = 28
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
const cells = P.flatMap((row, j) => row.map((p, i) => ({
  key: `${i}-${j}`,
  x: i * cw,
  y: T + (ny - 1 - j) * ch,
  style: { fill: mix(p >= 0.5 ? amber : blue, props.hard ? 0.58 : 0.08 + 0.5 * Math.abs(p - 0.5)) },
})))
const pts = d.X.map((p, i) => ({ key: i, cx: sx(p[0]), cy: sy(p[1]), c: d.y[i] }))
</script>

<template>
  <svg role="img" :aria-label="`${title} ${isData ? 'training points on two moons' : `decision regions on two moons; test accuracy ${Math.round(acc * 100)} percent`}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <text x="0" y="18" :style="{ fill: color, fontSize: '15px', fontWeight: 700 }">{{ title }}</text>
    <text v-if="!isData" :x="W" y="18" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '13px' }">test accuracy {{ (acc * 100).toFixed(1) }}%</text>
    <rect v-for="c in cells" :key="c.key" :x="c.x" :y="c.y" :width="cw + 0.5" :height="ch + 0.5" :style="c.style" />
    <circle v-for="p in pts" :key="p.key" :cx="p.cx" :cy="p.cy" r="3"
      :style="{ fill: p.c ? '#fde68a' : '#bfdbfe', stroke: '#0f172a', strokeWidth: 0.8 }" />
    <rect x="0.5" :y="T + 0.5" :width="W - 1" :height="H - T - 1" rx="4" :style="{ fill: 'none', stroke: '#475569', strokeWidth: 1 }" />
  </svg>
</template>
