<script setup lang="ts">
// Mahalanobis vs Euclidean distance. Click (or drag) anywhere on the plot to move the amber probe there;
// the panel shows its Euclidean and Mahalanobis distances from the mean and its density.
// A and B: two fixed points at the same Euclidean distance (1.5), along the long and the short axis.
import { computed, ref } from 'vue'
import { ellipsePath, maha2 } from '../utils/gmm'

const W = 420; const H = 300; const U = 36
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const th = Math.PI / 6; const L1 = 3; const L2 = 0.3
const v1 = [Math.cos(th), Math.sin(th)]; const v2 = [-Math.sin(th), Math.cos(th)]
const S = [
  [L1 * v1[0] ** 2 + L2 * v2[0] ** 2, L1 * v1[0] * v1[1] + L2 * v2[0] * v2[1]],
  [L1 * v1[0] * v1[1] + L2 * v2[0] * v2[1], L1 * v1[1] ** 2 + L2 * v2[1] ** 2],
]
const RE = 1.5
const A = [RE * v1[0], RE * v1[1]]; const B = [RE * v2[0], RE * v2[1]]
const dA = Math.sqrt(maha2(A, [0, 0], S)); const dB = Math.sqrt(maha2(B, [0, 0], S))
const P = ref([RE * Math.cos(1.2), RE * Math.sin(1.2)])
const dE = computed(() => Math.hypot(P.value[0], P.value[1]))
const dM = computed(() => Math.sqrt(maha2(P.value, [0, 0], S)))

// Pointer position -> data coordinates. The slide is CSS-scaled and the SVG may be letterboxed by max-height
// (preserveAspectRatio meet, centered), so map through the bounding box rather than offsetX.
const dragging = ref(false)
function moveTo(e: PointerEvent) {
  const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
  const k = Math.min(r.width / W, r.height / H)
  const x = (e.clientX - r.left - (r.width - W * k) / 2) / k
  const y = (e.clientY - r.top - (r.height - H * k) / 2) / k
  P.value = [(x - W / 2) / U, (H / 2 - y) / U]
}
function down(e: PointerEvent) {
  dragging.value = true
  ;(e.currentTarget as SVGSVGElement).setPointerCapture(e.pointerId)
  moveTo(e)
}
const rel = computed(() => Math.exp(-0.5 * dM.value ** 2)) // density relative to the peak
</script>

<template>
  <div class="grid grid-cols-[1.3fr_1fr] gap-5 items-center">
    <svg
      :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 320px; cursor: crosshair; touch-action: none" role="img"
      aria-label="Tilted Gaussian contours and a dashed circle of fixed Euclidean distance; click to place a probe point"
      @pointerdown="down" @pointermove="dragging && moveTo($event)" @pointerup="dragging = false" @pointercancel="dragging = false"
    >
      <path v-for="s in [3, 2, 1]" :key="s" :d="ellipsePath([0, 0], S, s, sx, sy)" :style="{ fill: '#2dd4bf', fillOpacity: 0.07 + 0.05 * (3 - s), stroke: '#2dd4bf', strokeOpacity: 0.7, strokeWidth: 1.3 }" />
      <text v-for="s in [1, 2, 3]" :key="`t${s}`" :x="sx(s * Math.sqrt(L1) * v1[0]) + 4" :y="sy(s * Math.sqrt(L1) * v1[1]) - 4" :style="{ fill: '#5eead4', fontSize: '11px' }">d_M={{ s }}</text>
      <circle :cx="W / 2" :cy="H / 2" :r="RE * U" :style="{ fill: 'none', stroke: '#e2e8f0', strokeOpacity: 0.6, strokeWidth: 1.5, strokeDasharray: '3 5' }" />
      <circle :cx="W / 2" :cy="H / 2" r="4" :style="{ fill: '#e2e8f0' }" />
      <g v-for="(p, i) in [A, B]" :key="`ab${i}`">
        <line :x1="W / 2" :y1="H / 2" :x2="sx(p[0])" :y2="sy(p[1])" :style="{ stroke: i ? '#f87171' : '#2dd4bf', strokeWidth: 2 }" />
        <circle :cx="sx(p[0])" :cy="sy(p[1])" r="6" :style="{ fill: i ? '#f87171' : '#2dd4bf', stroke: '#0b1020', strokeWidth: 2 }" />
        <text :x="sx(p[0]) + (i ? -26 : 10)" :y="sy(p[1]) + (i ? -8 : 16)" :style="{ fill: i ? '#fca5a5' : '#5eead4', fontSize: '15px', fontWeight: 700 }">{{ i ? 'B' : 'A' }}</text>
      </g>
      <line :x1="W / 2" :y1="H / 2" :x2="sx(P[0])" :y2="sy(P[1])" :style="{ stroke: '#fbbf24', strokeWidth: 1.5, strokeDasharray: '4 3' }" />
      <circle :cx="sx(P[0])" :cy="sy(P[1])" r="7" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2 }" />
    </svg>
    <div class="text-left space-y-3 text-sm">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono">
        <div>Euclidean <span class="float-right">{{ dE.toFixed(2) }}</span></div>
        <div class="text-amber-300">Mahalanobis <span class="float-right">{{ dM.toFixed(2) }}</span></div>
        <div class="mt-2 text-xs opacity-70 font-sans">density / peak</div>
        <div class="h-3 rounded-full overflow-hidden mt-1" style="background: rgba(148,163,184,0.18)">
          <div class="h-full rounded-full" :style="{ width: `${(100 * rel).toFixed(1)}%`, background: '#fbbf24' }" />
        </div>
        <div class="mt-2 text-xs opacity-60 font-sans">Click or drag on the plot to move the probe.</div>
      </div>
      <div class="font-mono px-1">
        <div class="text-teal-300">A: d_M = {{ dA.toFixed(2) }} · density {{ (100 * Math.exp(-0.5 * dA ** 2)).toFixed(0) }}% of peak</div>
        <div class="text-red-300">B: d_M = {{ dB.toFixed(2) }} · density {{ (100 * Math.exp(-0.5 * dB ** 2)).toFixed(1) }}% of peak</div>
      </div>
    </div>
  </div>
</template>
