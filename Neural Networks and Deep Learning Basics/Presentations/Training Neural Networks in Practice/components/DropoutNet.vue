<script setup lang="ts">
// Dropout (p = 0.5) on a small network. In training mode a new random half of each hidden layer is switched
// off every mini-batch (every 0.9 s here), and the survivors are scaled by 1/(1 − p) = 2 (inverted dropout).
// step ≥ 2: evaluation mode: every unit on, no scaling. Seeded, so print shows a fixed frame.
import { computed, ref } from 'vue'
import { C, rng, useLoop } from '../utils/plot'

const props = defineProps<{ step: number }>()
const W = 440; const H = 300
const LAYERS = [
  { x: 50, n: 4, hidden: false },
  { x: 175, n: 6, hidden: true },
  { x: 300, n: 6, hidden: true },
  { x: 400, n: 1, hidden: false },
]
const y = (n: number, i: number) => H / 2 + (i - (n - 1) / 2) * 42
const evalMode = computed(() => props.step >= 2)
const tick = ref(0)
let acc = 0
useLoop((dt) => { acc += dt; if (acc > 0.9) { acc = 0; tick.value++ } })
const dropped = computed(() => {
  const R = rng(31 + tick.value * 13)
  return LAYERS.map(L => Array.from({ length: L.n }, () => !evalMode.value && L.hidden && R.u() < 0.5))
})
const off = (l: number, i: number) => dropped.value[l][i]
</script>

<template>
  <div>
    <div class="flex justify-between items-center text-sm mb-1">
      <b class="text-amber-300">Dropout, p = 0.5</b>
      <code class="px-2 rounded" :style="{ background: evalMode ? 'rgba(45,212,191,0.2)' : 'rgba(251,191,36,0.2)', color: evalMode ? C.teal : C.amber }">{{ evalMode ? 'model.eval()' : 'model.train()' }}</code>
    </div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="A network with random hidden units switched off during training, and all units on during evaluation">
      <template v-for="(L, l) in LAYERS.slice(0, -1)" :key="`e${l}`">
        <template v-for="i in L.n" :key="`e${l}-${i}`">
          <line
            v-for="j in LAYERS[l + 1].n" :key="`e${l}-${i}-${j}`"
            :x1="L.x" :y1="y(L.n, i - 1)" :x2="LAYERS[l + 1].x" :y2="y(LAYERS[l + 1].n, j - 1)"
            :style="{ stroke: C.muted, strokeWidth: 1, strokeOpacity: off(l, i - 1) || off(l + 1, j - 1) ? 0.05 : 0.35, transition: 'stroke-opacity .3s' }"
          />
        </template>
      </template>
      <template v-for="(L, l) in LAYERS" :key="`n${l}`">
        <g v-for="i in L.n" :key="`n${l}-${i}`">
          <circle :cx="L.x" :cy="y(L.n, i - 1)" r="14"
                  :style="{ fill: off(l, i - 1) ? C.bg : (L.hidden ? 'rgba(251,191,36,0.25)' : 'rgba(96,165,250,0.25)'), stroke: off(l, i - 1) ? C.dim : (L.hidden ? C.amber : C.blue), strokeWidth: 2, transition: 'all .3s' }" />
          <text v-if="off(l, i - 1)" :x="L.x" :y="y(L.n, i - 1) + 5" text-anchor="middle" style="font-size: 15px; font-weight: 700" :style="{ fill: C.red }">✕</text>
          <text v-else-if="L.hidden && !evalMode" :x="L.x" :y="y(L.n, i - 1) + 4" text-anchor="middle" style="font-size: 10px; font-weight: 700" :style="{ fill: C.text }">×2</text>
        </g>
      </template>
    </svg>
    <div class="text-xs opacity-80 text-center">{{ evalMode ? 'Evaluation: every unit on, no scaling.' : 'Training: a new random half switched off every mini-batch; survivors ×2.' }}</div>
  </div>
</template>
