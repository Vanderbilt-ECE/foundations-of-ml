<script setup lang="ts">
// The perceptron learning rule as stochastic gradient descent.
// Loss: L(w, b) = Σᵢ max(0, −yᵢ(w·xᵢ + b)), i.e. how far each misclassified point sits on the wrong side.
// Points are visited in order. A correctly classified point has zero gradient and is skipped; a misclassified
// point has gradient (−y·x, −y), so the SGD step w ← w + η·y·x moves the line toward it.
// Left: the data and the current line (the point behind the latest step gets a steady red ring).
// Right: the total loss L after every gradient step.
//
// Two modes:
//   step given (click-driven): the run is precomputed; step k shows the state after k gradient steps,
//     and the line glides to each new position. The slide's `clicks:` should equal the step count (9 for 'sep').
//   step omitted (auto): steps on a timer and restarts after a pause (used for XOR, which never finishes).
// Print mode shows the final state in either mode.
import { computed, reactive } from 'vue'
import { halfPlane, lineInBox } from '../utils/geom'
import { C, pathOf, useActive, useLoop, useTween } from '../utils/plot'
import { separable, XOR } from '../utils/rng'

const props = withDefaults(defineProps<{ data?: 'sep' | 'xor', step?: number, clicks?: number, finishAt?: number }>(), { data: 'sep', step: undefined, clicks: 0, finishAt: undefined })
const isXor = props.data === 'xor'
const clickMode = props.step !== undefined
const pts = isXor ? XOR : separable()
const box = isXor ? [-0.45, 1.45, -0.45, 1.45] : [-1.15, 1.15, -1.15, 1.15]
const ETA = 0.5
const W0 = isXor ? [0.4, -0.3] : [-0.3, 0.8]; const B0 = isXor ? 0.1 : 0.2
const MAX_STEPS = 20 // XOR never finishes, so cap it
const lossOf = (w: number[], b: number) => pts.reduce((s, p) => s + Math.max(0, -p.y * (w[0] * p.x[0] + w[1] * p.x[1] + b)), 0)

// The whole run, precomputed: traj[k] = state after k gradient steps (traj[0] = start).
// pt = index of the misclassified point that triggered step k.
type State = { w: number[], b: number, L: number, pt: number, pass: number }
const traj: State[] = [{ w: W0, b: B0, L: lossOf(W0, B0), pt: -1, pass: 1 }]
{
  let w = [...W0]; let b = B0; let idx = 0; let pass = 1; let wrongThisPass = 0
  while (traj.length <= MAX_STEPS) {
    const p = pts[idx]
    if (p.y * (w[0] * p.x[0] + w[1] * p.x[1] + b) <= 0) {
      w = [w[0] + ETA * p.y * p.x[0], w[1] + ETA * p.y * p.x[1]]; b += ETA * p.y
      traj.push({ w: [...w], b, L: lossOf(w, b), pt: idx, pass })
      wrongThisPass++
    }
    idx++
    if (idx === pts.length) {
      if (wrongThisPass === 0) break // a full pass with no steps: done
      idx = 0; pass++; wrongThisPass = 0
    }
  }
}
const stepCount = traj.length - 1

const { isPrintMode } = useActive()

// ---- auto mode (XOR): walk through the precomputed run on a timer ----
// Without finishAt it loops forever. With finishAt = N, the run is split across the slide's clicks:
// playback pauses at a checkpoint before each click, and on click N it plays the remaining steps
// quickly and stops on the final state (no restart). Going back a click rewinds to that checkpoint.
const finishing = props.finishAt !== undefined
const cap = computed(() => {
  if (!finishing) return stepCount
  const c = Math.max(0, Math.min(props.finishAt!, props.clicks))
  return Math.round(stepCount * (c + 1) / (props.finishAt! + 1))
})
const auto = reactive({ k: 0, timer: 1 })
useLoop((dt) => {
  if (clickMode) return
  if (auto.k > cap.value) auto.k = cap.value
  auto.timer -= dt
  if (auto.timer > 0) return
  if (auto.k >= stepCount) {
    if (finishing) return
    auto.k = 0; auto.timer = 1.2; return
  }
  if (auto.k >= cap.value) return
  auto.k++
  const last = finishing && props.clicks >= props.finishAt!
  auto.timer = last ? 0.3 : auto.k >= stepCount ? 3 : 1.1
}, () => { auto.k = 0; auto.timer = 1 })

const k = computed(() => {
  if (isPrintMode.value) return stepCount
  return clickMode ? Math.max(0, Math.min(stepCount, props.step!)) : auto.k
})
const cur = computed(() => traj[k.value])
const wb = useTween(() => [cur.value.w[0], cur.value.w[1], cur.value.b], 700)

const S = 300; const pad = 14
const sx = (x: number) => pad + (x - box[0]) / (box[1] - box[0]) * (S - 2 * pad)
const sy = (y: number) => S - pad - (y - box[2]) / (box[3] - box[2]) * (S - 2 * pad)
const toS = (P: number[][]) => P.map(p => [sx(p[0]), sy(p[1])])
const wv = computed(() => [wb.value[0], wb.value[1]])
const pos = computed(() => pathOf(toS(halfPlane(wv.value, wb.value[2], box, 1))))
const neg = computed(() => pathOf(toS(halfPlane(wv.value, wb.value[2], box, -1))))
const seg = computed(() => toS(lineInBox(wv.value, wb.value[2], box)))

// loss-after-each-step chart
const LW = 300; const LH = 190; const L0 = 44; const B = 34
const Y_MAX = isXor ? 2 : 5
const lx = (i: number) => L0 + 8 + i * ((LW - L0 - 18) / stepCount)
const ly = (v: number) => LH - B - Math.min(v, Y_MAX) / Y_MAX * (LH - B - 14)
const shown = computed(() => traj.slice(0, k.value + 1))
const curve = computed(() => pathOf(shown.value.map((s, i) => [lx(i), ly(s.L)])))
const atZero = computed(() => cur.value.L < 1e-9)
</script>

<template>
  <div class="grid grid-cols-[1fr_1.05fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${S} ${S}`" class="w-full" style="max-height: 320px" role="img" :aria-label="isXor ? 'Gradient descent on XOR: the line never settles' : 'Gradient descent moving a line, one step per click, until every point is on the correct side'">
      <path :d="`${pos}Z`" :style="{ fill: C.teal, fillOpacity: 0.13 }" />
      <path :d="`${neg}Z`" :style="{ fill: C.violet, fillOpacity: 0.13 }" />
      <line v-if="seg.length === 2" :x1="seg[0][0]" :y1="seg[0][1]" :x2="seg[1][0]" :y2="seg[1][1]" :style="{ stroke: C.text, strokeWidth: 2.5 }" />
      <g v-for="(d, i) in pts" :key="i">
        <circle v-if="i === cur.pt" :cx="sx(d.x[0])" :cy="sy(d.x[1])" :r="isXor ? 18 : 10" :style="{ fill: 'none', stroke: C.red, strokeWidth: 2.5 }" />
        <circle v-if="d.y > 0" :cx="sx(d.x[0])" :cy="sy(d.x[1])" :r="isXor ? 11 : 5" :style="{ fill: C.teal }" />
        <rect v-else :x="sx(d.x[0]) - (isXor ? 10 : 4.5)" :y="sy(d.x[1]) - (isXor ? 10 : 4.5)" :width="isXor ? 20 : 9" :height="isXor ? 20 : 9" :style="{ fill: C.violet }" />
        <text v-if="isXor" :x="sx(d.x[0])" :y="sy(d.x[1]) + (d.x[1] ? -22 : 32)" text-anchor="middle" :style="{ fill: C.muted, fontSize: '12px', fontFamily: 'monospace' }">({{ d.x[0] }},{{ d.x[1] }})</text>
      </g>
    </svg>
    <div class="text-left">
      <div class="flex justify-between items-baseline">
        <span class="text-sm opacity-80">loss after each step</span>
        <span class="font-mono text-xl whitespace-nowrap" :class="atZero ? 'text-teal-300' : 'text-red-300'">L = {{ cur.L.toFixed(2) }}</span>
      </div>
      <svg :viewBox="`0 0 ${LW} ${LH}`" class="w-full" role="img" aria-label="The perceptron loss after each gradient step">
        <line v-for="v in [0, Y_MAX / 2, Y_MAX]" :key="v" :x1="L0" :x2="LW - 6" :y1="ly(v)" :y2="ly(v)" :style="{ stroke: C.grid, strokeDasharray: v ? '3 4' : '' }" />
        <text v-for="v in [0, Y_MAX / 2, Y_MAX]" :key="`t${v}`" :x="L0 - 6" :y="ly(v) + 4" text-anchor="end" :style="{ fill: C.muted, fontSize: '11px' }">{{ v }}</text>
        <text :x="12" :y="(LH - B) / 2 + 4" text-anchor="middle" :transform="`rotate(-90 12 ${(LH - B) / 2 + 4})`" :style="{ fill: C.muted, fontSize: '11px' }">loss L(w, b)</text>
        <path :d="curve" :style="{ fill: 'none', stroke: C.red, strokeWidth: 2.2 }" />
        <circle v-for="(s, i) in shown" :key="i" :cx="lx(i)" :cy="ly(s.L)" :r="i === k ? 5.5 : 3.8" :style="{ fill: s.L < 1e-9 ? C.teal : C.red }" />
        <text :x="(LW + L0) / 2" :y="LH - 8" text-anchor="middle" :style="{ fill: C.muted, fontSize: '11px' }">gradient step</text>
      </svg>
      <div class="text-sm mt-1 h-12 leading-snug">
        <span v-if="k === 0" class="opacity-80">Start: the misclassified points add up to L = {{ traj[0].L.toFixed(2) }}.</span>
        <template v-else>
          <span class="font-mono text-red-300">step {{ k }}</span>
          <span class="opacity-85"> · pass {{ cur.pass }} · the ringed <span :class="pts[cur.pt].y > 0 ? 'text-teal-300' : 'text-violet-300'">{{ pts[cur.pt].y > 0 ? 'teal (y = +1)' : 'violet (y = −1)' }}</span> point was wrong, so w ← w + η·y·x</span>
        </template>
      </div>
      <div class="text-base h-6">
        <span v-if="atZero" class="text-teal-300">✓ L = 0: every point correct</span>
        <span v-else-if="isXor && k >= 8" class="text-red-300">L never reaches 0</span>
      </div>
    </div>
  </div>
</template>
