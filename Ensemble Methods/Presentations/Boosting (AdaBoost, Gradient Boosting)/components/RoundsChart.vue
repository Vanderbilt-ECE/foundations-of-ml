<script setup lang="ts">
// Error against number of boosting rounds M (log scale), one fit per curve, read off with staged_predict.
//   src='oned':  the 50-point sine toy, stumps (data/oned.json → curves), test on 5,000 fresh points
//   src='eta':   California, depth-3 trees, several learning rates (data/cal_eta.json)
//   src='depth': California, learning rate 0.1, several tree depths (data/cal_depth.json)
// A dot marks each curve's lowest test error.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import oned from '../data/oned.json'
import calEta from '../data/cal_eta.json'
import calDepth from '../data/cal_depth.json'

const props = withDefaults(defineProps<{
  src: 'oned' | 'eta' | 'depth'
  keys: string[]
  train?: boolean
}>(), { train: false })

const colors: Record<string, string> = { '1.0': '#f87171', '0.3': '#fb923c', '0.1': '#a78bfa', '0.03': '#f0abfc', '1': '#fbbf24', '3': '#a78bfa', '6': '#f472b6' }
const name = (k: string) => (props.src === 'depth' ? (k === '1' ? 'depth 1 (stumps)' : `depth ${k}`) : `η = ${k}`)
const data: Record<string, any> = props.src === 'oned' ? oned.curves : props.src === 'eta' ? calEta : calDepth
const Ms: number[] = data.M
const maxM = Ms[Ms.length - 1]
// toy: y-axis fits the curves shown; California: fixed window (small-η curves start far above it)
const top = Math.max(...props.keys.map(k => Math.max(...data[k].test)))
const onedHi = Math.ceil(top * 10) / 10
const cfg = props.src === 'oned'
  ? { lo: 0, hi: onedHi, ticks: Array.from({ length: Math.round(onedHi / (onedHi > 0.35 ? 0.1 : 0.05)) + 1 }, (_, i) => +(i * (onedHi > 0.35 ? 0.1 : 0.05)).toFixed(2)), xt: [1, 3, 10, 30, 100, 300, 1000] }
  : { lo: 0.2, hi: 0.8, ticks: [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], xt: [1, 3, 10, 30, 100, 300, 1000, 2000] }

const W = 580
const H = 300
const L = 48
const R = 448
const T = 14
const Bot = 254
const sx = (m: number) => L + Math.log(m) / Math.log(maxM) * (R - L)
// unclamped: curves that start above the window enter from the top edge (clipped by #rc-clip)
const sy = (v: number) => Bot - (v - cfg.lo) / (cfg.hi - cfg.lo) * (Bot - T)
const path = (vals: number[]) => Ms.map((m, i) => `${sx(m).toFixed(1)},${sy(vals[i]).toFixed(1)}`).join(' ')

const series = props.keys.map(k => ({
  key: k,
  color: colors[k] ?? '#a78bfa',
  test: path(data[k].test),
  train: props.train && data[k].train ? path(data[k].train) : null,
  bx: sx(data[k].best),
  by: sy(data[k].bestTest),
  best: data[k].best as number,
  bestTest: data[k].bestTest as number,
  label: name(k),
}))
// legend labels at the right edge, spaced so they never collide
const ends = series.map((s, i) => ({ i, y: sy(data[s.key].test[Ms.length - 1]) })).sort((a, b) => a.y - b.y)
for (let j = 1; j < ends.length; j++) ends[j].y = Math.max(ends[j].y, ends[j - 1].y + 16)
const labelY: number[] = []
ends.forEach(e => { labelY[e.i] = e.y })
const trainY = props.train ? sy(data[props.keys[0]].train[Ms.length - 1]) : 0
const ref = props.src === 'oned' ? { v: oned.curves.noise, label: `noise floor σ²ε = ${oned.curves.noise.toFixed(2)}`, color: '#94a3b8' } : { v: calDepth.rf, label: `random forest ${calDepth.rf.toFixed(3)}`, color: '#2dd4bf' }
const aria = series.map(s => `${s.label}: lowest test MSE ${s.bestTest} at ${s.best} rounds`).join('; ')
</script>

<template>
  <svg role="img" :aria-label="`Test MSE against boosting rounds. ${aria}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in cfg.xt" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="Bot" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="Bot" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="L" :y1="T" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="R" :y1="sy(ref.v)" :y2="sy(ref.v)" :style="{ stroke: ref.color, strokeWidth: 1.5, strokeDasharray: '6 5', opacity: 0.8 }" />
    <text :x="L + 6" :y="sy(ref.v) + (src === 'oned' ? 15 : -6)" :style="{ fill: ref.color, fontSize: '12px' }">{{ ref.label }}</text>
    <defs>
      <clipPath :id="`rc-clip-${src}`"><rect :x="L" :y="T - 6" :width="R - L + 6" :height="Bot - T + 6" /></clipPath>
    </defs>
    <g v-for="(s, k) in series" :key="s.key" :clip-path="`url(#rc-clip-${src})`">
      <polyline v-if="s.train" :points="s.train" :style="{ fill: 'none', stroke: s.color, strokeWidth: 2.5, strokeDasharray: '7 5', opacity: 0.8 }" />
      <polyline :points="s.test" :style="{ fill: 'none', stroke: s.color, strokeWidth: 3.5, strokeLinejoin: 'round' }" />
      <circle :cx="s.bx" :cy="s.by" r="5.5" :style="{ fill: s.color, stroke: '#0f172a', strokeWidth: 2 }" />
    </g>
    <text v-for="(s, k) in series" :key="`l${s.key}`" :x="R + 8" :y="labelY[k] + 4" :style="{ fill: s.color, fontSize: '12px', fontWeight: 700 }">{{ s.label }}{{ train ? ' test' : '' }}</text>
    <text v-if="train" :x="R + 8" :y="Math.max(trainY, labelY[0] + 18) + 4" :style="{ fill: series[0].color, fontSize: '12px', opacity: 0.85 }">{{ series[0].label }} train</text>
    <text v-for="t in cfg.ticks" :key="`y${t}`" :x="L - 8" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ cfg.hi < 0.4 ? t.toFixed(2) : t.toFixed(1) }}</text>
    <text v-for="t in cfg.xt" :key="`x${t}`" :x="sx(t)" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text :x="(L + R) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">boosting rounds M (log scale)</text>
    <text x="13" :y="(T + Bot) / 2" text-anchor="middle" :transform="`rotate(-90 13 ${(T + Bot) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">MSE</text>
  </svg>
</template>
