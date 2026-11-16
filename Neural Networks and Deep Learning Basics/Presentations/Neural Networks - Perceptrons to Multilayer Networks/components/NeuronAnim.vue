<script setup lang="ts">
// One perceptron, computed in front of the class.
// step 0: three inputs · 1: each input travels along its edge and is multiplied by its weight
// 2: the products (plus the bias) are summed into z · 3: z goes through the step function and the output fires
import { computed } from 'vue'
import { C, clamp, useTween } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const ph = useTween(() => props.step, 900)

const x = [0.8, 0.3, 0.6]
const w = [1.5, -2.0, 1.0]
const b = -0.5
const prod = x.map((v, i) => v * w[i])
const z = prod.reduce((s, v) => s + v, 0) + b
const out = z > 0 ? 1 : 0

const W = 680; const H = 290
const inX = 70; const sumX = 340; const sumY = 140; const stepX = 470; const outX = 625
const inY = (i: number) => 60 + i * 80

const travel = computed(() => clamp(ph.value)) // inputs slide along the edges
const sumIn = computed(() => clamp(ph.value - 1)) // products merge into the sum
const fire = computed(() => clamp(ph.value - 2)) // through the step function to the output

// step-function mini plot
const PX = stepX; const PY = sumY; const PW = 90; const PH = 60
const zx = (v: number) => PX + (v + 2) / 4 * PW
const zy = (v: number) => PY + PH - 10 - v * (PH - 20)
const f2 = (v: number) => v.toFixed(2)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 300px" role="img" aria-label="A perceptron: three inputs are multiplied by weights, summed with a bias, and passed through a step function">
    <!-- edges with weights -->
    <g v-for="i in 3" :key="`e${i}`">
      <line :x1="inX + 22" :y1="inY(i - 1)" :x2="sumX - 32" :y2="sumY" :style="{ stroke: w[i - 1] >= 0 ? C.teal : C.violet, strokeWidth: 1.5 + Math.abs(w[i - 1]) * 1.4, strokeOpacity: 0.55 }" />
      <text :x="inX + 22 + (sumX - 54 - inX) * 0.1" :y="inY(i - 1) + (sumY - inY(i - 1)) * 0.16 - 12" text-anchor="start" :style="{ fill: w[i - 1] >= 0 ? C.teal : C.violet, fontSize: '15px', fontFamily: 'monospace' }">w{{ i }}={{ w[i - 1].toFixed(1) }}</text>
      <!-- traveling value -->
      <g v-if="travel > 0 && sumIn < 1" :style="{ opacity: 1 - sumIn }">
        <circle :cx="inX + 22 + (sumX - 32 - inX - 22) * travel * 0.62" :cy="inY(i - 1) + (sumY - inY(i - 1)) * travel * 0.62" r="15" :style="{ fill: '#0f172a', stroke: C.amber, strokeWidth: 1.5 }" />
        <text :x="inX + 22 + (sumX - 32 - inX - 22) * travel * 0.62" :y="inY(i - 1) + (sumY - inY(i - 1)) * travel * 0.62 + 4" text-anchor="middle" :style="{ fill: C.amber, fontSize: '10px', fontFamily: 'monospace' }">{{ (x[i - 1] * (1 + (w[i - 1] - 1) * travel)).toFixed(2) }}</text>
      </g>
    </g>
    <!-- inputs -->
    <g v-for="i in 3" :key="`x${i}`">
      <circle :cx="inX" :cy="inY(i - 1)" r="22" :style="{ fill: '#0f172a', stroke: C.blue, strokeWidth: 2.2 }" />
      <text :x="inX" :y="inY(i - 1) + 5" text-anchor="middle" :style="{ fill: C.text, fontSize: '14px', fontFamily: 'monospace' }">{{ x[i - 1] }}</text>
      <text :x="inX - 32" :y="inY(i - 1) + 5" text-anchor="end" :style="{ fill: C.blue, fontSize: '14px' }">x{{ i }}</text>
    </g>
    <!-- sum node -->
    <circle :cx="sumX" :cy="sumY" r="32" :style="{ fill: '#0f172a', stroke: C.teal, strokeWidth: 2.5 }" />
    <circle :cx="sumX" :cy="sumY" :r="32 + 10 * sumIn * (1 - fire)" :style="{ fill: C.teal, fillOpacity: 0.18 * sumIn * (1 - fire) }" />
    <text :x="sumX" :y="sumY + (sumIn > 0 ? -4 : 9)" text-anchor="middle" :style="{ fill: C.text, fontSize: sumIn > 0 ? '16px' : '26px' }">Σ</text>
    <text v-if="sumIn > 0" :x="sumX" :y="sumY + 16" text-anchor="middle" :style="{ fill: C.amber, fontSize: '14px', fontFamily: 'monospace', opacity: sumIn }">z={{ (z * sumIn).toFixed(2) }}</text>
    <text :x="sumX" :y="sumY + 58" text-anchor="middle" :style="{ fill: C.muted, fontSize: '13px', fontFamily: 'monospace' }">bias b = {{ b }}</text>
    <!-- the arithmetic -->
    <text :x="sumX" :y="H - 18" text-anchor="middle" :style="{ fill: C.text, fontSize: '15px', fontFamily: 'monospace', opacity: sumIn }">
      z = {{ prod.map(f2).join(' + ').replace('+ -', '− ') }} − 0.50 = {{ z.toFixed(2) }}
    </text>
    <!-- step function -->
    <line :x1="sumX + 32" :y1="sumY" :x2="PX - 6" :y2="sumY" :style="{ stroke: C.dim, strokeWidth: 1.5 }" />
    <rect :x="PX - 6" :y="PY - 6" :width="PW + 12" :height="PH + 12" rx="8" :style="{ fill: '#0f172a', stroke: C.dim }" />
    <line :x1="PX" :x2="PX + PW" :y1="zy(0)" :y2="zy(0)" :style="{ stroke: C.grid }" />
    <path :d="`M${zx(-2)},${zy(0)}L${zx(0)},${zy(0)}L${zx(0)},${zy(1)}L${zx(2)},${zy(1)}`" :style="{ fill: 'none', stroke: C.amber, strokeWidth: 2.5 }" />
    <circle v-if="fire > 0" :cx="zx(z)" :cy="zy(out)" r="5" :style="{ fill: C.amber, opacity: fire }" />
    <text :x="PX + PW / 2" :y="PY - 14" text-anchor="middle" :style="{ fill: C.muted, fontSize: '12px' }">step: z &gt; 0 ?</text>
    <!-- output -->
    <line :x1="PX + PW + 6" :y1="sumY" :x2="outX - 24" :y2="sumY" :style="{ stroke: C.dim, strokeWidth: 1.5 }" />
    <circle :cx="outX" :cy="sumY" :r="24 + 14 * fire * (1 - Math.abs(ph - 3) * 0)" :style="{ fill: C.amber, fillOpacity: 0.22 * fire }" />
    <circle :cx="outX" :cy="sumY" r="24" :style="{ fill: '#0f172a', stroke: C.amber, strokeWidth: 2.5 }" />
    <text :x="outX" :y="sumY + 7" text-anchor="middle" :style="{ fill: C.amber, fontSize: '22px', fontWeight: 700, opacity: fire }">{{ out }}</text>
    <text :x="outX" :y="sumY + 48" text-anchor="middle" :style="{ fill: C.muted, fontSize: '13px' }">output ŷ</text>
  </svg>
</template>
