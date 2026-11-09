<script setup lang="ts">
// Cluster membership as Bayes' rule, on the 1D mixture of the previous slide (data/mix1d.json).
// One probe point x (draggable); for each of the three Gaussians the table builds up
//   step 0: prior pi_k (the weight) · step 1: likelihood N(x | mu_k, sd_k) · step 2: prior × likelihood · step 3: normalize -> gamma_k
// Plot: faint dashed curves are the plain densities (likelihoods), solid filled curves the weighted ones (prior × likelihood).
import { computed, ref } from 'vue'
import d from '../data/mix1d.json'
import { color } from '../utils/clusters'
import { pdf1 } from '../utils/gmm'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const W = 520; const H = 290; const X0 = -5; const X1 = 8; const YMAX = 0.7
const sx = (x: number) => 20 + (x - X0) / (X1 - X0) * (W - 40)
const sy = (y: number) => H - 30 - y / YMAX * (H - 50)
const xs = Array.from({ length: 261 }, (_, i) => X0 + (X1 - X0) * i / 260)
const path = (f: (x: number) => number, close = false) =>
  xs.map((x, i) => `${i ? 'L' : 'M'}${sx(x).toFixed(1)},${sy(f(x)).toFixed(1)}`).join('') + (close ? `L${sx(X1)},${sy(0)}L${sx(X0)},${sy(0)}Z` : '')

const x = ref(-0.5)
const dragging = ref(false)
// The slide is CSS-scaled, so map the pointer through the bounding box (letterbox-safe).
function moveTo(e: PointerEvent) {
  const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
  const k = Math.min(r.width / W, r.height / H)
  const px = (e.clientX - r.left - (r.width - W * k) / 2) / k
  x.value = Math.max(X0, Math.min(X1, X0 + (px - 20) / (W - 40) * (X1 - X0)))
}
function down(e: PointerEvent) {
  dragging.value = true
  ;(e.currentTarget as SVGSVGElement).setPointerCapture(e.pointerId)
  moveTo(e)
}

const lik = computed(() => d.mu.map((m, k) => pdf1(x.value, m, d.sd[k])))
const prod = computed(() => lik.value.map((l, k) => d.w[k] * l))
const gamma = computed(() => { const s = prod.value.reduce((a, b) => a + b, 0); return prod.value.map(p => p / s) })
const fmt = (v: number) => (v < 0.0005 && v > 0 ? v.toExponential(1) : v.toFixed(4))
const rows = [
  { label: 'Prior  πₖ', sub: 'how common is this cluster?' },
  { label: 'Likelihood  N(x | μₖ, σₖ)', sub: 'how well does it explain x?' },
  { label: 'Prior × likelihood', sub: 'unnormalized score' },
  { label: 'Responsibility  γₖ', sub: 'score ÷ sum of the three' },
]
const cell = (r: number, k: number) => [d.w[k].toFixed(2), fmt(lik.value[k]), fmt(prod.value[k]), gamma.value[k].toFixed(3)][r]
</script>

<template>
  <div class="grid grid-cols-[1fr_1.15fr] gap-4 items-center">
    <div>
      <svg
        :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="cursor: ew-resize; touch-action: none" role="img"
        aria-label="Three weighted bell curves with a draggable probe point; the heights at the probe are the prior times likelihood for each cluster"
        @pointerdown="down" @pointermove="dragging && moveTo($event)" @pointerup="dragging = false" @pointercancel="dragging = false"
      >
        <line :x1="sx(X0)" :x2="sx(X1)" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#475569', strokeWidth: 1.5 }" />
        <g :style="{ opacity: step >= 1 ? 1 : 0, transition: 'opacity 0.5s' }">
          <path v-for="(m, k) in d.mu" :key="`u${k}`" :d="path(v => pdf1(v, m, d.sd[k]))" :style="{ fill: 'none', stroke: color(k), strokeWidth: 1.6, strokeDasharray: '5 4', strokeOpacity: 0.55 }" />
        </g>
        <path
          v-for="(m, k) in d.mu" :key="`w${k}`" :d="path(v => d.w[k] * pdf1(v, m, d.sd[k]), true)"
          :style="{ fill: color(k), fillOpacity: 0.22, stroke: color(k), strokeWidth: 2.4, opacity: step >= 2 ? 1 : 0.35, transition: 'opacity 0.5s' }"
        />
        <g v-for="t in [-4, -2, 0, 2, 4, 6]" :key="t">
          <text :x="sx(t)" :y="sy(0) + 16" text-anchor="middle" :style="{ fill: '#64748b', fontSize: '11px' }">{{ t }}</text>
        </g>
        <line :x1="sx(x)" :x2="sx(x)" :y1="12" :y2="sy(0)" :style="{ stroke: '#f8fafc', strokeWidth: 2 }" />
        <rect :x="sx(x) - 7" y="6" width="14" height="22" rx="4" :style="{ fill: '#f8fafc', stroke: '#0b1020', strokeWidth: 2 }" />
        <path :d="`M${sx(x) - 2},${10}V${20}M${sx(x) + 2},${10}V${20}`" :style="{ stroke: '#0b1020', strokeWidth: 1.4 }" />
        <text :x="sx(x)" y="46" text-anchor="middle" :style="{ fill: '#f8fafc', fontSize: '13px', fontWeight: 700 }">x = {{ x.toFixed(2) }}</text>
        <g v-if="step >= 1">
          <circle v-for="(m, k) in d.mu" :key="`pu${k}`" :cx="sx(x)" :cy="sy(lik[k])" r="4.5" :style="{ fill: 'none', stroke: color(k), strokeWidth: 2 }" />
        </g>
        <g v-if="step >= 2">
          <circle v-for="(m, k) in d.mu" :key="`pw${k}`" :cx="sx(x)" :cy="sy(prod[k])" r="5.5" :style="{ fill: color(k), stroke: '#0b1020', strokeWidth: 2 }" />
        </g>
      </svg>
      <slot />
    </div>

    <div class="text-left text-sm">
      <table class="w-full border-separate" style="border-spacing: 0 4px">
        <thead>
          <tr>
            <th />
            <th v-for="(m, k) in d.mu" :key="k" class="font-mono text-xs pb-1" :style="{ color: color(k) }">cluster {{ k + 1 }}<div class="opacity-60 font-sans">μ = {{ m }}</div></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in rows" :key="i" :style="{ opacity: step >= i ? 1 : 0.15, transition: 'opacity 0.4s' }">
            <td class="pr-2">
              <div class="font-bold" :class="i === 3 ? 'text-teal-300' : ''">{{ r.label }}</div>
              <div class="text-xs opacity-60">{{ r.sub }}</div>
            </td>
            <td
              v-for="(m, k) in d.mu" :key="k" class="text-center font-mono rounded-md"
              :style="{ background: i === 3 ? `${color(k)}33` : 'rgba(255,255,255,0.05)', color: color(k), fontWeight: i === 3 ? 700 : 400 }"
            >{{ step >= i ? cell(i, k) : '' }}</td>
          </tr>
        </tbody>
      </table>
      <div class="flex h-8 rounded-md overflow-hidden mt-3 text-sm font-bold" style="color: #0b1020" :style="{ opacity: step >= 3 ? 1 : 0, transition: 'opacity 0.4s' }">
        <div v-for="(g, k) in gamma" :key="k" class="flex items-center justify-center" :style="{ width: `${100 * g}%`, background: color(k) }">{{ g > 0.1 ? g.toFixed(3) : '' }}</div>
      </div>
    </div>
  </div>
</template>
