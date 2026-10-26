<script setup lang="ts">
// Why the map uses a Student-t kernel. Both curves are similarity against distance, scaled to 1 at distance 0:
// the Gaussian exp(−d²) of the original space and the Student-t (1 + d²)⁻¹ of the map.
// Drag the amber marker along the distance axis (a pair's distance in the original space). To get the same
// similarity in the map, the t-curve needs a larger distance: moderately far pairs are pushed further apart,
// which opens up room in 2D (the crowding problem) and separates clusters.
import { computed, ref } from 'vue'
import { toLocal } from '../utils/plot'

const W = 520; const H = 280; const L = 44; const B = 34
const XM = 4
const px = (d: number) => L + d / XM * (W - L - 14)
const py = (s: number) => H - B - s * (H - B - 16)
const g = (d: number) => Math.exp(-d * d)
const t = (d: number) => 1 / (1 + d * d)
const curve = (f: (d: number) => number) => Array.from({ length: 161 }, (_, i) => `${i ? 'L' : 'M'}${px(i * XM / 160).toFixed(1)},${py(f(i * XM / 160)).toFixed(1)}`).join('')
const dh = ref(1.2)
const s = computed(() => g(dh.value))
const dm = computed(() => Math.sqrt(Math.max(0, 1 / s.value - 1))) // solve 1/(1+d²) = s
const dragging = ref(false)
function moveTo(e: PointerEvent) {
  const [x] = toLocal(e, e.currentTarget as Element, W, H)
  dh.value = Math.max(0.05, Math.min(2.2, (x - L) / (W - L - 14) * XM))
}
function down(e: PointerEvent) {
  dragging.value = true
  ;(e.currentTarget as Element).setPointerCapture(e.pointerId)
  moveTo(e)
}
</script>

<template>
  <div>
    <svg
      :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 290px; cursor: ew-resize; touch-action: none" role="img"
      aria-label="Gaussian and Student-t similarity curves; the same similarity needs a larger distance under the t curve"
      @pointerdown="down" @pointermove="dragging && moveTo($event)" @pointerup="dragging = false" @pointercancel="dragging = false"
    >
      <line :x1="L" :x2="W - 10" :y1="H - B" :y2="H - B" :style="{ stroke: '#64748b' }" />
      <line :x1="L" :x2="L" y1="10" :y2="H - B" :style="{ stroke: '#64748b' }" />
      <text v-for="d in [0, 1, 2, 3, 4]" :key="d" :x="px(d)" :y="H - B + 16" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ d }}</text>
      <text :x="W - 12" :y="H - 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">distance</text>
      <text :x="L - 6" :y="py(1) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">1</text>
      <path :d="curve(g)" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 3 }" />
      <path :d="curve(t)" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 3 }" />
      <text :x="px(0.98)" :y="py(0.32)" text-anchor="end" :style="{ fill: '#5eead4', fontSize: '13px', fontWeight: 700 }">Gaussian (original space)</text>
      <text :x="px(2.2)" :y="py(t(2.2)) - 10" :style="{ fill: '#c4b5fd', fontSize: '13px', fontWeight: 700 }">Student-t (map)</text>
      <!-- matching construction -->
      <line :x1="px(dh)" :x2="px(dh)" :y1="H - B" :y2="py(s)" :style="{ stroke: '#fbbf24', strokeDasharray: '3 3' }" />
      <line :x1="px(dh)" :x2="px(Math.min(XM, dm))" :y1="py(s)" :y2="py(s)" :style="{ stroke: '#fbbf24', strokeWidth: 2 }" />
      <line :x1="px(Math.min(XM, dm))" :x2="px(Math.min(XM, dm))" :y1="py(s)" :y2="H - B" :style="{ stroke: '#fbbf24', strokeDasharray: '3 3' }" />
      <circle :cx="px(dh)" :cy="py(s)" r="5" :style="{ fill: '#2dd4bf' }" />
      <circle :cx="px(Math.min(XM, dm))" :cy="py(s)" r="5" :style="{ fill: '#a78bfa' }" />
      <circle :cx="px(dh)" :cy="H - B" r="9" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2 }" />
    </svg>
    <div class="font-mono text-sm text-center">
      original distance <span class="text-teal-300">{{ dh.toFixed(2) }}</span> → same similarity at map distance <span class="text-violet-300">{{ dm.toFixed(2) }}</span>
      <span class="text-amber-300">(× {{ (dm / dh).toFixed(2) }})</span>
    </div>
  </div>
</template>
