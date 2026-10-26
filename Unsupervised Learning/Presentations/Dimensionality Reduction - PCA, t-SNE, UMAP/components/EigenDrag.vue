<script setup lang="ts">
// What Σv = λv looks like, with the covariance of the projection cloud (data/drag.json).
// Drag the teal unit vector v around the circle. Amber: Σv. Faint arrows: Σu for 24 unit vectors u, and the
// dashed ellipse is where Σ sends the whole unit circle. Σv is parallel to v only along the ellipse's axes:
// the eigenvectors, where the readout lights up. vᵀΣv (the variance along v) peaks there too.
import { computed, ref } from 'vue'
import d from '../data/drag.json'
import { arrow, eig2, toLocal } from '../utils/plot'

const W = 420; const H = 330; const U = 62
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const S = d.S
const E = eig2(S)
const mul = (u: number[]) => [S[0][0] * u[0] + S[0][1] * u[1], S[1][0] * u[0] + S[1][1] * u[1]]

const th = ref(2.2)
const v = computed(() => [Math.cos(th.value), Math.sin(th.value)])
const Sv = computed(() => mul(v.value))
const q = computed(() => v.value[0] * Sv.value[0] + v.value[1] * Sv.value[1])
const gap = computed(() => { // angle between v and Σv, as a line angle in [0, 90] degrees
  const c = q.value / Math.hypot(Sv.value[0], Sv.value[1])
  return Math.acos(Math.min(1, Math.abs(c))) * 180 / Math.PI
})
const eigen = computed(() => gap.value < 2.5)
const field = Array.from({ length: 24 }, (_, i) => {
  const a = i * Math.PI / 12; const u = [Math.cos(a), Math.sin(a)]; const s = mul(u)
  return arrow(sx(u[0]), sy(u[1]), sx(s[0]), sy(s[1]), 5)
})
const image = Array.from({ length: 73 }, (_, i) => {
  const a = i * Math.PI / 36; const s = mul([Math.cos(a), Math.sin(a)])
  return `${i ? 'L' : 'M'}${sx(s[0]).toFixed(1)},${sy(s[1]).toFixed(1)}`
}).join('')
const av = computed(() => arrow(sx(0), sy(0), sx(v.value[0]), sy(v.value[1])))
const aS = computed(() => arrow(sx(0), sy(0), sx(Sv.value[0]), sy(Sv.value[1])))

const dragging = ref(false)
function moveTo(e: PointerEvent) {
  const [x, y] = toLocal(e, e.currentTarget as Element, W, H)
  let a = Math.atan2(H / 2 - y, x - W / 2)
  // gentle snap so the eigenvectors are easy to land on
  for (const e0 of [E.ang, E.ang + Math.PI / 2, E.ang + Math.PI, E.ang - Math.PI / 2]) {
    const dd = Math.atan2(Math.sin(a - e0), Math.cos(a - e0))
    if (Math.abs(dd) < 0.03) a = e0
  }
  th.value = a
}
function down(e: PointerEvent) {
  dragging.value = true
  ;(e.currentTarget as Element).setPointerCapture(e.pointerId)
  moveTo(e)
}
</script>

<template>
  <div class="grid grid-cols-[1.3fr_1fr] gap-5 items-center">
    <svg
      :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 330px; cursor: grab; touch-action: none" role="img"
      aria-label="A unit vector v and its image under the covariance matrix; they line up only along the eigenvectors"
      @pointerdown="down" @pointermove="dragging && moveTo($event)" @pointerup="dragging = false" @pointercancel="dragging = false"
    >
      <circle :cx="sx(0)" :cy="sy(0)" :r="U" :style="{ fill: 'none', stroke: '#475569', strokeWidth: 1.2 }" />
      <path :d="image" :style="{ fill: '#fbbf24', fillOpacity: 0.05, stroke: '#fbbf24', strokeOpacity: 0.5, strokeDasharray: '5 4' }" />
      <g v-for="(f, i) in field" :key="i" :style="{ stroke: '#94a3b8', strokeOpacity: 0.35, strokeWidth: 1, fill: 'none' }"><path :d="f.line" /><path :d="f.head" /></g>
      <line v-for="s in [-1, 1]" :key="s" :x1="sx(0)" :y1="sy(0)" :x2="sx(s * 2.6 * E.v1[0])" :y2="sy(s * 2.6 * E.v1[1])" :style="{ stroke: '#fbbf24', strokeOpacity: 0.25, strokeDasharray: '2 4' }" />
      <line v-for="s in [-1, 1]" :key="`b${s}`" :x1="sx(0)" :y1="sy(0)" :x2="sx(s * 1.6 * E.v2[0])" :y2="sy(s * 1.6 * E.v2[1])" :style="{ stroke: '#a78bfa', strokeOpacity: 0.3, strokeDasharray: '2 4' }" />
      <g :style="{ stroke: '#fbbf24', strokeWidth: 3.5, fill: 'none' }"><path :d="aS.line" /><path :d="aS.head" /></g>
      <g :style="{ stroke: eigen ? '#a3e635' : '#2dd4bf', strokeWidth: 3.5, fill: 'none' }"><path :d="av.line" /><path :d="av.head" /></g>
      <circle :cx="sx(v[0])" :cy="sy(v[1])" r="9" :style="{ fill: '#2dd4bf', fillOpacity: 0.25, stroke: '#2dd4bf', strokeWidth: 2 }" />
      <text :x="sx(1.25 * v[0])" :y="sy(1.25 * v[1]) + 5" text-anchor="middle" :style="{ fill: '#5eead4', fontSize: '15px', fontWeight: 700 }">v</text>
      <text :x="sx(Sv[0]) + 8" :y="sy(Sv[1]) - 6" :style="{ fill: '#fcd34d', fontSize: '15px', fontWeight: 700 }">Σv</text>
    </svg>
    <div class="text-left space-y-3 font-mono text-sm">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
        <div>angle(v, Σv) = {{ gap.toFixed(1) }}°</div>
        <div class="text-amber-300">vᵀΣv = {{ q.toFixed(3) }}</div>
        <div class="mt-2 font-sans text-xs opacity-60">Drag v around the circle.</div>
      </div>
      <div
        class="rounded-lg px-4 py-3 transition-all duration-300"
        :style="{ border: `2px solid ${eigen ? '#65a30d' : 'rgba(255,255,255,0.05)'}`, background: eigen ? 'rgba(101,163,13,0.2)' : 'rgba(255,255,255,0.03)', opacity: eigen ? 1 : 0.45 }"
      >
        <div class="font-bold" :class="eigen ? 'text-lime-300' : ''">{{ eigen ? 'Eigenvector!' : 'not an eigenvector' }}</div>
        <div v-if="eigen">Σv = {{ q.toFixed(3) }} · v</div>
        <div v-else>Σv points somewhere else</div>
      </div>
      <div class="font-sans text-xs opacity-75">λ₁ = {{ d.lam[0].toFixed(3) }}, λ₂ = {{ d.lam[1].toFixed(3) }}: the largest and smallest values vᵀΣv can take.</div>
    </div>
  </div>
</template>
