<script setup lang="ts">
// Optimizers racing down the same narrow valley L = ½(w₁² + 50 w₂²) from the same start.
// Settings chosen and checked by simulation (see utils/quad.ts):
//   SGD η = 0.036 (just under the 2/50 = 0.04 stability limit) · momentum η = 0.012, β = 0.9 · Adam η = 0.15
// Balls advance one step every 0.12 s together, then the race restarts. Print shows the full paths.
import { computed, ref } from 'vue'
import { contours, loss, run, type Opt } from '../utils/quad'
import { C, pathOf, useActive, useLoop } from '../utils/plot'

const props = defineProps<{ methods: Opt[] }>()
const { isPrintMode } = useActive()
const B = { a: 1, b: 50 }; const W0 = [-2.6, 0.9]; const STEPS = 60
const CFG: Record<Opt, { lr: number, color: string, name: string }> = {
  sgd: { lr: 0.036, color: C.muted, name: 'gradient descent' },
  momentum: { lr: 0.012, color: C.amber, name: 'momentum (β = 0.9)' },
  adam: { lr: 0.15, color: C.teal, name: 'Adam' },
}
const runs = computed(() => props.methods.map((m) => {
  const path = run(B, m, W0, STEPS, CFG[m].lr)
  const L = path.map(w => loss(B, w))
  return { m, ...CFG[m], path, toOnePct: L.findIndex(v => v < 0.01 * L[0]) }
}))

const W = 880; const H = 270
const ux = 190; const uy = 118
const map = (x: number, y: number) => [40 + (x + 2.85) * ux, H / 2 - y * uy]
const rings = contours(B, [0.03, 0.15, 0.4, 0.9, 1.7, 3, 5, 8, 12, 18, 26], map, 160)

const t = ref(0)
useLoop((dt) => { t.value = (t.value + dt / 0.12) % (STEPS + 15) }, () => { t.value = 0 })
const k = computed(() => (isPrintMode.value ? STEPS : Math.min(STEPS, Math.floor(t.value))))
</script>

<template>
  <div class="mt-2">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`${methods.join(', ')} racing down a narrow loss valley`">
      <defs><clipPath :id="`race-${methods.length}`"><rect x="0" y="0" :width="W" :height="H" rx="10" /></clipPath></defs>
      <rect x="0" y="0" :width="W" :height="H" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: C.grid }" />
      <g :clip-path="`url(#race-${methods.length})`">
        <path v-for="(r, i) in rings" :key="i" :d="r" :style="{ fill: 'none', stroke: C.blue, strokeOpacity: 0.2 + 0.03 * i, strokeWidth: 1.2 }" />
        <g v-for="r in runs" :key="r.m">
          <path :d="pathOf(r.path.slice(0, k + 1).map(w => map(w[0], w[1])))" :style="{ fill: 'none', stroke: r.color, strokeWidth: r.m === 'sgd' ? 1.8 : 2.6, strokeLinejoin: 'round', strokeOpacity: 0.9 }" />
          <circle :cx="map(r.path[k][0], r.path[k][1])[0]" :cy="map(r.path[k][0], r.path[k][1])[1]" r="7" :style="{ fill: r.color, stroke: C.bg, strokeWidth: 1.5 }" />
        </g>
      </g>
      <circle :cx="map(0, 0)[0]" :cy="map(0, 0)[1]" r="6" :style="{ fill: 'none', stroke: C.text, strokeWidth: 1.8 }" />
      <text :x="map(0, 0)[0] + 10" :y="map(0, 0)[1] - 10" style="font-size: 13px" :style="{ fill: C.text }">minimum</text>
      <!-- legend -->
      <g v-for="(r, i) in runs" :key="`lg${r.m}`">
        <circle :cx="W - 300" :cy="22 + i * 22" r="6" :style="{ fill: r.color }" />
        <text :x="W - 288" :y="27 + i * 22" style="font-size: 14px" :style="{ fill: r.color }">{{ r.name }}: 1% loss in <tspan style="font-weight: 700">{{ r.toOnePct }}</tspan> steps</text>
      </g>
      <text x="14" :y="H - 12" style="font-size: 13px" :style="{ fill: C.muted }">step {{ k }}</text>
    </svg>
  </div>
</template>
