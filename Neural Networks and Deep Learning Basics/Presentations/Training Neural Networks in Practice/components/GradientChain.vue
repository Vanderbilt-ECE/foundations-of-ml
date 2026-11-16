<script setup lang="ts">
// Left: the sigmoid and its slope (max 0.25 at z = 0).
// Right: how much gradient survives after passing back through n layers, best case:
//   sigmoid 0.25ⁿ (every unit at its steepest point) vs. ReLU 1ⁿ (every unit active). Log scale.
//   step 0: left only · step 1: sigmoid bars · step ≥ 2: ReLU bars beside them
import { computed } from 'vue'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const ZS = Array.from({ length: 121 }, (_, i) => -6 + i * 0.1)
const sig = (z: number) => 1 / (1 + Math.exp(-z))
const curves = [
  { x: ZS, y: ZS.map(sig), color: C.blue, width: 3 },
  { x: ZS, y: ZS.map(z => sig(z) * (1 - sig(z))), color: C.amber, width: 3 },
]

// bar chart, drawn by hand: n = 1..10 layers, log10 scale from 1e-7 to 1
const W = 470; const H = 300; const L = 60; const B = 44; const T = 30
const N = 10
const bx = (n: number) => L + (n - 0.5) / N * (W - L - 12)
const by = (v: number) => H - B - (Math.log10(v) + 7) / 7 * (H - B - T)
const showSig = computed(() => props.step >= 1)
const showRelu = computed(() => props.step >= 2)
const fmt = (v: number) => (v >= 0.01 ? v.toFixed(2) : v.toExponential(0).replace('e-', '×10⁻').replace(/(\d)$/, d => '⁰¹²³⁴⁵⁶⁷⁸⁹'[+d]))
</script>

<template>
  <div class="grid grid-cols-[1fr_1.15fr] gap-6 items-center mt-2">
    <div>
      <LineChart
        :series="curves" :width="440" :height="300" :y-range="[0, 1.05]" :x-range="[-6, 6]"
        :x-ticks="[-6, -4, -2, 0, 2, 4, 6]" :y-ticks="[0, 0.25, 0.5, 0.75, 1]" x-label="z" :font="13"
        :legend="[{ color: C.blue, text: 'sigmoid σ(z)' }, { color: C.amber, text: 'its slope σ′(z)' }]" legend-at="tl"
        :points="[{ x: 0, y: 0.25, color: C.amber, label: 'max 0.25', dy: -12 }]"
      />
      <div class="text-sm opacity-80 text-center">Flat for |z| &gt; 4: the sigmoid <b>saturates</b>.</div>
    </div>

    <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Gradient remaining after n layers: 0.25 to the n for sigmoid, falling to about one in a million after 10 layers; 1 for ReLU">
      <text :x="L" y="10" style="font-size: 14px; font-weight: 700" :style="{ fill: C.text }">Gradient left after n layers (best case)</text>
      <g v-for="e in [0, -2, -4, -6]" :key="e">
        <line :x1="L" :x2="W - 12" :y1="by(10 ** e)" :y2="by(10 ** e)" :style="{ stroke: C.grid, strokeOpacity: 0.7 }" />
        <text :x="L - 6" :y="by(10 ** e) + 4" text-anchor="end" style="font-size: 12px" :style="{ fill: C.muted }">{{ e === 0 ? '1' : `10${'⁻' + '⁰¹²³⁴⁵⁶⁷⁸⁹'[-e]}` }}</text>
      </g>
      <g v-for="n in N" :key="n">
        <rect :x="bx(n) - 15" :y="by(0.25 ** n)" width="14" :height="by(1e-7) - by(0.25 ** n)" rx="2"
              :style="{ fill: C.blue, opacity: showSig ? 0.9 : 0, transition: `opacity .4s ${n * 0.06}s` }" />
        <rect :x="bx(n) + 1" :y="by(1)" width="14" :height="by(1e-7) - by(1)" rx="2"
              :style="{ fill: C.teal, opacity: showRelu ? 0.9 : 0, transition: `opacity .4s ${n * 0.06}s` }" />
        <text :x="bx(n)" :y="H - B + 16" text-anchor="middle" style="font-size: 12px" :style="{ fill: C.muted }">{{ n }}</text>
      </g>
      <text :x="(L + W) / 2" :y="H - 8" text-anchor="middle" style="font-size: 12px" :style="{ fill: C.muted }">layers the gradient has passed back through</text>
    </svg>
    <div class="flex justify-center gap-6 text-sm mt-1">
      <span class="reveal" :class="{ shown: showSig }"><span class="inline-block w-3 h-3 rounded-sm align-middle mr-1" :style="{ background: C.blue }" /><b class="text-blue-300">sigmoid</b>: 0.25ⁿ, about 10⁻⁶ after 10</span>
      <span class="reveal" :class="{ shown: showRelu }"><span class="inline-block w-3 h-3 rounded-sm align-middle mr-1" :style="{ background: C.teal }" /><b class="text-teal-300">ReLU</b>: slope 1, nothing lost</span>
    </div>
    </div>
  </div>
</template>
