<script setup lang="ts">
// A stylized biological neuron. `step` (1–5) highlights one part at a time, matching the
// mapping rows on the slide: 1 dendrites, 2 synapses, 3 cell body, 4 axon hillock (threshold), 5 axon.
// step 0 or ≥ 6 shows everything in its own color. Static, so it prints as-is.
import { computed } from 'vue'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const W = 440; const H = 240
const SX = 165; const SY = 120; const SR = 32

// dendrites: soma → tip, with a side branch; a synapse (bouton from another neuron) sits at each tip
const DENDS = [
  { tip: [40, 38], br: [70, 22] },
  { tip: [22, 112], br: [44, 86] },
  { tip: [34, 196], br: [72, 218] },
  { tip: [92, 40], br: null },
  { tip: [96, 206], br: null },
]
const dPath = (d: typeof DENDS[number]) => {
  const [tx, ty] = d.tip
  const mx = (SX + tx) / 2 + (ty - SY) * 0.08; const my = (SY + ty) / 2
  let p = `M${SX},${SY} Q${mx},${my} ${tx},${ty}`
  if (d.br) p += ` M${mx},${my} L${d.br[0]},${d.br[1]}`
  return p
}
const HILLOCK = SX + SR + 10
const AX_END = 365
const MYELIN = [210, 250, 290, 330]
const TERMS = [[420, 82], [428, 120], [420, 158]]

const on = (k: number) => props.step === 0 || props.step >= 6 || props.step === k
const col = (k: number, c: string) => (on(k) ? c : C.dim)
const op = (k: number) => (on(k) ? 1 : 0.35)
const fire = computed(() => props.step >= 4)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="A biological neuron: dendrites with synapses on the left, a cell body, an axon hillock, and an axon with terminals on the right">
    <!-- 1 · dendrites -->
    <g :style="{ opacity: op(1), transition: 'opacity .4s' }">
      <path v-for="(d, i) in DENDS" :key="i" :d="dPath(d)" :style="{ fill: 'none', stroke: col(1, C.blue), strokeWidth: 3.5, strokeLinecap: 'round' }" />
    </g>

    <!-- 2 · synapses: boutons from other neurons touching the dendrite tips -->
    <g :style="{ opacity: op(2), transition: 'opacity .4s' }">
      <g v-for="(d, i) in DENDS" :key="i">
        <line :x1="d.tip[0] - 14" :y1="d.tip[1] - 6" :x2="d.tip[0] - 6" :y2="d.tip[1] - 2" :style="{ stroke: col(2, C.teal), strokeWidth: 2 }" />
        <circle :cx="d.tip[0] - 4" :cy="d.tip[1] - 1" :r="i === 1 ? 7 : i === 3 ? 3.5 : 5" :style="{ fill: col(2, C.teal) }" />
      </g>
    </g>

    <!-- 5 · axon, myelin, terminals -->
    <g :style="{ opacity: op(5), transition: 'opacity .4s' }">
      <line :x1="HILLOCK" :y1="SY" :x2="AX_END" :y2="SY" :style="{ stroke: col(5, C.violet), strokeWidth: 3.5 }" />
      <rect v-for="m in MYELIN" :key="m" :x="m" :y="SY - 7" width="30" height="14" rx="7" :style="{ fill: col(5, C.violet), fillOpacity: 0.35, stroke: col(5, C.violet), strokeWidth: 1.5 }" />
      <g v-for="(t, i) in TERMS" :key="i">
        <path :d="`M${AX_END},${SY} Q${AX_END + 25},${SY} ${t[0] - 6},${t[1]}`" :style="{ fill: 'none', stroke: col(5, C.violet), strokeWidth: 2.5 }" />
        <circle :cx="t[0]" :cy="t[1]" r="5.5" :style="{ fill: col(5, C.violet) }" />
      </g>
    </g>

    <!-- 4 · axon hillock: where the threshold decision is made -->
    <g :style="{ opacity: op(4), transition: 'opacity .4s' }">
      <path :d="`M${SX + SR - 6},${SY - 14} L${HILLOCK + 4},${SY - 4} L${HILLOCK + 4},${SY + 4} L${SX + SR - 6},${SY + 14} Z`" :style="{ fill: col(4, C.amber) }" />
    </g>

    <!-- 3 · cell body -->
    <g :style="{ opacity: op(3), transition: 'opacity .4s' }">
      <circle :cx="SX" :cy="SY" :r="SR" :style="{ fill: col(3, C.amber), fillOpacity: 0.22, stroke: col(3, C.amber), strokeWidth: 3 }" />
      <circle :cx="SX - 4" :cy="SY - 2" r="9" :style="{ fill: col(3, C.amber), fillOpacity: 0.5 }" />
    </g>

    <!-- the spike: all-or-nothing pulse leaving the hillock -->
    <g v-if="fire" :style="{ opacity: op(5) === 1 || props.step === 4 ? 1 : 0.35 }">
      <path :d="`M${AX_END - 70},${SY - 22} l8,0 l5,-14 l5,28 l5,-14 l8,0`" :style="{ fill: 'none', stroke: C.amber, strokeWidth: 2.2 }" />
    </g>

    <!-- labels -->
    <g style="font-size: 12px">
      <text x="6" y="14" style="font-size: 12px" :style="{ fill: col(1, C.blue), opacity: op(1) }">dendrites</text>
      <text x="6" y="236" style="font-size: 12px" :style="{ fill: col(2, C.teal), opacity: op(2) }">synapses</text>
      <text :x="SX" :y="SY + SR + 18" text-anchor="middle" style="font-size: 12px" :style="{ fill: col(3, C.amber), opacity: op(3) }">cell body</text>
      <text :x="HILLOCK + 4" :y="SY - 26" text-anchor="middle" style="font-size: 12px" :style="{ fill: col(4, C.amber), opacity: op(4) }">hillock</text>
      <text :x="270" :y="SY + 30" text-anchor="middle" style="font-size: 12px" :style="{ fill: col(5, C.violet), opacity: op(5) }">axon</text>
      <text :x="W - 4" :y="SY + 64" text-anchor="end" style="font-size: 12px" :style="{ fill: col(5, C.violet), opacity: op(5) }">to other neurons</text>
    </g>
  </svg>
</template>
