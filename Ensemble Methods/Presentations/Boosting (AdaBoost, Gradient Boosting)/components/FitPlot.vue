<script lang="ts">
// module scope, shared by every FitPlot: each instance needs its own arrow-marker id,
// because several plots can be mounted at once
let instances = 0
</script>

<script setup lang="ts">
// 1D toy regression y = sin(2πx) + noise (data/oned.json, the same 50 points as the bagging deck).
// `curves` names arrays in the data file by path, e.g. 'stump', 'snaps.20', 'rounds.1.Fg'.
// `arrows` draws the residual y − F from the curve at rounds[arrows].Fg to every point.
// `robust` swaps in data/robust.json: the same points with three corrupted labels, ringed in red.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import oned from '../data/oned.json'
import robustData from '../data/robust.json'


type Curve = { key: string, color: string, width?: number, dash?: string }
type Legend = { label: string, color: string, dash?: boolean }
const props = withDefaults(defineProps<{
  curves?: Curve[]
  legend?: Legend[]
  truth?: boolean
  arrows?: number
  robust?: boolean
  title?: string
  note?: string
  titleColor?: string
  legendPos?: 'bl' | 'tr'
  w?: number
  h?: number
}>(), { curves: () => [], legend: () => [], legendPos: 'bl', truth: true, arrows: -1, robust: false, titleColor: '#c4b5fd', w: 440, h: 260 })

const markerId = `fp-arrow-${++instances}`
const src: Record<string, any> = props.robust ? { ...oned, ...robustData } : oned
const get = (path: string): number[] => path.split('.').reduce((o: any, k) => o[k], src)
const bad: number[] = props.robust ? robustData.bad : []

const pad = { l: 30, r: 10, t: props.title ? 28 : 10, b: 22 }
const yMin = props.robust ? -2.9 : -2.15
const yMax = props.robust ? 2.9 : 1.9
const sx = (x: number) => pad.l + x * (props.w - pad.l - pad.r)
const sy = (y: number) => pad.t + (yMax - Math.max(yMin, Math.min(yMax, y))) / (yMax - yMin) * (props.h - pad.t - pad.b)
const line = (ys: number[]) => ys.map((y, i) => `${sx(oned.grid[i]).toFixed(1)},${sy(y).toFixed(1)}`).join(' ')
const lines = props.curves.map((c, i) => ({ key: i, pts: line(get(c.key)), c }))
const dots = (src.x as number[]).map((x, i) => ({ key: i, cx: sx(x), cy: sy(src.y[i]), bad: bad.includes(i) }))
// arrow from the current fit F(x_i) to the point y_i: the residual, i.e. the negative gradient of squared loss
const arrows = props.arrows >= 0
  ? (oned.rounds[props.arrows].F as number[]).map((f, i) => {
      const y1 = sy(f)
      const y2 = sy(oned.y[i])
      const dir = y2 > y1 ? 1 : -1
      const len = Math.abs(y2 - y1)
      return { key: i, x: sx(oned.x[i]), y1, y2: y2 - dir * Math.min(4, len / 2), len }
    })
  : []
</script>

<template>
  <svg role="img" :aria-label="title ?? 'Noisy sine data with fitted curves'" :viewBox="`0 0 ${w} ${h}`" class="w-full">
    <defs>
      <marker :id="markerId" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
        <path d="M0,0 L10,5 L0,10 z" style="fill: #f87171" />
      </marker>
    </defs>
    <rect :x="pad.l" :y="pad.t" :width="w - pad.l - pad.r" :height="h - pad.t - pad.b" rx="4" :style="{ fill: '#ffffff', fillOpacity: 0.025, stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="pad.l" :x2="w - pad.r" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <text :x="pad.l - 6" :y="sy(1) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">1</text>
    <text :x="pad.l - 6" :y="sy(-1) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">−1</text>
    <text :x="(pad.l + w - pad.r) / 2" :y="h - 5" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">x</text>
    <text v-if="title" :x="pad.l" y="18" :style="{ fill: titleColor, fontSize: '15px', fontWeight: 700 }">{{ title }}</text>
    <text v-if="note" :x="w - pad.r" y="18" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '13px' }">{{ note }}</text>
    <polyline v-if="truth" :points="line(oned.truth)" :style="{ fill: 'none', stroke: '#e2e8f0', strokeWidth: 2, strokeDasharray: '6 5', opacity: 0.6 }" />
    <circle v-for="p in dots" :key="p.key" :cx="p.cx" :cy="p.cy" :r="p.bad ? 4.5 : 3"
      :style="p.bad ? { fill: '#f87171', fillOpacity: 0.35, stroke: '#f87171', strokeWidth: 1.8 } : { fill: '#cbd5e1', fillOpacity: 0.6 }" />
    <template v-for="a in arrows" :key="`a${a.key}`">
      <line v-if="a.len > 6" :x1="a.x" :x2="a.x" :y1="a.y1" :y2="a.y2" :marker-end="`url(#${markerId})`" :style="{ stroke: '#f87171', strokeWidth: 1.6, opacity: 0.85 }" />
    </template>
    <polyline v-for="l in lines" :key="l.key" :points="l.pts"
      :style="{ fill: 'none', stroke: l.c.color, strokeWidth: l.c.width ?? 3, strokeDasharray: l.c.dash ?? 'none', strokeLinejoin: 'round' }" />
    <g v-for="(g, i) in legend" :key="`g${i}`" :transform="`translate(${legendPos === 'tr' ? w - pad.r - 232 : pad.l + 10}, ${legendPos === 'tr' ? pad.t + 16 + i * 17 : h - pad.b - 12 - (legend.length - 1 - i) * 17})`">
      <line x1="0" x2="18" y1="0" y2="0" :style="{ stroke: g.color, strokeWidth: 3, strokeDasharray: g.dash ? '5 4' : 'none' }" />
      <text x="24" y="4" :style="{ fill: g.color, fontSize: '12px', fontWeight: 700 }">{{ g.label }}</text>
    </g>
  </svg>
</template>
