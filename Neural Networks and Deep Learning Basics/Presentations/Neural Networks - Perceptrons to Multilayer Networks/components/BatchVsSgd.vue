<script setup lang="ts">
// Full-batch vs. stochastic gradient descent on the same perceptron loss, same data, same starting line.
//   Full batch: every misclassified point's gradient is summed into ONE step per pass through the data:
//     w ← w + η_B · Σ_{wrong i} yᵢxᵢ        (η_B = 0.05, smaller because it adds up ~12 points' worth)
//   Stochastic: visit points one at a time; each wrong point triggers its own step: w ← w + η·y·x  (η = 0.5)
// Both are driven by a shared clock: "points examined". One pass = 40 points = one batch step.
// step k (0-4) = after k passes. Each click sweeps the clock forward one pass, so the SGD panel takes its
// many small steps while the batch panel takes its single big one at the end of the pass.
// Red outline = point is wrong right now (it counts in L). Amber ring (SGD) = the point behind the latest step.
import { computed, ref, watch } from 'vue'
import { halfPlane, lineInBox } from '../utils/geom'
import { C, pathOf, useActive, useLoop, useTween } from '../utils/plot'
import { separable } from '../utils/rng'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const pts = separable()
const N = pts.length
const PASSES = 4
const box = [-1.15, 1.15, -1.15, 1.15]
const W0 = [-0.3, 0.8]; const B0 = 0.2
const ETA_SGD = 0.5; const ETA_BATCH = 0.05
const score = (w: number[], b: number, p: { x: number[] }) => w[0] * p.x[0] + w[1] * p.x[1] + b
const isWrong = (w: number[], b: number, p: { x: number[], y: number }) => p.y * score(w, b, p) <= 0
const lossOf = (w: number[], b: number) => pts.reduce((s, p) => s + Math.max(0, -p.y * score(w, b, p)), 0)

type S = { w: number[], b: number, L: number, pt: number, steps: number }
// batch[k] = state after k passes (k full-batch steps)
const batch: S[] = [{ w: W0, b: B0, L: lossOf(W0, B0), pt: -1, steps: 0 }]
for (let k = 1; k <= PASSES; k++) {
  const { w, b } = batch[k - 1]
  const wrong = pts.filter(p => isWrong(w, b, p))
  const nw = [w[0] + ETA_BATCH * wrong.reduce((s, p) => s + p.y * p.x[0], 0), w[1] + ETA_BATCH * wrong.reduce((s, p) => s + p.y * p.x[1], 0)]
  const nb = b + ETA_BATCH * wrong.reduce((s, p) => s + p.y, 0)
  batch.push({ w: nw, b: nb, L: lossOf(nw, nb), pt: -1, steps: k })
}
// sgd[v] = state after v points examined
const sgd: S[] = [batch[0]]
for (let v = 1; v <= PASSES * N; v++) {
  const s = sgd[v - 1]; const i = (v - 1) % N; const p = pts[i]
  if (isWrong(s.w, s.b, p)) {
    const w = [s.w[0] + ETA_SGD * p.y * p.x[0], s.w[1] + ETA_SGD * p.y * p.x[1]]; const b = s.b + ETA_SGD * p.y
    sgd.push({ w, b, L: lossOf(w, b), pt: i, steps: s.steps + 1 })
  }
  else sgd.push(s)
}
const sgdDoneAt = sgd.findIndex(s => s.L < 1e-9)

// ---- the shared clock (points examined) ----
const { isPrintMode } = useActive()
const target = computed(() => (isPrintMode.value ? PASSES : Math.max(0, Math.min(PASSES, props.step))) * N)
const clock = ref(target.value)
const SPEED = N / 3.2 // one pass in 3.2 s
watch(target, (t) => { if (t < clock.value) clock.value = t }) // going back a click: jump
useLoop((dt) => { if (clock.value < target.value) clock.value = Math.min(target.value, clock.value + SPEED * dt) })
const t = computed(() => (isPrintMode.value ? PASSES * N : Math.floor(clock.value)))

const bCur = computed(() => batch[Math.floor(t.value / N)])
const sCur = computed(() => sgd[t.value])
const bLine = useTween(() => [bCur.value.w[0], bCur.value.w[1], bCur.value.b], 900)
const sLine = useTween(() => [sCur.value.w[0], sCur.value.w[1], sCur.value.b], 250)

// ---- panels ----
const S = 260; const pad = 10
const sx = (x: number) => pad + (x - box[0]) / (box[1] - box[0]) * (S - 2 * pad)
const sy = (y: number) => S - pad - (y - box[2]) / (box[3] - box[2]) * (S - 2 * pad)
const toS = (P: number[][]) => P.map(p => [sx(p[0]), sy(p[1])])
function geo(l: number[]) {
  const w = [l[0], l[1]]
  return { pos: pathOf(toS(halfPlane(w, l[2], box, 1))), neg: pathOf(toS(halfPlane(w, l[2], box, -1))), seg: toS(lineInBox(w, l[2], box)) }
}
const panels = computed(() => [
  { key: 'b', g: geo(bLine.value), cur: bCur.value, ring: -1 },
  { key: 's', g: geo(sLine.value), cur: sCur.value, ring: sCur.value.pt },
])

// ---- loss vs points examined ----
const LW = 320; const LH = 230; const L0 = 34; const LB = 34; const YMAX = 5
const lx = (v: number) => L0 + v / (PASSES * N) * (LW - L0 - 12)
const ly = (L: number) => LH - LB - Math.min(L, YMAX) / YMAX * (LH - LB - 16)
// step-function curves, drawn up to the clock
function stairs(Lat: (v: number) => number) {
  const P: number[][] = [[lx(0), ly(Lat(0))]]
  for (let v = 1; v <= t.value; v++) {
    if (Lat(v) !== Lat(v - 1)) { P.push([lx(v), ly(Lat(v - 1))]); P.push([lx(v), ly(Lat(v))]) }
  }
  P.push([lx(t.value), ly(Lat(t.value))])
  return pathOf(P)
}
const bCurve = computed(() => stairs(v => batch[Math.floor(v / N)].L))
const sCurve = computed(() => stairs(v => sgd[v].L))
</script>

<template>
  <div class="grid grid-cols-[1fr_1fr_1.25fr] gap-4 items-start text-left">
    <div v-for="(P, j) in panels" :key="P.key">
      <div class="text-base font-bold" :class="j ? 'text-red-300' : 'text-blue-300'">{{ j ? 'Stochastic' : 'Full batch' }}</div>
      <div class="font-mono text-xs opacity-85 h-9 leading-snug">
        <template v-if="j">w ← w + η·yᵢxᵢ<br>each wrong point gets its own step</template>
        <template v-else>w ← w + η·Σ<sub>wrong</sub> yᵢxᵢ<br>all wrong points, one step per pass</template>
      </div>
      <svg :viewBox="`0 0 ${S} ${S}`" class="w-full mt-1" style="max-height: 250px" role="img" :aria-label="j ? 'Stochastic gradient descent: the line moves after each wrong point' : 'Full-batch gradient descent: the line moves once per pass, using every wrong point'">
        <path :d="`${P.g.pos}Z`" :style="{ fill: C.teal, fillOpacity: 0.13 }" />
        <path :d="`${P.g.neg}Z`" :style="{ fill: C.violet, fillOpacity: 0.13 }" />
        <line v-if="P.g.seg.length === 2" :x1="P.g.seg[0][0]" :y1="P.g.seg[0][1]" :x2="P.g.seg[1][0]" :y2="P.g.seg[1][1]" :style="{ stroke: C.text, strokeWidth: 2.5 }" />
        <g v-for="(d, i) in pts" :key="i">
          <circle v-if="isWrong(P.cur.w, P.cur.b, d)" :cx="sx(d.x[0])" :cy="sy(d.x[1])" r="8" :style="{ fill: 'none', stroke: C.red, strokeWidth: 2 }" />
          <circle v-if="i === P.ring" :cx="sx(d.x[0])" :cy="sy(d.x[1])" r="12" :style="{ fill: 'none', stroke: C.amber, strokeWidth: 2.5 }" />
          <circle v-if="d.y > 0" :cx="sx(d.x[0])" :cy="sy(d.x[1])" r="4.5" :style="{ fill: C.teal }" />
          <rect v-else :x="sx(d.x[0]) - 4" :y="sy(d.x[1]) - 4" width="8" height="8" :style="{ fill: C.violet }" />
        </g>
      </svg>
      <div class="font-mono text-sm mt-1 flex justify-between">
        <span>steps: {{ P.cur.steps }}</span>
        <span>wrong: <span :class="P.cur.L < 1e-9 ? 'text-teal-300' : 'text-red-300'">{{ pts.filter(p => isWrong(P.cur.w, P.cur.b, p)).length }}</span></span>
        <span>L = {{ P.cur.L.toFixed(2) }}</span>
      </div>
    </div>
    <div>
      <div class="text-base font-bold">Same loss, two paths</div>
      <div class="text-xs opacity-85 h-9 leading-snug">L(w, b) after every point examined.<br>One pass = all {{ N }} points.</div>
      <svg :viewBox="`0 0 ${LW} ${LH}`" class="w-full mt-1" role="img" aria-label="Loss against points examined for full-batch and stochastic gradient descent">
        <line v-for="k in PASSES + 1" :key="`p${k}`" :x1="lx((k - 1) * N)" :x2="lx((k - 1) * N)" :y1="ly(0)" :y2="ly(YMAX)" :style="{ stroke: C.grid, strokeDasharray: k > 1 ? '3 4' : '' }" />
        <line :x1="L0" :x2="LW - 12" :y1="ly(0)" :y2="ly(0)" :style="{ stroke: C.grid }" />
        <text v-for="v in [0, YMAX]" :key="`y${v}`" :x="L0 - 6" :y="ly(v) + 4" text-anchor="end" :style="{ fill: C.muted, fontSize: '11px' }">{{ v }}</text>
        <text v-for="k in PASSES" :key="`l${k}`" :x="lx((k - 0.5) * N)" :y="ly(0) + 15" text-anchor="middle" :style="{ fill: C.muted, fontSize: '11px' }">pass {{ k }}</text>
        <text :x="(LW + L0) / 2" :y="LH - 4" text-anchor="middle" :style="{ fill: C.muted, fontSize: '11px' }">points examined</text>
        <path :d="bCurve" :style="{ fill: 'none', stroke: C.blue, strokeWidth: 2.4 }" />
        <path :d="sCurve" :style="{ fill: 'none', stroke: C.red, strokeWidth: 2.4 }" />
        <circle :cx="lx(t)" :cy="ly(bCur.L)" r="4.5" :style="{ fill: C.blue }" />
        <circle :cx="lx(t)" :cy="ly(sCur.L)" r="4.5" :style="{ fill: C.red }" />
        <text v-if="t >= sgdDoneAt" :x="lx(sgdDoneAt) + 3" :y="ly(0) - 20" :style="{ fill: C.red, fontSize: '11px' }">L = 0</text>
        <text v-if="bCur.L < 1e-9" :x="lx(PASSES * N) - 2" :y="ly(0) - 20" text-anchor="end" :style="{ fill: C.blue, fontSize: '11px' }">L = 0</text>
      </svg>
      <div class="flex gap-4 text-xs mt-1">
        <span><span class="inline-block w-3 h-3 rounded-full align-middle mr-1" style="border: 2px solid #f87171" />wrong now (counts in L)</span>
        <span><span class="inline-block w-3 h-3 rounded-full align-middle mr-1" style="border: 2px solid #fbbf24" />drove SGD's last step</span>
      </div>
    </div>
  </div>
</template>
