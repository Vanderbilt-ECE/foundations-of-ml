<script setup lang="ts">
// The generative story, animated with the running example's real points (data/em.json, which make_data.py
// generated exactly this way): spin a wheel whose slices are the weights pi_k, then draw the point from
// the Gaussian of the slice it lands on. The point flies from the wheel to where it was drawn.
//   step 0: one point at a time, slowly · step 1: fast, until all 500 are drawn
//   step 2: erase the colors and ellipses: what we actually observe
// The PDF export shows all points.
import { computed, ref, watch } from 'vue'
import d from '../data/em.json'
import { color, domainOf, equalScale } from '../utils/clusters'
import { ellipsePath, rng, useLoop } from '../utils/gmm'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const W = 780; const H = 330
const CX = 125; const CY = 150; const RW = 92
const N = d.pts.length
const P = equalScale(domainOf(d.pts, 0.04), 470, H - 10)
const sx = (x: number) => 290 + P.sx(x); const sy = (y: number) => 5 + P.sy(y)
const T = d.true

// slices clockwise from 12 o'clock
const starts = T.w.map((_, k) => T.w.slice(0, k).reduce((a, b) => a + b, 0))
const slice = (k: number) => {
  const a0 = starts[k] * 2 * Math.PI; const a1 = (starts[k] + T.w[k]) * 2 * Math.PI
  const p = (a: number) => `${(CX + RW * Math.sin(a)).toFixed(1)},${(CY - RW * Math.cos(a)).toFixed(1)}`
  return `M${CX},${CY}L${p(a0)}A${RW},${RW} 0 ${T.w[k] > 0.5 ? 1 : 0} 1 ${p(a1)}Z`
}
const R = rng(9)
const land = d.truth.map(k => (starts[k] + T.w[k] * (0.15 + 0.7 * R.u())) * 2 * Math.PI) // where the needle stops

const placed = ref(0) // points already in the plot
const tIn = ref(0) // time into the current point's animation (slow mode)
const SPIN = 1.0; const FLY = 0.55; const HOLD = 0.5
const { active } = useLoop((dt) => {
  if (placed.value >= N) return
  if (props.step >= 1) {
    placed.value = Math.min(N, placed.value + Math.max(1, Math.round(dt * 45)))
    tIn.value = 0
    return
  }
  tIn.value += dt
  if (tIn.value > SPIN + FLY + HOLD) { placed.value += 1; tIn.value = 0 }
}, () => { if (props.step === 0) { placed.value = 0; tIn.value = 0 } })
watch(() => props.step, (s, o) => { if (s === 0 && o > 0) { placed.value = 0; tIn.value = 0 } })
const done = computed(() => !active.value || placed.value >= N)
const shown = computed(() => (done.value ? N : placed.value))

const cur = computed(() => (props.step === 0 && !done.value ? placed.value : -1))
const ease = (u: number) => 1 - (1 - u) ** 3
const needle = computed(() => {
  if (cur.value < 0) return land[Math.max(0, shown.value - 1)]
  const u = Math.min(1, tIn.value / SPIN)
  return land[cur.value] - (1 - ease(u)) * 4 * Math.PI
})
const curK = computed(() => (cur.value >= 0 && tIn.value >= SPIN ? d.truth[cur.value] : -1))
const flying = computed(() => {
  if (curK.value < 0) return null
  const u = ease(Math.min(1, (tIn.value - SPIN) / FLY))
  const [x, y] = d.pts[cur.value]
  const a = needle.value
  const x0 = CX + RW * 0.55 * Math.sin(a); const y0 = CY - RW * 0.55 * Math.cos(a)
  return { x: x0 + (sx(x) - x0) * u, y: y0 + (sy(y) - y0) * u - Math.sin(Math.PI * u) * 60 }
})
const observe = computed(() => props.step >= 2)
const ellipses = T.mu.map((mu, k) => ellipsePath(mu, T.cov[k], 2, sx, sy))
const sub = ['₁', '₂', '₃']
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="A spinning wheel with three weighted slices picks a component, then a point is drawn from that component's Gaussian">
    <g :style="{ opacity: observe ? 0.25 : 1, transition: 'opacity 0.6s' }">
      <path v-for="(_, k) in T.w" :key="`s${k}`" :d="slice(k)" :style="{ fill: color(k), fillOpacity: curK === k ? 0.85 : 0.35, stroke: '#0b1020', strokeWidth: 2, transition: 'fill-opacity 0.25s' }" />
      <text v-for="(w, k) in T.w" :key="`w${k}`" :x="CX + RW * 0.62 * Math.sin((starts[k] + w / 2) * 2 * Math.PI)" :y="CY - RW * 0.62 * Math.cos((starts[k] + w / 2) * 2 * Math.PI) + 5" text-anchor="middle" :style="{ fill: '#0b1020', fontSize: '13px', fontWeight: 700 }">π{{ sub[k] }}={{ w.toFixed(2) }}</text>
      <g :transform="`rotate(${(needle * 180 / Math.PI).toFixed(1)}, ${CX}, ${CY})`">
        <path :d="`M${CX - 5},${CY}L${CX},${CY - RW - 8}L${CX + 5},${CY}Z`" :style="{ fill: '#f8fafc' }" />
      </g>
      <circle :cx="CX" :cy="CY" r="8" :style="{ fill: '#f8fafc', stroke: '#0b1020', strokeWidth: 2 }" />
      <text :x="CX" :y="CY + RW + 32" text-anchor="middle" :style="{ fill: curK >= 0 ? color(curK) : '#94a3b8', fontSize: '15px', fontWeight: 700 }">
        {{ curK >= 0 ? `1. pick k = ${curK + 1}` : (step === 0 ? '1. spin: pick k with prob. πₖ' : `${shown} points drawn`) }}
      </text>
      <text :x="CX" :y="CY + RW + 54" text-anchor="middle" :style="{ fill: curK >= 0 ? color(curK) : '#94a3b8', fontSize: '14px' }">
        {{ curK >= 0 ? `2. draw x ~ N(μ${sub[curK]}, Σ${sub[curK]})` : (step === 0 ? '2. draw x from that Gaussian' : '') }}
      </text>
    </g>
    <path v-for="(e, k) in ellipses" :key="`e${k}`" :d="e" :style="{ fill: color(k), fillOpacity: 0.05, stroke: color(k), strokeDasharray: '5 4', strokeWidth: 1.4, opacity: observe ? 0 : 0.8, transition: 'opacity 0.6s' }" />
    <circle
      v-for="i in shown" :key="i" :cx="sx(d.pts[i - 1][0])" :cy="sy(d.pts[i - 1][1])" r="2.7" class="pt"
      :style="{ fill: observe ? '#94a3b8' : color(d.truth[i - 1]), fillOpacity: 0.85 }"
    />
    <circle v-if="flying" :cx="flying.x" :cy="flying.y" r="6" :style="{ fill: color(curK), stroke: '#fff', strokeWidth: 2 }" />
    <text v-if="observe" x="525" y="22" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '15px', fontWeight: 700 }">What we observe: no k, no ellipses</text>
  </svg>
</template>

<style scoped>
.pt { transition: fill 0.6s ease; }
</style>
