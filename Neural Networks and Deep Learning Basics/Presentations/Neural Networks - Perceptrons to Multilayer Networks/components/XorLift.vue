<script setup lang="ts">
// XOR lifted into 3D by one hidden neuron, h = AND(x₁, x₂) (= x₁·x₂ on 0/1 inputs).
//   step 0: the four points on the floor (h = 0 for all), viewed in 3D
//   step 1: (1,1) rises to h = 1; the other three stay put
//   step 2: the plane x₁ + x₂ − 2h = 0.5 appears: teal points sit below it, violet above
// Same move as the SVM deck's ring lift (z = x₁² + x₂²), but here the new coordinate is a neuron.
import { computed } from 'vue'
import { C, pathOf, useTween } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })

const W = 440; const H = 275
// simple 3D → 2D projection: rotate about the vertical axis, then tilt toward the viewer
const TH = -0.62; const PH = 0.42; const SC = 175; const CX = W / 2; const CY = 200
function P(x: number, y: number, z: number) {
  const u = (x - 0.5) * Math.cos(TH) - (y - 0.5) * Math.sin(TH)
  const v = (x - 0.5) * Math.sin(TH) + (y - 0.5) * Math.cos(TH)
  return [CX + SC * u, CY - SC * (z * Math.cos(PH) + v * Math.sin(PH))]
}

const lift = useTween(() => (props.step >= 1 ? 1 : 0), 900)
const showPlane = computed(() => props.step >= 2)

const PTS = [
  { x: 0, y: 0, cls: 0 },
  { x: 0, y: 1, cls: 1 },
  { x: 1, y: 0, cls: 1 },
  { x: 1, y: 1, cls: 0 },
]
const hOf = (p: typeof PTS[number]) => (p.x === 1 && p.y === 1 ? lift.value : 0)
const planeH = (x: number, y: number) => (x + y - 0.5) / 2
// draw the points under the plane first, so the plane sits visually on top of them
const below = computed(() => PTS.filter(p => !showPlane.value || hOf(p) < planeH(p.x, p.y)))
const above = computed(() => PTS.filter(p => showPlane.value && hOf(p) >= planeH(p.x, p.y)))

const floor = pathOf([P(0, 0, 0), P(1, 0, 0), P(1, 1, 0), P(0, 1, 0)])
const plane = pathOf([P(0, 0, planeH(0, 0)), P(1, 0, planeH(1, 0)), P(1, 1, planeH(1, 1)), P(0, 1, planeH(0, 1))])
const ax = { h: [P(0, 0, 0), P(0, 0, 1.15)] }
const x1Lbl = P(0.5, -0.12, 0); const x2Lbl = P(-0.12, 0.5, 0)
const planeLbl = P(0, 0, planeH(0, 0))
const lbl = (p: typeof PTS[number]) => `(${p.x},${p.y})`
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="The four XOR points in 3D with a third coordinate h = AND(x1, x2); the point (1,1) rises to h = 1 and a tilted plane separates the two classes">
    <!-- floor and axes -->
    <path :d="`${floor}Z`" :style="{ fill: C.grid, fillOpacity: 0.25, stroke: C.grid, strokeWidth: 1.5 }" />
    <line v-for="(a, k) in ax" :key="k" :x1="a[0][0]" :y1="a[0][1]" :x2="a[1][0]" :y2="a[1][1]" :style="{ stroke: C.muted, strokeWidth: 1.5 }" />
    <text :x="x1Lbl[0]" :y="x1Lbl[1] + 6" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.muted }">x₁</text>
    <text :x="x2Lbl[0]" :y="x2Lbl[1] + 4" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.muted }">x₂</text>
    <text :x="ax.h[1][0] - 4" :y="ax.h[1][1] - 6" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.amber }">h = AND(x₁, x₂)</text>

    <!-- vertical guide from (1,1) on the floor up to its lifted position -->
    <line :x1="P(1, 1, 0)[0]" :y1="P(1, 1, 0)[1]" :x2="P(1, 1, lift)[0]" :y2="P(1, 1, lift)[1]" :style="{ stroke: C.amber, strokeDasharray: '4 4', strokeWidth: 1.5, opacity: lift > 0.02 ? 0.8 : 0 }" />

    <!-- each point's vertical gap to the plane: teal points sit under it, violet points over it -->
    <line v-for="p in PTS" :key="`g${p.x}${p.y}`" :x1="P(p.x, p.y, hOf(p))[0]" :y1="P(p.x, p.y, hOf(p))[1]" :x2="P(p.x, p.y, planeH(p.x, p.y))[0]" :y2="P(p.x, p.y, planeH(p.x, p.y))[1]" :style="{ stroke: p.cls ? C.teal : C.violet, strokeWidth: 2, strokeDasharray: '3 3', opacity: showPlane ? 0.9 : 0, transition: 'opacity .6s' }" />

    <!-- points below the plane -->
    <g v-for="p in below" :key="`b${p.x}${p.y}`">
      <circle v-if="p.cls" :cx="P(p.x, p.y, hOf(p))[0]" :cy="P(p.x, p.y, hOf(p))[1]" r="8" :style="{ fill: C.teal }" />
      <rect v-else :x="P(p.x, p.y, hOf(p))[0] - 7" :y="P(p.x, p.y, hOf(p))[1] - 7" width="14" height="14" :style="{ fill: C.violet }" />
    </g>

    <!-- the separating plane -->
    <path :d="`${plane}Z`" :style="{ fill: C.amber, fillOpacity: showPlane ? 0.22 : 0, stroke: C.amber, strokeOpacity: showPlane ? 0.9 : 0, strokeWidth: 1.5, transition: 'fill-opacity .6s, stroke-opacity .6s' }" />

    <!-- points above the plane -->
    <g v-for="p in above" :key="`a${p.x}${p.y}`">
      <circle v-if="p.cls" :cx="P(p.x, p.y, hOf(p))[0]" :cy="P(p.x, p.y, hOf(p))[1]" r="8" :style="{ fill: C.teal }" />
      <rect v-else :x="P(p.x, p.y, hOf(p))[0] - 7" :y="P(p.x, p.y, hOf(p))[1] - 7" width="14" height="14" :style="{ fill: C.violet }" />
    </g>

    <!-- point labels -->
    <text v-for="p in PTS" :key="`l${p.x}${p.y}`" :x="P(p.x, p.y, hOf(p))[0] + (p.x === 0 && p.y === 1 ? -14 : 14)" :y="P(p.x, p.y, hOf(p))[1] + 5" :text-anchor="p.x === 0 && p.y === 1 ? 'end' : 'start'" style="font-size: 12px" :style="{ fill: C.text }">{{ lbl(p) }}<tspan v-if="p.x === 1 && p.y === 1 && lift > 0.5" :style="{ fill: C.amber }"> h = 1</tspan></text>

    <text v-if="showPlane" :x="planeLbl[0]" :y="planeLbl[1] + 20" text-anchor="middle" style="font-size: 12px" :style="{ fill: C.amber }">x₁ + x₂ − 2h = 0.5</text>
  </svg>
</template>
