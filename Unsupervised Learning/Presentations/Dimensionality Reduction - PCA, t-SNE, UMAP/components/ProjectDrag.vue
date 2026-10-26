<script setup lang="ts">
// Projecting a centered 2D cloud (data/drag.json) onto a unit direction v. Drag anywhere on the plot to turn v;
// until you do, it turns slowly on its own. Amber: each point's projection onto the line. Red: the residual,
// what the 1D summary loses. Right: projected variance + residual variance = total variance (a constant),
// and both as functions of the angle, with the current angle marked. "Snap to PC1" turns v to the top eigenvector.
import { computed, ref } from 'vue'
import d from '../data/drag.json'
import { toLocal, useLoop, useTween } from '../utils/plot'

const W = 440; const H = 320; const U = 46
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const S = d.S
const total = S[0][0] + S[1][1]
const v1ang = Math.atan2(d.v1[1], d.v1[0])
const varAt = (a: number) => S[0][0] * Math.cos(a) ** 2 + 2 * S[0][1] * Math.cos(a) * Math.sin(a) + S[1][1] * Math.sin(a) ** 2

const target = ref(1.9) // radians; tweened when snapping
const th = useTween(() => target.value, 900)
const touched = ref(false)
useLoop((dt) => {
  if (!touched.value) target.value = th.value = th.value + dt * 0.25 // move both: no tween to restart
}, () => { touched.value = false })

const v = computed(() => [Math.cos(th.value), Math.sin(th.value)])
const proj = computed(() => d.pts.map((p) => {
  const t = p[0] * v.value[0] + p[1] * v.value[1]
  return { p, t, q: [t * v.value[0], t * v.value[1]] }
}))
const pv = computed(() => varAt(th.value))
const deg = (a: number) => ((a * 180 / Math.PI) % 180 + 180) % 180

const dragging = ref(false)
function moveTo(e: PointerEvent) {
  const [x, y] = toLocal(e, e.currentTarget as Element, W, H)
  touched.value = true
  // keep the angle continuous (a line has no direction: a and a + pi are the same line)
  let a = Math.atan2(H / 2 - y, x - W / 2)
  while (a - th.value > Math.PI / 2) a -= Math.PI
  while (a - th.value < -Math.PI / 2) a += Math.PI
  target.value = a
  th.value = a
}
function down(e: PointerEvent) {
  dragging.value = true
  ;(e.currentTarget as Element).setPointerCapture(e.pointerId)
  moveTo(e)
}
function snap() {
  touched.value = true
  let a = v1ang
  while (a - th.value > Math.PI / 2) a -= Math.PI
  while (a - th.value < -Math.PI / 2) a += Math.PI
  target.value = a
}

// variance vs angle curve, 0..180 degrees
const CW = 260; const CH = 120
const cx = (a: number) => 10 + a / 180 * (CW - 20)
const cy = (v: number) => CH - 18 - v / total * (CH - 30)
const curve = (f: (a: number) => number) => Array.from({ length: 91 }, (_, i) => `${i ? 'L' : 'M'}${cx(2 * i).toFixed(1)},${cy(f(2 * i * Math.PI / 180)).toFixed(1)}`).join('')
const capPath = curve(varAt)
const resPath = curve(a => total - varAt(a))
</script>

<template>
  <div class="grid grid-cols-[1.35fr_1fr] gap-5 items-center">
    <svg
      :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 330px; cursor: grab; touch-action: none; overflow: hidden" role="img"
      aria-label="A point cloud with a rotatable line; each point is projected onto the line"
      @pointerdown="down" @pointermove="dragging && moveTo($event)" @pointerup="dragging = false" @pointercancel="dragging = false"
    >
      <line :x1="0" :x2="W" :y1="H / 2" :y2="H / 2" :style="{ stroke: '#1e293b' }" />
      <line :x1="W / 2" :x2="W / 2" :y1="0" :y2="H" :style="{ stroke: '#1e293b' }" />
      <line :x1="sx(-6 * v[0])" :y1="sy(-6 * v[1])" :x2="sx(6 * v[0])" :y2="sy(6 * v[1])" :style="{ stroke: '#fbbf24', strokeWidth: 2.5, strokeOpacity: 0.85 }" />
      <line v-for="(o, i) in proj" :key="`r${i}`" :x1="sx(o.p[0])" :y1="sy(o.p[1])" :x2="sx(o.q[0])" :y2="sy(o.q[1])" :style="{ stroke: '#f87171', strokeWidth: 1.2, strokeOpacity: 0.65 }" />
      <circle v-for="(o, i) in proj" :key="`p${i}`" :cx="sx(o.p[0])" :cy="sy(o.p[1])" r="3.6" :style="{ fill: '#cbd5e1' }" />
      <circle v-for="(o, i) in proj" :key="`q${i}`" :cx="sx(o.q[0])" :cy="sy(o.q[1])" r="3" :style="{ fill: '#fbbf24' }" />
      <circle :cx="sx(3.9 * v[0])" :cy="sy(3.9 * v[1])" r="9" :style="{ fill: '#fbbf24', fillOpacity: 0.25, stroke: '#fbbf24', strokeWidth: 2 }" />
      <text :x="sx(4.4 * v[0])" :y="sy(4.4 * v[1]) + 4" text-anchor="middle" :style="{ fill: '#fcd34d', fontSize: '15px', fontWeight: 700 }">v</text>
      <text x="10" :y="H - 10" :style="{ fill: '#64748b', fontSize: '12px' }">drag to turn v</text>
    </svg>
    <div class="text-left space-y-3">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono text-sm">
        <div class="flex justify-between"><span>angle</span><span>{{ deg(th).toFixed(0) }}°</span></div>
        <div class="h-4 rounded-sm overflow-hidden mt-2 flex" style="background: rgba(148,163,184,0.15)">
          <div :style="{ width: `${100 * pv / total}%`, background: '#fbbf24' }" />
          <div :style="{ width: `${100 * (1 - pv / total)}%`, background: '#f87171' }" />
        </div>
        <div class="flex justify-between mt-1"><span class="text-amber-300">kept vᵀΣv = {{ pv.toFixed(2) }}</span><span class="text-red-300">lost {{ (total - pv).toFixed(2) }}</span></div>
        <div class="text-xs opacity-60 mt-1">total variance tr Σ = {{ total.toFixed(2) }}, whatever v is</div>
      </div>
      <svg :viewBox="`0 0 ${CW} ${CH}`" class="w-full" role="img" aria-label="Kept and lost variance as functions of the angle">
        <path :d="capPath" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 2 }" />
        <path :d="resPath" :style="{ fill: 'none', stroke: '#f87171', strokeWidth: 2 }" />
        <line :x1="cx(deg(th))" :x2="cx(deg(th))" y1="6" :y2="CH - 18" :style="{ stroke: '#e2e8f0', strokeOpacity: 0.6 }" />
        <circle :cx="cx(deg(th))" :cy="cy(pv)" r="4.5" :style="{ fill: '#fbbf24' }" />
        <circle :cx="cx(deg(th))" :cy="cy(total - pv)" r="4.5" :style="{ fill: '#f87171' }" />
        <text v-for="a in [0, 90, 180]" :key="a" :x="cx(a)" :y="CH - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ a }}°</text>
      </svg>
      <button class="px-3 py-1 rounded-md text-sm border-2 border-amber-700 bg-amber-800/20 hover:bg-amber-800/40" @click="snap">
        Snap to PC1 · λ₁ = {{ d.lam[0].toFixed(2) }}
      </button>
    </div>
  </div>
</template>
