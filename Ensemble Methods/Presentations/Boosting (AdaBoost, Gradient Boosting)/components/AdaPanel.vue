<script setup lang="ts">
// AdaBoost by hand on 12 points (data/ada.json). Class +1 is amber, class −1 is blue.
//   round = 0, 1, 2: dot area ∝ that round's example weight; the stump's two sides are tinted
//                    by what it predicts; red rings mark the points it gets wrong
//   round = -1:      the combined vote sign(α₁h₁ + α₂h₂ + α₃h₃) over the whole square
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/ada.json'

const props = withDefaults(defineProps<{ round?: number }>(), { round: -1 })

const S = 230
const L = 6
const T = 44
const W = S + 2 * L
const H = T + S + 8
const sx = (v: number) => L + v * S
const sy = (v: number) => T + (1 - v) * S
const amber = '#fbbf24'
const blue = '#60a5fa'
// opaque blends over the slide background, so neighboring vote cells leave no seams
const bg = [15, 23, 42]
const mix = (c: number[], t: number) => `rgb(${c.map((v, k) => Math.round(bg[k] + (v - bg[k]) * t)).join(',')})`
const amberCell = mix([251, 191, 36], 0.2)
const blueCell = mix([96, 165, 250], 0.2)
const stumps = d.rounds
const h = (st: typeof stumps[number], p: number[]) => (p[st.f] > st.thr ? st.s : -st.s)
const vote = (p: number[]) => stumps.reduce((s, st) => s + st.alpha * h(st, p), 0)

const final = props.round < 0
const r = final ? null : stumps[props.round]
const weights = final ? d.rounds[0].w : r!.w
const pts = d.X.map((p, i) => ({
  key: i,
  cx: sx(p[0]),
  cy: sy(p[1]),
  rad: final ? 6 : 3 + 24 * Math.sqrt(weights[i]),
  color: d.y[i] > 0 ? amber : blue,
  miss: final ? Math.sign(vote(p)) !== d.y[i] : r!.miss[i],
}))

// stump: two tinted half-planes and the split line
let halves: { key: string, x: number, y: number, w: number, h: number, c: string }[] = []
let split = { x1: 0, y1: 0, x2: 0, y2: 0 }
if (r) {
  const below = -r.s // prediction on the low side of the threshold
  if (r.f === 0) {
    halves = [
      { key: 'lo', x: sx(0), y: sy(1), w: sx(r.thr) - sx(0), h: S, c: below > 0 ? amber : blue },
      { key: 'hi', x: sx(r.thr), y: sy(1), w: sx(1) - sx(r.thr), h: S, c: below > 0 ? blue : amber },
    ]
    split = { x1: sx(r.thr), y1: sy(0), x2: sx(r.thr), y2: sy(1) }
  }
  else {
    halves = [
      { key: 'lo', x: sx(0), y: sy(r.thr), w: S, h: sy(0) - sy(r.thr), c: below > 0 ? amber : blue },
      { key: 'hi', x: sx(0), y: sy(1), w: S, h: sy(r.thr) - sy(1), c: below > 0 ? blue : amber },
    ]
    split = { x1: sx(0), y1: sy(r.thr), x2: sx(1), y2: sy(r.thr) }
  }
}
// combined vote on a grid
const n = 46
const cells = final
  ? Array.from({ length: n * n }, (_, k) => {
      const i = k % n
      const j = Math.floor(k / n)
      const v = vote([(i + 0.5) / n, (j + 0.5) / n])
      return { key: k, x: sx(i / n), y: sy((j + 1) / n), c: v > 0 ? amberCell : blueCell }
    })
  : []
const title = final ? 'Combined vote' : `Round ${props.round + 1}`
const sub = final
  ? `${stumps.map((s, i) => `${s.alpha.toFixed(2)}·h${'₁₂₃'[i]}`).join(' + ')}`
  : `ε = ${r!.e.toFixed(3)}   `
const alphaStr = final ? '' : r!.alpha.toFixed(2)
const nMiss = pts.filter(p => p.miss).length
</script>

<template>
  <svg role="img" :aria-label="final ? 'Combined AdaBoost vote of three stumps classifies all 12 points correctly' : `Round ${round + 1}: weighted error ${r!.e}, stump weight ${r!.alpha}, ${nMiss} points misclassified`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <text :x="L" y="16" :style="{ fill: final ? '#c4b5fd' : '#e2e8f0', fontSize: '15px', fontWeight: 700 }">{{ title }}</text>
    <text :x="L" y="35" :style="{ fill: '#cbd5e1', fontSize: final ? '12px' : '13px' }">{{ sub }}<template v-if="!final"><tspan class="greek">α</tspan> = {{ alphaStr }}</template></text>
    <rect v-for="hv in halves" :key="hv.key" :x="hv.x" :y="hv.y" :width="hv.w" :height="hv.h" :style="{ fill: hv.c, fillOpacity: 0.13 }" />
    <rect v-for="c in cells" :key="c.key" :x="c.x" :y="c.y" :width="S / n + 0.6" :height="S / n + 0.6" :style="{ fill: c.c }" />
    <rect :x="L" :y="T" :width="S" :height="S" rx="4" :style="{ fill: 'none', stroke: '#475569', strokeWidth: 1 }" />
    <line v-if="r" :x1="split.x1" :y1="split.y1" :x2="split.x2" :y2="split.y2" :style="{ stroke: '#e2e8f0', strokeWidth: 2.5, strokeDasharray: '7 5' }" />
    <g v-for="p in pts" :key="p.key">
      <circle :cx="p.cx" :cy="p.cy" :r="p.rad" :style="{ fill: p.color, fillOpacity: 0.55, stroke: p.color, strokeWidth: 1.5 }" />
      <circle v-if="p.miss" :cx="p.cx" :cy="p.cy" :r="p.rad + 4" :style="{ fill: 'none', stroke: '#f87171', strokeWidth: 2.2 }" />
    </g>
  </svg>
</template>
