<script setup lang="ts">
// Responsibilities in 1D: components N(0, 1) and N(4, 1).
// Top: the weighted densities pi_k N(x | mu_k, sigma_k). Bottom: gamma_1(x) (teal) and gamma_2(x) = 1 - gamma_1 (amber),
// stacked to 1. Click or drag on the plot to move the probe; at each x, gamma is the teal share of the two heights above it.
//   step 0: probe at x = 0 · step 1: probe jumps to x = 1.5 (the worked example) · step 2: prior pi_1 = 0.8
// The probe stays draggable at every step.
import { computed, ref, watch } from 'vue'
import { useTween } from '../utils/clusters'
import { pdf1 } from '../utils/gmm'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const W = 600; const H = 330; const X0 = -3; const X1 = 7
const sx = (x: number) => 40 + (x - X0) / (X1 - X0) * (W - 60)
const TOP = { y0: 10, h: 150 }; const BOT = { y0: 200, h: 110 }
const ty = (v: number) => TOP.y0 + TOP.h - v / 0.34 * TOP.h
const by = (v: number) => BOT.y0 + BOT.h - v * BOT.h
const pi = useTween(() => (props.step >= 2 ? [0.8, 0.2] : [0.5, 0.5]), 900)

const x = ref(props.step >= 1 ? 1.5 : 0)
watch(() => props.step, (s, o) => { if (s >= 1 && o < 1) x.value = 1.5 })

// Pointer position -> x. The slide is CSS-scaled, so map through the bounding box (letterbox-safe).
const dragging = ref(false)
function moveTo(e: PointerEvent) {
  const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
  const k = Math.min(r.width / W, r.height / H)
  const px = (e.clientX - r.left - (r.width - W * k) / 2) / k
  x.value = Math.max(X0, Math.min(X1, X0 + (px - 40) / (W - 60) * (X1 - X0)))
}
function down(e: PointerEvent) {
  dragging.value = true
  ;(e.currentTarget as SVGSVGElement).setPointerCapture(e.pointerId)
  moveTo(e)
}

const xs = Array.from({ length: 201 }, (_, i) => X0 + (X1 - X0) * i / 200)
const f1 = (v: number) => pi.value[0] * pdf1(v, 0, 1)
const f2 = (v: number) => pi.value[1] * pdf1(v, 4, 1)
const g1 = (v: number) => f1(v) / (f1(v) + f2(v))
const line = (f: (v: number) => number, y: (v: number) => number) => xs.map((v, i) => `${i ? 'L' : 'M'}${sx(v).toFixed(1)},${y(f(v)).toFixed(1)}`).join('')
const area = (f: (v: number) => number, y: (v: number) => number, base: number) => `${line(f, y)}L${sx(X1)},${base}L${sx(X0)},${base}Z`
const c1 = computed(() => area(f1, ty, ty(0)))
const c2 = computed(() => area(f2, ty, ty(0)))
const gArea = computed(() => area(g1, by, by(0)))
const gLine = computed(() => line(g1, by))
const half = computed(() => 2 + Math.log(pi.value[0] / pi.value[1]) / 4) // where gamma_1 = 0.5
const r = computed(() => ({ a: f1(x.value), b: f2(x.value), g: g1(x.value) }))
</script>

<template>
  <div class="grid grid-cols-[1.6fr_1fr] gap-5 items-center">
    <svg
      :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="cursor: ew-resize; touch-action: none" role="img"
      aria-label="Two weighted bell curves and, below, the responsibility curve that switches from one component to the other between them; drag to move the probe"
      @pointerdown="down" @pointermove="dragging && moveTo($event)" @pointerup="dragging = false" @pointercancel="dragging = false"
    >
      <text x="4" :y="TOP.y0 + 12" :style="{ fill: '#94a3b8', fontSize: '12px' }">πₖ N(x | μₖ, σₖ)</text>
      <path :d="c1" :style="{ fill: '#2dd4bf', fillOpacity: 0.22, stroke: '#2dd4bf', strokeWidth: 2.4 }" />
      <path :d="c2" :style="{ fill: '#fbbf24', fillOpacity: 0.22, stroke: '#fbbf24', strokeWidth: 2.4 }" />
      <line :x1="sx(X0)" :x2="sx(X1)" :y1="ty(0)" :y2="ty(0)" :style="{ stroke: '#475569' }" />
      <rect :x="sx(X0)" :y="BOT.y0" :width="sx(X1) - sx(X0)" :height="BOT.h" :style="{ fill: '#fbbf24', fillOpacity: 0.35 }" />
      <path :d="gArea" :style="{ fill: '#2dd4bf', fillOpacity: 0.55 }" />
      <path :d="gLine" :style="{ fill: 'none', stroke: '#f8fafc', strokeWidth: 2 }" />
      <text x="4" :y="BOT.y0 - 8" :style="{ fill: '#94a3b8', fontSize: '12px' }">responsibilities γ₁ (teal) + γ₂ (amber) = 1</text>
      <line :x1="sx(half)" :x2="sx(half)" :y1="BOT.y0" :y2="BOT.y0 + BOT.h" :style="{ stroke: '#f8fafc', strokeDasharray: '3 4', strokeOpacity: 0.6 }" />
      <text :x="sx(half)" :y="BOT.y0 + BOT.h + 16" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '11px' }">50/50 at x = {{ half.toFixed(2) }}</text>
      <g v-for="t in [-2, 0, 2, 4, 6]" :key="t">
        <text :x="sx(t)" :y="ty(0) + 15" text-anchor="middle" :style="{ fill: '#64748b', fontSize: '11px' }">{{ t }}</text>
      </g>
      <line :x1="sx(x)" :x2="sx(x)" :y1="TOP.y0" :y2="BOT.y0 + BOT.h" :style="{ stroke: '#f8fafc', strokeWidth: 2 }" />
      <rect :x="sx(x) - 7" :y="TOP.y0 - 2" width="14" height="22" rx="4" :style="{ fill: '#f8fafc', stroke: '#0b1020', strokeWidth: 2 }" />
      <path :d="`M${sx(x) - 2},${TOP.y0 + 4}V${TOP.y0 + 14}M${sx(x) + 2},${TOP.y0 + 4}V${TOP.y0 + 14}`" :style="{ stroke: '#0b1020', strokeWidth: 1.4 }" />
      <circle :cx="sx(x)" :cy="ty(r.a)" r="5.5" :style="{ fill: '#2dd4bf', stroke: '#0b1020', strokeWidth: 2 }" />
      <circle :cx="sx(x)" :cy="ty(r.b)" r="5.5" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2 }" />
      <circle :cx="sx(x)" :cy="by(r.g)" r="6" :style="{ fill: '#f8fafc', stroke: '#0b1020', strokeWidth: 2 }" />
    </svg>
    <div class="text-left space-y-2 font-mono text-sm">
      <div class="opacity-80">x = {{ x.toFixed(2) }} · π = ({{ pi[0].toFixed(2) }}, {{ pi[1].toFixed(2) }})</div>
      <div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
        <div class="text-teal-300">π₁N₁ = {{ r.a.toFixed(4) }}</div>
        <div class="text-amber-300">π₂N₂ = {{ r.b.toFixed(4) }}</div>
      </div>
      <div class="flex h-7 rounded-md overflow-hidden text-xs font-bold" style="color: #0b1020">
        <div class="flex items-center justify-center" :style="{ width: `${100 * r.g}%`, background: '#2dd4bf' }">{{ r.g > 0.12 ? r.g.toFixed(3) : '' }}</div>
        <div class="flex items-center justify-center" :style="{ width: `${100 * (1 - r.g)}%`, background: '#fbbf24' }">{{ 1 - r.g > 0.12 ? (1 - r.g).toFixed(3) : '' }}</div>
      </div>
      <div class="text-xs opacity-70 font-sans">γ = each height divided by the sum of the heights</div>
      <div class="text-xs opacity-60 font-sans">Drag the line (or click the plot) to move x.</div>
    </div>
  </div>
</template>
