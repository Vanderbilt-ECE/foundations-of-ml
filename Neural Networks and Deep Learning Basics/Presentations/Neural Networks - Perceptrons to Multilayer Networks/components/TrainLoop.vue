<script setup lang="ts">
// The training loop as a cycle: forward → loss → backward → update, over and over.
// A marker travels round the loop; each time it passes "update" the loss (right) takes one step down.
// Print mode shows the loop with the marker at "backward" and a loss curve already partly drawn.
import { computed, ref } from 'vue'
import { C, pathOf, useLoop } from '../utils/plot'

const STAGES = [
  { name: 'Forward', sub: 'predict ŷ', col: C.teal },
  { name: 'Loss', sub: 'how wrong?', col: C.red },
  { name: 'Backward', sub: 'blame each weight', col: C.amber },
  { name: 'Update', sub: 'nudge downhill', col: C.violet },
]
const lossAt = (t: number) => 0.12 + 2.2 * Math.exp(-t / 7) + 0.05 * Math.sin(t * 2.3)
const PER_STAGE = 0.75 // seconds
const pos = ref(2.4) // position around the loop, in stages
const iters = ref(14)
useLoop((dt) => {
  pos.value += dt / PER_STAGE
  if (pos.value >= 4) { pos.value -= 4; iters.value = iters.value >= 40 ? 0 : iters.value + 1 }
}, () => { pos.value = 0; iters.value = 0 })

const W = 380; const H = 350; const cx = 190; const cy = 172; const R = 122
const ang = (s: number) => -Math.PI / 2 + s * Math.PI / 2
const at = (s: number) => [cx + R * Math.cos(ang(s)), cy + R * Math.sin(ang(s))]
const cur = computed(() => Math.floor(pos.value) % 4)
const marker = computed(() => at(pos.value))

const LW = 300; const LH = 220
const lx = (t: number) => 36 + t / 40 * (LW - 46)
const ly = (l: number) => LH - 28 - l / 2.5 * (LH - 44)
const curve = computed(() => pathOf(Array.from({ length: iters.value + 1 }, (_, t) => [lx(t), ly(lossAt(t))])))
</script>

<template>
  <div class="grid grid-cols-[1.1fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 320px" role="img" aria-label="The training loop: forward pass, loss, backward pass, update, repeated">
      <circle :cx="cx" :cy="cy" :r="R" :style="{ fill: 'none', stroke: C.grid, strokeWidth: 2, strokeDasharray: '4 6' }" />
      <g v-for="(s, k) in STAGES" :key="k">
        <circle :cx="at(k)[0]" :cy="at(k)[1]" :r="k === cur ? 34 : 30" :style="{ fill: '#0f172a', stroke: s.col, strokeWidth: k === cur ? 3.5 : 2, transition: 'all 0.25s' }" />
        <circle :cx="at(k)[0]" :cy="at(k)[1]" :r="44" :style="{ fill: s.col, fillOpacity: k === cur ? 0.16 : 0, transition: 'all 0.25s' }" />
        <text :x="at(k)[0]" :y="at(k)[1] + 5" text-anchor="middle" :style="{ fill: s.col, fontSize: '13px', fontWeight: 700 }">{{ s.name }}</text>
      </g>
      <circle :cx="marker[0]" :cy="marker[1]" r="7" :style="{ fill: C.text }" />
      <text :x="cx" :y="cy - 4" text-anchor="middle" :style="{ fill: C.text, fontSize: '15px' }">{{ STAGES[cur].sub }}</text>
      <text :x="cx" :y="cy + 18" text-anchor="middle" :style="{ fill: C.muted, fontSize: '12px', fontFamily: 'monospace' }">iteration {{ iters }}</text>
    </svg>
    <svg :viewBox="`0 0 ${LW} ${LH}`" class="w-full" role="img" aria-label="Loss dropping with each iteration">
      <line x1="36" :x2="LW - 10" :y1="ly(0)" :y2="ly(0)" :style="{ stroke: C.grid }" />
      <line x1="36" x2="36" :y1="ly(0)" :y2="ly(2.5)" :style="{ stroke: C.grid }" />
      <text x="30" :y="ly(2.5) + 4" text-anchor="end" :style="{ fill: C.muted, fontSize: '11px' }">high</text>
      <text x="30" :y="ly(0) + 4" text-anchor="end" :style="{ fill: C.muted, fontSize: '11px' }">0</text>
      <text :x="(LW + 36) / 2" :y="LH - 6" text-anchor="middle" :style="{ fill: C.muted, fontSize: '12px' }">iteration</text>
      <text x="44" y="16" :style="{ fill: C.red, fontSize: '13px' }">loss</text>
      <path :d="curve" :style="{ fill: 'none', stroke: C.red, strokeWidth: 2.5 }" />
      <circle :cx="lx(iters)" :cy="ly(lossAt(iters))" r="4.5" :style="{ fill: C.red }" />
    </svg>
  </div>
</template>
