<script setup lang="ts">
// 1D toy regression y = sin(2πx) + noise, from data/oned.json (scripts/make_data.py).
// Draws any mix of: data points, bootstrap counts, single-tree fits, the bagged average, linear fits.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/oned.json'

const props = withDefaults(defineProps<{
  points?: boolean
  boot?: number // index of a bootstrap sample: size dots by how often each row was drawn
  trees?: number // draw the first `trees` bootstrapped tree fits as thin lines
  tree?: number // highlight one bootstrapped tree fit
  avg?: boolean // average of all bootstrapped trees
  lins?: number // draw the first `lins` bootstrapped linear fits
  truth?: boolean
  title?: string
  color?: string
  w?: number
  h?: number
  axes?: boolean
}>(), { points: true, boot: -1, trees: 0, tree: -1, avg: false, lins: 0, truth: false, color: '#fbbf24', w: 420, h: 250, axes: true })

const pad = { l: props.axes ? 30 : 8, r: 8, t: props.title ? 28 : 8, b: props.axes ? 24 : 8 }
const yMin = -1.9
const yMax = 1.9
const sx = (x: number) => pad.l + x * (props.w - pad.l - pad.r)
const sy = (y: number) => pad.t + (yMax - Math.max(yMin, Math.min(yMax, y))) / (yMax - yMin) * (props.h - pad.t - pad.b)
const line = (ys: number[]) => ys.map((y, i) => `${sx(d.grid[i]).toFixed(1)},${sy(y).toFixed(1)}`).join(' ')
const linLine = ([a, b]: number[]) => `${sx(0)},${sy(a)} ${sx(1)},${sy(a + b)}`

const counts = props.boot >= 0 ? d.counts[props.boot] : null
const dots = d.x.map((x, i) => {
  const c = counts ? counts[i] : 1
  return { key: i, cx: sx(x), cy: sy(d.y[i]), r: c === 0 ? 3.2 : 2.6 + 1.6 * c, out: c === 0 }
})
const treeLines = d.trees.slice(0, props.trees).map(line)
const linLines = d.lin.slice(0, props.lins).map(linLine)
</script>

<template>
  <svg role="img" :aria-label="title ?? 'Noisy sine data with fitted curves'" :viewBox="`0 0 ${w} ${h}`" class="w-full">
    <rect :x="pad.l" :y="pad.t" :width="w - pad.l - pad.r" :height="h - pad.t - pad.b" rx="4" :style="{ fill: '#ffffff', fillOpacity: 0.025, stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="pad.l" :x2="w - pad.r" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <template v-if="axes">
      <text :x="pad.l - 6" :y="sy(1) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">1</text>
      <text :x="pad.l - 6" :y="sy(-1) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">−1</text>
      <text :x="(pad.l + w - pad.r) / 2" :y="h - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">x</text>
    </template>
    <text v-if="title" :x="(pad.l + w - pad.r) / 2" y="18" text-anchor="middle" :style="{ fill: color, fontSize: '15px', fontWeight: 700 }">{{ title }}</text>
    <polyline v-if="truth" :points="line(d.truth)" :style="{ fill: 'none', stroke: '#e2e8f0', strokeWidth: 2, strokeDasharray: '6 5', opacity: 0.7 }" />
    <template v-if="points">
      <circle v-for="p in dots" :key="p.key" :cx="p.cx" :cy="p.cy" :r="p.r"
        :style="p.out ? { fill: 'none', stroke: '#f87171', strokeWidth: 1.3, opacity: 0.8 } : { fill: '#cbd5e1', fillOpacity: boot >= 0 ? 0.75 : 0.55 }" />
    </template>
    <polyline v-for="(pl, i) in linLines" :key="`l${i}`" :points="pl" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 1.5, opacity: 0.45 }" />
    <polyline v-for="(pl, i) in treeLines" :key="`t${i}`" :points="pl" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 1.2, opacity: 0.28 }" />
    <polyline v-if="tree >= 0" :points="line(d.trees[tree])" :style="{ fill: 'none', stroke: color, strokeWidth: 2.4, strokeLinejoin: 'round' }" />
    <polyline v-if="avg" :points="line(d.avg)" :style="{ fill: 'none', stroke: '#60a5fa', strokeWidth: 3.5, strokeLinejoin: 'round' }" />
  </svg>
</template>
