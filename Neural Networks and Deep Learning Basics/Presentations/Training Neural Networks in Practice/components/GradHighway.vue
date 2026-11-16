<script setup lang="ts">
// Measured gradient size at the first Linear layer of each of the 10 blocks, at initialization, one batch
// (scripts/make_data.py, section 5). Log scale, stored to 4 significant figures.
//   step 1: plain 22-layer network · step ≥ 2: residual 22-layer network beside it
import { computed } from 'vue'
import D from '../data/depth.json'
import { C } from '../utils/plot'

const props = defineProps<{ step: number }>()
const W = 600; const H = 330; const L = 64; const B = 52; const T = 16
const N = D.plain_20.grad.length
const LO = -9; const HI = 1
const bx = (i: number) => L + (i + 0.5) / N * (W - L - 12)
const by = (v: number) => H - B - (Math.log10(Math.max(v, 10 ** LO)) - LO) / (HI - LO) * (H - B - T)
const plain = computed(() => props.step >= 1)
const res = computed(() => props.step >= 2)
const sci = (v: number) => v.toExponential(0).replace('e-', '×10⁻').replace(/\d+$/, d => [...d].map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹'[+c]).join(''))
const tick = (e: number) => (e === 0 ? '1' : e === 1 ? '10' : `10${'⁻' + '⁰¹²³⁴⁵⁶⁷⁸⁹'[-e]}`)
</script>

<template>
  <div class="grid grid-cols-[1.5fr_1fr] gap-6 items-center mt-2 text-left">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Gradient size per block: vanishing to zero in the first blocks of the plain network, of order 1 in every block of the residual network">
      <g v-for="e in [1, 0, -2, -4, -6, -8]" :key="e">
        <line :x1="L" :x2="W - 12" :y1="by(10 ** e)" :y2="by(10 ** e)" :style="{ stroke: C.grid, strokeOpacity: 0.6 }" />
        <text :x="L - 8" :y="by(10 ** e) + 4" text-anchor="end" style="font-size: 12px" :style="{ fill: C.muted }">{{ tick(e) }}</text>
      </g>
      <g v-for="i in N" :key="i">
        <rect :x="bx(i - 1) - 19" :y="by(D.plain_20.grad[i - 1])" width="18" :height="Math.max(2, by(10 ** LO) - by(D.plain_20.grad[i - 1]))" rx="2"
              :style="{ fill: C.red, opacity: plain ? 0.9 : 0, transition: `opacity .4s ${(N - i) * 0.07}s` }" />
        <rect :x="bx(i - 1) + 1" :y="by(D.res_20.grad[i - 1])" width="18" :height="by(10 ** LO) - by(D.res_20.grad[i - 1])" rx="2"
              :style="{ fill: C.teal, opacity: res ? 0.9 : 0, transition: `opacity .4s ${(N - i) * 0.07}s` }" />
        <text :x="bx(i - 1)" :y="H - B + 17" text-anchor="middle" style="font-size: 12px" :style="{ fill: C.muted }">{{ i }}</text>
      </g>
      <text :x="(L + W) / 2" :y="H - 12" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.muted }">block (1 = nearest the input, 10 = nearest the output)</text>
      <text :transform="`translate(16 ${(T + H - B) / 2}) rotate(-90)`" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.muted }">gradient size (log)</text>
    </svg>
    <div class="flex flex-col gap-3 text-sm">
      <div class="reveal" :class="{ shown: step >= 1 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-2>
        <b class="text-red-300">Plain:</b> {{ D.plain_20.grad.at(-1)!.toFixed(2) }} at the last block, <b>{{ sci(D.plain_20.grad[0]) }}</b> at the first: about {{ Math.round(D.plain_20.grad.at(-1)! / D.plain_20.grad[0] / 1e6) }} million times smaller. The early layers get almost no signal.
      </div>
      <div class="reveal" :class="{ shown: step >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
        <b class="text-teal-300">Residual:</b> between {{ Math.min(...D.res_20.grad).toFixed(1) }} and {{ Math.max(...D.res_20.grad).toFixed(1) }} in every block.
      </div>
      <div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2 class="text-center">
        <div class="text-lg font-serif italic my-1">y = x + F(x) &nbsp;⟹&nbsp; ∂y/∂x = <b class="text-amber-300 not-italic">1</b> + ∂F/∂x</div>
        <div>The <b class="text-amber-300">1</b> is a direct path back through every block.</div>
      </div>
    </div>
  </div>
</template>
